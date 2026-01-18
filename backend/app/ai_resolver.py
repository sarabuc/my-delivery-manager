from __future__ import annotations

import dataclasses
from typing import Protocol


@dataclasses.dataclass
class AIResolution:
    resolved_content: str
    confidence: float
    message: str = ""


class AIClient(Protocol):
    def resolve_conflict(self, prompt: str) -> AIResolution:
        ...


def build_conflict_prompt(diff: str, file_path: str, content: str) -> str:
    return (
        "You are an expert software merge assistant.\n"
        "Resolve the conflict using the diff and file context below.\n"
        "Return ONLY the resolved file content, no explanations.\n\n"
        f"File: {file_path}\n\n"
        "Diff:\n"
        f"{diff}\n\n"
        "Current content with conflict markers:\n"
        f"{content}\n"
    )


def resolve_conflict(diff: str, file_path: str, content: str, client: AIClient | None = None) -> AIResolution:
    prompt = build_conflict_prompt(diff=diff, file_path=file_path, content=content)
    if client is None:
        return AIResolution(
            resolved_content="",
            confidence=0.0,
            message="AI client not configured",
        )
    return client.resolve_conflict(prompt)
