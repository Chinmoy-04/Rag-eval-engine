# ADR-002: Chroma vs Managed Vector DB for Internal RAG

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Marcus Vance

## Context

Internal policy RAG currently uses local Chroma. Product wants multi-tenant isolation and PITR for customer pilots.

## Decision drivers

- RPO ≤ 15 minutes for vector indexes
- Per-tenant collection isolation
- Keep embed latency under 80ms p95 for MiniLM

## Decision

Keep Chroma for internal HelixForge handbook RAG; use managed OpenSearch k-NN for customer-facing retrieval only.

## Consequences

Two retrieval stacks remain. Internal eval tooling continues to target Chroma; customer RAG uses OpenSearch.
