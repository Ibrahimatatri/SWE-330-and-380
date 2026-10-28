"""Keep domain/parsing independent and detector plugins free of storage or UI."""

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2] / "src" / "skillguard"


@pytest.mark.parametrize("relative,forbidden", [
    ("domain.py", {"skillguard"}),
    ("parsing.py", {"skillguard.adapters", "skillguard.detectors", "skillguard.pipeline", "skillguard.cli"}),
    ("detectors", {"skillguard.adapters", "skillguard.parsing", "skillguard.pipeline", "skillguard.cli", "skillguard.baseline"}),
])
def test_imports_respect_module_boundaries(relative, forbidden):
    """Reject dependencies that would couple reusable logic to storage or orchestration."""
    from importlib.util import resolve_name
    target = ROOT / relative
    paths = sorted(target.rglob("*.py")) if target.is_dir() else [target]
    assert paths
    for path in paths:
        module_parts = ("skillguard", *path.relative_to(ROOT).with_suffix("").parts)
        package = ".".join(module_parts[:-1])
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                name = "." * node.level + (node.module or "")
                names = [resolve_name(name, package) if node.level else name]
            for name in names:
                assert not any(name == prefix or name.startswith(prefix + ".") for prefix in forbidden), (path, name)
