"""ChangeLens: understand what actually changed between two versions of a document."""
from .compare import compare, Change, Severity

__version__ = "0.1.0"
__all__ = ["compare", "Change", "Severity", "__version__"]
