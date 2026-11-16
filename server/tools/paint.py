"""Painted surface tool: paint_surface (styles/<style>/STYLE.md §4, surface `painted`)."""
from __future__ import annotations

import json

from .. import ai as AI
from .. import character as C
from ..blender import run_job
from ..paths import STYLES, character_dir
from ..style import load_style


def paint_surface(name: str, approach: str | None = None, seed: int | None = None,
                  subject: str | None = None, keep_roles: list[str] | None = None) -> dict:
    """Bake the character's painted texture into character.blend. approach/seed default to spec.paint,
    then to the style (paint.default_approach, seed 1). approach 'ai' also needs `subject` (what the
    character is, for the prompt); keep_roles (projection/ai) keeps the procedural paint on those roles,
    e.g. a simple cartoon face the image model would redraw. Passing any of them stores it in spec.paint, so
    the approval (spec hash) covers it."""
    blend = C.require(name)
    st = C.style_of(name)
    style = load_style(st)
    if style.get("surface") != "painted":
        raise C.CharacterError(f"style {st!r} uses surface {style.get('surface')!r}; paint_surface is for "
                               "'painted' styles (palette styles: apply_palette / recolor)")
    cfg = style["paint"]
    spec = C.load_spec(name) or {}
    saved = dict(spec.get("paint") or {})
    if keep_roles is not None:
        bad = [r for r in keep_roles if r not in style["roles"]]
        if bad:
            raise C.CharacterError(f"keep_roles: unknown roles {bad}; roles are {style['roles']}")
    if approach is not None or seed is not None or subject is not None or keep_roles is not None:
        if approach is not None:
            saved["approach"] = approach
        if seed is not None:
            saved["seed"] = int(seed)
        if subject is not None:
            saved["subject"] = subject.strip()
        if keep_roles is not None:
            if keep_roles:
                saved["keep_roles"] = list(keep_roles)
            else:
                saved.pop("keep_roles", None)
        spec["paint"] = saved
        C.save_spec(name, spec)
    approach = saved.get("approach", cfg["default_approach"])
    if approach not in cfg["approaches"]:
        raise C.CharacterError(f"approach must be one of {cfg['approaches']}, got {approach!r}")
    args = {"approach": approach, "colors": spec.get("colors") or {}, "seed": saved.get("seed", 1),
            "out_dir": str(character_dir(name) / "paint"), "out_blend": str(blend)}
    if saved.get("keep_roles") and approach != "auto":
        args["keep_roles"] = saved["keep_roles"]
    if approach == "projection":
        ref_dir = character_dir(name) / "reference"
        if not (ref_dir / "reference.json").exists():
            raise C.CharacterError("projection needs a reference sheet; call add_reference first")
        ref = json.loads((ref_dir / "reference.json").read_text())
        args.update({"ref": ref, "ref_image": str(ref_dir / ref["source"])})
    if approach == "ai":
        r = _paint_ai(name, st, cfg, args, saved)
    else:
        r = run_job("paint_surface", args, blend=blend, timeout=900, style=st)
    if r.get("ok"):
        r["stats"]["spec_hash"] = C.spec_hash(spec)
    return r


def _paint_ai(name: str, st: str, cfg: dict, args: dict, saved: dict) -> dict:
    """auto paint (start image + fallback) -> guides -> generation (ai/.venv) -> projection."""
    if not saved.get("subject"):
        raise C.CharacterError("approach 'ai' needs a subject (what the character is, e.g. 'chibi skeleton "
                               "knight, purple iron helmet with gold trim'); pass subject=")
    if not AI.available():
        raise C.CharacterError(f"approach 'ai' needs the AI environment ({AI.ai_python()}); see README")
    ai = cfg["ai"]
    blend = args["out_blend"]
    paint_dir = character_dir(name) / "paint"
    steps = {}
    r = run_job("paint_surface", {**args, "approach": "auto", "keep_roles": None}, blend=blend, timeout=900, style=st)
    if not r.get("ok"):
        return {**r, "error": f"ai: auto paint failed: {r.get('error')}"}
    steps["auto_s"] = r.get("elapsed_s")
    g = run_job("ai_guides", {"out_dir": str(paint_dir / "ai" / "guides")}, blend=blend, timeout=600, style=st)
    if not g.get("ok"):
        return {**g, "error": f"ai: guides failed: {g.get('error')}"}
    steps["guides_s"] = g.get("elapsed_s")
    gen_args = {"guides_dir": str(paint_dir / "ai" / "guides"), "out_dir": str(paint_dir / "ai"),
                "prompt": f"{saved['subject']}, {ai['style_prompt']}", "negative": ai["negative"],
                "style_ref": str(STYLES / st / ai["style_ref"]), "seed": args["seed"], "steps": ai["steps"],
                "strength": ai["strength"], "controlnet": ai["controlnet"], "ip_adapter": ai["ip_adapter"],
                "guidance": ai["guidance"], "view_size": ai["view_size"], "background": ai["background"],
                "models": ai["models"]}
    gr = AI.run_gen(gen_args)
    if not gr.get("ok"):
        return {"ok": False, "outputs": [], "stats": {}, "previews": [], "warnings": [],
                "error": f"ai: generation failed: {gr.get('error')}", "log": gr.get("log") or gr.get("traceback")}
    steps["generation_s"] = gr.get("elapsed_s")
    ref = json.loads((paint_dir / "ai" / "reference.json").read_text())
    p = run_job("paint_surface", {**args, "approach": "ai", "ref": ref, "ref_image": str(paint_dir / "ai" / "sheet.png")},
                blend=blend, timeout=900, style=st)
    if not p.get("ok"):
        return {**p, "error": f"ai: projection failed: {p.get('error')}"}
    steps["projection_s"] = p.get("elapsed_s")
    sheet = str(paint_dir / "ai" / "sheet.png")
    p["outputs"] = p["outputs"] + gr["outputs"]
    p["previews"] = p["previews"] + [sheet]
    p["stats"]["ai"] = {"prompt": gen_args["prompt"], "frame": g["stats"].get("frame"), **gr.get("stats", {}),
                        "steps": steps}
    return p
