import { ChevronDown } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { categoryLabel } from "@/lib/labels";
import { cn } from "@/lib/utils";

interface SuggestedQuestionCategoryProps {
  category: string;
  questions: string[];
  open: boolean;
  onToggle: () => void;
  onAsk: (question: string) => void;
}

function SuggestedQuestionCategory({
  category,
  questions,
  open,
  onToggle,
  onAsk,
}: SuggestedQuestionCategoryProps) {
  const visible = questions.slice(0, 4);

  return (
    <div className="hf-panel overflow-hidden !p-0" data-ask-stagger>
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={open}
        className="flex w-full items-center justify-between gap-2 px-4 py-3 text-left transition-colors hover:bg-hf-elevated/50"
      >
        <span className="text-xs font-medium text-hf-teal">
          {categoryLabel(category)}
        </span>
        <span className="flex items-center gap-1.5 text-[10px] font-mono uppercase tracking-wider text-hf-muted">
          {visible.length}
          <ChevronDown
            aria-hidden
            className={cn(
              "size-3.5 transition-transform duration-200",
              open && "rotate-180",
            )}
          />
        </span>
      </button>
      <div
        className={cn(
          "grid transition-[grid-template-rows] duration-200 ease-out",
          open ? "grid-rows-[1fr]" : "grid-rows-[0fr]",
        )}
      >
        <div className="min-h-0 overflow-hidden">
          <ul className="space-y-0.5 border-t border-hf-border px-2 py-2">
            {visible.map((q) => (
              <li key={q}>
                <button
                  type="button"
                  onClick={() => onAsk(q)}
                  className="w-full rounded-lg px-2 py-1.5 text-left text-sm leading-snug text-hf-muted transition-colors hover:bg-hf-elevated hover:text-hf-text"
                >
                  {q}
                </button>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

interface SuggestedQuestionGridProps {
  suggested: Record<string, string[]>;
  onAsk: (question: string) => void;
}

function buildExpandedState(categories: string[], value: boolean) {
  return Object.fromEntries(categories.map((c) => [c, value]));
}

export function SuggestedQuestionGrid({
  suggested,
  onAsk,
}: SuggestedQuestionGridProps) {
  const entries = useMemo(
    () => Object.entries(suggested),
    [suggested],
  );
  const categories = useMemo(
    () => entries.map(([category]) => category),
    [entries],
  );
  const [leftColumn, rightColumn] = useMemo(() => {
    const left: typeof entries = [];
    const right: typeof entries = [];
    for (let i = 0; i < entries.length; i++) {
      (i % 2 === 0 ? left : right).push(entries[i]);
    }
    return [left, right];
  }, [entries]);

  const [expanded, setExpanded] = useState<Record<string, boolean>>(() =>
    buildExpandedState(categories, false),
  );

  useEffect(() => {
    setExpanded((prev) => {
      const next = { ...prev };
      for (const category of categories) {
        if (!(category in next)) next[category] = false;
      }
      for (const key of Object.keys(next)) {
        if (!categories.includes(key)) delete next[key];
      }
      return next;
    });
  }, [categories]);

  if (entries.length === 0) return null;

  const allOpen = categories.every((c) => expanded[c] !== false);

  function renderCategory([category, questions]: (typeof entries)[number]) {
    return (
      <SuggestedQuestionCategory
        key={category}
        category={category}
        questions={questions}
        open={expanded[category] !== false}
        onToggle={() =>
          setExpanded((prev) => ({
            ...prev,
            [category]: !prev[category],
          }))
        }
        onAsk={onAsk}
      />
    );
  }

  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-3" data-ask-stagger>
        <div>
          <h2 className="text-sm font-medium text-hf-text">
            Try an example question
          </h2>
          <p className="mt-0.5 text-xs text-hf-muted">
            Expand a category and click a question — or type your own below.
          </p>
        </div>
        <button
          type="button"
          onClick={() =>
            setExpanded(buildExpandedState(categories, !allOpen))
          }
          className="text-xs text-hf-muted transition-colors hover:text-hf-teal"
        >
          {allOpen ? "Collapse all" : "Expand all"}
        </button>
      </div>

      {/* Mobile: single stack */}
      <div className="flex flex-col gap-4 sm:hidden">
        {entries.map(renderCategory)}
      </div>

      {/* sm+: two independent stacks — no column chrome, reflow on collapse */}
      <div className="hidden gap-4 sm:grid sm:grid-cols-2 sm:items-start">
        <div className="flex min-w-0 flex-col gap-4">
          {leftColumn.map(renderCategory)}
        </div>
        <div className="flex min-w-0 flex-col gap-4">
          {rightColumn.map(renderCategory)}
        </div>
      </div>
    </section>
  );
}
