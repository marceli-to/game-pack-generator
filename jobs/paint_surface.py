"""Painted surface (styles/painted, STYLE.md §4, SPIKE): UV-unwrap the open character, fill a
base-colour texture with one approach and render previews.

args: { approach: "auto" | "projection", colors: {role: palette index}, out_dir, out_blend?,
        ref?: <reference.json dict>, ref_image?: path (projection), seed?: int,
        frame?: {center, extent} (preview framing), projection?: {overrides of paint.projection} }
Outputs <out_dir>/<approach>.png (texture), previews lit (STUDIO) and unlit (FLAT).
"""
from pathlib import Path

import bpy
import numpy as np

from lib import paint as PT
from lib import render as RD
from lib import style as S


def run(args):
    style = S.load()
    cfg = style["paint"]
    obj = bpy.context.scene.objects.get(style["skeleton"]["mesh_object"])
    if obj is None:
        raise RuntimeError("no Character mesh; run assemble_from_parts first")
    arm = bpy.context.scene.objects.get(style["skeleton"]["armature_object"])
    if arm is not None:
        arm.data.pose_position = "REST"
    size = args.get("size", cfg["texture_size"])
    out_dir = Path(args["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    approach = args["approach"]

    _, uv_fixed = PT.unwrap(obj, margin=cfg["uv_margin_px"] * 2 / size, check_size=size)
    tm = PT.TexelMap(obj, size)
    auto, stats = PT.auto_paint(obj, tm, args["colors"], cfg["auto"], seed=args.get("seed", 1))
    stats["uv_overlap_faces_fixed"] = uv_fixed
    rgb = auto
    if approach == "projection":
        ref_img = RD.load_rgba(args["ref_image"])
        rgb, cov, pst = PT.project_paint(obj, tm, args["ref"], ref_img, auto,
                                          {**cfg["projection"], **args.get("projection", {})})
        stats["projection"] = pst
    elif approach != "auto":
        raise ValueError(f"unknown approach {approach!r}")

    img = tm.dilate(tm.image(rgb), cfg["uv_margin_px"] * 2)
    tex_path = out_dir / f"{approach}.png"
    RD.save_rgba(img[::-1], tex_path)            # TexelMap rows are bottom-up
    image = bpy.data.images.load(str(tex_path))
    image.pack()
    PT.painted_material(obj, image, cfg["material"])
    if args.get("out_blend"):
        bpy.ops.wm.save_as_mainfile(filepath=str(args["out_blend"]))

    previews = []
    for light in ("STUDIO", "FLAT"):
        _, sheet = RD.render_views(out_dir, prefix=f"{approach}_{light.lower()}", frame=args.get("frame"), light=light)
        previews.append(sheet)
    stats["texture"] = str(tex_path)
    return {"outputs": [str(tex_path)] + previews, "previews": previews, "stats": stats}
