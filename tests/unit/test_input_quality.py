"""Check bounded reads, explicit failures, portable paths and record quality."""

import hashlib
import io
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from skillguard.adapters.files import SkillInputError, SkillTooLargeError, load_skills, read_skill
from skillguard.domain import Finding, Skill


def test_single_file_keeps_raw_hash_and_reports_decoding_replacement(tmp_path):
    """Never silently change identity when decoding invalid UTF-8."""
    path = tmp_path / "example.md"
    raw = b"Text \xff"
    path.write_bytes(raw)
    record = read_skill(path)
    assert record.repository == ""
    assert record.sha256 == hashlib.sha256(raw).hexdigest()
    assert record.decoding_replaced
    assert path.read_bytes() == raw


@pytest.mark.parametrize("limit", [0, -1, True, 1.5])
def test_invalid_read_limit_is_rejected(tmp_path, limit):
    """Invalid configuration must not accidentally request an unbounded read."""
    with pytest.raises(SkillInputError, match="positive integer"):
        read_skill(tmp_path / "file", max_bytes=limit)


def test_oversized_single_file_is_rejected_not_truncated(tmp_path):
    """Partial text must not look like a successful complete-file analysis."""
    path = tmp_path / "SKILL.md"
    path.write_bytes(b"12345")
    with pytest.raises(SkillTooLargeError):
        read_skill(path, max_bytes=4)
    assert read_skill(path, max_bytes=5).text == "12345"


def test_growth_during_read_is_bounded(tmp_path, monkeypatch):
    """Detect overflow even if size changed after the initial stat check."""
    path = tmp_path / "SKILL.md"
    path.write_bytes(b"x")
    requests = []

    class GrowingFile(io.BytesIO):
        """Simulate additional bytes appearing after stat without changing a file."""

        def read(self, size=-1):
            """Record the requested size and return the simulated bytes."""
            requests.append(size)
            return super().read(size)

    monkeypatch.setattr(Path, "open", lambda self, *a, **k: GrowingFile(b"12345"))
    with pytest.raises(SkillTooLargeError):
        read_skill(path, max_bytes=4)
    assert requests == [5]


def test_batch_paths_portable_and_root_skill_not_misidentified(tmp_path):
    """Do not mislabel a root-level filename as the repository name."""
    (tmp_path / "SKILL.md").write_text("root", encoding="utf-8")
    directory = tmp_path / "repo" / "nested"
    directory.mkdir(parents=True)
    (directory / "SKILL.md").write_text("body", encoding="utf-8")
    with pytest.warns(UserWarning, match="without repository folder"):
        records = list(load_skills(tmp_path))
    assert records[0].source == "repo/nested/SKILL.md"
    assert records[0].repository == "repo"


def test_empty_valid_root_is_distinct_from_invalid_input(tmp_path):
    """Valid empty folders succeed, while invalid paths raise an error."""
    assert list(load_skills(tmp_path)) == []
    with pytest.raises(SkillInputError):
        list(load_skills(tmp_path / "missing"))
    with pytest.raises(SkillInputError):
        read_skill(tmp_path)


def test_link_directory_is_pruned_without_os_link_privileges(tmp_path, monkeypatch):
    """Check traversal pruning deterministically even where links cannot be created."""
    import skillguard.adapters.files as adapter
    directory = tmp_path / "linked-repo"
    directory.mkdir()
    (directory / "SKILL.md").write_text("not to be read", encoding="utf-8")
    real_check = adapter._is_link
    monkeypatch.setattr(adapter, "_is_link", lambda path: path == directory or real_check(path))
    with pytest.warns(UserWarning, match="linked directory"):
        assert list(load_skills(tmp_path)) == []


def test_record_immutability_and_finding_validation():
    """Prevent accidental mutation and malformed review records."""
    record = Skill("repo", "source", "test-hash", "text")
    with pytest.raises(FrozenInstanceError):
        record.text = "changed"
    for line in [0, -1, True, 1.5]:
        with pytest.raises(ValueError):
            Finding("source", line, "CMD", "CMD-001", "evidence", "why", context="prose")
    with pytest.raises(ValueError, match="review_level"):
        Finding("source", 1, "CMD", "CMD-001", "evidence", "why", context="prose", review_level="malicious")
    with pytest.raises(ValueError, match="rule_id"):
        Finding("source", 1, "CMD", "", "evidence", "why", context="prose")
    assert Finding("source", 1, "NET", "NET-001", "url", "documentation", context="prose", review_level="info").review_level == "info"
