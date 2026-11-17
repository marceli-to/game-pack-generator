"""Comparison sheet: reference crops (top) vs renders at the same scale (middle) vs silhouette
overlay (bottom: red = reference only, blue = render only, grey = both). STYLE.md §11.

args: { ref: <reference.json dict>, ref_dir, out_dir, arms_down_deg?: float, hide_slots?: [...] }
arms_down_deg rotates the upper arms down from the T-pose (references are often drawn in an
A-pose); this only affects this render, nothing is saved.
Returns per-view silhouette IoU (1.0 = identical outline).
"""
import math
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Matrix

from lib import render as RD
from lib import scene as SC
from lib import style as S


def pose_arms(arm, deg):
    arm.data.pose_position = "POSE"
    for side, sign in (("l", 1), ("r", -1)):
        pb = arm.pose.bones[f"upperarm.{side}"]
        head = pb.head.copy()
        rot = Matrix.Translation(head) @ Matrix.Rotation(math.radians(deg) * sign, 4, "Y") @ Matrix.Translation(-head)
        pb.matrix = rot @ pb.matrix
        bpy.context.view_layer.update()


def hide_slots(obj, names):
    slots = S.load()["slots"]
    idx = {slots.index(n) for n in names if n in slots}
    a = obj.data.attributes.get("slot")
    if not idx or a is None:
        return 0
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    layer = bm.faces.layers.int.get("slot")
    dead = [f for f in bm.faces if f[layer] in idx]
    bmesh.ops.delete(bm, geom=dead, context="FACES")
    bm.to_mesh(obj.data)
    bm.free()
    return len(dead)


def run(args):
    ref = args["ref"]
    ref_dir = Path(args["ref_dir"])
    out_dir = Path(args["out_dir"])
    style = S.load()
    views = list(ref["views"])
    mpp, s, pad = ref["m_per_px"], ref["crop_px"], ref["pad_px"]
    size = ref["size"]

    char = bpy.context.scene.objects.get(style["skeleton"]["mesh_object"])
    if char is None:
        raise RuntimeError("no Character mesh; run assemble_from_parts first")
    hidden = hide_slots(char, args.get("hide_slots", []))
    arm = SC.main_armature()
    deg = float(args.get("arms_down_deg", 0) or 0)
    if arm is not None:
        # an animated character keeps its idle clip assigned: drop it (this render only, nothing is saved),
        # else pose_arms() would lower the arms from the clip's pose instead of the T-pose
        if arm.animation_data is not None:
            arm.animation_data.action = None
        for pb in arm.pose.bones:
            pb.location = (0, 0, 0)
            pb.rotation_mode = "QUATERNION"
            pb.rotation_quaternion = (1, 0, 0, 0)
            pb.scale = (1, 1, 1)
        arm.data.pose_position = "REST"
        bpy.context.view_layer.update()
        if deg:
            pose_arms(arm, deg)
    frame = {"center": [0.0, 0.0, (s / 2 - pad) * mpp], "extent": s * mpp}
    paths, _ = RD.render_views(out_dir, views, size=size, prefix="render", frame=frame)

    render_bg = [c / 255 for c in bytes.fromhex(style["preview"]["background"].lstrip("#"))]
    ref_bg = ref["background"]
    rows = [[], [], []]
    iou = {}
    for v, rp in zip(views, paths):
        a = RD.load_rgba(ref_dir / ref["crops"][v])
        b = RD.load_rgba(rp)
        ma, mb = RD.mask(a, ref_bg), RD.mask(b, render_bg)
        inter, union = np.logical_and(ma, mb).sum(), np.logical_or(ma, mb).sum()
        iou[v] = round(float(inter / union), 3) if union else None
        ov = np.ones_like(a)
        ov[..., :3] = 0.97
        ov[ma & ~mb, :3] = (0.85, 0.2, 0.2)
        ov[mb & ~ma, :3] = (0.2, 0.35, 0.9)
        ov[ma & mb, :3] = 0.6
        rows[0].append(a)
        rows[1].append(b)
        rows[2].append(ov)
    sheet = np.concatenate([np.concatenate(r, axis=1) for r in rows], axis=0)
    out = RD.save_rgba(sheet, out_dir / "compare_sheet.png")
    return {"outputs": [out], "previews": [out],
            "stats": {"iou": iou, "arms_down_deg": deg, "hidden_faces": hidden, "views": views}}
