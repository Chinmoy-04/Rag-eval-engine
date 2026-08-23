# ADR-033: Carbon Metrics for GPU Jobs

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Sustainability WG

## Context

FinOps reports omitted estimated kgCO2e for training runs.

## Decision drivers

- Per-job estimate
- Monthly rollup
- No blocking of research

## Decision

Emit estimates into `sustainability_and_carbon_metrics.csv` using the green-compute policy factors.

## Consequences

Estimates are advisory; they do not change Slurm scheduling priority in v1.
