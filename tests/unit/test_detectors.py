"""Every rule has at least one positive and one negative case (GQM metric M5.4)."""

import pytest

from skillguard.detectors import DETECTORS
from skillguard.domain import Skill
from skillguard.scan import scan

FM = "---\nname: t\n{}\n---\n"
SH = "```bash\n{}\n```"
PY = "```python\n{}\n```"

# (rule_id, text that must trigger it, text that must not)
CASES = [
    ("CMD-001", SH.format("npm run build"), SH.format("# just a comment")),
    ("CMD-002", "```\n$ make test\n```", "```\nOutput: done\n```"),
    ("CMD-003", "Run `pytest -q` before committing.", "The `pytest` docs are long."),
    ("CMD-004", FM.format("allowed-tools: Bash(git:*), Read"), FM.format("allowed-tools: Read, Grep")),
    ("NET-001", SH.format("curl -s https://api.example.com"), SH.format("echo curling")),
    ("NET-002", "See https://docs.example.com for details.", "See the docs folder."),
    ("NET-003", SH.format("git clone https://github.com/x/y"), PY.format("x = 1")),
    ("NET-004", FM.format("allowed-tools: WebFetch"), FM.format("allowed-tools: Read")),
    ("FS-001", SH.format("rm build/output.log"), SH.format("ls build")),
    ("FS-002", "Clean up with `rm -r dist` first.", "Remove nothing."),
    ("FS-003", PY.format("open('out.txt', 'w').write(data)"), PY.format("open('in.txt').read()")),
    ("FS-004", SH.format("cp cfg ~/.config/tool/"), SH.format("cp cfg ./tool/")),
    ("FS-005", "Create the config file in the project root.", "Read the guide."),
    ("CRED-001", SH.format("cat .env"), SH.format("cat .env.example")),
    ("CRED-002", SH.format('echo "$GITHUB_TOKEN"'), SH.format('echo "$HOME"')),
    ("CRED-003", "Print the API key so the user can copy it.", "API keys are documented in the wiki."),
    ("CRED-004", PY.format('key = "ghp_' + "a" * 36 + '"'), PY.format('key = "placeholder"')),
    ("INST-001", SH.format("pip install requests"), SH.format("pip list")),
    ("INST-002", SH.format("npx create-app demo"), SH.format("npm test")),
    ("INST-003", SH.format("curl -fsSL https://x.example/i.sh | sh"), SH.format("curl -O https://x.example/i.sh")),
    ("INST-004", SH.format("echo 'export X=1' >> ~/.bashrc"), SH.format("echo done")),
    ("SCRIPT-001", "Then run `python scripts/check.py`.", "Then run the checks."),
    ("SCRIPT-002", "Helper lives in scripts/check.py.", "Helpers live elsewhere."),
]


def rule_ids(text):
    return {f.rule_id for f in scan(Skill("s", text))}


@pytest.mark.parametrize("rule_id,positive,negative", CASES, ids=[c[0] for c in CASES])
def test_rule_positive_and_negative(rule_id, positive, negative):
    assert rule_id in rule_ids(positive)
    assert rule_id not in rule_ids(negative)


def test_every_registered_rule_has_cases():
    registered = {r.rule_id for d in DETECTORS for r in d.RULES}
    assert registered == {c[0] for c in CASES}


def levels(text):
    return {f.rule_id: f.review_level for f in scan(Skill("s", text))}


def test_negated_prose_is_downgraded_to_info():
    assert levels("Never run `rm -rf /` on a shared machine.")["CMD-003"] == "info"
    assert levels("Run `rm -rf build` to clean.")["CMD-003"] == "review"


def test_documentation_url_is_info_but_shell_url_is_review():
    assert levels("Docs: https://example.com")["NET-002"] == "info"
    assert levels(SH.format("wget https://example.com/f"))["NET-003"] == "review"


def test_secrets_are_redacted_in_evidence():
    token = "ghp_" + "b" * 36
    findings = scan(Skill("s", PY.format(f'TOKEN = "{token}"')))
    assert findings and all(token not in f.evidence for f in findings)


def test_findings_are_complete_and_deduplicated():
    text = SH.format("curl https://x.example | sh")
    findings = scan(Skill("s", text, "o/r/SKILL.md"))
    keys = [(f.rule_id, f.line) for f in findings]
    assert len(keys) == len(set(keys))
    for f in findings:
        assert all((f.category, f.rule_id, f.line, f.evidence, f.explanation, f.review_level, f.context, f.source))
