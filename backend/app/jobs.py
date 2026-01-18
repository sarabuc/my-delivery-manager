from __future__ import annotations

import dataclasses
import threading
from typing import Dict, List


@dataclasses.dataclass
class JobState:
    job_id: str
    status: str
    step: str
    logs: List[str]
    blocked_reason: str | None = None

    def append(self, message: str) -> None:
        self.logs.append(message)


class JobStore:
    def __init__(self) -> None:
        self._jobs: Dict[str, JobState] = {}
        self._lock = threading.Lock()

    def create(self, job_id: str) -> JobState:
        job = JobState(job_id=job_id, status="queued", step="init", logs=[])
        with self._lock:
            self._jobs[job_id] = job
        return job

    def get(self, job_id: str) -> JobState:
        with self._lock:
            return self._jobs[job_id]

    def update(self, job_id: str, **kwargs: str) -> JobState:
        with self._lock:
            job = self._jobs[job_id]
            for key, value in kwargs.items():
                setattr(job, key, value)
            return job
