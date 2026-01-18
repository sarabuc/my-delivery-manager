# GitLab Content Delivery Agent Blueprint

## Architecture Diagram Description

**Actors**
- **Next.js 14 App Router UI**: Wizard UI with status timeline, progress bars, and log panel.
- **FastAPI Service**: Handles repository inspection, long-running Git operations, AI conflict resolution, and GitLab API interactions.
- **Git Workspaces**: Ephemeral working directories per delivery session (e.g., `/var/tmp/delivery/{job_id}`).
- **External Services**: GitLab API, OpenAI/Anthropic AI provider.

**Communication Pattern**
1. **Frontend → Backend (REST)**: Wizard steps call FastAPI endpoints to fetch metadata and start delivery jobs.
2. **Backend → Frontend (Job Updates)**:
   - **Polling**: Frontend polls `/api/jobs/{job_id}` every 1–2 seconds for status, step progress, and logs.
   - **Optional WebSocket**: For real-time logs, the backend exposes `/ws/jobs/{job_id}` and streams log events.
3. **Backend → Git**: Background tasks run `git` commands in isolated workspaces.
4. **Backend → AI**: On conflict detection, submit diff/context to AI, apply result, and update job status.

**State Model**
- A `DeliveryJob` tracks step states (`pending`, `running`, `blocked`, `failed`, `completed`), logs, and the current repo/submodule context.
- Each job can run in a BackgroundTask or an in-process queue (future-ready for Celery/Redis if higher concurrency is required).

---

## API Schema (Key Endpoints)

### Metadata
- `GET /api/repos`
  - Returns GitLab repos available to the user.
- `GET /api/repos/{repo_id}/branches`
  - Returns branches for a repo.
- `GET /api/repos/{repo_id}/commits?branch=main`
  - Returns commits for a branch.
- `GET /api/repos/{repo_id}/submodules`
  - Returns `.gitmodules` info, if present.

### Delivery Planning & Execution
- `POST /api/delivery/plan`
  - Validates inputs and returns a normalized plan (including submodule selections).
- `POST /api/delivery/execute`
  - Starts a delivery job; returns `{ job_id }`.
- `GET /api/jobs/{job_id}`
  - Returns job status, logs, progress, and block reason (if any).
- `POST /api/jobs/{job_id}/resume`
  - Resumes a job after manual conflict resolution.

### Conflict Handling
- `POST /api/resolve-conflict`
  - Accepts conflict details and attempts AI resolution.

### GitLab
- `POST /api/gitlab/mr`
  - Creates a merge request with CI selection and delivery summary.

---

## Core Code Snippets

### Python: `GitManager` (Rebase / Cherry-Pick)
The `GitManager` class orchestrates checkout, rebase, cherry-pick, and submodule updates with traceable logs and error states.

```python
class GitManager:
    def rebase_delivery(self, source_branch: str, target_branch: str) -> DeliveryResult:
        # checkout source, rebase onto target, resolve conflicts if needed
        ...

    def cherry_pick_delivery(self, target_branch: str, commits: list[str]) -> DeliveryResult:
        # temp branch off target, cherry-pick sequence
        ...
```

### Python: `AIConflictResolver`
The AI resolver receives the diff + conflict markers and attempts a merge. The response includes a confidence score.

```python
def resolve_conflict(diff: str, file_path: str, content: str) -> AIResolution:
    # send structured prompt to LLM
    # return resolved content + confidence
    ...
```

### Frontend: Wizard State Store
A Zustand store keeps step-by-step wizard state in one place.

```ts
const useWizardStore = create<WizardState>((set) => ({
  step: 1,
  sourceRepo: null,
  targetRepo: null,
  setStep: (step) => set({ step }),
}));
```

---

## Error Handling & User Feedback

- **Progress UI**: Stepper + log console. Each backend step emits log entries with severity (info/warn/error).
- **Conflict Block State**: If AI fails or returns low confidence, job transitions to `blocked` and the UI displays a conflict resolver.
- **Retry Mechanics**: For transient failures (network, GitLab API), jobs can be retried from the last stable step.
- **Failure Containment**: Each job runs in an isolated workspace to prevent cross-job contamination.

---

## Testing Strategy (Pytest)

### Fixtures
- `temp_git_repo`: Creates a temporary repo with branches and commits for deterministic testing.
- `mock_openai`: Mock AI response for conflict resolution tests.
- `mock_gitlab`: Mock GitLab MR creation.

### Tests
1. **Cherry-pick Engine**: Ensures commit B is cherry-picked onto target with new hash.
2. **Submodule Pointer Update**: Confirms parent repo records a new submodule hash.
3. **AI Conflict Logic**: Confirms resolved content is applied and rebase continues.

### Self-Verification (Dry Run)
A `--dry-run` mode runs predefined scenarios on temp repos to ensure basic health.
