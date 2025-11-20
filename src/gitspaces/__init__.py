"""GitSpaces - A git development workspace manager."""

__version__ = "2.0.36"
__author__ = "David Rowe"
__email__ = "davfive@gmail.com"

from .modules.project import Project
from .modules.space import Space

__all__ = ["Project", "Space", "__version__"]
