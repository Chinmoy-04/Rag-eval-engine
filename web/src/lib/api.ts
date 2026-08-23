export type PipelineName = string;

export interface HealthResponse {
  status: string;
  vectors: number;
  pipelines: string[];
}

export interface AskResponse {
  answer: string;
  sources: string[];
  contexts: string[];
  latency_ms: number;
  pipeline: string;
}

export interface RunOverview {
  run_id: number;
  created_at: string | null;
  corpus_name: string;
  num_questions: number;
  status: string;
  pipelines: string[];
  eval_errors: number;
  avg_faithfulness: number | null;
  notes?: string | null;
}

export interface PipelineScores {
  pipeline: string;
  num_results: number;
  num_errors: number;
  averages: Record<string, number | null>;
  avg_latency_ms: number | null;
}

export interface CompareResponse {
  run_id: number;
  num_questions: number;
  pipelines: PipelineScores[];
  breakdown: Array<Record<string, unknown>>;
}

const API_BASE = import.meta.env.VITE_API_URL ?? "";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || res.statusText);
  }
  return res.json() as Promise<T>;
}

export function getHealth() {
  return apiFetch<HealthResponse>("/api/health");
}

export function getSuggestedQuestions() {
  return apiFetch<Record<string, string[]>>("/api/suggested-questions");
}

export function postAsk(body: {
  question: string;
  pipeline: string;
  show_contexts: boolean;
}) {
  return apiFetch<AskResponse>("/api/ask", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function getRuns() {
  return apiFetch<RunOverview[]>("/api/runs");
}

export function getCompare(runId: number) {
  return apiFetch<CompareResponse>(`/api/runs/${runId}/compare`);
}
