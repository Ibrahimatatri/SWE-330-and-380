"""Built-in detector registry; adding a category does not change the pipeline."""

from .scripts import ScriptDetector
from .installation import InstallationDetector
from .credentials import CredentialDetector
from .commands import CommandDetector
from .network import NetworkDetector
from .filesystem import FileSystemDetector
from .interface import Detector


def default_detectors() -> tuple[Detector, ...]:
    """Return the six planned categories; PRIV remains reserved for the experiment."""
    return (
        CommandDetector(), NetworkDetector(), FileSystemDetector(),
        CredentialDetector(), InstallationDetector(), ScriptDetector(),
    )
