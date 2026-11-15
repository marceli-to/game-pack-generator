"""Style access inside Blender: core.json merged with styles/<GPG_STYLE>/style.json
(the runner sets GPG_STYLE; default: core.json default_style). Same merge as server/style.py."""
import json
import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
_cache = None


def load():
    global _cache
    if _cache is None:
        core = json.loads((REPO / "core.json").read_text())
        name = os.environ.get("GPG_STYLE") or core["default_style"]
        style = json.loads((REPO / "styles" / name / "style.json").read_text())
        _cache = {**core, **{k: v for k, v in style.items() if k != "_comment"}, "style": name}
    return _cache


def repo_path(rel):
    return REPO / rel


def role_index(name):
    return load()["roles"].index(name)


def slot_index(name):
    return load()["slots"].index(name)


def palette_uv(index):
    """UV of the centre of palette cell `index` (row 0 = top row of the image)."""
    grid = load()["palette"]["grid"]
    row, col = divmod(index, grid)
    return ((col + 0.5) / grid, 1.0 - (row + 0.5) / grid)


def palette_cell_of_uv(u, v):
    """(index, inside) for a UV coordinate; inside=False if outside [0,1]."""
    grid = load()["palette"]["grid"]
    inside = 0.0 <= u <= 1.0 and 0.0 <= v <= 1.0
    col = min(grid - 1, max(0, int(u * grid)))
    row = min(grid - 1, max(0, int((1.0 - v) * grid)))
    return row * grid + col, inside
