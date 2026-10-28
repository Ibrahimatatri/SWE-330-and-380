"""Check the local-file adapter against the original baseline contract."""

import hashlib
from pathlib import Path

import pytest

from skillguard.adapters.files import MAX_BYTES, SkillInputError, SkillTooLargeError, load_skills, read_skill
from skillguard.baseline import load_dir

FIXTURES = Path(__file__).parents[1] / "fixtures" / "repos"


def write_skill(root, repository, folder, data):
    """Create a temporary skill file and return its path."""
    path = root / repository / folder / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def test_fixture_records_preserve_baseline_values_and_order():
    """Changing the record format must not change the baseline's inputs."""
    records = [
        (skill.repository, skill.source, skill.sha256, skill.text)
        for skill in load_skills(FIXTURES)
    ]
    assert records
    expected = [(repo, Path(source).as_posix(), sha, text)
                for repo, source, sha, text in load_dir(FIXTURES)]
    assert records == expected


def test_duplicate_copies_remain_available_for_reuse_counting(tmp_path):
    """The reader must not discard copies from different repositories."""
    data = b"# Shared skill\n"
    write_skill(tmp_path, "zeta", "skills", data)
    write_skill(tmp_path, "alpha", "skills", data)
    records = list(load_skills(tmp_path))
    assert [record.repository for record in records] == ["alpha", "zeta"]
    assert records[0].sha256 == records[1].sha256
    assert records[0].source != records[1].source


def test_invalid_utf8_is_replaced_but_fingerprint_uses_original_bytes(tmp_path):
    """Decoding repairs text without changing the identity of original bytes."""
    data = b"Example: \xff\n"
    path = write_skill(tmp_path, "repo", "skills", data)
    record, = load_skills(tmp_path)
    assert record.text == "Example: \ufffd\n"
    assert record.decoding_replaced
    assert record.sha256 == hashlib.sha256(data).hexdigest()
    assert path.read_bytes() == data


def test_size_limit_includes_boundary_and_skips_larger_files(tmp_path):
    """Accept the exact baseline limit and skip files one byte above it."""
    write_skill(tmp_path, "repo", "boundary", b"x" * MAX_BYTES)
    write_skill(tmp_path, "repo", "oversized", b"x" * (MAX_BYTES + 1))
    with pytest.warns(UserWarning, match="exceeds"):
        records = list(load_skills(tmp_path))
    assert len(records) == 1
    assert "boundary" in records[0].source


def test_only_skill_files_are_loaded(tmp_path):
    """Ignore other filenames and directories named SKILL.md."""
    (tmp_path / "repo" / "SKILL.md").mkdir(parents=True)
    (tmp_path / "repo" / "README.md").write_text("Not a skill", encoding="utf-8")
    assert list(load_skills(tmp_path)) == []


def test_missing_root_raises_clear_error(tmp_path):
    """An invalid path must not masquerade as an empty successful scan."""
    with pytest.raises(SkillInputError, match="Root"):
        list(load_skills(tmp_path / "missing"))


def test_symbolic_link_file_is_skipped(tmp_path):
    """Do not follow a SKILL.md file link when the OS permits link creation."""
    target = tmp_path / "target.txt"
    target.write_text("Example", encoding="utf-8")
    link = tmp_path / "repo" / "SKILL.md"
    link.parent.mkdir()
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("Creating symbolic links is unavailable in this environment")
    with pytest.warns(UserWarning, match="Skipping skill"):
        assert list(load_skills(tmp_path)) == []
