"use client";

import { useEffect, useMemo, useState } from "react";

import { LogPanel } from "@/components/LogPanel";
import { StepCard } from "@/components/StepCard";
import { Stepper } from "@/components/Stepper";
import { Button } from "@/components/ui/Button";
import { api } from "@/lib/api";
import { useWizardStore } from "@/state/wizardStore";

const modes = [
  { id: "branch", label: "Branch rebase" },
  { id: "commit", label: "Commit cherry-pick" }
] as const;

export default function HomePage() {
  const {
    step,
    sourceRepo,
    targetRepo,
    sourceBranch,
    targetBranch,
    selectedCommits,
    includeSubmodules,
    mode,
    jobStatus,
    setStep,
    setSourceRepo,
    setTargetRepo,
    setSourceBranch,
    setTargetBranch,
    toggleCommit,
    setIncludeSubmodules,
    setMode,
    setJobStatus,
    appendLog
  } = useWizardStore();

  const [repos, setRepos] = useState<{ id: number; name: string }[]>([]);
  const [sourceBranches, setSourceBranches] = useState<string[]>([]);
  const [targetBranches, setTargetBranches] = useState<string[]>([]);
  const [commits, setCommits] = useState<{ id: string; title: string; author: string }[]>([]);

  const canContinue = useMemo(() => {
    if (step === 1) {
      return Boolean(sourceRepo && targetRepo);
    }
    if (step === 2) {
      return Boolean(sourceBranch && targetBranch);
    }
    return true;
  }, [step, sourceRepo, targetRepo, sourceBranch, targetBranch]);

  useEffect(() => {
    api
      .listRepos()
      .then(setRepos)
      .catch((error) => appendLog(`Repo load failed: ${error.message}`));
  }, [appendLog]);

  useEffect(() => {
    if (!sourceRepo) return;
    api
      .listBranches(sourceRepo.id)
      .then(setSourceBranches)
      .catch((error) => appendLog(`Source branches failed: ${error.message}`));
  }, [appendLog, sourceRepo]);

  useEffect(() => {
    if (!targetRepo) return;
    api
      .listBranches(targetRepo.id)
      .then(setTargetBranches)
      .catch((error) => appendLog(`Target branches failed: ${error.message}`));
  }, [appendLog, targetRepo]);

  useEffect(() => {
    if (!sourceRepo || !sourceBranch || mode !== "commit") return;
    api
      .listCommits(sourceRepo.id, sourceBranch)
      .then(setCommits)
      .catch((error) => appendLog(`Commit list failed: ${error.message}`));
  }, [appendLog, mode, sourceBranch, sourceRepo]);

  const startDelivery = async () => {
    if (!sourceRepo || !targetRepo || !sourceBranch || !targetBranch) return;
    const payload = {
      source_repo: sourceRepo,
      target_repo: targetRepo,
      source_branch: sourceBranch,
      target_branch: targetBranch,
      mode,
      commits: selectedCommits,
      include_submodules: includeSubmodules
    };
    try {
      const response = await api.executeDelivery(payload);
      setJobStatus({ job_id: response.job_id, status: "queued", step: "init", logs: [] });
    } catch (error) {
      appendLog(`Execution failed: ${(error as Error).message}`);
    }
  };

  useEffect(() => {
    if (!jobStatus?.job_id) return;
    const interval = window.setInterval(async () => {
      try {
        const status = await api.fetchJob(jobStatus.job_id);
        setJobStatus(status);
      } catch (error) {
        appendLog(`Job polling failed: ${(error as Error).message}`);
      }
    }, 1500);
    return () => window.clearInterval(interval);
  }, [appendLog, jobStatus?.job_id, setJobStatus]);

  return (
    <div className="space-y-6">
      <Stepper current={step} />

      <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
        <div className="space-y-6">
          <StepCard title="Step 1 · Repository Selection">
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="text-xs font-semibold uppercase text-slate-500">Source Repo</label>
                <select
                  className="mt-2 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                  value={sourceRepo?.id ?? ""}
                  onChange={(event) => {
                    const repo = repos.find((item) => item.id === Number(event.target.value)) ?? null;
                    setSourceRepo(repo);
                  }}
                >
                  <option value="">Select repository</option>
                  {repos.map((repo) => (
                    <option key={repo.id} value={repo.id}>
                      {repo.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold uppercase text-slate-500">Target Repo</label>
                <select
                  className="mt-2 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                  value={targetRepo?.id ?? ""}
                  onChange={(event) => {
                    const repo = repos.find((item) => item.id === Number(event.target.value)) ?? null;
                    setTargetRepo(repo);
                  }}
                >
                  <option value="">Select repository</option>
                  {repos.map((repo) => (
                    <option key={repo.id} value={repo.id}>
                      {repo.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </StepCard>

          <StepCard title="Step 2 · Content Selection">
            <div className="flex flex-wrap gap-2">
              {modes.map((item) => (
                <button
                  key={item.id}
                  className={`rounded-full border px-3 py-1 text-xs font-semibold ${
                    mode === item.id
                      ? "border-brand-500 bg-brand-500 text-white"
                      : "border-slate-200 bg-white text-slate-600"
                  }`}
                  onClick={() => setMode(item.id)}
                  type="button"
                >
                  {item.label}
                </button>
              ))}
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="text-xs font-semibold uppercase text-slate-500">Source Branch</label>
                <select
                  className="mt-2 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                  value={sourceBranch ?? ""}
                  onChange={(event) => setSourceBranch(event.target.value)}
                >
                  <option value="">Select branch</option>
                  {sourceBranches.map((branch) => (
                    <option key={branch} value={branch}>
                      {branch}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold uppercase text-slate-500">Target Branch</label>
                <select
                  className="mt-2 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                  value={targetBranch ?? ""}
                  onChange={(event) => setTargetBranch(event.target.value)}
                >
                  <option value="">Select branch</option>
                  {targetBranches.map((branch) => (
                    <option key={branch} value={branch}>
                      {branch}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            {mode === "commit" && (
              <div>
                <p className="text-xs font-semibold uppercase text-slate-500">Select commits</p>
                <div className="mt-2 space-y-2">
                  {commits.map((commit) => (
                    <label key={commit.id} className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={selectedCommits.includes(commit.id)}
                        onChange={() => toggleCommit(commit.id)}
                      />
                      <span className="font-medium text-slate-700">{commit.title}</span>
                      <span className="text-xs text-slate-400">{commit.author}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}
          </StepCard>

          <StepCard title="Step 3 · Submodule Handling">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={includeSubmodules}
                onChange={(event) => setIncludeSubmodules(event.target.checked)}
              />
              Deliver selected submodules and update pointers in the parent repo.
            </label>
          </StepCard>

          <StepCard title="Step 4 · Execution Strategy">
            <p>
              The agent will {mode === "branch" ? "rebase" : "cherry-pick"} your selected content onto
              the target branch and run AI conflict resolution when needed.
            </p>
          </StepCard>

          <StepCard title="Step 5 · Submodule Updates">
            <p>
              Selected submodules are processed first. The parent repository will stage updated submodule
              pointers and include them in the final delivery branch.
            </p>
          </StepCard>

          <StepCard title="Step 6 · CI Selection">
            <input
              className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
              placeholder="CI job to trigger (optional)"
            />
          </StepCard>

          <StepCard title="Step 7 · Finalize & Create MR">
            <p>
              The delivery branch will be pushed to GitLab and an MR will be created with a summary of
              delivered commits and submodules.
            </p>
            <div className="flex flex-wrap gap-3">
              <Button
                className="bg-brand-500 text-white hover:bg-brand-600 disabled:cursor-not-allowed disabled:opacity-50"
                onClick={startDelivery}
                disabled={!canContinue}
              >
                Start delivery
              </Button>
              <Button
                className="border border-slate-200 text-slate-600 hover:bg-slate-100"
                onClick={() => setStep(Math.min(7, step + 1) as typeof step)}
              >
                Next step
              </Button>
              <Button
                className="border border-slate-200 text-slate-600 hover:bg-slate-100"
                onClick={() => setStep(Math.max(1, step - 1) as typeof step)}
              >
                Previous step
              </Button>
            </div>
          </StepCard>
        </div>

        <aside className="space-y-6">
          <StepCard title="Job Status">
            <p className="text-sm text-slate-700">
              {jobStatus
                ? `Job ${jobStatus.job_id} · ${jobStatus.status} · ${jobStatus.step}`
                : "No job running yet."}
            </p>
            {jobStatus?.blocked_reason && (
              <p className="text-xs text-amber-600">Blocked: {jobStatus.blocked_reason}</p>
            )}
          </StepCard>
          <LogPanel logs={jobStatus?.logs ?? []} />
        </aside>
      </div>
    </div>
  );
}
