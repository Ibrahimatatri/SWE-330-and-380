"""Recognize metadata and fenced-code context once for all detectors.

Supports backtick/tilde fences, matching closing lengths, language info strings,
and closed YAML front matter at the beginning of a file. Original text and line
numbers are retained. This is a small structural parser, not full CommonMark or
YAML validation: indented code, blockquote/list nesting, HTML and inline code are
not classified. No data is executed and no files or network resources are opened.
"""

import re

from skillguard.domain import ParsedLine, ParsedSkill, Skill

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def parse_skill(skill: Skill) -> ParsedSkill:
    """Classify each line without modifying or executing the Skill.

    Args:
        skill: Already-loaded text and provenance.

    Returns:
        ParsedSkill with all original lines, immutable context and diagnostics.
        Empty text has no lines. Metadata requires an initial --- and a closing
        --- or ...; unclosed metadata is treated as prose with a warning.
        A code fence closes only with the same marker, at least the opening
        length, and no trailing content. Unclosed code extends to end-of-file.

    Notes:
        Delimiters may have up to three leading spaces. A UTF-8 BOM on the first
        line is ignored for structure only. Backticks in a backtick info string
        are invalid. The first whitespace-delimited info token is the language.
        Code labels are lowercased; metadata contents are not parsed as YAML.
    """
    texts = skill.text.splitlines()
    diagnostics = []
    metadata_end = -1
    if texts and texts[0].lstrip("\ufeff").strip() == "---":
        metadata_end = next((i for i in range(1, len(texts))
                             if texts[i].strip() in {"---", "..."}), -1)
        if metadata_end == -1:
            diagnostics.append("Unclosed front matter; treated as prose")

    marker, fence_length, language, opening_line = "", 0, "", 0
    lines = []
    for index, text in enumerate(texts):
        number = index + 1
        if index <= metadata_end:
            lines.append(ParsedLine(number, text, "front_matter"))
            continue
        structural = text.lstrip("\ufeff") if index == 0 else text
        match = FENCE.match(structural)
        if marker:
            if (match and match[1][0] == marker and len(match[1]) >= fence_length
                    and not match[2].strip()):
                lines.append(ParsedLine(number, text, "boundary", True))
                marker, fence_length, language = "", 0, ""
            else:
                lines.append(ParsedLine(number, text, f"code:{language}"))
            continue
        if match and not (match[1][0] == "`" and "`" in match[2]):
            marker, fence_length = match[1][0], len(match[1])
            info = match[2].strip().split()
            language = info[0].lower() if info else ""
            opening_line = number
            lines.append(ParsedLine(number, text, "boundary", True))
        else:
            lines.append(ParsedLine(number, text))
    if marker:
        diagnostics.append(f"Unclosed code fence starting at line {opening_line}")
    return ParsedSkill(skill, tuple(lines), tuple(diagnostics))
