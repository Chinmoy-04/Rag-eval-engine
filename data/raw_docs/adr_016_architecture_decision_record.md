# ADR-016: Slurm Fair-Share for Research GPUs

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Gabriel O'Connor

## Context

Interactive Jupyter jobs starved batch training queues.

## Decision drivers

- Protect batch queue latency
- Publish per-team allocations
- Preemption for idle interactive sessions

## Decision

Adopt fair-share weights from `slurm_queue_allocations.csv`; interactive sessions preempted after 45 idle minutes.

## Consequences

See `gpu_cluster_scheduling_and_slurm_policy.md` and `sop_slurm_gpu_job_submission.txt`.
