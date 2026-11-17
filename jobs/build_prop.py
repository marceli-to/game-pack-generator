"""Build one prop from an agent-written script (STYLE.md §9b): same builder `P` as parts, no template.

args: { prop: "<name>", type: "weapon" | "thrown" | "pickup", script: "<python>", out_dir, save: bool }
The script runs with P (PartBuilder), Vector, Matrix, math, bmesh, bpy (lm, bones, guides empty) and names its
anchors with P.anchor(name, point). Hard problems -> ok=false and nothing is saved (the preview is still rendered).
"""
import json
from pathlib import Path

import bpy

from lib import palette as PAL
from lib import parts as PT
from lib import render as RD
from lib import scene as SC
from lib import shading as SH
from lib import style as S

OBJECT = "prop"


def run(args):
    style = S.load()
    prop, ptype = args["prop"], args["type"]
    SC.empty_scene()
    B = PT.PartBuilder()
    ns = PT.script_namespace(B, {"landmarks": {}, "bones": {}, "guides": {}})
    exec(compile(args["script"], f"<prop {prop}>", "exec"), ns)  # noqa: S102 - agent-written prop script
    obj, unset = B.to_object(OBJECT)
    obj.name = obj.data.name = OBJECT
    hard, soft, st = PT.check_prop(obj, ptype, unset, B.anchors)
    st["type"] = ptype

    out_dir = Path(args["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    PAL.apply_roles(obj, style["parts"]["preview_colors"])
    SH.apply(obj.data)
    _, sheet = RD.render_views(out_dir, style["props"]["views"], size=384, prefix=prop)

    ok = not hard
    outputs = [sheet]
    if ok and args.get("save", True):
        mesh = obj.data   # roles only (STYLE.md §4): no UVs or materials in the library
        for uv in list(mesh.uv_layers):
            mesh.uv_layers.remove(uv)
        mesh.materials.clear()
        mesh.shade_flat()
        if "sharp_edge" in mesh.attributes:
            mesh.attributes.remove(mesh.attributes["sharp_edge"])
        obj["anchors"] = json.dumps(B.anchors)
        obj["prop_type"] = ptype
        for o in list(bpy.context.scene.objects):
            if o is not obj:
                bpy.data.objects.remove(o, do_unlink=True)
        blend = out_dir / f"{prop}.blend"
        SC.save(blend)
        outputs.insert(0, str(blend))
    return {"ok": ok, "valid": ok, "hard": hard, "soft": soft, "stats": st, "outputs": outputs,
            "previews": [sheet], **({"error": "; ".join(hard)} if hard else {})}
