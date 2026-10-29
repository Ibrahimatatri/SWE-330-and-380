"""Architecture conformance (ADR-0002): dependency direction is checked on every test run.

GQM metric M2.2 is the number of violations this test reports.
"""

import ast
import sys
from pathlib import Path

SRC = Path(__file__).parents[2] / "src" / "skillguard"

# Internal modules each layer may import. Anything not listed is a violation.
ALLOWED = {
    "domain": set(),
    "parsing": {"domain"},
    "detectors": {"domain", "parsing", "detectors"},
    "scan": {"domain", "parsing", "detectors"},
    "analysis": {"domain"},
    "adapters": {"domain", "adapters"},
    "cli": {"analysis", "adapters", "detectors", "scan", "domain"},
    "baseline": set(),  # Sprint 1 baseline stays a standalone single file
}
CORE = ("domain", "parsing", "detectors", "scan", "analysis")
CORE_FORBIDDEN_STDLIB = {"sqlite3", "csv", "json", "os", "pathlib", "io", "shutil", "subprocess", "socket", "urllib"}


def layer(path: Path) -> str:
    rel = path.relative_to(SRC).parts
    return rel[0].removesuffix(".py")


def imports(path: Path):
    """Yield (internal_layer or None, top-level module name) for each import in a file."""
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.ImportFrom) and node.level:
            base = path.parent
            for _ in range(node.level - 1):
                base = base.parent
            target = (base / (node.module or "").replace(".", "/")).resolve()
            parts = target.relative_to(SRC.resolve()).parts if target != SRC.resolve() else ()
            if not parts:  # "from . import x" at package root
                for alias in node.names:
                    yield alias.name, alias.name
            else:
                yield parts[0].removesuffix(".py"), parts[0]
        elif isinstance(node, ast.ImportFrom):
            yield None, (node.module or "").split(".")[0]
        elif isinstance(node, ast.Import):
            for alias in node.names:
                yield None, alias.name.split(".")[0]


def violations():
    found = []
    for py in SRC.rglob("*.py"):
        if py.name in ("__init__.py", "__main__.py") and py.parent == SRC:
            continue
        me = layer(py)
        for internal, module in imports(py):
            if internal is not None and internal != me and internal not in ALLOWED[me]:
                found.append(f"{py.relative_to(SRC)} -> {internal}")
            if internal is None and me in CORE and module in CORE_FORBIDDEN_STDLIB:
                found.append(f"{py.relative_to(SRC)} -> {module} (I/O in core)")
    return found


def test_no_dependency_rule_violations():
    assert violations() == []


def test_checker_catches_a_violation(tmp_path, monkeypatch):
    fake = tmp_path / "skillguard"
    (fake / "detectors").mkdir(parents=True)
    (fake / "detectors" / "bad.py").write_text("import sqlite3\nfrom ..adapters import report\n")
    monkeypatch.setattr(sys.modules[__name__], "SRC", fake)
    assert sorted(violations()) == ["detectors/bad.py -> adapters", "detectors/bad.py -> sqlite3 (I/O in core)"]
