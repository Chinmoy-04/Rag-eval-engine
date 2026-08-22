import { gsap } from "@/providers/SmoothScrollProvider";
import { useEffect, useRef, useState } from "react";
import { getRuns, type RunOverview } from "@/lib/api";
import { METRIC_LABELS } from "@/lib/labels";
import { formatScore } from "@/lib/utils";
import { MetricHint } from "@/components/MetricHint";

export function RunsPage() {
  const [runs, setRuns] = useState<RunOverview[]>([]);
  const [error, setError] = useState<string | null>(null);
  const tableRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getRuns()
      .then(setRuns)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load runs"));
  }, []);

  useEffect(() => {
    if (!tableRef.current || runs.length === 0) return;
    const ctx = gsap.context(() => {
      gsap.from("[data-run-row]", {
        opacity: 0,
        x: -12,
        duration: 0.35,
        stagger: 0.04,
        ease: "power2.out",
      });
    }, tableRef);
    return () => ctx.revert();
  }, [runs]);

  const scored = runs.filter((r) => r.pipelines.length > 0);
  const lastFaith = scored.find((r) => r.avg_faithfulness != null)?.avg_faithfulness;

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Runs</h1>
        <p className="mt-1 text-sm text-hf-muted">
          Evaluation campaigns stored in SQLite.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="hf-panel">
          <p className="hf-label">Total runs</p>
          <p className="mt-1 text-3xl font-semibold">{runs.length}</p>
          <p className="text-xs text-hf-muted">{scored.length} with eval scores</p>
        </div>
        <div className="hf-panel">
          <p className="hf-label flex flex-wrap items-center gap-x-1">
            <span>Last avg</span>
            <MetricHint
              label="Faithfulness"
              hint={METRIC_LABELS.faithfulness.hint}
            />
          </p>
          <p className="mt-1 text-3xl font-semibold">
            {formatScore(lastFaith ?? null)}
          </p>
        </div>
        <div className="hf-panel">
          <p className="hf-label">Latest run</p>
          <p className="mt-1 text-3xl font-semibold">
            {runs[0]?.run_id ?? "—"}
          </p>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-red-500/30 bg-red-950/20 px-4 py-3 text-sm text-red-200">
          {error}
        </div>
      )}

      <div ref={tableRef} className="hf-panel overflow-x-auto" data-lenis-prevent>
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead>
            <tr className="border-b border-hf-border text-hf-muted">
              <th className="pb-3 pr-4 font-mono text-xs uppercase">Run</th>
              <th className="pb-3 pr-4 font-mono text-xs uppercase">Created</th>
              <th className="pb-3 pr-4 font-mono text-xs uppercase">Questions</th>
              <th className="pb-3 pr-4 font-mono text-xs uppercase">Status</th>
              <th className="pb-3 pr-4 font-mono text-xs uppercase">Pipelines</th>
              <th className="pb-3 pr-4 font-mono text-xs uppercase">Errors</th>
              <th className="pb-3 font-mono text-xs uppercase">
                <MetricHint
                  label="Faith"
                  hint={METRIC_LABELS.faithfulness.hint}
                  className="font-mono uppercase"
                />
              </th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => (
              <tr
                key={run.run_id}
                data-run-row
                className="border-b border-hf-border/60 last:border-0"
              >
                <td className="py-3 pr-4 font-mono">{run.run_id}</td>
                <td className="py-3 pr-4 text-hf-muted">
                  {run.created_at
                    ? new Date(run.created_at).toLocaleString()
                    : "—"}
                </td>
                <td className="py-3 pr-4">{run.num_questions}</td>
                <td className="py-3 pr-4">{run.status}</td>
                <td className="py-3 pr-4 text-hf-muted">
                  {run.pipelines.join(", ") || "—"}
                </td>
                <td className="py-3 pr-4">{run.eval_errors}</td>
                <td className="py-3">{formatScore(run.avg_faithfulness)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
