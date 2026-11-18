"""Part tools: build_part, list_parts, render_parts_catalog (STYLE.md §9a)."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from pathlib import Path

from ..blender import run_job
from ..paths import REPO, workspace
from ..style import load_style, style_name

VARIANT_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class PartError(ValueError):
    pass


def parts_dir(style: str | None = None) -> Path:
    return REPO / load_style(style)["parts"]["dir"]


def split(part: str) -> tuple[str, str]:
    for s in sorted(load_style()["slots"], key=len, reverse=True):
        if part.startswith(s + "-") and VARIANT_RE.match(part[len(s) + 1:] or ""):
            return s, part[len(s) + 1:]
    raise PartError(f"part name {part!r} must be '<slot>-<variant>' (variant kebab-case), "
                    f"slot one of {load_style()['slots']}")


def build_part(part: str, script: str, archetype: str | None = None, overwrite: bool = False,
               style: str | None = None) -> dict:
    slot, _ = split(part)
    style = load_style(style)
    archetype = archetype or style["default_archetype"]
    lib_dir = parts_dir(style["style"]) / slot
    blend = lib_dir / f"{part}.blend"
    if blend.exists() and not overwrite:
        raise PartError(f"part {part!r} exists (pass overwrite=true to replace it)")
    if archetype not in style["archetypes"] or "template" not in style["archetypes"][archetype]:
        raise PartError(f"style {style['style']!r} has no template for archetype {archetype!r}")
    scratch = workspace() / "_parts" / style["style"] / part
    r = run_job("build_part", {"part": part, "script": script, "archetype": archetype,
                               "out_dir": str(scratch), "save": True}, style=style["style"])
    if not r.get("ok"):
        return r
    lib_dir.mkdir(parents=True, exist_ok=True)
    (scratch / f"{part}.blend").replace(blend)
    preview = lib_dir / f"{part}.png"
    Path(r["previews"][0]).replace(preview)
    script = script.rstrip() + "\n"  # stored as-is; script_sha256 is the hash of this file
    (lib_dir / f"{part}.py").write_text(script)
    meta = {
        "part": part, "slot": slot, "style": style["style"], "archetypes": [archetype],
        "script_sha256": hashlib.sha256(script.encode()).hexdigest(),
        "built": dt.date.today().isoformat(), "blender": style["blender"]["version"],
        **{k: r["stats"][k] for k in ("tris", "verts", "roles", "shells", "bbox")},
        **({"covers": r["stats"]["covers"]} if r["stats"].get("covers") else {}),
        **({"skirt": r["stats"]["skirt"]} if r["stats"].get("skirt") else {}),
        "warnings": r.get("soft", []),
    }
    (lib_dir / f"{part}.json").write_text(json.dumps(meta, indent=1) + "\n")
    r["outputs"] = [str(blend), str(lib_dir / f"{part}.py"), str(lib_dir / f"{part}.json"), str(preview)]
    r["previews"] = [str(preview)]
    return r


def props_dir(style: str | None = None) -> Path:
    st = load_style(style)
    return REPO / "styles" / st["style"] / st["props"]["dir"]


def build_prop(prop: str, script: str, type: str, overwrite: bool = False, style: str | None = None) -> dict:  # noqa: A002
    """STYLE.md §9b: build a prop with the part builder; stored in styles/<style>/props/ if it passes."""
    if not VARIANT_RE.match(prop or ""):
        raise PartError(f"prop name {prop!r} must be kebab-case, e.g. 'pistol-kestrel'")
    style = load_style(style)
    types = style["props"]["types"]
    if type not in types:
        raise PartError(f"unknown prop type {type!r}; types: {sorted(types)}")
    if types[type]["budget"] not in style["budget"]:
        raise PartError(f"style {style['style']!r} has no {types[type]['budget']!r} budget (its STYLE.md §3)")
    lib_dir = props_dir(style["style"])
    blend = lib_dir / f"{prop}.blend"
    if blend.exists() and not overwrite:
        raise PartError(f"prop {prop!r} exists (pass overwrite=true to replace it)")
    scratch = workspace() / "_props" / style["style"] / prop
    r = run_job("build_prop", {"prop": prop, "type": type, "script": script, "out_dir": str(scratch), "save": True},
                style=style["style"])
    if not r.get("ok"):
        return r
    lib_dir.mkdir(parents=True, exist_ok=True)
    (scratch / f"{prop}.blend").replace(blend)
    preview = lib_dir / f"{prop}.png"
    Path(r["previews"][0]).replace(preview)
    script = script.rstrip() + "\n"
    (lib_dir / f"{prop}.py").write_text(script)
    meta = {
        "prop": prop, "type": type, "style": style["style"],
        "script_sha256": hashlib.sha256(script.encode()).hexdigest(),
        "built": dt.date.today().isoformat(), "blender": style["blender"]["version"],
        **{k: r["stats"][k] for k in ("tris", "verts", "roles", "shells", "bbox", "anchors")},
        "warnings": r.get("soft", []),
    }
    (lib_dir / f"{prop}.json").write_text(json.dumps(meta, indent=1) + "\n")
    r["outputs"] = [str(blend), str(lib_dir / f"{prop}.py"), str(lib_dir / f"{prop}.json"), str(preview)]
    r["previews"] = [str(preview)]
    return r


def list_props(style: str | None = None) -> dict:
    out = []
    for meta in sorted(props_dir(style).glob("*.json")):
        m = json.loads(meta.read_text())
        out.append({k: m.get(k) for k in ("prop", "type", "tris", "roles", "anchors")})
    return {"ok": True, "style": style_name(style), "props": out}


def list_parts(slot: str | None = None, style: str | None = None) -> dict:
    out = {}
    for meta in sorted(parts_dir(style).glob("*/*.json")):
        m = json.loads(meta.read_text())
        if slot and m["slot"] != slot:
            continue
        out.setdefault(m["slot"], []).append({k: m[k] for k in ("part", "archetypes", "tris", "roles")})
    return {"ok": True, "style": style_name(style), "parts": out}


def render_parts_catalog(slot: str | None = None, parts: list[str] | None = None,
                         style: str | None = None) -> dict:
    style = style_name(style)
    if parts is None:
        listing = list_parts(slot, style)["parts"]
        parts = [p["part"] for s in load_style()["slots"] for p in listing.get(s, [])]
    for p in parts:
        split(p)
    if not parts:
        raise PartError(f"no parts{' in slot ' + slot if slot else ''} yet")
    out_dir = workspace() / "_catalog" / style / (slot or "all")
    r = run_job("parts_catalog", {"parts": parts, "out_dir": str(out_dir)}, timeout=600, style=style)
    return r
