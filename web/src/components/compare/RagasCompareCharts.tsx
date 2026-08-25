import { useMemo, useState } from "react";
import { BarChart } from "@/components/charts/bar-chart";
import { Bar } from "@/components/charts/bar";
import { Grid } from "@/components/charts/grid";
import { BarYAxis } from "@/components/charts/bar-y-axis";
import { ChartTooltip } from "@/components/charts/tooltip";
import { RadarChart } from "@/components/charts/radar-chart";
import { RadarGrid } from "@/components/charts/radar-grid";
import { RadarAxis } from "@/components/charts/radar-axis";
import { RadarLabels } from "@/components/charts/radar-labels";
import { RadarArea } from "@/components/charts/radar-area";
import type { RadarData, RadarMetric } from "@/components/charts/radar-context";
import { MetricHint } from "@/components/MetricHint";
import {
  METRIC_LABELS,
  pipelineChartColor,
  pipelineLabel,
  sortPipelines,
} from "@/lib/labels";
import type { PipelineScores } from "@/lib/api";
import { cn } from "@/lib/utils";

const METRIC_KEYS = [
  "faithfulness",
  "answer_relevancy",
  "context_precision",
  "context_recall",
] as const;

type MetricKey = (typeof METRIC_KEYS)[number];

const RADAR_METRICS: RadarMetric[] = METRIC_KEYS.map((key) => ({
  key,
  label: METRIC_LABELS[key].label,
}));

type RagasCompareChartsProps = {
  pipelines: PipelineScores[];
  runId: number;
};

export function RagasCompareCharts({ pipelines, runId }: RagasCompareChartsProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [hidden, setHidden] = useState<Set<string>>(() => new Set());

  const ordered = useMemo(
    () =>
      sortPipelines(pipelines.map((p) => p.pipeline)).map(
        (name) => pipelines.find((p) => p.pipeline === name)!,
      ),
    [pipelines],
  );

  const visible = useMemo(
    () => ordered.filter((p) => !hidden.has(p.pipeline)),
    [ordered, hidden],
  );

  const radarData: RadarData[] = useMemo(
    () =>
      visible.map((p, index) => ({
        label: pipelineLabel(p.pipeline),
        color: pipelineChartColor(p.pipeline, index),
        values: Object.fromEntries(
          METRIC_KEYS.map((key) => [
            key,
            Math.round((p.averages[key] ?? 0) * 100),
          ]),
        ),
      })),
    [visible],
  );

  const togglePipeline = (pipeline: string) => {
    setHidden((prev) => {
      const next = new Set(prev);
      if (next.has(pipeline)) next.delete(pipeline);
      else next.add(pipeline);
      return next;
    });
    setHoveredIndex(null);
  };

  return (
    <div className="space-y-6">
      <div className="hf-panel" data-chart-panel>
        <p className="hf-label mb-1">Pipeline profiles</p>
        <p className="mb-4 text-xs text-hf-muted">
          Radar view — hover a pipeline or use the legend to focus. Scores are
          0–100 (Ragas average × 100).
        </p>
        <div className="mx-auto max-w-lg">
          <RadarChart
            key={`radar-${runId}-${visible.length}`}
            data={radarData}
            metrics={RADAR_METRICS}
            className="aspect-square w-full"
            hoveredIndex={hoveredIndex}
            onHoverChange={setHoveredIndex}
            motionReplayKey={`radar-${runId}`}
          >
            <RadarGrid />
            <RadarAxis />
            <RadarLabels />
            {radarData.map((_, index) => (
              <RadarArea key={visible[index]?.pipeline ?? index} index={index} />
            ))}
          </RadarChart>
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          {ordered.map((p, index) => {
            const isHidden = hidden.has(p.pipeline);
            const isHovered = hoveredIndex === visible.findIndex((v) => v.pipeline === p.pipeline);
            const color = pipelineChartColor(p.pipeline, index);
            return (
              <button
                key={p.pipeline}
                type="button"
                onClick={() => togglePipeline(p.pipeline)}
                onMouseEnter={() => {
                  if (isHidden) return;
                  const idx = visible.findIndex((v) => v.pipeline === p.pipeline);
                  if (idx >= 0) setHoveredIndex(idx);
                }}
                onMouseLeave={() => setHoveredIndex(null)}
                className={cn(
                  "inline-flex items-center gap-1.5 rounded-lg border px-2.5 py-1 text-xs transition-colors",
                  isHidden
                    ? "border-hf-border/60 text-hf-muted opacity-50"
                    : isHovered
                      ? "border-hf-teal/50 bg-hf-teal-dim text-hf-teal"
                      : "border-hf-border text-hf-text hover:border-hf-teal/30",
                )}
              >
                <span
                  className="size-2.5 shrink-0 rounded-sm"
                  style={{ background: isHidden ? "var(--hf-border)" : color }}
                />
                {pipelineLabel(p.pipeline)}
              </button>
            );
          })}
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {METRIC_KEYS.map((key) => (
          <MetricPanel
            key={key}
            metricKey={key}
            runId={runId}
            pipelines={ordered}
          />
        ))}
      </div>
    </div>
  );
}

function MetricPanel({
  metricKey,
  runId,
  pipelines,
}: {
  metricKey: MetricKey;
  runId: number;
  pipelines: PipelineScores[];
}) {
  const rows = useMemo(() => {
    return [...pipelines]
      .map((p, index) => ({
        name: pipelineLabel(p.pipeline),
        pipeline: p.pipeline,
        score: p.averages[metricKey] ?? 0,
        color: pipelineChartColor(p.pipeline, index),
      }))
      .sort((a, b) => b.score - a.score);
  }, [pipelines, metricKey]);

  return (
    <div className="hf-panel" data-chart-panel>
      <p className="hf-label mb-3">
        <MetricHint
          label={METRIC_LABELS[metricKey].label}
          hint={METRIC_LABELS[metricKey].hint}
        />
      </p>
      <BarChart
        key={`${metricKey}-${runId}`}
        data={rows}
        xDataKey="name"
        orientation="horizontal"
        aspectRatio="4 / 3"
        className="min-h-[260px] w-full"
        margin={{ top: 8, right: 24, bottom: 8, left: 108 }}
        barGap={0.12}
        revealSignature={`${metricKey}-${runId}`}
      >
        <Grid vertical horizontal={false} strokeDasharray="3,6" />
        <Bar dataKey="score" fillKey="color" fill="var(--chart-1)" />
        <BarYAxis showAllLabels />
        <ChartTooltip />
      </BarChart>
      <div className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-[10px] text-hf-muted">
        {rows.map((row) => (
          <span key={row.pipeline} className="inline-flex items-center gap-1">
            <span
              className="size-2 rounded-sm"
              style={{ background: row.color }}
            />
            {row.name}
          </span>
        ))}
      </div>
    </div>
  );
}
