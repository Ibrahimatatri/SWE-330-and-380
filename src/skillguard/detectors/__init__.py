"""Built-in detector registry; adding a category does not change the pipeline."""

from .credentials import CredentialDetector
from .commands import CommandDetector
from .network import NetworkDetector
from .filesystem import FileSystemDetector
from .interface import Detector


def default_detectors() -> tuple[Detector, ...]:
    """Return fresh built-in plugins in stable order; includes FS and credential access."""
    return (CommandDetector(), NetworkDetector(), FileSystemDetector(), CredentialDetector())
