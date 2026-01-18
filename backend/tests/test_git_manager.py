from __future__ import annotations

import pathlib
import subprocess

from backend.app.git_manager import GitManager


def _run_git(repo: pathlib.Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def test_cherry_pick_engine(temp_git_repo: pathlib.Path):
    repo = temp_git_repo
    _run_git(repo, ["checkout", "feature"])
    (repo / "bugfix.txt").write_text("fix\n", encoding="utf-8")
    _run_git(repo, ["add", "."])
    _run_git(repo, ["commit", "-m", "fix"])
    commit_hash = _run_git(repo, ["rev-parse", "HEAD"])
    _run_git(repo, ["checkout", "main"])

    manager = GitManager(repo)
    result = manager.cherry_pick_delivery("main", [commit_hash])

    _run_git(repo, ["checkout", result.branch])
    log = _run_git(repo, ["log", "--oneline", "-1"])
    assert "fix" in log
    assert commit_hash not in log


def test_submodule_pointer_update(temp_git_repo: pathlib.Path):
    repo = temp_git_repo
    submodule = repo / "sub"
    submodule.mkdir()
    _run_git(submodule, ["init"])
    _run_git(submodule, ["config", "user.email", "test@example.com"])
    _run_git(submodule, ["config", "user.name", "Tester"])
    (submodule / "lib.txt").write_text("v1\n", encoding="utf-8")
    _run_git(submodule, ["add", "."])
    _run_git(submodule, ["commit", "-m", "v1"])
    _run_git(repo, ["submodule", "add", "./sub", "libs/sub"])
    _run_git(repo, ["commit", "-m", "add submodule"])

    (submodule / "lib.txt").write_text("v2\n", encoding="utf-8")
    _run_git(submodule, ["add", "."])
    _run_git(submodule, ["commit", "-m", "v2"])

    manager = GitManager(repo)
    logs: list[str] = []
    manager.update_submodule_pointer(pathlib.Path("libs/sub"), logs)

    diff = _run_git(repo, ["diff", "--cached"])
    assert "+Subproject commit" in diff


def test_ai_conflict_logic(temp_git_repo: pathlib.Path, mock_openai):
    repo = temp_git_repo
    _run_git(repo, ["checkout", "-b", "branch-a"])
    (repo / "conflict.txt").write_text("Hello World\n", encoding="utf-8")
    _run_git(repo, ["add", "."])
    _run_git(repo, ["commit", "-m", "a"])

    _run_git(repo, ["checkout", "main"])
    (repo / "conflict.txt").write_text("Hello Git\n", encoding="utf-8")
    _run_git(repo, ["add", "."])
    _run_git(repo, ["commit", "-m", "b"])

    manager = GitManager(repo)
    result = manager.rebase_delivery("branch-a", "main")

    assert result.conflicts_resolved == 1
    content = (repo / "conflict.txt").read_text(encoding="utf-8")
    assert "resolved" in content
