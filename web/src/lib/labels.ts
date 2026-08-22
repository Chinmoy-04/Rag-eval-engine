import type { PipelineName } from "@/lib/api";

/** Pipeline ids as shown in the UI (matches backend config names). */
export const PIPELINE_LABELS: Record<PipelineName, string> = {
  baseline: "baseline",
  degraded: "degraded",
  optimized: "optimized",
};

export const PIPELINE_DESCRIPTIONS: Record<PipelineName, string> = {
  baseline: "k=4, context-only answers",
  degraded: "k=1, truncated context, may guess",
  optimized: "k=8, query expansion",
};

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
  "Travel and expenses": "Travel & expenses",
  "Remote work": "Remote work",
  "Compensation": "Pay & levels",
  "Security & incidents": "Security & incidents",
  "Trick / abstain": "Outside the handbook",
};

export function categoryLabel(key: string): string {
  return QUESTION_CATEGORY_LABELS[key] ?? key;
}
