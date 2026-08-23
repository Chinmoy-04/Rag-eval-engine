# ADR-032: Documentation Style for Public APIs

**Status**: Accepted
**Date**: 2026-02-01
**Owner**: DevRel

## Context

Endpoint docs disagreed with OpenAPI and support macros.

## Decision drivers

- OpenAPI as source of truth
- Examples runnable
- Versioned changelog

## Decision

Public API docs follow `documentation_standards_and_style_guide.md`; OpenAPI wins on conflicts.

## Consequences

Support macros must link to versioned docs, not Notion drafts.
