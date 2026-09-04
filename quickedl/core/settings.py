"""
Application settings (YAML), stored outside the repository in the user data dir.

Unlike the project file, these are machine/user preferences: they must never
carry show data.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

from . import paths

logger = logging.getLogger(__name__)

DEFAULTS: dict[str, Any] = {
    # Backspace deletes the last marker. Off by default (v3 behaviour) because
    # an accidental keypress during a live show is expensive.
    "delete_key_enabled": False,
    "default_project_dir": str(Path.home()),
    "log_level": "INFO",
    "last_project": None,
    "reopen_last_project": True,
}


class Settings:
    """Thin YAML-backed settings store with defaults."""

    def __init__(self, file_path: Path | None = None) -> None:
        self.file_path = Path(file_path) if file_path else paths.SETTINGS_FILE
        self.values: dict[str, Any] = dict(DEFAULTS)
        self.load()

    def load(self) -> None:
        if not self.file_path.is_file():
            return
        try:
            with self.file_path.open("r", encoding="utf-8") as handle:
                stored = yaml.safe_load(handle) or {}
            if isinstance(stored, dict):
                self.values.update(stored)
            else:
                logger.error("Settings file %s does not contain a mapping.", self.file_path)
        except (OSError, yaml.YAMLError) as error:
            logger.error("Could not read settings %s: %s", self.file_path, error)

    def save(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.file_path.open("w", encoding="utf-8") as handle:
                yaml.safe_dump(self.values, handle, allow_unicode=True, sort_keys=True)
        except OSError as error:
            logger.error("Could not write settings %s: %s", self.file_path, error)

    def get(self, key: str, fallback: Any = None) -> Any:
        return self.values.get(key, DEFAULTS.get(key, fallback))

    def set(self, key: str, value: Any, save: bool = True) -> None:
        self.values[key] = value
        if save:
            self.save()
