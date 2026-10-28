"""Read local skill copies with bounded memory and explicit input diagnostics.

read_skill supports a single file; load_skills supports root/<repository>/**/SKILL.md.
Duplicate copies are retained for reuse analysis. Reads never execute content.
Batch paths use forward slashes for reproducible output across operating systems.
This adapter does not read the GitSkills SQLite database. Link checks reduce
accidental traversal, but are not a sandbox against concurrent filesystem changes.
"""

import hashlib
import os
import warnings
from collections.abc import Iterator
from pathlib import Path

from skillguard.domain import Skill

MAX_BYTES = 1_000_000


class SkillInputError(ValueError):
    """A supplied path is unsuitable for reading as a complete skill file."""


class SkillTooLargeError(SkillInputError):
    """A skill exceeds the configured byte limit; partial text is not analyzed."""


def _is_link(path: Path) -> bool:
    """Recognize symbolic links and Windows junctions where Python supports them."""
    return path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction())


def read_skill(path: str | Path, *, repository: str = "", source: str | None = None,
               max_bytes: int = MAX_BYTES) -> Skill:
    """Read one complete local file, rejecting links and oversized content.

    Args:
        path: Local file path; the filename need not be SKILL.md for single-file use.
        repository: Explicit identifier, left unknown by default.
        source: Optional provenance label; defaults to the supplied POSIX path.
        max_bytes: Positive integer limit on bytes accepted, inclusive.

    Returns:
        Skill containing SHA-256 of the original bytes and decoded UTF-8 text.
        Invalid UTF-8 is replaced and recorded in decoding_replaced. Empty files
        are valid. At most max_bytes + 1 bytes are read to detect overflow.

    Raises:
        SkillInputError: Invalid limit, missing/non-file input, or file link.
        SkillTooLargeError: Input exceeds the byte limit, including during reading.
        OSError: Inspection or reading fails, such as permission or device errors.
    """
    if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or max_bytes < 1:
        raise SkillInputError("max_bytes must be a positive integer")
    path = Path(path)
    if _is_link(path) or not path.is_file():
        raise SkillInputError(f"Not a regular, non-link file: {path}")
    if path.stat().st_size > max_bytes:
        raise SkillTooLargeError(f"File exceeds {max_bytes} bytes: {path}")
    with path.open("rb") as handle:
        data = handle.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise SkillTooLargeError(f"File exceeds {max_bytes} bytes: {path}")
    try:
        text = data.decode("utf-8")
        replaced = False
    except UnicodeDecodeError:
        text = data.decode("utf-8", errors="replace")
        replaced = True
    return Skill(repository, source if source is not None else path.as_posix(),
                 hashlib.sha256(data).hexdigest(), text, replaced)


def _raise_walk_error(error: OSError) -> None:
    """Expose inaccessible directories instead of silently scanning partial input."""
    raise error


def load_skills(root: str | Path) -> Iterator[Skill]:
    """Yield skill copies in sorted relative-path order, preserving duplicates.

    Args:
        root: Existing parent directory containing repository folders.

    Yields:
        Skill records with repository names taken from the first relative folder.
        File links, oversized files, linked directories and root-level SKILL.md
        files are skipped with UserWarning diagnostics rather than silently.

    Raises:
        SkillInputError: The root is missing, linked, or not a directory.
        OSError: Directory traversal or file reading fails; a partial scan must
            not appear successful. The pipeline should surface the error.

    Notes:
        An empty valid root yields no records. Directory/file candidates are
        materialized for globally stable ordering; file contents are read lazily.
        Parent-path links and file replacement races are not sandboxed.
    """
    root = Path(root)
    if _is_link(root) or not root.is_dir():
        raise SkillInputError(f"Root must be an existing, non-link directory: {root}")
    candidates = []
    for directory, folders, names in os.walk(root, followlinks=False, onerror=_raise_walk_error):
        kept = []
        for folder in sorted(folders):
            child = Path(directory) / folder
            if _is_link(child):
                warnings.warn(f"Skipping linked directory: {child}", UserWarning, stacklevel=2)
            else:
                kept.append(folder)
        folders[:] = kept
        if "SKILL.md" in names:
            candidates.append(Path(directory) / "SKILL.md")
    for path in sorted(candidates, key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root)
        if len(relative.parts) < 2:
            warnings.warn(f"Skipping skill without repository folder: {path}", UserWarning, stacklevel=2)
            continue
        try:
            yield read_skill(path, repository=relative.parts[0], source=relative.as_posix())
        except SkillInputError as error:
            warnings.warn(f"Skipping skill: {error}", UserWarning, stacklevel=2)
