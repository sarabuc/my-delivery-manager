from __future__ import annotations

import os
import pathlib
import uuid
from typing import Dict

from fastapi import BackgroundTasks, FastAPI, HTTPException

from .git_manager import GitManager
from .gitlab_client import GitLabClient, GitLabConfig
from .jobs import JobStore
from .schemas import CommitRef, DeliveryExecuteResponse, DeliveryPlan, JobStatus

app = FastAPI(title="GitLab Content Delivery Agent")

JOB_STORE = JobStore()


def _get_gitlab_client() -> GitLabClient:
    base_url = os.environ.get("GITLAB_BASE_URL", "https://gitlab.com")
    token = os.environ.get("GITLAB_TOKEN")
    if not token:
        raise HTTPException(status_code=401, detail="Missing GitLab token")
    return GitLabClient(GitLabConfig(base_url=base_url, token=token))


@app.get("/api/repos")
def list_repos() -> list[dict]:
    client = _get_gitlab_client()
    repos = client.list_repos()
    return [{"id": repo["id"], "name": repo["name"]} for repo in repos]


@app.get("/api/repos/{repo_id}/branches")
def list_branches(repo_id: int) -> list[str]:
    client = _get_gitlab_client()
    branches = client.list_branches(repo_id)
    return [branch["name"] for branch in branches]


@app.get("/api/repos/{repo_id}/commits")
def list_commits(repo_id: int, branch: str) -> list[CommitRef]:
    client = _get_gitlab_client()
    commits = client.list_commits(repo_id, branch)
    return [
        CommitRef(id=commit["id"], title=commit["title"], author=commit["author_name"])
        for commit in commits
    ]


@app.get("/api/repos/{repo_id}/submodules")
def list_submodules(repo_id: int) -> list[str]:
    client = _get_gitlab_client()
    return client.list_submodules(repo_id)


@app.post("/api/delivery/plan")
def plan_delivery(plan: DeliveryPlan) -> DeliveryPlan:
    if plan.mode == "commit" and not plan.commits:
        raise HTTPException(status_code=400, detail="Commit mode requires commits")
    return plan


@app.post("/api/delivery/execute", response_model=DeliveryExecuteResponse)
def execute_delivery(plan: DeliveryPlan, background_tasks: BackgroundTasks) -> DeliveryExecuteResponse:
    job_id = str(uuid.uuid4())
    JOB_STORE.create(job_id)
    background_tasks.add_task(_run_job, job_id, plan)
    return DeliveryExecuteResponse(job_id=job_id)


@app.get("/api/jobs/{job_id}", response_model=JobStatus)
def get_job(job_id: str) -> JobStatus:
    job = JOB_STORE.get(job_id)
    return JobStatus(
        job_id=job.job_id,
        status=job.status,
        step=job.step,
        logs=job.logs,
        blocked_reason=job.blocked_reason,
    )


def _run_job(job_id: str, plan: DeliveryPlan) -> None:
    job = JOB_STORE.update(job_id, status="running", step="prepare")
    job.append(f"Preparing workspace for {plan.source_branch} -> {plan.target_branch}")

    workspace_root = pathlib.Path(os.environ.get("DELIVERY_WORKSPACE", "/tmp/delivery"))
    workspace = workspace_root / job_id
    workspace.mkdir(parents=True, exist_ok=True)

    job.append("Workspace created")
    job.step = "execute"

    repo_path = workspace / "repo"
    repo_path.mkdir(exist_ok=True)

    manager = GitManager(repo_path=repo_path, log_sink=job.append)
    try:
        if plan.mode == "branch":
            job.append("Executing rebase delivery")
            manager.rebase_delivery(plan.source_branch, plan.target_branch)
        else:
            job.append("Executing cherry-pick delivery")
            manager.cherry_pick_delivery(plan.target_branch, plan.commits)
        job.step = "finalize"
        job.append("Delivery execution complete")
        job.status = "completed"
        job.step = "done"
    except Exception as error:  # noqa: BLE001
        job.status = "failed"
        job.step = "error"
        job.append(f"Job failed: {error}")
