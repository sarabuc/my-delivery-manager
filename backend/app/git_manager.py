from __future__ import annotations

import dataclasses
import pathlib
import subprocess
import time
from typing import Callable, Iterable, Optional

from .ai_resolver import AIClient, AIResolution, resolve_conflict


class GitCommandError(RuntimeError):
    def __init__(self, message: str, command: list[str], output: str) -> None:
        super().__init__(message)
        self.command = command
        self.output = output


@dataclasses.dataclass
class DeliveryResult:
    branch: str
    logs: list[str]
    conflicts_resolved: int = 0


@dataclasses.dataclass
class ConflictContext:
    path: pathlib.Path
    diff: str
    content: str


class GitManager:
    def __init__(
        self,
        repo_path: pathlib.Path,
        log_sink: Optional[Callable[[str], None]] = None,
        ai_client: AIClient | None = None,
    ) -> None:
        self.repo_path = repo_path
        self.log_sink = log_sink or (lambda _: None)
        self.ai_client = ai_client

    def rebase_delivery(self, source_branch: str, target_branch: str) -> DeliveryResult:
        logs: list[str] = []
        self._log(logs, f"Starting rebase delivery: {source_branch} -> {target_branch}")
        self._checkout(source_branch, logs)
        self._run_git(["fetch", "--all"], logs)
        try:
            self._run_git(["rebase", target_branch], logs)
        except GitCommandError:
            self._log(logs, "Rebase conflict detected, invoking resolver")
            resolved = self._resolve_conflicts(logs)
            self._run_git(["rebase", "--continue"], logs)
            return DeliveryResult(branch=source_branch, logs=logs, conflicts_resolved=resolved)
        return DeliveryResult(branch=source_branch, logs=logs)

    def cherry_pick_delivery(self, target_branch: str, commits: Iterable[str]) -> DeliveryResult:
        logs: list[str] = []
        temp_branch = f"delivery/cherry-pick-{int(time.time())}"
        self._log(logs, f"Starting cherry-pick delivery onto {target_branch}")
        self._checkout(target_branch, logs)
        self._run_git(["checkout", "-b", temp_branch], logs)
        resolved = 0
        for commit in commits:
            try:
                self._run_git(["cherry-pick", commit], logs)
            except GitCommandError:
                self._log(logs, f"Cherry-pick conflict detected on {commit}")
                resolved += self._resolve_conflicts(logs)
                self._run_git(["cherry-pick", "--continue"], logs)
        return DeliveryResult(branch=temp_branch, logs=logs, conflicts_resolved=resolved)

    def update_submodule_pointer(self, submodule_path: pathlib.Path, logs: list[str]) -> None:
        self._log(logs, f"Updating submodule pointer for {submodule_path}")
        self._run_git(["add", str(submodule_path)], logs)

    def collect_conflict_contexts(self) -> list[ConflictContext]:
        diff = self._run_git(["diff"], None)
        conflicts = []
        for line in diff.splitlines():
            if line.startswith("+++ b/"):
                path = pathlib.Path(line.replace("+++ b/", ""))
                content = (self.repo_path / path).read_text(encoding="utf-8")
                conflicts.append(ConflictContext(path=path, diff=diff, content=content))
        return conflicts

    def _resolve_conflicts(self, logs: list[str]) -> int:
        conflicts = self.collect_conflict_contexts()
        resolved = 0
        for conflict in conflicts:
            self._log(logs, f"Resolving {conflict.path}")
            resolution: AIResolution = resolve_conflict(
                diff=conflict.diff,
                file_path=str(conflict.path),
                content=conflict.content,
                client=self.ai_client,
            )
            if not resolution.resolved_content or resolution.confidence < 0.7:
                raise GitCommandError(
                    "AI resolution confidence too low",
                    ["resolve_conflict"],
                    resolution.message,
                )
            (self.repo_path / conflict.path).write_text(
                resolution.resolved_content,
                encoding="utf-8",
            )
            self._run_git(["add", str(conflict.path)], logs)
            resolved += 1
        return resolved

    def _checkout(self, branch: str, logs: list[str]) -> None:
        self._run_git(["checkout", branch], logs)

    def _run_git(self, args: list[str], logs: Optional[list[str]]) -> str:
        command = ["git", *args]
        result = subprocess.run(
            command,
            cwd=self.repo_path,
            check=False,
            capture_output=True,
            text=True,
        )
        output = (result.stdout + result.stderr).strip()
        if logs is not None:
            self._log(logs, f"$ {' '.join(command)}")
            if output:
                self._log(logs, output)
        if result.returncode != 0:
            raise GitCommandError("Git command failed", command, output)
        return output

    def _log(self, logs: list[str], message: str) -> None:
        logs.append(message)
        self.log_sink(message)
