import pytest

from skillguard.adapters.files import read_skill
from skillguard.cli import main


def test_read_skill_and_scan_file(tmp_path, capsys):
    path = tmp_path / "SKILL.md"
    path.write_text("---\nname: t\n---\n```bash\npip install x\n```\n")
    skill = read_skill(str(path))
    assert skill.text.startswith("---") and len(skill.sha) == 64
    main(["scan-file", str(path)])
    out = capsys.readouterr().out
    assert "INST-001" in out and "CMD-001" in out


def test_read_skill_rejects_symlinks(tmp_path):
    target = tmp_path / "real.md"
    target.write_text("x")
    link = tmp_path / "SKILL.md"
    link.symlink_to(target)
    with pytest.raises(ValueError):
        read_skill(str(link))
