# ADR-007: ONNX MiniLM for Local Embedding Pipeline

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Hannah Tanaka

## Context

Eval laptop ingest needed offline embeddings without OpenAI spend.

## Decision drivers

- No API key required for default ingest
- Deterministic vectors across Windows/Linux
- Acceptable recall for handbook-scale corpora

## Decision

Default `EMBEDDING_PROVIDER=local` with Chroma ONNX MiniLM; OpenAI embeddings remain optional for production A/B.

## Consequences

Eval comparisons must record embedding fingerprint in ingest_meta.json.
