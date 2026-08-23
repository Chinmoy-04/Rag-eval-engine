# ADR-013: Prompt Injection Reporting Path

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: Isla Bhat

## Context

Red-team findings were filed as ordinary Jira bugs and missed security triage SLAs.

## Decision drivers

- Dedicated ticket type
- 24h ack for active exploits
- Link to model safety review

## Decision

All prompt-injection reports use the Security Intake form and `sop_prompt_injection_reporting.txt`.

## Consequences

Product bugs that are not security-relevant stay in the engineering backlog.
