import { useCallback, useEffect, useRef, useState } from "react";
import { getHealth, type HealthResponse } from "@/lib/api";

export type BackendStatus = "checking" | "waking" | "online" | "offline";

export type BackendHealthState = {
  status: BackendStatus;
  health: HealthResponse | null;
  /** Milliseconds since we started waiting for the backend (while not online). */
  waitingMs: number;
};

const HEALTH_TIMEOUT_MS = 8_000;
/** Poll while waiting for Render cold start. */
const WAKE_POLL_MS = 3_000;
/** Poll once online to detect sleep / outages. */
const ONLINE_POLL_MS = 45_000;
/** After this many consecutive failures, show offline (still retrying). */
const OFFLINE_AFTER_FAILURES = 8;

async function fetchHealthWithTimeout(): Promise<HealthResponse> {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), HEALTH_TIMEOUT_MS);
  try {
    return await getHealth({ signal: controller.signal });
  } finally {
    window.clearTimeout(timer);
  }
}

/**
 * Polls `/api/health` so the UI can show Render cold-start vs ready.
 * Fast polling while down; slower once online.
 */
export function useBackendHealth(): BackendHealthState {
  const [status, setStatus] = useState<BackendStatus>("checking");
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [waitingMs, setWaitingMs] = useState(0);
  const failuresRef = useRef(0);
  const waitStartedRef = useRef<number | null>(Date.now());
  const onlineRef = useRef(false);

  const tickWait = useCallback(() => {
    if (waitStartedRef.current == null) {
      setWaitingMs(0);
      return;
    }
    setWaitingMs(Date.now() - waitStartedRef.current);
  }, []);

  useEffect(() => {
    let cancelled = false;
    let timeoutId: number | undefined;

    const schedule = (ms: number) => {
      timeoutId = window.setTimeout(run, ms);
    };

    const run = async () => {
      tickWait();
      try {
        const next = await fetchHealthWithTimeout();
        if (cancelled) return;
        failuresRef.current = 0;
        waitStartedRef.current = null;
        onlineRef.current = true;
        setHealth(next);
        setStatus("online");
        setWaitingMs(0);
        schedule(ONLINE_POLL_MS);
      } catch {
        if (cancelled) return;
        onlineRef.current = false;
        setHealth(null);
        failuresRef.current += 1;
        if (waitStartedRef.current == null) {
          waitStartedRef.current = Date.now();
        }
        tickWait();
        setStatus(
          failuresRef.current >= OFFLINE_AFTER_FAILURES ? "offline" : "waking",
        );
        schedule(WAKE_POLL_MS);
      }
    };

    void run();

    return () => {
      cancelled = true;
      if (timeoutId != null) window.clearTimeout(timeoutId);
    };
  }, [tickWait]);

  // Keep waiting timer updating while waking/offline.
  useEffect(() => {
    if (status === "online" || status === "checking") return;
    const id = window.setInterval(tickWait, 1_000);
    return () => window.clearInterval(id);
  }, [status, tickWait]);

  return { status, health, waitingMs };
}
