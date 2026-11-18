"""Build one part from an agent-written script against a proportion template (STYLE.md §9a).

args: { part: "<slot>-<variant>", script: "<python>", archetype?: "human",
        out_dir: <dir for .blend/.py/.json/.png>, save: bool }
The script runs with P (PartBuilder), lm, bones, guides, tpl, Vector, Matrix, math, bmesh, bpy.
Hard problems -> ok=false and nothing is saved to the library (the preview is still rendered).
"""
import json
from pathlib import Path

import bpy
from mathutils import Vector

from lib import palette as PAL
from lib import parts as PT
from lib import render as RD
from lib import scene as SC
from lib import shading as SH
from lib import style as S


def stick_figure(tpl):
    """Template bones as thin grey bars, for context in the part preview."""
    B = PT.PartBuilder()
    for n, b in tpl["bones"].items():
        if n == "root" or "slot" in n:
            continue
        a, t = Vector(b["head"]), Vector(b["tail"])
        if (t - a).length < 1e-4:
            continue
        B.cylinder(a, t, 0.008, n=4, role="dark")
    obj, _ = B.to_object("guide")
    obj.name = "_guide"
    PAL.apply_roles(obj, {"dark": 7})
    return obj


def run(args):
    style = S.load()
    part = args["part"]
    slot, _ = PT.split_part_name(part)
    arch = args.get("archetype", style["default_archetype"])
    tpl_rel = style["archetypes"][arch].get("template")
    if not tpl_rel:
        raise RuntimeError(f"archetype {arch!r} has no proportion template yet")
    tpl = json.loads(S.repo_path(tpl_rel).read_text())

    SC.empty_scene()
    B = PT.PartBuilder()
    ns = PT.script_namespace(B, tpl)
    exec(compile(args["script"], f"<part {part}>", "exec"), ns)  # noqa: S102 - agent-written part script
    obj, unset = B.to_object(slot)
    hard, soft, st = PT.check_part(obj, slot, tpl, unset)
    bad = [c for c in B.covers if c not in style["part_covers"]]
    if bad:
        hard.append(f"P.covers: unknown {bad} (known: {sorted(style['part_covers'])})")
    st["covers"] = sorted(set(B.covers))
    known = set(style["skinning"]["skirt"]) | {"centre_width_front"}
    if B.skirt and (slot != "torso" or set(B.skirt) - known):
        hard.append(f"P.skirt: torso parts only, keys {sorted(known)} (got {B.skirt} on {slot})")
    st["skirt"] = dict(B.skirt)

    out_dir = Path(args["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    # preview: part in its preview colours + the template stick figure, full-body framing
    colors = style["parts"]["preview_colors"]
    PAL.apply_roles(obj, colors)
    SH.apply(obj.data)
    guide = stick_figure(tpl)
    lo = Vector(st["bbox"][0])
    hi = Vector(st["bbox"][1])
    top = max(hi.z, tpl["landmarks"]["head_top"][2]) + 0.05
    bottom = min(lo.z, 0.0) - 0.05
    span = max(top - bottom, hi.x - lo.x + 0.1, hi.y - lo.y + 0.1)
    frame = {"center": [0, 0, (top + bottom) / 2], "extent": span * 1.05}
    _, sheet = RD.render_views(out_dir, ["front", "side", "three_quarter"], size=384, prefix=part, frame=frame)
    bpy.data.objects.remove(guide, do_unlink=True)

    ok = not hard
    outputs = [sheet]
    if ok and args.get("save", True):
        # parts carry roles only (STYLE.md §4): drop the preview UVs/material before saving
        mesh = obj.data
        for uv in list(mesh.uv_layers):
            mesh.uv_layers.remove(uv)
        mesh.materials.clear()
        mesh.shade_flat()  # shading is applied at assembly, on the joined mesh
        if "sharp_edge" in mesh.attributes:
            mesh.attributes.remove(mesh.attributes["sharp_edge"])
        for o in list(bpy.context.scene.objects):
            if o is not obj:
                bpy.data.objects.remove(o, do_unlink=True)
        blend = out_dir / f"{part}.blend"
        SC.save(blend)
        outputs.insert(0, str(blend))
    return {"ok": ok, "valid": ok, "hard": hard, "soft": soft, "stats": {"slot": slot, "archetype": arch, **st},
            "outputs": outputs, "previews": [sheet],
            **({"error": "; ".join(hard)} if hard else {})}
