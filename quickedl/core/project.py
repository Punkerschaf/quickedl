"""
The v4 project model: one project == one JSON file (``*.qedl``).

This replaces the v3 layout (a folder holding ``*_EDL.txt``, ``*_MARKERLABEL.txt``
and ``*_PLAYLIST.txt``). Marker list, playlist, marker labels and project metadata
now live together in a single document.

Reliability: every mutation is written to disk immediately, and writes go through
a temp file plus ``os.replace()``. The original file is never modified in place,
so a crash mid-write can never leave a half-written project behind -- the
equivalent of the append-only guarantee the v3 text file provided.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

from . import paths
from .models import (
    DEFAULT_MARKER_LABEL_COUNT,
    Marker,
    MarkerLabel,
    MarkerType,
    PlaylistEntry,
    default_marker_labels,
)

logger = logging.getLogger(__name__)

FORMAT_VERSION = 1

#: Written for markers created from an empty marker label (v3 behaviour).
EMPTY_LABEL_FALLBACK = "Button {index}"


class ProjectError(Exception):
    """Raised when a project file cannot be read or written."""


@dataclass
class Project:
    """A QuickEDL project and everything belonging to it."""

    name: str
    path: Path | None = None
    production_date: date | None = None
    notes: str = ""
    color_set: str = ""
    default_popup_marker_color: str | None = None
    default_playlist_marker_color: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    marker_labels: list[MarkerLabel] = field(default_factory=default_marker_labels)
    playlist: list[PlaylistEntry] = field(default_factory=list)
    markers: list[Marker] = field(default_factory=list)

    # ------------------------------------------------------------------ create

    @classmethod
    def create(
        cls,
        name: str,
        path: Path,
        color_set: str,
        production_date: date | None = None,
        notes: str = "",
    ) -> "Project":
        """Create a new project and write it to ``path`` immediately."""
        project = cls(
            name=name,
            path=Path(path),
            color_set=color_set,
            production_date=production_date,
            notes=notes,
        )
        project.save()
        return project

    # ------------------------------------------------------------- (de)serialize

    def to_dict(self) -> dict:
        return {
            "format_version": FORMAT_VERSION,
            "project": {
                "name": self.name,
                "production_date": self.production_date.isoformat() if self.production_date else None,
                "notes": self.notes,
                "color_set": self.color_set,
                "default_popup_marker_color": self.default_popup_marker_color,
                "default_playlist_marker_color": self.default_playlist_marker_color,
                "created_at": self.created_at.isoformat(timespec="seconds"),
                "modified_at": self.modified_at.isoformat(timespec="seconds"),
            },
            "marker_labels": [label.to_dict() for label in self.marker_labels],
            "playlist": [entry.to_dict() for entry in self.playlist],
            "markers": [marker.to_dict() for marker in self.markers],
        }

    @classmethod
    def from_dict(cls, data: dict, path: Path | None = None) -> "Project":
        version = data.get("format_version", FORMAT_VERSION)
        if version > FORMAT_VERSION:
            logger.warning(
                "Project file uses format version %s, this build understands %s. "
                "Loading anyway; unknown fields are ignored.",
                version,
                FORMAT_VERSION,
            )

        info = data.get("project", {})
        production_date = info.get("production_date")
        marker_labels = [MarkerLabel.from_dict(item) for item in data.get("marker_labels", [])]
        if not marker_labels:
            marker_labels = default_marker_labels()

        return cls(
            name=info.get("name", path.stem if path else "Unnamed"),
            path=Path(path) if path else None,
            production_date=date.fromisoformat(production_date) if production_date else None,
            notes=info.get("notes", ""),
            color_set=info.get("color_set", ""),
            default_popup_marker_color=info.get("default_popup_marker_color"),
            default_playlist_marker_color=info.get("default_playlist_marker_color"),
            created_at=_parse_datetime(info.get("created_at")),
            modified_at=_parse_datetime(info.get("modified_at")),
            marker_labels=marker_labels,
            playlist=[PlaylistEntry.from_dict(item) for item in data.get("playlist", [])],
            markers=[Marker.from_dict(item) for item in data.get("markers", [])],
        )

    # -------------------------------------------------------------------- io

    @classmethod
    def load(cls, path: Path | str) -> "Project":
        path = Path(path)
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except OSError as error:
            raise ProjectError(f"Could not read project file {path}: {error}") from error
        except json.JSONDecodeError as error:
            raise ProjectError(f"{path} is not a valid QuickEDL project file: {error}") from error
        return cls.from_dict(data, path=path)

    def save(self, path: Path | str | None = None) -> Path:
        """Write the project atomically. Returns the path written to."""
        target = Path(path) if path else self.path
        if target is None:
            raise ProjectError("Cannot save a project without a path.")

        target.parent.mkdir(parents=True, exist_ok=True)
        self.modified_at = datetime.now()
        temp_path = target.with_name(target.name + ".tmp")

        try:
            with temp_path.open("w", encoding="utf-8") as handle:
                json.dump(self.to_dict(), handle, indent=2, ensure_ascii=False)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, target)
        except OSError as error:
            temp_path.unlink(missing_ok=True)
            raise ProjectError(f"Could not save project to {target}: {error}") from error

        self.path = target
        return target

    # --------------------------------------------------------------- markers

    def add_marker(
        self,
        label: str,
        marker_type: MarkerType = MarkerType.LABEL,
        color: str | None = None,
        source_label_index: int | None = None,
        created_at: datetime | None = None,
        save: bool = True,
    ) -> Marker:
        """Append a marker and (by default) persist immediately.

        ``created_at`` allows passing the moment the user triggered the marker
        rather than the moment the marker is stored -- needed for the popup
        marker, where the text is typed after the fact.
        """
        marker = Marker(
            label=label,
            type=marker_type,
            color=color,
            source_label_index=source_label_index,
            created_at=created_at or datetime.now(),
        )
        self.markers.append(marker)
        if save:
            self.save()
        return marker

    def add_label_marker(self, index: int, save: bool = True) -> Marker:
        """Create a marker from the numbered marker label ``index`` (1-based).

        The label's color is copied into the marker so that later changes to the
        label do not alter markers that were already logged.
        """
        marker_label = self.marker_label(index)
        if marker_label is None:
            raise ProjectError(f"No marker label with index {index}")
        text = marker_label.label or EMPTY_LABEL_FALLBACK.format(index=index)
        return self.add_marker(
            label=text,
            marker_type=MarkerType.LABEL,
            color=marker_label.color,
            source_label_index=index,
            save=save,
        )

    def add_popup_marker(self, text: str, created_at: datetime | None = None, save: bool = True) -> Marker:
        return self.add_marker(
            label=text,
            marker_type=MarkerType.POPUP,
            color=self.default_popup_marker_color,
            created_at=created_at,
            save=save,
        )

    def add_playlist_marker(self, text: str, save: bool = True) -> Marker:
        return self.add_marker(
            label=text,
            marker_type=MarkerType.PLAYLIST,
            color=self.default_playlist_marker_color,
            save=save,
        )

    def add_separator(self, save: bool = True) -> Marker:
        return self.add_marker(label="", marker_type=MarkerType.SEPARATOR, save=save)

    def delete_last_marker(self, save: bool = True) -> Marker | None:
        """Remove and return the most recent marker, if any."""
        if not self.markers:
            return None
        marker = self.markers.pop()
        if save:
            self.save()
        return marker

    # ---------------------------------------------------------------- labels

    def marker_label(self, index: int) -> MarkerLabel | None:
        for marker_label in self.marker_labels:
            if marker_label.index == index:
                return marker_label
        return None

    def set_marker_label(
        self,
        index: int,
        label: str | None = None,
        color: str | None = None,
        update_color: bool = False,
        save: bool = True,
    ) -> None:
        """Update text and/or color of a marker label.

        ``color`` is only applied when ``update_color`` is True, so that passing
        ``None`` can explicitly mean "no color" rather than "leave unchanged".
        """
        marker_label = self.marker_label(index)
        if marker_label is None:
            raise ProjectError(f"No marker label with index {index}")
        if label is not None:
            marker_label.label = label
        if update_color:
            marker_label.color = color
        if save:
            self.save()

    def ensure_marker_label_count(self, count: int = DEFAULT_MARKER_LABEL_COUNT) -> None:
        existing = {marker_label.index for marker_label in self.marker_labels}
        for index in range(1, count + 1):
            if index not in existing:
                self.marker_labels.append(MarkerLabel(index=index))
        self.marker_labels.sort(key=lambda item: item.index)

    # -------------------------------------------------------------- playlist

    def set_playlist(self, labels: list[str], save: bool = True) -> None:
        self.playlist = [PlaylistEntry(label=text) for text in labels]
        if save:
            self.save()

    @property
    def playlist_labels(self) -> list[str]:
        return [entry.label for entry in self.playlist]


def _parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.now()
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        logger.warning("Unparseable timestamp %r, falling back to now.", value)
        return datetime.now()


def suggest_project_path(directory: Path | str, name: str) -> Path:
    """Build a project file path from a directory and a project name."""
    safe_name = "".join(char for char in name if char not in '/\\:*?"<>|').strip()
    safe_name = safe_name or "project"
    return Path(directory) / f"{safe_name}{paths.PROJECT_FILE_SUFFIX}"
