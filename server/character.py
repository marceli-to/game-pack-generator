"""Character workspace: workspace/<name>/{character.blend, spec.json, renders/, export/}."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .paths import character_dir

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class CharacterError(ValueError):
    pass


def check_name(name: str) -> str:
    if not NAME_RE.match(name or ""):
        raise CharacterError(f"invalid character name {name!r}: use kebab-case, e.g. 'knight' or 'forest-mage'")
    return name


def blend_path(name: str) -> Path:
    return character_dir(check_name(name)) / "character.blend"


def require(name: str) -> Path:
    p = blend_path(name)
    if not p.exists():
        raise CharacterError(f"character {name!r} does not exist; call init_character first")
    return p


def spec_path(name: str) -> Path:
    return character_dir(check_name(name)) / "spec.json"


def load_spec(name: str) -> dict | None:
    p = spec_path(name)
    return json.loads(p.read_text()) if p.exists() else None


def save_spec(name: str, spec: dict) -> Path:
    p = spec_path(name)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n")
    return p


def style_of(name: str) -> str:
    """The character's style (spec.style; specs without one use core.json default_style)."""
    from .style import style_name
    return style_name((load_spec(name) or {}).get("style"))


def spec_hash(spec: dict) -> str:
    """STYLE.md §14: SHA-256 of the spec JSON without the approval block, keys sorted."""
    body = {k: v for k, v in spec.items() if k != "approval"}
    return "sha256:" + hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def is_prop(spec: dict | None) -> bool:
    """STYLE.md §9b: specs with kind "prop" are props (weapons, thrown items, pickups), else characters."""
    return (spec or {}).get("kind") == "prop"


def require_character(name: str) -> dict:
    """The spec of `name`; raises for props (tools that need a rig: animation, pose test, fitting)."""
    spec = load_spec(name) or {}
    if is_prop(spec):
        raise CharacterError(f"{name!r} is a prop (STYLE.md §9b): no rig, no animation")
    return spec
