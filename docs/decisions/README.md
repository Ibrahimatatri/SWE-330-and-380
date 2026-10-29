# Architectural Decision Records

Status key: **Proposed** = drafted 2026-10-26 for team review (issue #14); the architecture lead (Baiselaired) accepts, amends, or rejects each one in the PR review. Each record lists context, options, decision, rationale and benefits, costs and risks, and consequences, as SWE 330 Phase 2 requires.

| ADR | Decision | Phase 2 topic |
|---|---|---|
| [0001](0001-modular-monolith.md) | Modular monolith with ports-and-adapters boundaries | Decomposition and boundaries |
| [0002](0002-dependency-direction.md) | Dependencies point inward; pure core; enforced by a test | Dependency direction and interfaces |
| [0003](0003-detector-registry.md) | Detectors are declarative rule modules in one registry | Interfaces; extension point; what counts as "core" for GQM Q1 |
| [0004](0004-data-management.md) | Read the SQLite release in place; derive a small hash index | Data management and persistence |
| [0005](0005-integration.md) | In-process calls; steps exchange files (JSONL/CSV) via a CLI and Makefile | Communication and integration |
| [0006](0006-error-handling.md) | Fail fast on configuration, degrade gracefully on data | Error handling and failure behavior |
| [0007](0007-security-privacy.md) | Never execute content; read-only data; masked secrets; blind validation | Security and privacy |
| [0008](0008-testing-observability.md) | Layered tests, conformance test, deterministic outputs, counted logs | Testing and observability |
| [0009](0009-execution-environment.md) | Local single-process Python 3.10+; no containers or services | Deployment and execution environment |
