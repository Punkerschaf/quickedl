"""
Import of v3.x projects (a folder with three text files) into the v4 single-file format.

v3 marker lines only carried a wall clock time (``HH:MM:SS``) and no date, so the
date has to be reconstructed. The EDL file's modification time is taken as the
date of the *last* marker and the list is walked backwards, moving one day back
whenever the time jumps forward -- which is how a show that ran across midnight
shows up in the old format.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

from .models import Marker, MarkerLabel, MarkerType, PlaylistEntry, default_marker_labels
from .project import Project

logger = logging.getLogger(__name__)

MARKER_LINE_PATTERN = re.compile(r"^(?P<time>\d{2}:\d{2}:\d{2})\s+-\s+(?P<label>.*)$")
SEPARATOR_PATTERN = re.compile(r"^-{3,}$")


class MigrationError(Exception):
    """Raised when a folder cannot be read as a v3 project."""


@dataclass
class V3ProjectFiles:
    """The three files a v3 project folder is made of."""

    name: str
    folder: Path
    edl: Path
    markerlabel: Path | None
    playlist: Path | None


def find_v3_project(folder: Path | str) -> V3ProjectFiles:
    """Locate the v3 project files inside ``folder``.

    The project name is derived from the ``*_EDL.txt`` file, mirroring how v3
    discovered its own files by naming convention.
    """
    folder = Path(folder)
    if not folder.is_dir():
        raise MigrationError(f"{folder} is not a folder.")

    edl_candidates = sorted(folder.glob("*_EDL.txt"))
    if not edl_candidates:
        raise MigrationError(f"No '*_EDL.txt' file found in {folder}.")
    if len(edl_candidates) > 1:
        logger.warning("Multiple EDL files in %s, using %s", folder, edl_candidates[0].name)

    edl = edl_candidates[0]
    name = edl.name[: -len("_EDL.txt")]

    markerlabel = folder / f"{name}_MARKERLABEL.txt"
    playlist = folder / f"{name}_PLAYLIST.txt"

    return V3ProjectFiles(
        name=name,
        folder=folder,
        edl=edl,
        markerlabel=markerlabel if markerlabel.is_file() else None,
        playlist=playlist if playlist.is_file() else None,
    )


def parse_edl_lines(lines: list[str], base_date: date) -> list[Marker]:
    """Turn v3 EDL text lines into markers, reconstructing dates.

    Lines that match neither a marker nor a separator are skipped (v3 files were
    hand-editable, so stray content is possible).
    """
    parsed: list[tuple[str | None, str]] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if SEPARATOR_PATTERN.match(line):
            parsed.append((None, ""))
            continue
        match = MARKER_LINE_PATTERN.match(line)
        if match:
            parsed.append((match.group("time"), match.group("label")))
        else:
            logger.warning("Skipping unrecognised EDL line: %r", raw_line)

    markers: list[Marker] = []
    current_date = base_date
    previous_time: datetime | None = None

    # Walk backwards so the newest marker keeps the known date and earlier
    # markers move back a day whenever the clock appears to run forwards.
    for time_string, label in reversed(parsed):
        if time_string is None:
            timestamp = previous_time or datetime.combine(current_date, datetime.min.time())
            markers.append(Marker(label="", type=MarkerType.SEPARATOR, created_at=timestamp))
            continue

        parsed_time = datetime.strptime(time_string, "%H:%M:%S").time()
        timestamp = datetime.combine(current_date, parsed_time)
        if previous_time is not None and timestamp > previous_time:
            current_date -= timedelta(days=1)
            timestamp = datetime.combine(current_date, parsed_time)
        previous_time = timestamp
        markers.append(Marker(label=label, type=MarkerType.LABEL, created_at=timestamp))

    markers.reverse()
    return markers


def _read_lines(path: Path | None) -> list[str]:
    if path is None or not path.is_file():
        return []
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as error:
        logger.error("Could not read %s: %s", path, error)
        return []


def import_v3_project(
    folder: Path | str,
    target_path: Path | str,
    color_set: str = "",
    production_date: date | None = None,
) -> Project:
    """Convert a v3 project folder into a new v4 project file.

    Returns the saved project. ``production_date`` defaults to the date derived
    from the EDL file's modification time.
    """
    files = find_v3_project(folder)

    try:
        edl_mtime = datetime.fromtimestamp(files.edl.stat().st_mtime)
    except OSError:
        edl_mtime = datetime.now()
    base_date = production_date or edl_mtime.date()

    markers = parse_edl_lines(_read_lines(files.edl), base_date)

    marker_labels = default_marker_labels()
    for index, text in enumerate(_read_lines(files.markerlabel)[:9], start=1):
        marker_labels[index - 1] = MarkerLabel(index=index, label=text.strip())

    playlist = [PlaylistEntry(label=line.strip()) for line in _read_lines(files.playlist) if line.strip()]

    project = Project(
        name=files.name,
        path=Path(target_path),
        production_date=base_date,
        notes=f"Importiert aus v3-Projekt: {files.folder}",
        color_set=color_set,
        created_at=edl_mtime,
        marker_labels=marker_labels,
        playlist=playlist,
        markers=markers,
    )
    project.save()
    logger.info(
        "Imported v3 project '%s' (%s markers, %s playlist entries) to %s",
        files.name,
        len(markers),
        len(playlist),
        target_path,
    )
    return project
