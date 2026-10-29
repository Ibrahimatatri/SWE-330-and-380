# Issue 16: capability detectors

Status: FS and CRED implemented; INST and SCRIPT pending. CMD/NET are inherited
from issue #15. PRIV remains reserved pending Ibrahim's response on PR #33.
FS was committed separately; CRED is the next local change for review.

## File-system detector

`detectors/filesystem.py` checks parsed skill text; it never reads or modifies the
files mentioned by that text. `detect(parsed)` returns findings through the shared
interface. The pipeline and CSV writer were not changed to support the category.

| Rule | Signal | Context notes |
| --- | --- | --- |
| FS-101 | File-reading command such as cat or Get-Content | Requires a path-looking argument |
| FS-102 | File-changing command such as cp, mkdir or Set-Content | Prose mentions need a preceding action verb to count |
| FS-103 | File write/remove API such as open(..., 'w') or writeFile | Recognizes Python and JavaScript-family code contexts |
| FS-104 | Home/system path such as /etc/ or USERPROFILE | Prose needs an action; path mention alone is info |

New rules use IDs starting at 101 to avoid reusing IDs with a different meaning
in Ibrahim's candidate implementation. Cross-implementation rule mapping must be
explicit during comparison; category-level results remain comparable only after
checking differences in definitions and context policy.

`PatternRule` and `evaluate_rules` in `_rules.py` share matching and review policy.
Negated prose, comments and nested non-executable examples remain informational;
metadata is skipped. Warnings and examples are heuristics, not proven intent.
Python/JavaScript API rules can count explicit write code while unrelated code is
not automatically considered shell execution.

## Verification

126 passed, 1 skipped after adding FS. Every FS rule has positive and negative
examples, with tests for context, CSV integration and no instruction execution.
The skip needs real symbolic-link creation permission. No full-dataset accuracy,
coverage completeness, or manual precision/recall result is claimed.

## Known limits

- Supported commands/APIs are a finite pattern set, not a complete language parser.
- File access may be legitimate; actual permissions and project boundaries are unknown.
- Negation and prose-action handling can misread complex clauses.
- Local file loading does not establish whether referenced scripts are bundled.
- Tests are synthetic; real dataset examples still need manual validation.

## Credential detector

`detectors/credentials.py` detects credential references without reading the
referenced files or environment variables. CRED-101 covers .env (excluding common
template names), AWS credentials and selected SSH private-key paths. CRED-102
covers credential environment variables, including Python/JavaScript examples.
CRED-103 covers explicit prose instructions involving credentials or API keys.
Prose needs a preceding action; warnings and comments remain informational.
Evidence uses the shared masking helper, which is not a complete secret filter.
These finite patterns do not establish that credentials exist or are disclosed.

Verification after CRED: 141 passed, 1 symbolic-link test skipped. Synthetic tests
cover each rule, contextual negatives, password masking and CSV integration.
Real GitSkills database validation is still pending.
