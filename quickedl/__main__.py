"""
Entry point: ``python -m quickedl``.

The v3 entry point (``python main.py``) is untouched and keeps working until the
rewrite reaches feature parity.
"""

from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication

from . import VERSION
from .core import paths
from .core.settings import Settings
from .gui.main_window import MainWindow
from .gui.style import STYLESHEET


def setup_logging(level: str = "INFO") -> None:
    paths.ensure_user_dirs()
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(paths.LOG_FILE, mode="w", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    logging.info("QuickEDL %s starting, log file: %s", VERSION, paths.LOG_FILE)


def main() -> int:
    paths.ensure_user_dirs()
    setup_logging(str(Settings().get("log_level", "INFO")).upper())

    app = QApplication(sys.argv)
    app.setApplicationName("QuickEDL")
    app.setApplicationVersion(VERSION)
    app.setStyleSheet(STYLESHEET)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
