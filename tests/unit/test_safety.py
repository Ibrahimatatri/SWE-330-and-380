"""Content is handled only as text (THREAT_MODEL.md §1B, issue #10)."""

import ast
from pathlib import Path

from skillguard.baseline import scan

SRC = Path(__file__).parents[2] / "src" / "skillguard"
FORBIDDEN_MODULES = {"subprocess", "socket", "urllib", "http", "requests", "httpx", "importlib", "pty", "shutil"}
FORBIDDEN_BUILTINS = {"eval", "exec", "compile", "__import__"}
FORBIDDEN_OS_PREFIXES = ("system", "popen", "spawn", "exec", "fork")


def test_source_never_imports_execution_or_network_modules():
    for py in SRC.rglob("*.py"):
        for node in ast.walk(ast.parse(py.read_text())):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            for name in names:
                assert name.split(".")[0] not in FORBIDDEN_MODULES, f"{py.name} imports {name}"


def test_source_never_calls_exec_like_functions():
    for py in SRC.rglob("*.py"):
        for node in ast.walk(ast.parse(py.read_text())):
            if isinstance(node, ast.Call):
                fn = node.func
                if isinstance(fn, ast.Name):
                    assert fn.id not in FORBIDDEN_BUILTINS, f"{py.name} calls {fn.id}"
                elif isinstance(fn, ast.Attribute) and getattr(fn.value, "id", "") == "os":
                    assert not fn.attr.startswith(FORBIDDEN_OS_PREFIXES), f"{py.name} calls os.{fn.attr}"


def test_scanning_a_command_does_not_run_it(tmp_path):
    canary = tmp_path / "canary"
    text = f"```bash\ntouch {canary}\necho pwned > {canary}\n```"
    findings = scan(text, "canary")
    assert findings, "command should be detected"
    assert not canary.exists(), "scanning must never execute content"
