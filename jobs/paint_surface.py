"""Painted surface (styles/painted, STYLE.md §4, SPIKE): UV-unwrap the open character, fill a
base-colour texture with one approach and render previews.

args: { approach: "auto" | "projection" | "ai", colors: {role: palette index}, out_dir, out_blend?,
        ref?: <reference.json dict>, ref_image?: path (projection; ai: the generated sheet), seed?: int,
        frame?: {center, extent} (preview framing), projection?: {overrides of paint.projection},
        auto?: {overrides of paint.auto; sub-dicts (light, brush, …) merged key by key},
        keep_roles?: [role, …] (projection/ai: these roles keep the auto paint, plus paint.ai.keep_margin m
        around them), keep_margin?: m }
Outputs <out_dir>/<approach>.png (texture), previews lit (STUDIO) and unlit (FLAT). The texture is packed
into the material `paint.material` (unlit if `paint.unlit`); stats.texture_sha256 binds an approval (§14).
"""
import hashlib
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
    acfg = {k: ({**cfg["auto"][k], **v} if isinstance(v, dict) and isinstance(cfg["auto"].get(k), dict) else v)
            for k, v in args.get("auto", {}).items()}
    acfg = {**cfg["auto"], **acfg}
    auto, stats = PT.auto_paint(obj, tm, args["colors"], acfg, seed=args.get("seed", 1))
    stats["uv_overlap_faces_fixed"] = uv_fixed
    rgb = auto
    if approach in ("projection", "ai"):   # ai: the generated 4-view sheet, same projection code
        ref_img = RD.load_rgba(args["ref_image"])
        pcfg = {**cfg["projection"], **(cfg["ai"]["projection"] if approach == "ai" else {}),
                **args.get("projection", {})}
        rgb, cov, pst = PT.project_paint(obj, tm, args["ref"], ref_img, auto, pcfg)
        stats["projection"] = pst
        if args.get("keep_roles"):   # e.g. a simple cartoon face: keep the procedural paint there
            roles, prole = PT.role_names(obj)
            keep = np.isin(prole[tm.poly], [roles.index(r) for r in args["keep_roles"]])
            margin = args.get("keep_margin", cfg["ai"]["keep_margin"])
            if margin > 0:   # the model's version of the kept part spills onto its neighbours (a mouth on the beard)
                keep |= PT.near_mask(tm.P, keep, margin)
            rgb = np.where(keep[:, None], auto, rgb)
            stats["kept_texels"] = int(keep.sum())
    elif approach != "auto":
        raise ValueError(f"unknown approach {approach!r}")

    img = tm.dilate(tm.image(rgb), cfg["uv_margin_px"] * 2)
    tex_path = out_dir / f"{approach}.png"
    RD.save_rgba(img[::-1], tex_path)            # TexelMap rows are bottom-up
    old = bpy.data.images.get("paint.png")
    if old is not None:
        bpy.data.images.remove(old)
    image = bpy.data.images.load(str(tex_path))
    image.name = "paint.png"
    image.pack()
    PT.painted_material(obj, image, cfg["material"], unlit=cfg.get("unlit", False))
    pal = bpy.data.materials.get(style["palette"]["material"])
    if pal is not None and pal.users == 0:
        bpy.data.materials.remove(pal)
    if args.get("out_blend"):
        bpy.ops.wm.save_as_mainfile(filepath=str(args["out_blend"]))

    previews = []
    for light in ("STUDIO", "FLAT"):
        _, sheet = RD.render_views(out_dir, prefix=f"{approach}_{light.lower()}", frame=args.get("frame"), light=light)
        previews.append(sheet)
    stats["texture"] = str(tex_path)
    stats["texture_sha256"] = "sha256:" + hashlib.sha256(tex_path.read_bytes()).hexdigest()
    stats["approach"] = approach
    stats["unlit"] = bool(cfg.get("unlit", False))
    return {"outputs": [str(tex_path)] + previews, "previews": previews, "stats": stats}
