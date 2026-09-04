"""
Plain text export in the v3 EDL format.

Since v4 projects are JSON documents, the human readable text file that v3 used
as its primary storage becomes an explicit export: for handover to other people,
for archiving, and for compatibility with anything that consumed the old files.
"""

from __future__ import annotations

from pathlib import Path

from .models import Marker, MarkerType

#: v3 wrote exactly twenty dashes as a divider line.
SEPARATOR_LINE = "-" * 20


def marker_to_line(marker: Marker) -> str:
    """Render one marker the way v3 wrote it (``HH:MM:SS - label``)."""
    if marker.type is MarkerType.SEPARATOR:
        return SEPARATOR_LINE
    return f"{marker.time_string} - {marker.label}"


def render_markers(markers: list[Marker]) -> str:
    lines = [marker_to_line(marker) for marker in markers]
    return "\n".join(lines) + ("\n" if lines else "")


def export_project(project, path: Path | str) -> Path:
    """Write the project's markers to ``path`` as a v3-style text file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markers(project.markers), encoding="utf-8")
    return path
