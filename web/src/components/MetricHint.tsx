import { CircleHelp } from "lucide-react";
import { useCallback, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { cn } from "@/lib/utils";

interface MetricHintProps {
  /** Visible metric name (e.g. Faithfulness). */
  label: string;
  /** Plain-language explanation shown on hover. */
  hint: string;
  className?: string;
}

/** Metric name with an info tooltip portaled above other UI layers. */
export function MetricHint({ label, hint, className }: MetricHintProps) {
  const triggerRef = useRef<HTMLButtonElement>(null);
  const [open, setOpen] = useState(false);
  const [coords, setCoords] = useState({ top: 0, left: 0 });

  const updatePosition = useCallback(() => {
    const el = triggerRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    setCoords({
      top: rect.top - 8,
      left: rect.left + rect.width / 2,
    });
  }, []);

  const show = useCallback(() => {
    updatePosition();
    setOpen(true);
  }, [updatePosition]);

  const hide = useCallback(() => setOpen(false), []);

  return (
    <>
      <span className={cn("inline-flex items-center gap-1", className)}>
        {label}
        <button
          ref={triggerRef}
          type="button"
          className="inline-flex shrink-0 rounded-sm text-hf-muted transition-colors hover:text-hf-teal focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-hf-teal"
          aria-label={`About ${label}`}
          onMouseEnter={show}
          onMouseLeave={hide}
          onFocus={show}
          onBlur={hide}
        >
          <CircleHelp className="size-3.5" aria-hidden />
        </button>
      </span>
      {open &&
        createPortal(
          <div
            role="tooltip"
            className="pointer-events-none fixed z-[9999] w-56 max-w-[calc(100vw-2rem)] -translate-x-1/2 -translate-y-full rounded-lg border border-hf-border bg-hf-elevated px-3 py-2 text-left text-xs font-normal normal-case leading-snug tracking-normal text-hf-muted shadow-xl"
            style={{ top: coords.top, left: coords.left }}
          >
            {hint}
          </div>,
          document.body,
        )}
    </>
  );
}
