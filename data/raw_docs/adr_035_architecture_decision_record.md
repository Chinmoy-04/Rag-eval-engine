# ADR-035: Telemetry Metric Catalog Ownership

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Observability

## Context

Duplicate metric names broke burn-rate alerts.

## Decision drivers

- Unique metric registry
- Owner per metric family
- Cardinality budgets

## Decision

New metrics must be registered in `telemetry_metrics_catalog_*.csv` before production dashboards reference them.

## Consequences

Unregistered metrics are dropped from the global recording rules pack.
