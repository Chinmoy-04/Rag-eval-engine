"""Streamlit Ask UI for the baseline RAG pipeline."""

from __future__ import annotations

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

st.set_page_config(
    page_title="HelixForge RAG Ask",
    page_icon="HF",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .stApp { background: #0f1419; }
      [data-testid="stSidebar"] { background: #161c24; }
      .block-container { padding-top: 1.4rem; max-width: 1100px; }
      h1, h2, h3 { letter-spacing: -0.02em; }
      .metric-row { color: #9aa7b4; font-size: 0.85rem; }
      .source-chip {
        display: inline-block;
        background: #243044;
        color: #d7e3f4;
        border-radius: 999px;
        padding: 0.15rem 0.65rem;
        margin: 0.15rem 0.25rem 0.15rem 0;
        font-size: 0.8rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def _init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None


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


def main() -> None:
    _init_state()
    config = load_config()
    vector_count = collection_count(config)

    st.title("HelixForge policy assistant")
    st.caption(
        "Baseline RAG: retrieve policy chunks, then generate an answer from that context only. "
        "This is the same path as `python -m src.cli ask`."
    )

    with st.sidebar:
        st.subheader("Run settings")
        pipeline_name = st.selectbox(
            "Pipeline",
            options=list(PIPELINE_CONFIGS.keys()),
            index=0,
            help="degraded and optimized configs arrive in Phase 7.",
        )
        show_contexts = st.toggle("Show retrieved chunks", value=True)
        st.divider()
        st.markdown(
            f"**Index:** {vector_count} vectors  \n"
            f"**LLM:** `{config.llm_provider.value}` / `{config.llm_model}`  \n"
            f"**Embeddings:** `{config.embedding_provider.value}`"
        )
        if vector_count == 0:
            st.error("Index is empty. Run `uv run python -m src.cli ingest` first.")
        st.divider()
        if st.button("Clear conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.subheader("Try a question")
        for group, questions in SUGGESTED_QUESTIONS.items():
            with st.expander(group, expanded=group == "Simple lookup"):
                for i, question in enumerate(questions):
                    if st.button(question, key=f"{group}-{i}", use_container_width=True):
                        st.session_state.pending_question = question
                        st.rerun()

    if vector_count == 0:
        st.info("Ingest the corpus before asking questions.")
        return

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and not message.get("error"):
                chips = " ".join(
                    f'<span class="source-chip">{source}</span>'
                    for source in message.get("sources") or []
                )
                latency = message.get("latency_ms") or 0
                st.markdown(
                    f'<div class="metric-row">{latency:.0f} ms · {message.get("pipeline", "")}</div>'
                    + (f"<div>{chips}</div>" if chips else ""),
                    unsafe_allow_html=True,
                )
                if show_contexts and message.get("contexts"):
                    with st.expander("Retrieved context"):
                        for i, chunk in enumerate(message["contexts"], start=1):
                            st.markdown(f"**Chunk {i}**")
                            st.text(chunk)

    typed = st.chat_input("Ask about HelixForge policy…")
    question = typed or st.session_state.pending_question
    if question:
        st.session_state.pending_question = None
        with st.spinner("Retrieving and generating…"):
            _ask(question, pipeline_name)
        st.rerun()


if __name__ == "__main__":
    main()
