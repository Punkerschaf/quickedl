"""
Storage locations for user data (settings, project registry, custom color sets).

During v4 development these are deliberately kept separate from the v3 location
(``~/quickedl/settings.yaml``) so that a v3 installation still in productive use
cannot be damaged by the rewrite. See roadmap.md before release: the v4 folder is
meant to be promoted to ``~/quickedl/`` once v3 is retired.
"""

from pathlib import Path

USER_DATA_DIR = Path.home() / "quickedl" / "v4"
SETTINGS_FILE = USER_DATA_DIR / "settings.yaml"
REGISTRY_FILE = USER_DATA_DIR / "projects.json"
USER_COLORSETS_DIR = USER_DATA_DIR / "colorsets"
LOG_FILE = Path.home() / "quickedl_v4.log"

BUNDLED_COLORSETS_DIR = Path(__file__).resolve().parent.parent / "colorsets"

PROJECT_FILE_SUFFIX = ".qedl"


def ensure_user_dirs() -> None:
    """Create the user data directories if they do not exist yet."""
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    USER_COLORSETS_DIR.mkdir(parents=True, exist_ok=True)
