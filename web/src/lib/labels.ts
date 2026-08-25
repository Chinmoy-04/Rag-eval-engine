/** Preferred display order when the API returns pipeline names. */
export const PIPELINE_ORDER: string[] = [
  "baseline",
  "degraded",
  "optimized",
  "hybrid",
  "hybrid_plus",
  "rerank",
  "csv_route",
];

/** Pipeline ids as shown in the UI (matches backend config names). */
export const PIPELINE_LABELS: Record<string, string> = {
  baseline: "baseline",
  degraded: "degraded",
  optimized: "optimized",
  hybrid: "hybrid",
  hybrid_plus: "hybrid+",
  rerank: "rerank",
  csv_route: "csv route",
};

export const PIPELINE_DESCRIPTIONS: Record<string, string> = {
  baseline: "k=4, dense vector retrieval",
  degraded: "k=1, truncated context, may guess",
  optimized: "k=8, vector + keyword expansion",
  hybrid: "BM25 + dense RRF, k=6",
  hybrid_plus: "hybrid + keyword expansion, k=8",
  rerank: "vector k=16 → lexical rerank → k=6",
  csv_route: "hybrid with CSV metadata boost",
};

const CHART_PALETTE = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
  "var(--chart-6)",
  "var(--chart-7)",
];

const PIPELINE_CHART_COLORS: Record<string, string> = {
  baseline: "var(--chart-2)",
  degraded: "var(--chart-3)",
  optimized: "var(--chart-1)",
  hybrid: "var(--chart-4)",
  hybrid_plus: "var(--chart-5)",
  rerank: "var(--chart-6)",
  csv_route: "var(--chart-7)",
};

export function sortPipelines(names: string[]): string[] {
  const remaining = new Set(names);
  const ordered = PIPELINE_ORDER.filter((name) => remaining.has(name));
  const extras = [...remaining]
    .filter((name) => !PIPELINE_ORDER.includes(name))
    .sort();
  return [...ordered, ...extras];
}

export function pipelineLabel(name: string): string {
  return PIPELINE_LABELS[name] ?? name;
}

export function pipelineDescription(name: string): string {
  return PIPELINE_DESCRIPTIONS[name] ?? name;
}

export function pipelineChartColor(name: string, index = 0): string {
  return PIPELINE_CHART_COLORS[name] ?? CHART_PALETTE[index % CHART_PALETTE.length];
}

/** Ragas metric names (unchanged) with tooltip copy for non-technical readers. */
export const METRIC_LABELS = {
  faithfulness: {
    label: "Faithfulness",
    hint: "Is the answer supported by the retrieved document sections? Low scores mean the model may have added facts not found in the sources.",
  },
  answer_relevancy: {
    label: "Relevancy",
    hint: "Does the answer actually address the question that was asked?",
  },
  context_precision: {
    label: "Precision",
    hint: "Of the document sections retrieved, how many were actually useful for answering the question?",
  },
  context_recall: {
    label: "Recall",
    hint: "Did retrieval find the document sections needed to answer the question completely?",
  },
} as const;

/** Friendlier category titles for suggested questions. */
export const QUESTION_CATEGORY_LABELS: Record<string, string> = {
  "Simple lookup": "Quick facts",
  "PTO and leave": "Time off & leave",
  "On-call (multi-hop)": "On-call duty",
  "On-call schedules (CSV)": "On-call schedules",
  "Travel and expenses": "Travel & expenses",
  "Remote, security, AI": "Remote & security",
  "Tables and matrices": "Handbook tables",
  "Compensation & equity": "Pay & equity bands",
  "API limits & FinOps": "API limits & cloud spend",
  "SOC2 & compliance": "SOC2 controls",
  "Vault & secrets": "Vault & rotation",
  "GPU & Slurm": "GPU cluster",
  "Architecture (ADR)": "Architecture decisions",
  "Vendors & subprocessors": "Vendors & DPAs",
  "Incidents & CVEs": "Incidents & CVEs",
  "Employee directory": "Employee directory",
  "Should abstain": "Outside the handbook",
};

export function categoryLabel(key: string): string {
  return QUESTION_CATEGORY_LABELS[key] ?? key;
}
