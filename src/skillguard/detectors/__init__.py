"""Built-in detector registry; adding a category does not change the pipeline."""

from .commands import CommandDetector
from .network import NetworkDetector
from .filesystem import FileSystemDetector
from .interface import Detector


def default_detectors() -> tuple[Detector, ...]:
    """Return fresh built-in plugins in stable order; FS is the first #16 addition."""
    return (CommandDetector(), NetworkDetector(), FileSystemDetector())
