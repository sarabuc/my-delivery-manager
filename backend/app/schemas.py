from __future__ import annotations

from pydantic import BaseModel, Field


class RepoRef(BaseModel):
    repo_id: int
    name: str


class CommitRef(BaseModel):
    id: str
    title: str
    author: str


class DeliveryPlan(BaseModel):
    source_repo: RepoRef
    target_repo: RepoRef
    source_branch: str
    target_branch: str
    mode: str = Field(pattern="^(branch|commit)$")
    commits: list[str] = []
    include_submodules: bool = False
    ci_job: str | None = None


class DeliveryExecuteResponse(BaseModel):
    job_id: str


class JobStatus(BaseModel):
    job_id: str
    status: str
    step: str
    logs: list[str]
    blocked_reason: str | None = None
