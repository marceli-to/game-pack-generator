"""Load the merged style: core.json (shared rules) + styles/<name>/style.json (the look).

The style is picked explicitly (`load_style("clean")`), else from the env var GPG_STYLE, else
core.json `default_style`. Blender jobs get the same name through GPG_STYLE (server/blender.py).
"""
from __future__ import annotations

import json
import os
from functools import lru_cache

from .paths import CORE_JSON, STYLES


class StyleError(ValueError):
    pass


@lru_cache(maxsize=1)
def load_core() -> dict:
    return json.loads(CORE_JSON.read_text())


def available_styles() -> list[str]:
    return sorted(p.parent.name for p in STYLES.glob("*/style.json"))


def style_name(name: str | None = None) -> str:
    name = name or os.environ.get("GPG_STYLE") or load_core()["default_style"]
    if not (STYLES / name / "style.json").exists():
        raise StyleError(f"unknown style {name!r}; available: {available_styles()}")
    return name


@lru_cache(maxsize=16)
def _merged(name: str) -> dict:
    core = load_core()
    style = json.loads((STYLES / name / "style.json").read_text())
    clash = (set(core) & set(style)) - {"_comment"}
    if clash:
        raise StyleError(f"styles/{name}/style.json redefines core keys {sorted(clash)}")
    return {**core, **{k: v for k, v in style.items() if k != "_comment"}, "style": name}


def load_style(name: str | None = None) -> dict:
    return _merged(style_name(name))


def reload_style(name: str | None = None) -> dict:
    load_core.cache_clear()
    _merged.cache_clear()
    return load_style(name)


def dump_style(style: dict) -> str:
    """JSON with 2-space indent, but lists of scalars and small flat objects on one line."""
    import json as _json

    def flat(v):
        return not isinstance(v, (dict, list)) or (
            isinstance(v, dict) and all(not isinstance(x, (dict, list)) for x in v.values()) and len(v) <= 6
        )

    def enc(v, ind):
        pad, pad2 = "  " * ind, "  " * (ind + 1)
        if isinstance(v, list) and all(not isinstance(x, (dict, list)) for x in v):
            items = [_json.dumps(x, ensure_ascii=False) for x in v]
            line = "[" + ", ".join(items) + "]"
            if len(line) <= 100:
                return line
            rows, row = [], []
            for it in items:
                if row and len(", ".join(row + [it])) > 96:
                    rows.append(", ".join(row))
                    row = []
                row.append(it)
            rows.append(", ".join(row))
            return "[\n" + ",\n".join(pad2 + r for r in rows) + "\n" + pad + "]"
        if isinstance(v, list):
            return "[\n" + ",\n".join(pad2 + enc(x, ind + 1) for x in v) + "\n" + pad + "]"
        if isinstance(v, dict):
            if flat(v) and ind > 0:
                line = "{ " + ", ".join(f"{_json.dumps(k)}: {_json.dumps(x, ensure_ascii=False)}" for k, x in v.items()) + " }"
                if len(line) <= 110:
                    return line
            return "{\n" + ",\n".join(f"{pad2}{_json.dumps(k)}: {enc(x, ind + 1)}" for k, x in v.items()) + "\n" + pad + "}"
        return _json.dumps(v, ensure_ascii=False)

    return enc(style, 0) + "\n"
