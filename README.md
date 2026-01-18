# GitLab Content Delivery Agent

A full-stack wizard for preparing, validating, and delivering code content (branches or commits) between GitLab repositories, including submodule updates and AI-assisted conflict resolution.

## Architecture Overview
- **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS
- **Backend:** FastAPI (Python) with background job execution
- **Integrations:** GitLab API, optional AI conflict resolver

## Prerequisites
- **Node.js** 18+
- **Python** 3.11+
- **Git** CLI available in PATH
- **GitLab token** with repository access

## Configuration
Set these environment variables before running the backend:

```bash
export GITLAB_BASE_URL="https://gitlab.com"  # or your GitLab instance
export GITLAB_TOKEN="<your-token>"
export DELIVERY_WORKSPACE="/tmp/delivery"    # optional
```

For the frontend, you can optionally point to a non-default backend:

```bash
export NEXT_PUBLIC_API_BASE="http://localhost:8000"
```

## Run the Backend (FastAPI)
From the repo root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn requests pydantic

uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Run the Frontend (Next.js)
From the repo root:

```bash
cd frontend
npm install
npm run dev
```

Then open: `http://localhost:3000`

## Running Tests (Backend)
From the repo root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install pytest
pytest backend/tests
```

## Notes
- The backend job runner currently uses an in-memory store and background tasks. For production, replace with a durable queue (e.g., Redis + RQ/Celery) and persistent storage.
- AI conflict resolution requires wiring an AI client into `AIClient` and passing it to `GitManager`.

