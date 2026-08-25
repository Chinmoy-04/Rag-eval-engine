import { gsap } from "@/providers/SmoothScrollProvider";
import { useEffect, useMemo, useRef, useState } from "react";
import { BarChart } from "@/components/charts/bar-chart";
import { Bar } from "@/components/charts/bar";
import { Grid } from "@/components/charts/grid";
import { BarYAxis } from "@/components/charts/bar-y-axis";
import { ChartTooltip } from "@/components/charts/tooltip";
import { RagasCompareCharts } from "@/components/compare/RagasCompareCharts";
import { MetricHint } from "@/components/MetricHint";
import { ThemeSelect } from "@/components/ThemeSelect";
import { getCompare, getRuns, type CompareResponse } from "@/lib/api";
import { METRIC_LABELS, pipelineChartColor, sortPipelines } from "@/lib/labels";
import { formatMs, formatScore } from "@/lib/utils";

const METRIC_KEYS = [
  "faithfulness",
  "answer_relevancy",
  "context_precision",
  "context_recall",
] as const;

export function ComparePage() {
  const [runIds, setRunIds] = useState<number[]>([]);
  const [runId, setRunId] = useState<number | null>(null);
  const [data, setData] = useState<CompareResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const chartsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getRuns()
      .then((runs) => {
        const ids = runs.map((r) => r.run_id);
        setRunIds(ids);
        if (ids.length) setRunId(ids[0]);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load runs"));
  }, []);

  useEffect(() => {
    if (runId == null) return;
    setError(null);
    getCompare(runId)
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : "No scores yet"));
  }, [runId]);

  const latencyRows = useMemo(() => {
    if (!data) return [];
    return sortPipelines(data.pipelines.map((p) => p.pipeline)).map((name, index) => {
      const p = data.pipelines.find((pipe) => pipe.pipeline === name)!;
      return {
        name: p.pipeline,
        seconds:
          typeof p.avg_latency_ms === "number" ? p.avg_latency_ms / 1000 : 0,
        color: pipelineChartColor(p.pipeline, index),
      };
    });
  }, [data]);

  useEffect(() => {
    if (!chartsRef.current || !data) return;
    const ctx = gsap.context(() => {
      gsap.from("[data-chart-panel]", {
        opacity: 0,
        y: 20,
        duration: 0.45,
        stagger: 0.08,
        ease: "power2.out",
        scrollTrigger: {
          trigger: chartsRef.current,
          start: "top 85%",
        },
      });
    }, chartsRef);
    return () => ctx.revert();
  }, [data]);

  const breakdownPipelines = useMemo(() => {
    if (!data?.breakdown.length) return data?.pipelines.map((p) => p.pipeline) ?? [];
    const fromRow = data.breakdown[0]?.pipelines;
    if (Array.isArray(fromRow) && fromRow.length) {
      return fromRow as string[];
    }
    return data.pipelines.map((p) => p.pipeline);
  }, [data]);

  const best = data?.pipelines.reduce((a, b) => {
    const af = a.averages.faithfulness ?? 0;
    const bf = b.averages.faithfulness ?? 0;
    return bf > af ? b : a;
  });

  return (
    <div className="mx-auto max-w-6xl space-y-6 pb-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Compare</h1>
          <p className="mt-1 max-w-xl text-sm leading-relaxed text-hf-muted">
            Same test set, different pipelines — Ragas averages. Hover the{" "}
            <CircleHelpInline /> icons to learn what each metric means.
          </p>
        </div>
        {runIds.length > 0 && (
          <label className="flex items-center gap-2.5 text-sm">
            <span className="hf-label normal-case tracking-normal">Test batch</span>
            <ThemeSelect
              aria-label="Test batch"
              value={runId ?? runIds[0]}
              onChange={setRunId}
              options={runIds.map((id) => ({
                value: id,
                label: `Batch #${id}`,
              }))}
            />
          </label>
        )}
      </div>

      {error && (
        <div className="rounded-xl border border-amber-500/30 bg-amber-950/20 px-4 py-3 text-sm text-amber-100">
          {error}
        </div>
      )}

      {data && (
        <>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="hf-panel">
              <p className="hf-label">
                <MetricHint
                  label="Best faithfulness"
                  hint={METRIC_LABELS.faithfulness.hint}
                />
              </p>
              <p className="mt-1 text-xl font-semibold font-mono">
                {best?.pipeline}{" "}
                · {formatScore(best?.averages.faithfulness ?? null)}
              </p>
            </div>
            <div className="hf-panel">
              <p className="hf-label">Questions tested</p>
              <p className="mt-1 text-xl font-semibold">{data.num_questions}</p>
              <p className="mt-1 text-xs text-hf-muted">
                Each mode answered the same set for a fair comparison.
              </p>
            </div>
          </div>

          <div className="hf-panel">
            <p className="mb-3 text-xs text-hf-muted">
              Ragas metrics — scores from automated evaluation (LLM-as-judge):
            </p>
            <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm">
              {METRIC_KEYS.map((key) => (
                <MetricHint
                  key={key}
                  label={METRIC_LABELS[key].label}
                  hint={METRIC_LABELS[key].hint}
                  className="text-hf-text"
                />
              ))}
            </div>
          </div>

          <div ref={chartsRef} className="space-y-6">
            {runId != null ? (
              <RagasCompareCharts pipelines={data.pipelines} runId={runId} />
            ) : null}

            <div className="hf-panel" data-chart-panel>
              <p className="hf-label mb-1">Average latency</p>
              <p className="mb-3 text-xs text-hf-muted">
                How long each pipeline took to answer (lower is faster).
              </p>
              <BarChart
                key={`latency-${runId}`}
                data={latencyRows}
                xDataKey="name"
                orientation="horizontal"
                aspectRatio="5 / 2"
                className="min-h-[320px] w-full"
                margin={{ top: 16, right: 32, bottom: 24, left: 96 }}
                barGap={0.12}
                revealSignature={`latency-${runId}`}
              >
                <Grid vertical horizontal={false} strokeDasharray="3,6" />
                <Bar dataKey="seconds" fillKey="color" fill="var(--chart-1)" />
                <BarYAxis showAllLabels />
                <ChartTooltip />
              </BarChart>
              <div className="mt-3 flex flex-wrap gap-4 text-xs text-hf-muted">
                {latencyRows.map((row) => (
                  <span key={row.name} className="inline-flex items-center gap-1.5">
                    <span
                      className="size-2.5 rounded-sm"
                      style={{ background: row.color }}
                    />
                    {row.name}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {data.pipelines.map((row) => (
              <div key={row.pipeline} className="hf-panel" data-chart-panel>
                <p className="font-medium font-mono text-hf-text">{row.pipeline}</p>
                <ul className="mt-3 space-y-1.5 text-sm text-hf-muted">
                  {METRIC_KEYS.map((key) => (
                    <li key={key} className="flex items-center justify-between gap-2">
                      <MetricHint
                        label={METRIC_LABELS[key].label}
                        hint={METRIC_LABELS[key].hint}
                      />
                      <span className="font-mono text-hf-text">
                        {formatScore(row.averages[key] ?? null)}
                      </span>
                    </li>
                  ))}
                  <li className="flex items-center justify-between gap-2 pt-1">
                    <span className="text-hf-text">Latency</span>
                    <span className="font-mono">{formatMs(row.avg_latency_ms)}</span>
                  </li>
                  <li className="text-xs">
                    {row.num_results} results · {row.num_errors} errors
                  </li>
                </ul>
              </div>
            ))}
          </div>

          <details className="hf-panel" data-lenis-prevent>
            <summary className="cursor-pointer text-sm text-hf-muted">
              Per-question faithfulness ({data.breakdown.length} items)
            </summary>
            <div className="mt-4 max-h-96 overflow-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-hf-border text-hf-muted">
                    <th className="pb-2 pr-3">Question</th>
                    <th className="pb-2 pr-3">Type</th>
                    {breakdownPipelines.map((pipe) => (
                      <th key={pipe} className="pb-2 pr-3 last:pr-0">
                        {pipe}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data.breakdown.map((row, i) => (
                    <tr key={i} className="border-b border-hf-border/50">
                      <td className="max-w-xs truncate py-2 pr-3">
                        {String(row.question ?? "")}
                      </td>
                      <td className="py-2 pr-3">{String(row.type ?? "")}</td>
                      {breakdownPipelines.map((pipe) => (
                        <td key={pipe} className="py-2 pr-3 font-mono last:pr-0">
                          {formatScore(row[`${pipe}_faithfulness`] as number | null)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </details>
        </>
      )}
    </div>
  );
}

function CircleHelpInline() {
  return (
    <span className="inline-flex align-middle text-hf-muted">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden
      >
        <circle cx="12" cy="12" r="10" />
        <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
        <path d="M12 17h.01" />
      </svg>
    </span>
  );
}
