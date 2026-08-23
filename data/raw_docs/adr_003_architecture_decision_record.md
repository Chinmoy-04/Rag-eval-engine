# ADR-003: vLLM PagedAttention for Shared GPU Inference

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Devon Hale

## Context

A100 nodes under-utilized at 41% due to KV-cache fragmentation across concurrent chat sessions.

## Decision drivers

- Increase tokens/sec/GPU by ≥1.8×
- Support continuous batching
- No regression on SEV-1 on-call paging latency

## Decision

Standardize production LLM serving on vLLM with PagedAttention; deprecate HuggingFace text-generation-inference by Q3.

## Consequences

Slurm queue `gpu-infer` updated. Checkpoint restore SOPs must reference vLLM engine versions.
