"""
Color sets: the marker color palettes QuickEDL offers per project.

A color set mirrors the marker colors available in one target NLE. Built-in sets
ship with the application; users can drop additional sets into
``paths.USER_COLORSETS_DIR``. A project references exactly one color set, and
marker labels reference individual colors by their stable ``id``.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from . import paths

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Color:
    """One entry of a color set.

    ``id`` is the stable key stored in project files, ``label`` is what the user
    sees, ``display_color`` is how QuickEDL renders it, and ``export_string`` is
    the identifier the target NLE expects when the marker is exported.
    """

    id: str
    label: str
    display_color: str
    export_string: str

    @classmethod
    def from_dict(cls, data: dict) -> "Color":
        return cls(
            id=data["id"],
            label=data.get("label", data["id"]),
            display_color=data.get("display_color", "#888888"),
            export_string=data.get("export_string", ""),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "display_color": self.display_color,
            "export_string": self.export_string,
        }


@dataclass
class ColorSet:
    """A named palette of marker colors, loaded from a JSON file."""

    id: str
    name: str
    colors: list[Color]
    #: False while the export_string values have not been checked against the
    #: real NLE API (see roadmap.md / phase0-spike).
    export_strings_verified: bool = False
    source_path: Path | None = None

    @classmethod
    def from_dict(cls, data: dict, source_path: Path | None = None) -> "ColorSet":
        return cls(
            id=data["id"],
            name=data.get("name", data["id"]),
            colors=[Color.from_dict(c) for c in data.get("colors", [])],
            export_strings_verified=bool(data.get("export_strings_verified", False)),
            source_path=source_path,
        )

    @classmethod
    def load(cls, path: Path) -> "ColorSet":
        with path.open("r", encoding="utf-8") as handle:
            return cls.from_dict(json.load(handle), source_path=path)

    def get(self, color_id: str | None) -> Color | None:
        """Return the color with ``color_id``, or None if unset/unknown."""
        if color_id is None:
            return None
        for color in self.colors:
            if color.id == color_id:
                return color
        return None

    def display_color_of(self, color_id: str | None, fallback: str = "#888888") -> str:
        color = self.get(color_id)
        return color.display_color if color else fallback

    def export_string_of(self, color_id: str | None) -> str | None:
        color = self.get(color_id)
        return color.export_string if color else None


def load_colorsets() -> dict[str, ColorSet]:
    """Load all available color sets, keyed by id.

    Bundled sets are loaded first; user sets from ``paths.USER_COLORSETS_DIR``
    are loaded afterwards and override a bundled set with the same id.
    """
    colorsets: dict[str, ColorSet] = {}

    for directory in (paths.BUNDLED_COLORSETS_DIR, paths.USER_COLORSETS_DIR):
        if not directory.is_dir():
            continue
        for file_path in sorted(directory.glob("*.json")):
            try:
                colorset = ColorSet.load(file_path)
            except (OSError, json.JSONDecodeError, KeyError) as error:
                logger.error("Could not load color set %s: %s", file_path, error)
                continue
            colorsets[colorset.id] = colorset

    if not colorsets:
        logger.warning("No color sets found in %s", paths.BUNDLED_COLORSETS_DIR)
    return colorsets


def default_colorset_id(colorsets: dict[str, ColorSet]) -> str:
    """Pick a sensible default color set id for new projects."""
    for preferred in ("premiere_pro", "davinci_resolve"):
        if preferred in colorsets:
            return preferred
    return next(iter(colorsets), "")
