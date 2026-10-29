"""Local-file adapter: one SKILL.md on disk -> Skill. Read as text with a size cap; never executed."""

import hashlib
from pathlib import Path

from ..domain import Skill

MAX_BYTES = 1_000_000


def read_skill(path: str) -> Skill:
    p = Path(path)
    if p.is_symlink() or not p.is_file():
        raise ValueError(f"not a regular file: {path}")
    data = p.read_bytes()[:MAX_BYTES]
    return Skill(hashlib.sha256(data).hexdigest(), data.decode("utf-8", errors="replace"), str(p))
