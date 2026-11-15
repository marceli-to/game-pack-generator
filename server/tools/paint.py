"""Painted surface tool: paint_surface (styles/<style>/STYLE.md §4, surface `painted`)."""
from __future__ import annotations

import json

from .. import character as C
from ..blender import run_job
from ..paths import character_dir
from ..style import load_style


def paint_surface(name: str, approach: str | None = None, seed: int | None = None) -> dict:
    """Bake the character's painted texture into character.blend. approach/seed default to spec.paint,
    then to the style (paint.default_approach, seed 1). Passing them stores them in spec.paint, so the
    approval (spec hash) covers them."""
    blend = C.require(name)
    st = C.style_of(name)
    style = load_style(st)
    if style.get("surface") != "painted":
        raise C.CharacterError(f"style {st!r} uses surface {style.get('surface')!r}; paint_surface is for "
                               "'painted' styles (palette styles: apply_palette / recolor)")
    cfg = style["paint"]
    spec = C.load_spec(name) or {}
    saved = dict(spec.get("paint") or {})
    if approach is not None or seed is not None:
        if approach is not None:
            saved["approach"] = approach
        if seed is not None:
            saved["seed"] = int(seed)
        spec["paint"] = saved
        C.save_spec(name, spec)
    approach = saved.get("approach", cfg["default_approach"])
    if approach not in cfg["approaches"]:
        raise C.CharacterError(f"approach must be one of {cfg['approaches']}, got {approach!r}")
    args = {"approach": approach, "colors": spec.get("colors") or {}, "seed": saved.get("seed", 1),
            "out_dir": str(character_dir(name) / "paint"), "out_blend": str(blend)}
    if approach == "projection":
        ref_dir = character_dir(name) / "reference"
        if not (ref_dir / "reference.json").exists():
            raise C.CharacterError("projection needs a reference sheet; call add_reference first")
        ref = json.loads((ref_dir / "reference.json").read_text())
        args.update({"ref": ref, "ref_image": str(ref_dir / ref["source"])})
    r = run_job("paint_surface", args, blend=blend, timeout=900, style=st)
    if r.get("ok"):
        r["stats"]["spec_hash"] = C.spec_hash(spec)
    return r
