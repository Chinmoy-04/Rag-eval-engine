import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { postAsk, type AskResponse } from "@/lib/api";

const STORAGE_KEY = "hf-ask-chat";
const LEGACY_SESSION_KEY = STORAGE_KEY;

function readStorage(): string | null {
  return localStorage.getItem(STORAGE_KEY) ?? sessionStorage.getItem(LEGACY_SESSION_KEY);
}

function saveStorage(payload: string) {
  localStorage.setItem(STORAGE_KEY, payload);
  sessionStorage.removeItem(LEGACY_SESSION_KEY);
}

export interface ChatMessage {
  role: "user" | "assistant" | "error";
  content: string;
  meta?: AskResponse;
}

interface PersistedAskState {
  messages: ChatMessage[];
  pipeline: string;
  showContexts: boolean;
  showExamples: boolean;
}

interface AskChatContextValue extends PersistedAskState {
  loading: boolean;
  setPipeline: (pipeline: string) => void;
  setShowContexts: (show: boolean) => void;
  setShowExamples: (show: boolean | ((prev: boolean) => boolean)) => void;
  ask: (question: string) => Promise<void>;
  startNewChat: () => void;
}

const defaultState: PersistedAskState = {
  messages: [],
  pipeline: "baseline",
  showContexts: true,
  showExamples: true,
};

function loadPersistedState(): PersistedAskState {
  try {
    const raw = readStorage();
    if (!raw) return defaultState;
    const parsed = JSON.parse(raw) as Partial<PersistedAskState>;
    return {
      messages: Array.isArray(parsed.messages) ? parsed.messages : [],
      pipeline:
        typeof parsed.pipeline === "string" && parsed.pipeline.trim()
          ? parsed.pipeline
          : defaultState.pipeline,
      showContexts:
        typeof parsed.showContexts === "boolean"
          ? parsed.showContexts
          : defaultState.showContexts,
      showExamples:
        typeof parsed.showExamples === "boolean"
          ? parsed.showExamples
          : defaultState.showExamples,
    };
  } catch {
    return defaultState;
  }
}

const AskChatContext = createContext<AskChatContextValue | null>(null);

export function AskChatProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<PersistedAskState>(() => {
    const loaded = loadPersistedState();
    if (loaded.messages.length > 0 || readStorage()) {
      saveStorage(JSON.stringify(loaded));
    }
    return loaded;
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    saveStorage(JSON.stringify(state));
  }, [state]);

  const setPipeline = useCallback((pipeline: string) => {
    setState((prev) => ({ ...prev, pipeline }));
  }, []);

  const setShowContexts = useCallback((showContexts: boolean) => {
    setState((prev) => ({ ...prev, showContexts }));
  }, []);

  const setShowExamples = useCallback(
    (value: boolean | ((prev: boolean) => boolean)) => {
      setState((prev) => ({
        ...prev,
        showExamples:
          typeof value === "function" ? value(prev.showExamples) : value,
      }));
    },
    [],
  );

  const startNewChat = useCallback(() => {
    setState((prev) => ({
      ...prev,
      messages: [],
      showExamples: true,
    }));
  }, []);

  const ask = useCallback(async (question: string) => {
    const q = question.trim();
    if (!q) return;

    let pipeline = defaultState.pipeline;
    let showContexts = defaultState.showContexts;

    setState((prev) => {
      pipeline = prev.pipeline;
      showContexts = prev.showContexts;
      return {
        ...prev,
        messages: [...prev.messages, { role: "user", content: q }],
        showExamples: false,
      };
    });

    setLoading(true);

    try {
      const res = await postAsk({
        question: q,
        pipeline,
        show_contexts: showContexts,
      });
      setState((prev) => ({
        ...prev,
        messages: [
          ...prev.messages,
          { role: "assistant", content: res.answer, meta: res },
        ],
      }));
    } catch (err) {
      setState((prev) => ({
        ...prev,
        messages: [
          ...prev.messages,
          {
            role: "error",
            content: err instanceof Error ? err.message : "Request failed",
          },
        ],
      }));
    } finally {
      setLoading(false);
    }
  }, []);

  const value = useMemo(
    () => ({
      ...state,
      loading,
      setPipeline,
      setShowContexts,
      setShowExamples,
      ask,
      startNewChat,
    }),
    [
      state,
      loading,
      setPipeline,
      setShowContexts,
      setShowExamples,
      ask,
      startNewChat,
    ],
  );

  return (
    <AskChatContext.Provider value={value}>{children}</AskChatContext.Provider>
  );
}

export function useAskChat() {
  const ctx = useContext(AskChatContext);
  if (!ctx) {
    throw new Error("useAskChat must be used within AskChatProvider");
  }
  return ctx;
}
