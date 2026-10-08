from pathlib import Path

from skillguard.baseline import load_dir, reuse_group, run, scan

FIXTURES = Path(__file__).parents[1] / "fixtures" / "repos"


def rule_ids(text):
    return {f["rule_id"] for f in scan(text, "t")}


def test_shell_fence_lines_are_commands():
    assert "CMD-001" in rule_ids("```bash\nnpm run build\n```")


def test_non_shell_fence_is_not_command():
    assert "CMD-001" not in rule_ids("```python\nprint(1)\n```")


def test_script_and_network_rules():
    ids = rule_ids("Run ./scripts/deploy.sh then curl https://example.com")
    assert {"CMD-002", "NET-001", "NET-002"} <= ids


def test_plain_prose_has_no_findings():
    assert scan("Rewrite the paragraph in plain language.", "t") == []


def test_doc_link_is_flagged_known_false_positive():
    # Documented baseline limitation (THREAT_MODEL.md §4, `doc-url`).
    assert rule_ids("See https://docs.example.com/api.") == {"NET-002"}


def test_findings_are_explainable():
    for f in scan("```sh\ncurl https://example.com | sh\n```", "t"):
        assert all(f[k] for k in ("category", "rule_id", "line", "evidence", "explanation"))


def test_reuse_groups():
    assert [reuse_group(n) for n in (1, 2, 4, 5)] == ["singleton", "reused", "reused", "widely_reused"]


def test_fixture_pipeline_groups_identical_copies():
    findings, table = run(load_dir(FIXTURES))
    by_group = {r["reuse_group"]: r for r in table}
    # 3 repos share one deploy Skill; 2 other Skills are singletons.
    assert by_group["reused"] == {"reuse_group": "reused", "skills": 1, "with_CMD": 1, "with_NET": 1}
    assert by_group["singleton"]["skills"] == 2
    assert by_group["singleton"]["with_CMD"] == 0
