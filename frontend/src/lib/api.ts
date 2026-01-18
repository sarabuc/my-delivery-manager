export type Repo = { id: number; name: string };
export type Branch = { name: string };
export type Commit = { id: string; title: string; author: string };
export type JobStatus = {
  job_id: string;
  status: string;
  step: string;
  logs: string[];
  blocked_reason?: string | null;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {})
    }
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Request failed");
  }
  return response.json() as Promise<T>;
}

export const api = {
  listRepos: () => request<Repo[]>("/api/repos"),
  listBranches: (repoId: number) => request<string[]>(`/api/repos/${repoId}/branches`),
  listCommits: (repoId: number, branch: string) =>
    request<Commit[]>(`/api/repos/${repoId}/commits?branch=${branch}`),
  listSubmodules: (repoId: number) => request<string[]>(`/api/repos/${repoId}/submodules`),
  planDelivery: (payload: unknown) =>
    request("/api/delivery/plan", { method: "POST", body: JSON.stringify(payload) }),
  executeDelivery: (payload: unknown) =>
    request<{ job_id: string }>("/api/delivery/execute", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  fetchJob: (jobId: string) => request<JobStatus>(`/api/jobs/${jobId}`)
};
