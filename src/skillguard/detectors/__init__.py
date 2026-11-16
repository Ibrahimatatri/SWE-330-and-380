"""Built-in detector registry; adding a category does not change the pipeline."""

from .commands import CommandDetector
from .network import NetworkDetector
from .interface import Detector


def default_detectors() -> tuple[Detector, ...]:
    """Return fresh built-in plugins in a stable order (CMD and NET for issue #15)."""
    return (CommandDetector(), NetworkDetector())
