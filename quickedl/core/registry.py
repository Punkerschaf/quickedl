"""
Registry of known projects -- the backing store of the project manager.

Project files can live anywhere on disk, so the registry keeps a list of paths
rather than scanning a fixed folder. Entries whose file has disappeared are kept
and flagged as missing instead of being dropped silently, so a moved project is
visible in the manager rather than just gone.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from . import paths

logger = logging.getLogger(__name__)


@dataclass
class RegistryEntry:
    path: Path
    name: str
    last_opened: datetime | None = None

    @property
    def exists(self) -> bool:
        return self.path.is_file()

    @property
    def modified_at(self) -> datetime | None:
        try:
            return datetime.fromtimestamp(self.path.stat().st_mtime)
        except OSError:
            return None

    def to_dict(self) -> dict:
        return {
            "path": str(self.path),
            "name": self.name,
            "last_opened": self.last_opened.isoformat(timespec="seconds") if self.last_opened else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RegistryEntry":
        last_opened = data.get("last_opened")
        return cls(
            path=Path(data["path"]),
            name=data.get("name", Path(data["path"]).stem),
            last_opened=datetime.fromisoformat(last_opened) if last_opened else None,
        )


class ProjectRegistry:
    """Persistent list of projects the user has created or opened."""

    def __init__(self, file_path: Path | None = None) -> None:
        self.file_path = Path(file_path) if file_path else paths.REGISTRY_FILE
        self.entries: list[RegistryEntry] = []
        self.load()

    def load(self) -> None:
        if not self.file_path.is_file():
            self.entries = []
            return
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            self.entries = [RegistryEntry.from_dict(item) for item in data.get("projects", [])]
        except (OSError, json.JSONDecodeError, KeyError) as error:
            logger.error("Could not read project registry %s: %s", self.file_path, error)
            self.entries = []

    def save(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"projects": [entry.to_dict() for entry in self.entries]}
        try:
            with self.file_path.open("w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2, ensure_ascii=False)
        except OSError as error:
            logger.error("Could not write project registry %s: %s", self.file_path, error)

    def find(self, path: Path | str) -> RegistryEntry | None:
        path = Path(path)
        for entry in self.entries:
            if entry.path == path:
                return entry
        return None

    def add(self, path: Path | str, name: str, touch: bool = True) -> RegistryEntry:
        """Add a project (or update its name) and move it to the top."""
        path = Path(path)
        entry = self.find(path)
        if entry is None:
            entry = RegistryEntry(path=path, name=name)
            self.entries.append(entry)
        entry.name = name
        if touch:
            entry.last_opened = datetime.now()
        self.entries.sort(key=lambda item: item.last_opened or datetime.min, reverse=True)
        self.save()
        return entry

    def remove(self, path: Path | str) -> bool:
        """Remove an entry from the list. Does not touch the file on disk."""
        path = Path(path)
        before = len(self.entries)
        self.entries = [entry for entry in self.entries if entry.path != path]
        if len(self.entries) != before:
            self.save()
            return True
        return False

    def rename(self, old_path: Path | str, new_path: Path | str, new_name: str) -> None:
        entry = self.find(old_path)
        if entry is None:
            self.add(new_path, new_name, touch=False)
            return
        entry.path = Path(new_path)
        entry.name = new_name
        self.save()
