# ADR-018: Laptop Imaging and Deprovisioning

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Chen Garcia

## Context

Departing employees retained admin images for weeks after access revocation.

## Decision drivers

- Same-day deprovision for involuntary exits
- Verified disk wipe
- Asset ID reconciliation

## Decision

Follow `sop_laptop_imaging_deprovisioning.txt` and `sop_employee_departure_and_revocation.txt` in order.

## Consequences

People Ops closes the Workday case only after IT confirms wipe attestation.
