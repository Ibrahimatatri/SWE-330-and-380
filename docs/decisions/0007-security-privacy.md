# ADR-0007: Never execute content; read-only data; masked secrets; blind validation

**Status:** Proposed · **Date:** 2026-10-26 · **Issues:** #5, #10, #19

## Context
Skill text contains shell commands, URLs, install steps, and sometimes secrets. The team's work must not run any of it, must not modify the release, and must not expose people or credentials in reports.

## Options considered
1. Rely on care and code review.
2. **Structural controls checked by tests, plus reporting rules.**

## Decision
Option 2.
- **No execution path:** the package never imports `subprocess`, `socket`, `urllib`, `http`, `importlib`, or `shutil`, and never calls `eval`, `exec`, `compile`, or `os.system`/`popen`/`spawn`/`exec*` (AST test). A canary test shows that scanning a command does not run it.
- **Read-only data:** the release is opened with `mode=ro&immutable=1`.
- **Secrets:** evidence is masked before it is stored (`CRED-004` matches token formats such as `ghp_…` and `AKIA…`; values are replaced with `[REDACTED]`).
- **Privacy:** results are aggregate. Validation sheets hold hashes and GitHub links, not Skill text. Authors are not named or profiled.
- **Validation bias:** raters see a sheet without predictions; predictions are in a separate key file.

## Rationale and expected benefits
The controls are cheap and tested on every run, rather than promised.

## Costs and risks
Masking is pattern-based and can miss unusual secret formats. Links in the validation sheet point to live repositories, which can change after collection.

## Consequences
49 sampled Skills contain strings that match hard-coded secret patterns (81 findings). They are reported only as counts, with masked evidence, and must be validated before any claim is made.
