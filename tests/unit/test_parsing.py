"""Test intended context improvements separately from baseline compatibility."""

from pathlib import Path

import pytest

from skillguard.baseline import scan
from skillguard.domain import Skill
from skillguard.parsing import parse_skill

FIXTURES = Path(__file__).parents[1] / "fixtures" / "repos"


def parsed(text):
    """Parse an in-memory example without filesystem or dataset dependencies."""
    return parse_skill(Skill("repo", "SKILL.md", "test-hash", text))


def contexts(text):
    """Show meaningful content lines while keeping original numbering."""
    return [(line.number, line.context) for line in parsed(text).lines
            if not line.is_fence and line.text.strip() not in {"---", "..."}]


def test_metadata_prose_and_both_fence_markers():
    """Metadata is separate from prose and executable-looking code examples."""
    text = "---\nname: x\n---\nIntro\n```bash\nls\n```\n~~~python\nprint(1)\n~~~\n```\nplain\n```"
    assert contexts(text) == [(2, "front_matter"), (4, "prose"), (6, "code:bash"),
                              (9, "code:python"), (12, "code:")]


def test_nested_shorter_fence_and_info_string_do_not_close_outer_block():
    """A documented shell example inside Markdown must remain Markdown content."""
    text = "````md\n```bash\nls\n```\n````\nafter"
    assert contexts(text) == [(2, "code:md"), (3, "code:md"), (4, "code:md"), (6, "prose")]


@pytest.mark.parametrize("closing", ["~~~", "``", "```python"])
def test_wrong_marker_short_or_labeled_fence_does_not_close(closing):
    """Only a sufficiently long matching bare marker ends a code block."""
    result = parsed(f"```bash\necho hi\n{closing}\necho still inside")
    assert result.lines[-1].in_shell_block
    assert result.warnings


@pytest.mark.parametrize("label", ["bash", "SH", "shell", "zsh", "console",
                                    "powershell", "pwsh", "ps1", "cmd", "bat", "batch", "fish", "ksh"])
def test_supported_shell_labels(label):
    """Classify common Unix and Windows shell labels case-insensitively."""
    result = parsed(f"```{label} title=example\necho hi\n```")
    assert result.lines[1].in_shell_block
    assert not result.warnings


@pytest.mark.parametrize("label", ["python", "md", "", "javascript"])
def test_other_code_is_not_implicitly_shell(label):
    """Do not turn every code example into shell command execution."""
    assert not parsed(f"```{label}\nexample\n```").lines[1].in_shell_block


def test_unclosed_metadata_is_prose_and_diagnostic():
    """Avoid suppressing all content when the metadata closing delimiter is missing."""
    result = parsed("---\nname: x\nbody")
    assert [line.context for line in result.lines] == ["prose"] * 3
    assert result.warnings == ("Unclosed front matter; treated as prose",)


def test_bom_crlf_and_metadata_end_marker_preserve_original_text():
    """Support Windows text without changing content identity or line numbering."""
    text = "\ufeff---\r\nname: x\r\n...\r\n~~~PowerShell\r\nGet-Item .\r\n~~~~\r\n"
    result = parsed(text)
    assert [line.text for line in result.lines] == text.splitlines()
    assert [line.number for line in result.lines] == list(range(1, 7))
    assert result.lines[1].context == "front_matter"
    assert result.lines[4].in_shell_block
    assert not result.warnings


def test_metadata_fences_are_not_executable_context():
    """A fence-like metadata value must not start a code block."""
    result = parsed("---\n```bash\necho example\n---\nprose")
    assert not any(line.in_shell_block for line in result.lines)


def test_unclosed_code_has_location_diagnostic():
    """Keep remaining content inside the block and report the opening line."""
    result = parsed("Intro\n```sh\necho hi")
    assert result.lines[-1].in_shell_block
    assert result.warnings == ("Unclosed code fence starting at line 2",)


def test_empty_input():
    """An empty skill has no lines or structural warnings."""
    assert parsed("").lines == ()
    assert parsed("").warnings == ()


@pytest.mark.parametrize("text", ["    ```bash\necho hi", "```ba`sh\necho hi"])
def test_unsupported_or_invalid_opening_is_not_a_fence(text):
    """Indented code and invalid backtick info are outside supported fence syntax."""
    assert not any(line.is_fence for line in parsed(text).lines)


def test_standard_fixture_shell_candidates_still_match_baseline():
    """Preserve known valid baseline cases while testing improvements separately."""
    paths = list(FIXTURES.rglob("SKILL.md"))
    assert paths
    for path in paths:
        text = path.read_text(encoding="utf-8")
        result = parsed(text)
        actual = [line.number for line in result.lines if line.in_shell_block and line.text.strip()]
        expected = [row["line"] for row in scan(text, str(path)) if row["rule_id"] == "CMD-001"]
        assert actual == expected
