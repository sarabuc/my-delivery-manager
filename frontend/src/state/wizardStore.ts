"use client";

import { create } from "zustand";

export type RepoOption = {
  id: number;
  name: string;
};

export type WizardStep = 1 | 2 | 3 | 4 | 5 | 6 | 7;
export type Mode = "branch" | "commit";

export type JobStatus = {
  job_id: string;
  status: string;
  step: string;
  logs: string[];
  blocked_reason?: string | null;
};

export type WizardState = {
  step: WizardStep;
  mode: Mode;
  sourceRepo: RepoOption | null;
  targetRepo: RepoOption | null;
  sourceBranch: string | null;
  targetBranch: string | null;
  selectedCommits: string[];
  includeSubmodules: boolean;
  jobStatus: JobStatus | null;
  logLines: string[];
  setStep: (step: WizardStep) => void;
  setMode: (mode: Mode) => void;
  setSourceRepo: (repo: RepoOption | null) => void;
  setTargetRepo: (repo: RepoOption | null) => void;
  setSourceBranch: (branch: string | null) => void;
  setTargetBranch: (branch: string | null) => void;
  toggleCommit: (commit: string) => void;
  setIncludeSubmodules: (value: boolean) => void;
  setJobStatus: (status: JobStatus | null) => void;
  appendLog: (line: string) => void;
};

export const useWizardStore = create<WizardState>((set) => ({
  step: 1,
  mode: "branch",
  sourceRepo: null,
  targetRepo: null,
  sourceBranch: null,
  targetBranch: null,
  selectedCommits: [],
  includeSubmodules: false,
  jobStatus: null,
  logLines: [],
  setStep: (step) => set({ step }),
  setMode: (mode) => set({ mode }),
  setSourceRepo: (repo) => set({ sourceRepo: repo }),
  setTargetRepo: (repo) => set({ targetRepo: repo }),
  setSourceBranch: (branch) => set({ sourceBranch: branch }),
  setTargetBranch: (branch) => set({ targetBranch: branch }),
  toggleCommit: (commit) =>
    set((state) => ({
      selectedCommits: state.selectedCommits.includes(commit)
        ? state.selectedCommits.filter((item) => item !== commit)
        : [...state.selectedCommits, commit],
    })),
  setIncludeSubmodules: (value) => set({ includeSubmodules: value }),
  setJobStatus: (status) => set({ jobStatus: status }),
  appendLog: (line) => set((state) => ({ logLines: [...state.logLines, line] })),
}));
