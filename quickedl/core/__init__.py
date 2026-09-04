"""Core domain logic of QuickEDL v4 -- no GUI dependencies."""

from .colorset import Color, ColorSet, default_colorset_id, load_colorsets
from .models import Marker, MarkerLabel, MarkerType, PlaylistEntry
from .project import Project, ProjectError, suggest_project_path
from .registry import ProjectRegistry, RegistryEntry
from .settings import Settings

__all__ = [
    "Color",
    "ColorSet",
    "Marker",
    "MarkerLabel",
    "MarkerType",
    "PlaylistEntry",
    "Project",
    "ProjectError",
    "ProjectRegistry",
    "RegistryEntry",
    "Settings",
    "default_colorset_id",
    "load_colorsets",
    "suggest_project_path",
]
