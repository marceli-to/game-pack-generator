"""Guides for the `ai` painted approach (styles/painted STYLE.md §4). Run on a character that already has
its `auto` paint (the start image is that paint, rendered unlit).

args: { out_dir, ai?: {overrides of paint.ai} }
Outputs <out_dir>/init_|depth_|mask_<view>.png (front, side, back, side_mirror) and reference.json."""
import json
from pathlib import Path

import bpy

from lib import aiguides as AG
from lib import style as S


def run(args):
    style = S.load()
    cfg = {**style["paint"]["ai"], **args.get("ai", {})}
    obj = bpy.context.scene.objects.get(style["skeleton"]["mesh_object"])
    if obj is None:
        raise RuntimeError("no Character mesh; run assemble_from_parts first")
    if obj.data.uv_layers.get("Paint") is None:
        raise RuntimeError("character is not painted; the start image is its auto paint")
    arm = bpy.context.scene.objects.get(style["skeleton"]["armature_object"])
    if arm is not None:
        arm.data.pose_position = "REST"
    out = Path(args["out_dir"])
    out.mkdir(parents=True, exist_ok=True)
    ref, frame = AG.render_guides(obj, out, cfg)
    (out / "reference.json").write_text(json.dumps(ref, indent=1))
    files = sorted(str(p) for p in out.glob("*.png") if not p.name.endswith("_sheet.png"))
    return {"outputs": files + [str(out / "reference.json")], "previews": [str(out / "init_sheet.png")],
            "stats": {"frame": frame, "views": AG.VIEWS, "view_size": cfg["view_size"]}}
