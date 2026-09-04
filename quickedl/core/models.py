"""
Core data types of a QuickEDL project: markers, marker labels and playlist entries.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

DEFAULT_MARKER_LABEL_COUNT = 9


class MarkerType(str, Enum):
    """How a marker was created.

    The type is kept explicitly (rather than inferred at export time) so that
    exporters can decide per type what to do -- separators for instance are
    QuickEDL-internal dividers and are never sent to an NLE.
    """

    LABEL = "label"
    POPUP = "popup"
    PLAYLIST = "playlist"
    SEPARATOR = "separator"


def _new_id() -> str:
    return uuid.uuid4().hex


@dataclass
class Marker:
    """A single logged event.

    ``color`` holds the id of a color inside the project's color set. For label
    markers it is copied from the marker label at creation time and stays fixed
    afterwards -- changing a label's color later does not rewrite past markers.
    """

    label: str = ""
    type: MarkerType = MarkerType.LABEL
    color: str | None = None
    source_label_index: int | None = None
    created_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=_new_id)

    @property
    def time_string(self) -> str:
        """Wall clock time of the marker as ``HH:MM:SS`` (v3-compatible)."""
        return self.created_at.strftime("%H:%M:%S")

    @property
    def is_separator(self) -> bool:
        return self.type is MarkerType.SEPARATOR

    def to_dict(self) -> dict:
        data = {
            "id": self.id,
            "created_at": self.created_at.isoformat(timespec="seconds"),
            "type": self.type.value,
            "label": self.label,
        }
        if self.color is not None:
            data["color"] = self.color
        if self.source_label_index is not None:
            data["source_label_index"] = self.source_label_index
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Marker":
        try:
            marker_type = MarkerType(data.get("type", MarkerType.LABEL.value))
        except ValueError:
            marker_type = MarkerType.LABEL
        return cls(
            id=data.get("id", _new_id()),
            created_at=datetime.fromisoformat(data["created_at"]),
            type=marker_type,
            label=data.get("label", ""),
            color=data.get("color"),
            source_label_index=data.get("source_label_index"),
        )


@dataclass
class MarkerLabel:
    """One of the numbered marker buttons (hotkeys 1-9)."""

    index: int
    label: str = ""
    color: str | None = None

    def to_dict(self) -> dict:
        return {"index": self.index, "label": self.label, "color": self.color}

    @classmethod
    def from_dict(cls, data: dict) -> "MarkerLabel":
        return cls(
            index=int(data["index"]),
            label=data.get("label", ""),
            color=data.get("color"),
        )


@dataclass
class PlaylistEntry:
    """A one-shot cue label, consumed in order during a show."""

    label: str

    def to_dict(self) -> dict:
        return {"label": self.label}

    @classmethod
    def from_dict(cls, data: dict) -> "PlaylistEntry":
        return cls(label=data.get("label", ""))


def default_marker_labels(count: int = DEFAULT_MARKER_LABEL_COUNT) -> list[MarkerLabel]:
    return [MarkerLabel(index=i) for i in range(1, count + 1)]
