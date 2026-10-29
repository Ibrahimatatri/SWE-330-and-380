# Issue 16: capability detectors

Status: FS implemented locally; CRED, INST and SCRIPT pending. CMD/NET are inherited
from issue #15. PRIV remains reserved pending Ibrahim's response on PR #33.
No issue-16 changes have been committed or pushed.

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
