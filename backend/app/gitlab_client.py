from __future__ import annotations

import dataclasses
from typing import Any

import requests


@dataclasses.dataclass
class GitLabConfig:
    base_url: str
    token: str


class GitLabClient:
    def __init__(self, config: GitLabConfig) -> None:
        self.config = config

    def list_repos(self) -> list[dict[str, Any]]:
        return self._get("/api/v4/projects", params={"membership": True})

    def list_branches(self, repo_id: int) -> list[dict[str, Any]]:
        return self._get(f"/api/v4/projects/{repo_id}/repository/branches")

    def list_commits(self, repo_id: int, branch: str) -> list[dict[str, Any]]:
        return self._get(
            f"/api/v4/projects/{repo_id}/repository/commits",
            params={"ref_name": branch, "per_page": 50},
        )

    def list_submodules(self, repo_id: int) -> list[str]:
        tree = self._get(f"/api/v4/projects/{repo_id}/repository/tree", params={"recursive": True})
        return [item["path"] for item in tree if item.get("name") == ".gitmodules"]

    def create_merge_request(self, repo_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        return self._post(f"/api/v4/projects/{repo_id}/merge_requests", payload)

    def _get(self, path: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        response = requests.get(
            f"{self.config.base_url}{path}",
            headers={"PRIVATE-TOKEN": self.config.token},
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = requests.post(
            f"{self.config.base_url}{path}",
            headers={"PRIVATE-TOKEN": self.config.token},
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
