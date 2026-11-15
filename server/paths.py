"""Repository paths. Everything is resolved relative to the repo root."""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CORE_JSON = REPO / "core.json"
STYLES = REPO / "styles"
JOBS = REPO / "jobs"
LIBRARY = REPO / "library"
NODE = REPO / "node"
VIEWER = REPO / "viewer"

DEFAULT_BLENDER_MAC = "/Applications/Blender.app/Contents/MacOS/Blender"


def blender_bin() -> str:
    return os.environ.get("BLENDER_BIN", DEFAULT_BLENDER_MAC)


def workspace() -> Path:
    """workspace/ (override with GPG_WORKSPACE, e.g. in tests)."""
    return Path(os.environ.get("GPG_WORKSPACE", REPO / "workspace"))


def character_dir(name: str) -> Path:
    return workspace() / name
