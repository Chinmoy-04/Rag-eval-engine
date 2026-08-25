"""Pluggable retrieval strategies for RAG pipelines."""

from __future__ import annotations

import logging
import re
from typing import Literal

from llama_index.core.schema import NodeWithScore, TextNode
from rapidfuzz import fuzz

from src.config import AppConfig, load_config
from src.ingestion.indexer import get_bm25_nodes, query_index
from src.rag_pipeline.configs import PipelineConfig

logger = logging.getLogger("rag_eval")

RetrievalMode = Literal[
    "vector",
    "hybrid",
    "hybrid_expand",
    "vector_rerank",
    "csv_hybrid",
]

_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "how",
        "i",
        "in",
        "is",
        "it",
        "me",
        "my",
        "of",
        "on",
        "or",
        "our",
        "should",
        "the",
        "to",
        "what",
        "when",
        "where",
        "which",
        "who",
        "with",
    }
)

_TABULAR_CUE_RE = re.compile(
    r"\b("
    r"SLA|PagerDuty|midpoint|salary|CSV|row|roster|directory|employee|"
    r"job\s+level|compensation|cost\s+center|quota|CVE|on-?call\s+schedule|"
    r"CC-\d+|PD-SVC|L\d+|HF-EMP|ONCALL"
    r")\b",
    re.IGNORECASE,
)

# Proper names / IDs often buried in large CSV chunks — useful for a sparse second pass.
_PROPER_TOKEN_RE = re.compile(
    r"\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+|CC-\d+|PD-SVC-[A-Z0-9-]+|CVE-\d+-\d+|HF-EMP-[A-Z0-9-]+|ONCALL-[A-Z0-9-]+|SOC2-[A-Z]+-\d+|L[3-8])\b"
)

_bm25_retriever_cache: dict[int, object] = {}


def keyword_query(question: str) -> str:
    """Drop stopwords so retrieval can match table/CSV terms more directly."""
    tokens = re.findall(r"[A-Za-z0-9_./-]+", question)
    kept = [tok for tok in tokens if tok.lower() not in _STOPWORDS and len(tok) > 1]
    return " ".join(kept)


def _node_key(hit: NodeWithScore) -> str:
    node = hit.node
    meta = node.metadata or {}
    name = str(meta.get("file_name") or meta.get("filename") or "")
    text = (node.get_content() or "")[:160]
    return f"{name}::{text}"


def _merge_hits(hits: list[NodeWithScore], limit: int) -> list[NodeWithScore]:
    ranked = sorted(hits, key=lambda h: float(h.score or 0.0), reverse=True)
    seen: set[str] = set()
    merged: list[NodeWithScore] = []
    for hit in ranked:
        key = _node_key(hit)
        if key in seen:
            continue
        seen.add(key)
        merged.append(hit)
        if len(merged) >= limit:
            break
    return merged


def retrieve_vector(
    question: str, config: AppConfig, k: int
) -> list[NodeWithScore]:
    return query_index(question, config=config, top_k=k)


def _get_bm25_retriever(nodes: list[TextNode], k: int):
    from llama_index.retrievers.bm25 import BM25Retriever

    cache_key = id(nodes)
    retriever = _bm25_retriever_cache.get(cache_key)
    if retriever is None:
        retriever = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=k)
        _bm25_retriever_cache[cache_key] = retriever
    else:
        retriever.similarity_top_k = k
    return retriever


def retrieve_bm25(
    question: str, config: AppConfig, k: int
) -> list[NodeWithScore]:
    nodes = get_bm25_nodes(config)
    if not nodes:
        logger.warning("BM25 node cache empty; run ingest --rebuild")
        return []
    retriever = _get_bm25_retriever(nodes, k)
    return list(retriever.retrieve(question))


def reciprocal_rank_fusion(
    ranked_lists: list[list[NodeWithScore]],
    limit: int,
    *,
    k: int = 60,
) -> list[NodeWithScore]:
    """Merge multiple ranked lists with RRF scores."""
    scores: dict[str, float] = {}
    nodes: dict[str, NodeWithScore] = {}
    for ranked in ranked_lists:
        for rank, hit in enumerate(ranked, start=1):
            key = _node_key(hit)
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
            nodes.setdefault(key, hit)

    fused = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    merged: list[NodeWithScore] = []
    for key, score in fused[:limit]:
        hit = nodes[key]
        merged.append(NodeWithScore(node=hit.node, score=score))
    return merged


def _is_csv_chunk(hit: NodeWithScore) -> bool:
    meta = hit.node.metadata or {}
    name = str(meta.get("file_name") or meta.get("filename") or "").lower()
    return name.endswith(".csv")


def csv_boost(hits: list[NodeWithScore], question: str) -> list[NodeWithScore]:
    """Boost CSV chunks when the question looks tabular or ID-heavy."""
    if not _TABULAR_CUE_RE.search(question) and not _PROPER_TOKEN_RE.search(question):
        return hits
    boosted: list[NodeWithScore] = []
    for hit in hits:
        score = float(hit.score or 0.0)
        if _is_csv_chunk(hit):
            score *= 1.35
        boosted.append(NodeWithScore(node=hit.node, score=score))
    boosted.sort(key=lambda h: float(h.score or 0.0), reverse=True)
    return boosted


def _entity_query(question: str) -> str | None:
    """Extract proper names / IDs for a focused BM25 pass."""
    tokens = _PROPER_TOKEN_RE.findall(question)
    if not tokens:
        return None
    return " ".join(tokens)


def lexical_rerank(
    question: str, hits: list[NodeWithScore], top_k: int
) -> list[NodeWithScore]:
    """Re-score vector hits with rapidfuzz against a keyword-stripped query."""
    alt = keyword_query(question) or question.strip()
    alt_lower = alt.lower()
    entity = (_entity_query(question) or "").lower()
    scored: list[tuple[float, NodeWithScore]] = []
    for hit in hits:
        text = (hit.node.get_content() or "").lower()
        overlap = sum(1 for tok in alt_lower.split() if tok in text)
        overlap_score = overlap / max(len(alt_lower.split()), 1)
        fuzzy = fuzz.partial_ratio(alt_lower, text) / 100.0
        combined = 0.55 * fuzzy + 0.45 * overlap_score
        # Exact person/ID match is decisive for CSV row lookup.
        if entity and entity in text:
            combined = min(1.0, combined + 0.35)
        scored.append((combined, hit))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [
        NodeWithScore(node=hit.node, score=score)
        for score, hit in scored[:top_k]
    ]


def _retrieve_hybrid(
    question: str,
    config: AppConfig,
    fetch_k: int,
    top_k: int,
    *,
    csv_route: bool,
) -> list[NodeWithScore]:
    pool_k = fetch_k
    if csv_route:
        # Name/row hits are often buried past top-12 in large CSV corpora.
        pool_k = max(fetch_k, 40)

    dense = retrieve_vector(question, config, pool_k)
    sparse = retrieve_bm25(question, config, pool_k)
    ranked_lists: list[list[NodeWithScore]] = [dense, sparse]
    entity_hits: list[NodeWithScore] = []

    if csv_route:
        entity_q = _entity_query(question)
        if entity_q:
            entity_hits = retrieve_bm25(entity_q, config, pool_k)
            ranked_lists.append(entity_hits)
            logger.info("csv_route entity BM25 query=%r", entity_q[:80])
        alt = keyword_query(question)
        if alt and alt.lower() != question.strip().lower():
            ranked_lists.append(retrieve_bm25(alt, config, pool_k))
            ranked_lists.append(retrieve_vector(alt, config, pool_k))

    fused = reciprocal_rank_fusion(ranked_lists, pool_k)
    if csv_route:
        fused = csv_boost(fused, question)
        # Keep entity BM25 candidates in the pool — RRF often buries rank-10..30 name hits.
        if entity_hits:
            fused = _merge_hits([*entity_hits[:25], *fused], limit=max(pool_k, 50))
        fused = lexical_rerank(question, fused, top_k)
        return fused
    return fused[:top_k]


def retrieve(
    question: str,
    config: AppConfig,
    pipe: PipelineConfig,
) -> list[NodeWithScore]:
    """Dispatch retrieval according to pipeline config."""
    fetch_k = pipe.retrieve_k or pipe.top_k
    mode = pipe.retrieval_mode

    if mode == "vector":
        hits = retrieve_vector(question, config, fetch_k)
        if pipe.expand_query:
            alt = keyword_query(question)
            if alt and alt.lower() != question.strip().lower():
                extra = retrieve_vector(alt, config, fetch_k)
                hits = _merge_hits([*hits, *extra], pipe.top_k)
                logger.info(
                    "Pipeline %s merged expanded retrieval (alt=%r) -> %d chunks",
                    pipe.name,
                    alt[:80],
                    len(hits),
                )
                return hits
        return hits[: pipe.top_k]

    if mode == "hybrid":
        return _retrieve_hybrid(question, config, fetch_k, pipe.top_k, csv_route=False)

    if mode == "csv_hybrid":
        return _retrieve_hybrid(question, config, fetch_k, pipe.top_k, csv_route=True)

    if mode == "hybrid_expand":
        hits = _retrieve_hybrid(question, config, fetch_k, fetch_k, csv_route=False)
        alt = keyword_query(question)
        if alt and alt.lower() != question.strip().lower():
            extra_dense = retrieve_vector(alt, config, fetch_k)
            extra_sparse = retrieve_bm25(alt, config, fetch_k)
            extra = reciprocal_rank_fusion([extra_dense, extra_sparse], fetch_k)
            hits = reciprocal_rank_fusion([hits, extra], pipe.top_k)
            logger.info(
                "Pipeline %s hybrid_expand (alt=%r) -> %d chunks",
                pipe.name,
                alt[:80],
                len(hits),
            )
            return hits
        return hits[: pipe.top_k]

    if mode == "vector_rerank":
        pool_k = pipe.rerank_candidates or max(fetch_k, pipe.top_k * 2)
        hits = retrieve_vector(question, config, pool_k)
        return lexical_rerank(question, hits, pipe.top_k)

    raise ValueError(f"Unknown retrieval_mode: {mode}")
