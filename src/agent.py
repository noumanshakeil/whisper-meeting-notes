"""Tiny ReAct-style agent loop (rule + optional LLM hook)."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from .tools import TOOLS

@dataclass
class Step:
    thought: str
    action: str | None = None
    action_input: str | None = None
    observation: str | None = None

@dataclass
class AgentResult:
    answer: str
    trace: list[Step] = field(default_factory=list)

ACTION_RE = re.compile(r"Action:\s*(\w+)\s*Input:\s*(.+)", re.I)

def plan(question: str) -> list[Step]:
    q = question.lower()
    steps: list[Step] = []
    if any(c in question for c in "+-*/") or "calculate" in q:
        expr = re.findall(r"[0-9\.+\-\*/\(\) ]+", question)
        steps.append(Step("Need math", "calculator", (expr[0] if expr else "1+1").strip()))
    elif "http://" in q or "https://" in q:
        url = re.findall(r"https?://\S+", question)
        steps.append(Step("Fetch URL", "http_get", url[0] if url else "https://example.com"))
    elif "read" in q and ".txt" in q:
        path = re.findall(r"[\w./\\-]+\.txt", question)
        steps.append(Step("Read file", "read_file", path[0] if path else "README.md"))
    else:
        steps.append(Step("No tool needed — answer directly"))
    return steps

def run_agent(question: str) -> AgentResult:
    trace = plan(question)
    observations = []
    for step in trace:
        if step.action and step.action in TOOLS:
            step.observation = TOOLS[step.action](step.action_input or "")
            observations.append(step.observation)
    if observations:
        answer = " | ".join(observations)
    else:
        answer = (
            f"(demo) I would ask an LLM to answer: {question}. "
            "Wire Ollama/OpenAI in src/agent.py for live generations."
        )
    return AgentResult(answer=answer, trace=trace)

def dump_trace(result: AgentResult) -> str:
    return json.dumps(
        [
            {
                "thought": s.thought,
                "action": s.action,
                "input": s.action_input,
                "observation": s.observation,
            }
            for s in result.trace
        ],
        indent=2,
    )
