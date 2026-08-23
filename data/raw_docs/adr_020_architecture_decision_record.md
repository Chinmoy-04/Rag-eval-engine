# ADR-020: Cost Center Tagging on Cloud Resources

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Marcus Vance

## Context

Untagged GPU instances attributed incorrectly to CC-0000.

## Decision drivers

- 100% tag coverage for compute
- Monthly FinOps report by CC
- Block deploy without tags

## Decision

Required tags: `cost_center`, `team`, `environment`. CI fails if missing.

## Consequences

Canonical CC list is `cost_centers.csv`; billing extracts live in `cloud_billing_cost_center_report_*.csv`.
