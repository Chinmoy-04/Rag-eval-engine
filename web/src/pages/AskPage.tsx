import { gsap } from "@/providers/SmoothScrollProvider";
import { useAskChat } from "@/providers/AskChatProvider";
import { useEffect, useMemo, useRef, useState } from "react";
import { BookOpen, ChevronDown, Loader2, MessageSquarePlus, Send } from "lucide-react";
import { getHealth, getSuggestedQuestions } from "@/lib/api";
import {
  PIPELINE_ORDER,
  pipelineDescription,
  pipelineLabel,
  sortPipelines,
} from "@/lib/labels";
import { cn, formatMs } from "@/lib/utils";
import { SuggestedQuestionGrid } from "@/components/SuggestedQuestionCategory";

/** Prefer one chip per category so mid-chat examples cover the expanded corpus. */
const CHAT_EXAMPLE_CATEGORIES = [
  "On-call schedules (CSV)",
  "Compensation & equity",
  "API limits & FinOps",
  "SOC2 & compliance",
  "Vault & secrets",
  "GPU & Slurm",
  "Architecture (ADR)",
  "Vendors & subprocessors",
  "Incidents & CVEs",
  "Employee directory",
  "Tables and matrices",
  "Remote, security, AI",
] as const;

function pickChatExampleQuestions(
  suggested: Record<string, string[]>,
  limit = 10,
): string[] {
  const picked: string[] = [];
  const seen = new Set<string>();

  for (const category of CHAT_EXAMPLE_CATEGORIES) {
    if (picked.length >= limit) break;
    const first = suggested[category]?.[0];
    if (first && !seen.has(first)) {
      seen.add(first);
      picked.push(first);
    }
  }

  if (picked.length < limit) {
    for (const questions of Object.values(suggested)) {
      for (const q of questions) {
        if (picked.length >= limit) break;
        if (!seen.has(q)) {
          seen.add(q);
          picked.push(q);
        }
      }
      if (picked.length >= limit) break;
    }
  }

  return picked;
}

export function AskPage() {
  const {
    messages,
    pipeline,
    showContexts,
    showExamples,
    loading,
    setPipeline,
    setShowContexts,
    setShowExamples,
    ask,
    startNewChat,
  } = useAskChat();
  const [vectors, setVectors] = useState(0);
  // Always show known pipelines (incl. hybrid/rerank/csv); merge API list when available.
  const [pipelines, setPipelines] = useState<string[]>(PIPELINE_ORDER);
  const [suggested, setSuggested] = useState<Record<string, string[]>>({});
  const [input, setInput] = useState("");
  const chatRef = useRef<HTMLDivElement>(null);
  const pageRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getHealth()
      .then((h) => {
        setVectors(h.vectors);
        const fromApi = sortPipelines(h.pipelines);
        setPipelines(sortPipelines([...new Set([...PIPELINE_ORDER, ...fromApi])]));
      })
      .catch(() => {
        setPipelines(PIPELINE_ORDER);
      });
    getSuggestedQuestions().then(setSuggested).catch(() => {});
  }, []);

  useEffect(() => {
    if (pipelines.length && !pipelines.includes(pipeline)) {
      setPipeline(pipelines[0]);
    }
  }, [pipelines, pipeline, setPipeline]);

  useEffect(() => {
    if (!pageRef.current) return;
    const reduce =
      window.matchMedia("(prefers-reduced-motion: reduce)").matches ||
      window.matchMedia("(max-width: 767px)").matches;
    if (reduce) return;
    const ctx = gsap.context(() => {
      gsap.from("[data-ask-stagger]", {
        opacity: 0,
        y: 12,
        duration: 0.4,
        stagger: 0.05,
        ease: "power2.out",
      });
    }, pageRef);
    return () => ctx.revert();
  }, [messages.length]);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages, loading]);

  async function handleAsk(question: string) {
    const q = question.trim();
    if (!q || loading) return;
    setInput("");
    await ask(q);
  }

  const hasConversation = messages.length > 0;
  const chatExampleQuestions = useMemo(
    () => pickChatExampleQuestions(suggested),
    [suggested],
  );

  return (
    <div
      ref={pageRef}
      className="mx-auto flex w-full max-w-3xl flex-col gap-3 pb-2 sm:gap-4 sm:pb-4"
    >
      <header data-ask-stagger className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h1 className="text-xl font-semibold tracking-tight sm:text-2xl">
            Ask the employee handbook
          </h1>
          <p className="mt-1 text-sm leading-relaxed text-hf-muted">
            Type a question about HelixForge policies. We search indexed company
            documents and draft an answer — you can see which sources were used.
          </p>
        </div>
        {hasConversation && (
          <button
            type="button"
            onClick={startNewChat}
            disabled={loading}
            className="inline-flex shrink-0 items-center gap-1.5 rounded-lg border border-hf-border bg-hf-panel px-3 py-2 text-xs font-medium text-hf-muted transition-colors hover:border-hf-teal/40 hover:text-hf-teal disabled:opacity-40"
          >
            <MessageSquarePlus className="size-3.5" />
            New chat
          </button>
        )}
      </header>

      <section className="hf-panel space-y-3 py-3" data-ask-stagger>
        <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center sm:justify-between">
          <p className="text-sm font-medium text-hf-text">Pipeline</p>
          <div className="flex flex-wrap items-center gap-x-3 gap-y-2 text-xs text-hf-muted">
            <span className="inline-flex items-center gap-1.5">
              <BookOpen className="size-3.5 shrink-0" />
              {vectors.toLocaleString()} document sections indexed
            </span>
            <label className="inline-flex cursor-pointer items-center gap-2">
              <span>Show sources</span>
              <button
                type="button"
                role="switch"
                aria-checked={showContexts}
                onClick={() => setShowContexts(!showContexts)}
                className={cn(
                  "relative h-5 w-9 rounded-full transition-colors",
                  showContexts ? "bg-hf-teal" : "bg-hf-chip",
                )}
              >
                <span
                  className={cn(
                    "absolute top-0.5 size-4 rounded-full bg-hf-bg transition-transform",
                    showContexts ? "left-[18px]" : "left-0.5",
                  )}
                />
              </button>
            </label>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          {pipelines.map((id) => (
            <button
              key={id}
              type="button"
              onClick={() => setPipeline(id)}
              className={cn(
                "rounded-full px-3.5 py-1.5 text-sm transition-colors",
                pipeline === id
                  ? "bg-hf-teal text-hf-on-teal font-medium"
                  : "border border-hf-border bg-hf-elevated/60 text-hf-muted hover:text-hf-text",
              )}
            >
              {pipelineLabel(id)}
            </button>
          ))}
        </div>
        <p className="text-xs leading-relaxed text-hf-muted">
          {pipelineDescription(pipeline)}
        </p>
      </section>

      {hasConversation && (
        <div
          ref={chatRef}
          className="max-h-[min(70vh,720px)] space-y-4 overflow-y-auto pr-1"
          data-lenis-prevent
        >
          {messages.map((msg, i) => (
            <div
              key={`${i}-${msg.content.slice(0, 24)}`}
              className={cn(
                "max-w-[92%]",
                msg.role === "user" ? "ml-auto" : "mr-auto",
              )}
              data-ask-stagger
            >
              {msg.role === "user" ? (
                <div className="rounded-2xl rounded-tr-sm bg-hf-teal/15 px-4 py-3 text-sm text-hf-text">
                  {msg.content}
                </div>
              ) : msg.role === "error" ? (
                <div className="rounded-2xl border border-red-500/30 bg-red-950/30 px-4 py-3 text-sm text-red-200">
                  {msg.content}
                </div>
              ) : (
                <div className="space-y-2">
                  <div className="rounded-2xl rounded-tl-sm border border-hf-border bg-hf-panel px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap">
                    {msg.content}
                  </div>
                  {msg.meta && (
                    <p className="text-xs text-hf-muted">
                      pipeline: {msg.meta.pipeline} · {formatMs(msg.meta.latency_ms)}
                      {msg.meta.sources.length > 0 && (
                        <>
                          {" · "}
                          from {msg.meta.sources.length} source
                          {msg.meta.sources.length === 1 ? "" : "s"}
                        </>
                      )}
                    </p>
                  )}
                  {showContexts && msg.meta?.contexts?.length ? (
                    <details className="rounded-lg border border-hf-border bg-hf-panel/60 px-3 py-2 text-xs">
                      <summary className="cursor-pointer text-hf-muted">
                        View {msg.meta.contexts.length} document section
                        {msg.meta.contexts.length === 1 ? "" : "s"} used
                      </summary>
                      <div className="mt-3 space-y-2">
                        {msg.meta.contexts.map((chunk, idx) => (
                          <pre
                            key={idx}
                            className="overflow-x-auto rounded-lg bg-hf-bg/60 p-2 font-mono text-[11px] text-hf-muted whitespace-pre-wrap"
                          >
                            {chunk.slice(0, 900)}
                            {chunk.length > 900 ? "…" : ""}
                          </pre>
                        ))}
                      </div>
                    </details>
                  ) : null}
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="flex items-center gap-2 text-sm text-hf-muted">
              <Loader2 className="size-4 animate-spin text-hf-teal" />
              Searching documents and writing an answer…
            </div>
          )}
        </div>
      )}

      {!hasConversation && showExamples && (
        <SuggestedQuestionGrid suggested={suggested} onAsk={handleAsk} />
      )}

      {hasConversation && (
        <button
          type="button"
          onClick={() => setShowExamples((v) => !v)}
          className="flex items-center gap-1 self-start text-xs text-hf-muted hover:text-hf-teal"
        >
          <ChevronDown
            className={cn("size-3.5 transition-transform", showExamples && "rotate-180")}
          />
          {showExamples ? "Hide example questions" : "Show example questions"}
        </button>
      )}

      {hasConversation && showExamples && (
        <section
          className="max-h-48 space-y-2 overflow-y-auto rounded-xl border border-hf-border bg-hf-panel/50 p-3"
          data-lenis-prevent
        >
          <p className="text-xs font-medium text-hf-muted">Example questions</p>
          <div className="flex flex-wrap gap-2">
            {chatExampleQuestions.map((q) => (
              <button
                key={q}
                type="button"
                onClick={() => handleAsk(q)}
                className="rounded-full border border-hf-border px-3 py-1 text-left text-xs text-hf-muted transition-colors hover:border-hf-teal/40 hover:text-hf-text"
              >
                {q.length > 56 ? `${q.slice(0, 56)}…` : q}
              </button>
            ))}
          </div>
        </section>
      )}

      <form
        className="shrink-0 border-t border-hf-border pt-4"
        onSubmit={(e) => {
          e.preventDefault();
          handleAsk(input);
        }}
      >
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="e.g. How much PTO do new employees get?"
            className="min-w-0 flex-1 rounded-xl border border-hf-border bg-hf-panel px-3 py-3 text-sm outline-none transition-colors focus:border-hf-teal sm:px-4"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="inline-flex shrink-0 items-center gap-2 rounded-xl bg-hf-teal px-3 py-3 text-sm font-medium text-hf-on-teal transition-opacity hover:opacity-90 disabled:opacity-40 sm:px-4"
          >
            {loading ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <Send className="size-4" />
            )}
            <span className="hidden sm:inline">Ask</span>
          </button>
        </div>
      </form>
    </div>
  );
}
