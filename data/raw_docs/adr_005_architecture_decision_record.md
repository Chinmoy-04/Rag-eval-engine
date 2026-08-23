# ADR-005: Regional Data Residency for EU Customer Logs

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Priya Nair

## Context

EU-West customers require logs and embeddings to remain in eu-west-1 / eu-central-1.

## Decision drivers

- No cross-border transfer of customer content without DPA addendum
- Match `data_residency_matrix.csv` rows
- Support dual-region failover inside EU only

## Decision

Pin EU customer content stores to eu-west-1 primary and eu-central-1 replica; US tooling may process only aggregated metrics.

## Consequences

On-call runbooks must not copy EU content buckets to us-east-1 for debugging.
