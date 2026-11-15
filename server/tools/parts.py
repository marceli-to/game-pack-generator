"""Part tools: build_part, list_parts, render_parts_catalog (STYLE.md §9a)."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from pathlib import Path

from ..blender import run_job
from ..paths import REPO, workspace
from ..style import load_style

VARIANT_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class PartError(ValueError):
    pass


def parts_dir() -> Path:
    return REPO / load_style()["parts"]["dir"]


def split(part: str) -> tuple[str, str]:
    for s in sorted(load_style()["slots"], key=len, reverse=True):
        if part.startswith(s + "-") and VARIANT_RE.match(part[len(s) + 1:] or ""):
            return s, part[len(s) + 1:]
    raise PartError(f"part name {part!r} must be '<slot>-<variant>' (variant kebab-case), "
                    f"slot one of {load_style()['slots']}")


def build_part(part: str, script: str, archetype: str | None = None, overwrite: bool = False) -> dict:
    slot, _ = split(part)
    style = load_style()
    archetype = archetype or style["default_archetype"]
    lib_dir = parts_dir() / slot
    blend = lib_dir / f"{part}.blend"
    if blend.exists() and not overwrite:
        raise PartError(f"part {part!r} exists (pass overwrite=true to replace it)")
    scratch = workspace() / "_parts" / part
    r = run_job("build_part", {"part": part, "script": script, "archetype": archetype,
                               "out_dir": str(scratch), "save": True})
    if not r.get("ok"):
        return r
    lib_dir.mkdir(parents=True, exist_ok=True)
    (scratch / f"{part}.blend").replace(blend)
    preview = lib_dir / f"{part}.png"
    Path(r["previews"][0]).replace(preview)
    script = script.rstrip() + "\n"  # stored as-is; script_sha256 is the hash of this file
    (lib_dir / f"{part}.py").write_text(script)
    meta = {
        "part": part, "slot": slot, "archetypes": [archetype],
        "script_sha256": hashlib.sha256(script.encode()).hexdigest(),
        "built": dt.date.today().isoformat(), "blender": style["blender"]["version"],
        **{k: r["stats"][k] for k in ("tris", "verts", "roles", "shells", "bbox")},
        "warnings": r.get("soft", []),
    }
    (lib_dir / f"{part}.json").write_text(json.dumps(meta, indent=1) + "\n")
    r["outputs"] = [str(blend), str(lib_dir / f"{part}.py"), str(lib_dir / f"{part}.json"), str(preview)]
    r["previews"] = [str(preview)]
    return r


def list_parts(slot: str | None = None) -> dict:
    out = {}
    for meta in sorted(parts_dir().glob("*/*.json")):
        m = json.loads(meta.read_text())
        if slot and m["slot"] != slot:
            continue
        out.setdefault(m["slot"], []).append({k: m[k] for k in ("part", "archetypes", "tris", "roles")})
    return {"ok": True, "parts": out}


def render_parts_catalog(slot: str | None = None, parts: list[str] | None = None) -> dict:
    if parts is None:
        listing = list_parts(slot)["parts"]
        parts = [p["part"] for s in load_style()["slots"] for p in listing.get(s, [])]
    for p in parts:
        split(p)
    if not parts:
        raise PartError(f"no parts{' in slot ' + slot if slot else ''} yet")
    out_dir = workspace() / "_catalog" / (slot or "all")
    r = run_job("parts_catalog", {"parts": parts, "out_dir": str(out_dir)}, timeout=600)
    return r
