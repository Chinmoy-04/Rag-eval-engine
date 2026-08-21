"""HelixForge RAG Eval — Streamlit UI matching design/stitch/new Ask screen."""

from __future__ import annotations

import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.config import load_config
from src.ingestion.indexer import collection_count
from src.rag_pipeline.configs import PIPELINE_CONFIGS
from src.rag_pipeline.pipeline import run_pipeline
from src.rag_pipeline.questions import SUGGESTED_QUESTIONS

PIPELINE_LABELS: dict[str, str] = {
    "baseline": "Baseline RAG",
    "degraded": "Degraded Vectors",
    "optimized": "Optimized v2.4",
}

# Show Stitch pipeline choices; only keys in PIPELINE_CONFIGS are runnable.
PIPELINE_CHOICES = [
    ("baseline", "Baseline RAG"),
    ("degraded", "Degraded Vectors"),
    ("optimized", "Optimized v2.4"),
]

st.set_page_config(
    page_title="HelixForge RAG Eval",
    page_icon="HF",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Streamlit 1.33+ : st.html injects into the document (markdown strips <style>).
st.html(
    """
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<style>
  :root {
    --hf-bg: #0b0f14;
    --hf-panel: #101419;
    --hf-rail: #0c1016;
    --hf-border: #1e2833;
    --hf-elevated: #1a222c;
    --hf-chip: #27313d;
    --hf-text: #e8eef5;
    --hf-muted: #8b9aab;
    --hf-teal: #2dd4bf;
    --hf-teal-bright: #57f1db;
    --hf-teal-dim: #0a3d38;
  }

  html, body, .stApp, [data-testid="stAppViewContainer"] {
    font-family: "Space Grotesk", system-ui, sans-serif !important;
    background-color: var(--hf-bg) !important;
    color: var(--hf-text) !important;
  }

  .stApp {
    background-image:
      linear-gradient(rgba(30, 40, 51, 0.18) 1px, transparent 1px),
      linear-gradient(90deg, rgba(30, 40, 51, 0.18) 1px, transparent 1px) !important;
    background-size: 24px 24px !important;
  }

  [data-testid="stHeader"] { background: transparent !important; }
  [data-testid="stToolbar"] { display: none !important; }
  #MainMenu, footer { visibility: hidden; }
  [data-testid="stSidebar"] { display: none !important; }

  .block-container {
    padding: 0.75rem 1.25rem 2rem !important;
    max-width: 1440px !important;
  }

  .hf-shell { display: contents; }

  .hf-brand {
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: var(--hf-text);
    line-height: 1.15;
  }
  .hf-brand span {
    display: block;
    margin-top: 0.15rem;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--hf-teal);
  }

  .hf-nav-btn button {
    width: 100% !important;
    justify-content: flex-start !important;
    border-radius: 12px !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    color: var(--hf-muted) !important;
    font-weight: 500 !important;
    padding: 0.65rem 0.85rem !important;
  }
  .hf-nav-btn button:hover {
    border-color: var(--hf-border) !important;
    color: var(--hf-text) !important;
    background: var(--hf-elevated) !important;
  }
  .hf-nav-btn.active button {
    background: var(--hf-teal) !important;
    color: #042f2e !important;
    font-weight: 700 !important;
  }

  .hf-panel {
    background: rgba(16, 20, 25, 0.92);
    border: 1px solid var(--hf-border);
    border-radius: 16px;
    padding: 1rem 1.1rem;
    margin-bottom: 0.75rem;
  }
  .hf-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--hf-muted);
    margin-bottom: 0.55rem;
  }
  .hf-mono {
    font-family: "JetBrains Mono", ui-monospace, monospace;
    font-size: 0.82rem;
  }
  .hf-muted { color: var(--hf-muted); font-size: 0.88rem; }

  .hf-pill {
    display: inline-block;
    background: var(--hf-chip);
    border: 1px solid var(--hf-border);
    color: var(--hf-text);
    border-radius: 999px;
    padding: 0.22rem 0.7rem;
    margin: 0.15rem 0.3rem 0.15rem 0;
    font-size: 0.72rem;
    font-family: "JetBrains Mono", ui-monospace, monospace;
  }
  .hf-pill.on {
    background: rgba(45, 212, 191, 0.14);
    border-color: rgba(45, 212, 191, 0.4);
    color: var(--hf-teal-bright);
  }

  .hf-health {
    font-family: "JetBrains Mono", ui-monospace, monospace;
    font-size: 1.35rem;
    font-weight: 600;
    color: var(--hf-text);
  }
  .hf-bar {
    margin-top: 0.55rem;
    height: 7px;
    border-radius: 999px;
    background: var(--hf-chip);
    overflow: hidden;
  }
  .hf-bar > i {
    display: block;
    height: 100%;
    width: 70%;
    background: linear-gradient(90deg, var(--hf-teal-dim), var(--hf-teal));
  }

  .hf-answer {
    background: var(--hf-panel);
    border: 1px solid var(--hf-border);
    border-radius: 16px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.65rem;
  }
  .hf-user {
    background: var(--hf-elevated);
    border: 1px solid var(--hf-border);
    border-radius: 14px;
    padding: 0.85rem 1rem;
    margin: 0.75rem 0;
    color: var(--hf-text);
  }
  .hf-meta {
    font-family: "JetBrains Mono", ui-monospace, monospace;
    font-size: 0.75rem;
    color: var(--hf-muted);
    margin: 0.55rem 0 0.75rem;
  }
  .hf-meta .pipe { color: var(--hf-teal); }

  .source-chip {
    display: inline-block;
    background: var(--hf-chip);
    border: 1px solid var(--hf-border);
    color: var(--hf-text);
    border-radius: 8px;
    padding: 0.18rem 0.55rem;
    margin: 0.15rem 0.3rem 0.15rem 0;
    font-size: 0.72rem;
    font-family: "JetBrains Mono", ui-monospace, monospace;
  }

  .hf-chunk {
    background: var(--hf-elevated);
    border: 1px solid var(--hf-border);
    border-radius: 12px;
    padding: 0.75rem 0.9rem;
    margin-bottom: 0.5rem;
  }
  .hf-chunk-title {
    font-family: "JetBrains Mono", ui-monospace, monospace;
    font-size: 0.75rem;
    color: var(--hf-teal-bright);
    margin-bottom: 0.35rem;
  }

  .hf-empty {
    border: 1px dashed var(--hf-border);
    border-radius: 18px;
    padding: 3rem 1.5rem;
    text-align: center;
    background: rgba(12, 16, 22, 0.75);
  }
  .hf-empty h2 {
    margin: 0 0 0.4rem;
    font-size: 1.5rem;
    letter-spacing: -0.03em;
  }

  .hf-engineer {
    margin-top: 1.5rem;
    padding-top: 1rem;
    border-top: 1px solid var(--hf-border);
    font-size: 0.85rem;
    color: var(--hf-muted);
  }
  .hf-engineer strong { color: var(--hf-text); display: block; }

  div[data-testid="stChatInput"] {
    background: transparent !important;
  }
  div[data-testid="stChatInput"] > div {
    border: 1px solid var(--hf-border) !important;
    border-radius: 16px !important;
    background: var(--hf-panel) !important;
  }

  .stButton > button {
    border-radius: 10px !important;
    border: 1px solid var(--hf-border) !important;
    background: var(--hf-elevated) !important;
    color: var(--hf-text) !important;
  }
  .stButton > button:hover {
    border-color: var(--hf-teal) !important;
    color: var(--hf-teal-bright) !important;
  }
  .stButton > button[kind="primary"] {
    background: var(--hf-teal) !important;
    color: #042f2e !important;
    border: none !important;
    font-weight: 700 !important;
  }

  div[data-baseweb="radio"] label {
    color: var(--hf-text) !important;
  }
</style>
"""
)


def _init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None
    if "page" not in st.session_state:
        st.session_state.page = "Ask"
    if "pipeline_key" not in st.session_state:
        st.session_state.pipeline_key = "baseline"


def _ask(question: str, pipeline_name: str) -> None:
    st.session_state.messages.append({"role": "user", "content": question})
    try:
        result = run_pipeline(question, pipeline_config=pipeline_name)
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result.answer,
                "sources": result.sources,
                "latency_ms": result.latency_ms,
                "contexts": result.retrieved_contexts,
                "pipeline": result.pipeline_config_name,
            }
        )
    except Exception as exc:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": f"Could not answer: {exc}",
                "sources": [],
                "latency_ms": 0.0,
                "contexts": [],
                "pipeline": pipeline_name,
                "error": True,
            }
        )


def _nav_column() -> None:
    st.html('<div class="hf-brand">HelixForge<span>RAG Eval</span></div>')
    st.write("")
    for name in ("Ask", "Runs", "Compare"):
        active = st.session_state.page == name
        clicked = st.button(
            name,
            key=f"nav-{name}",
            use_container_width=True,
            type="primary" if active else "secondary",
        )
        if clicked and not active:
            st.session_state.page = name
            st.rerun()

    st.html(
        '<div class="hf-engineer"><strong>Engineer</strong>v0.1.0-local</div>'
    )


def _config_column(config, vector_count: int) -> tuple[str, bool]:
    st.html('<div class="hf-label">Target pipeline</div>')
    labels = [label for _, label in PIPELINE_CHOICES]
    current_label = dict(PIPELINE_CHOICES).get(
        st.session_state.pipeline_key, "Baseline RAG"
    )
    choice = st.radio(
        "pipeline",
        options=labels,
        index=labels.index(current_label) if current_label in labels else 0,
        label_visibility="collapsed",
    )
    key = next(k for k, lab in PIPELINE_CHOICES if lab == choice)
    if key not in PIPELINE_CONFIGS:
        st.caption(f"{choice} arrives in Phase 7 — using Baseline RAG.")
        key = "baseline"
    st.session_state.pipeline_key = key

    show_contexts = st.toggle("Show retrieved chunks", value=True)

    st.html(
        f"""
        <div class="hf-panel">
          <div class="hf-label">Active models</div>
          <span class="hf-pill on">{html.escape(config.llm_provider.value)}</span>
          <span class="hf-pill">{html.escape(config.llm_model.split("/")[-1])}</span>
          <span class="hf-pill">{html.escape(config.embedding_provider.value)}</span>
        </div>
        <div class="hf-panel">
          <div class="hf-label">Index health</div>
          <div class="hf-health">{vector_count} vectors</div>
          <div class="hf-bar"><i></i></div>
        </div>
        """
    )

    st.html('<div class="hf-label">Suggested tests</div>')
    for group, questions in SUGGESTED_QUESTIONS.items():
        with st.expander(group, expanded=group in {"Simple lookup", "Should abstain"}):
            for i, q in enumerate(questions):
                if st.button(q, key=f"sug-{group}-{i}", use_container_width=True):
                    st.session_state.pending_question = q
                    st.session_state.page = "Ask"
                    st.rerun()

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    return key, show_contexts


def _chat_column(pipeline_name: str, show_contexts: bool, vector_count: int) -> None:
    if vector_count == 0:
        st.warning("Index is empty. Run `uv run python -m src.cli ingest` first.")
        return

    if not st.session_state.messages:
        st.html(
            """
            <div class="hf-empty">
              <h2>Ask the handbook</h2>
              <p class="hf-muted">
                Same path as <code>python -m src.cli ask</code> —
                retrieve policy chunks, then answer from that context only.
              </p>
            </div>
            """
        )

    for message in st.session_state.messages:
        if message["role"] == "user":
            st.html(
                f'<div class="hf-user">{html.escape(message["content"])}</div>'
            )
            continue

        if message.get("error"):
            st.error(message["content"])
            continue

        st.markdown('<div class="hf-answer">', unsafe_allow_html=True)
        st.markdown(message["content"])
        st.markdown("</div>", unsafe_allow_html=True)
        latency = message.get("latency_ms") or 0
        pipe = html.escape(str(message.get("pipeline", "")))
        chips = " ".join(
            f'<span class="source-chip">{html.escape(str(s))}</span>'
            for s in (message.get("sources") or [])
        )
        st.html(
            f'<div class="hf-meta">'
            f'<span class="pipe">pipeline: {pipe}</span>'
            f' &nbsp;·&nbsp; latency: {latency:.0f} ms'
            f'{" &nbsp;·&nbsp; sources: " + chips if chips else ""}'
            f"</div>"
        )

        if show_contexts and message.get("contexts"):
            with st.expander(
                f"Retrieved content ({len(message['contexts'])} chunks)",
                expanded=True,
            ):
                for i, chunk in enumerate(message["contexts"], start=1):
                    src = ""
                    if message.get("sources") and i <= len(message["sources"]):
                        src = html.escape(str(message["sources"][i - 1]))
                    st.html(
                        f'<div class="hf-chunk">'
                        f'<div class="hf-chunk-title">#{i} {src}</div>'
                        f'<div class="hf-mono" style="white-space:pre-wrap;color:#c5ced9;font-size:0.78rem">'
                        f"{html.escape(chunk[:1200])}"
                        f"{'…' if len(chunk) > 1200 else ''}"
                        f"</div></div>"
                    )

    typed = st.chat_input("Ask a question about your documents…")
    question = typed or st.session_state.pending_question
    if question:
        st.session_state.pending_question = None
        with st.spinner("Retrieving and generating…"):
            _ask(question, pipeline_name)
        st.rerun()


def _runs_page(vector_count: int) -> None:
    st.html('<h2 style="letter-spacing:-0.03em;margin:0.2rem 0 0.35rem">Runs</h2>')
    st.caption("Monitor and analyze RAG evaluation runs.")
    a, b, c = st.columns(3)
    for col, label, value, sub in (
        (a, "Total runs", "—", "Phase 6"),
        (b, "Last score", "—", "No evals yet"),
        (c, "Vectors indexed", str(vector_count), "Local Chroma"),
    ):
        with col:
            st.html(
                f'<div class="hf-panel"><div class="hf-label">{label}</div>'
                f'<div class="hf-health">{html.escape(value)}</div>'
                f'<div class="hf-muted">{html.escape(sub)}</div></div>'
            )
    st.html(
        """
        <div class="hf-panel">
          <div class="hf-label">Evaluation history</div>
          <p class="hf-muted" style="margin:0.4rem 0 0">
            Table from <code>design/stitch/new/images/runs.png</code> wires up after
            Phase 6 stores EvalResult rows. Use Ask for live queries until then.
          </p>
        </div>
        """
    )


def _compare_page() -> None:
    st.html('<h2 style="letter-spacing:-0.03em;margin:0.2rem 0 0.35rem">Compare</h2>')
    st.caption("Baseline vs optimized — Ragas metrics side by side.")
    st.html(
        """
        <div class="hf-panel">
          <div class="hf-label">Metric distribution</div>
          <p class="hf-muted" style="margin:0.4rem 0 0">
            Faithfulness / relevancy / precision / recall charts land with
            Phase 7 pipelines + Phase 9 dashboard. Preview:
            <code>design/stitch/new/images/compare.png</code>.
          </p>
        </div>
        """
    )


def main() -> None:
    _init_state()
    config = load_config()
    vector_count = collection_count(config)

    page = st.session_state.page
    if page == "Ask":
        nav, cfg, chat = st.columns([0.9, 1.35, 3.0], gap="medium")
        with nav:
            _nav_column()
        with cfg:
            pipeline_name, show_contexts = _config_column(config, vector_count)
        with chat:
            _chat_column(pipeline_name, show_contexts, vector_count)
    else:
        nav, main_col = st.columns([0.9, 4.35], gap="medium")
        with nav:
            _nav_column()
        with main_col:
            if page == "Runs":
                _runs_page(vector_count)
            else:
                _compare_page()


if __name__ == "__main__":
    main()
