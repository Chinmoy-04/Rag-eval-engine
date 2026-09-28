import { useBackendHealth } from "@/hooks/useBackendHealth";
import { cn } from "@/lib/utils";

function formatWait(ms: number): string {
  const sec = Math.max(0, Math.floor(ms / 1000));
  if (sec < 60) return `${sec}s`;
  const min = Math.floor(sec / 60);
  const rem = sec % 60;
  return `${min}m ${rem}s`;
}

export function BackendStatus() {
  const { status, waitingMs } = useBackendHealth();

  const label =
    status === "online"
      ? "API online"
      : status === "checking"
        ? "Checking API…"
        : status === "waking"
          ? `API waking… ${formatWait(waitingMs)}`
          : `API offline · retrying ${formatWait(waitingMs)}`;

  const shortLabel =
    status === "online"
      ? "Online"
      : status === "checking"
        ? "…"
        : status === "waking"
          ? "Waking"
          : "Offline";

  const title =
    status === "online"
      ? "Backend is ready"
      : status === "checking"
        ? "Checking whether the backend is reachable"
        : "Render free tier spins down when idle. The API is starting; this can take up to a minute.";

  return (
    <div
      className={cn(
        "inline-flex max-w-[11rem] items-center gap-1.5 rounded-lg border px-2 py-1 text-[11px] font-medium sm:max-w-none sm:px-2.5 sm:text-xs",
        status === "online" &&
          "border-hf-teal/35 bg-hf-teal-dim text-hf-teal",
        status === "checking" &&
          "border-hf-border bg-hf-elevated/60 text-hf-muted",
        (status === "waking" || status === "offline") &&
          "border-amber-500/35 bg-amber-500/10 text-amber-800 dark:text-amber-200",
      )}
      title={title}
      role="status"
      aria-live="polite"
    >
      <span
        className={cn(
          "size-1.5 shrink-0 rounded-full",
          status === "online" && "bg-hf-teal",
          status === "checking" && "bg-hf-muted animate-pulse",
          (status === "waking" || status === "offline") &&
            "bg-amber-500 animate-pulse",
        )}
        aria-hidden
      />
      <span className="truncate sm:hidden">{shortLabel}</span>
      <span className="hidden truncate sm:inline">{label}</span>
    </div>
  );
}
