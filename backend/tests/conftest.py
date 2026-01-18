from __future__ import annotations

import pathlib
import subprocess
from typing import Generator

import pytest


def _run_git(repo: pathlib.Path, args: list[str]) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


@pytest.fixture()
def temp_git_repo(tmp_path: pathlib.Path) -> Generator[pathlib.Path, None, None]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, ["init"])
    _run_git(repo, ["config", "user.email", "test@example.com"])
    _run_git(repo, ["config", "user.name", "Tester"])
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    _run_git(repo, ["add", "."])
    _run_git(repo, ["commit", "-m", "base"])
    _run_git(repo, ["checkout", "-b", "feature"])
    (repo / "feature.txt").write_text("feature\n", encoding="utf-8")
    _run_git(repo, ["add", "."])
    _run_git(repo, ["commit", "-m", "feature"])
    _run_git(repo, ["checkout", "main"])
    yield repo


@pytest.fixture()
def mock_openai(monkeypatch: pytest.MonkeyPatch):
    from backend.app import ai_resolver

    def _mock_resolve_conflict(*_args, **_kwargs):
        return ai_resolver.AIResolution(
            resolved_content="resolved\n",
            confidence=0.9,
            message="mock",
        )

    monkeypatch.setattr(ai_resolver, "resolve_conflict", _mock_resolve_conflict)


@pytest.fixture()
def mock_gitlab(monkeypatch: pytest.MonkeyPatch):
    class _MockMR:
        def __init__(self):
            self.created_with = None

        def create(self, payload):
            self.created_with = payload
            return {"id": 123}

    mock = _MockMR()
    monkeypatch.setenv("GITLAB_TOKEN", "fake")
    return mock
