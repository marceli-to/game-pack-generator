"""Guides for the `ai` painted approach (styles/painted STYLE.md §4): per view the current paint rendered
unlit (start image), a depth map from a smoothed copy (near = white) and the silhouette mask, plus the
reference.json that maps the generated 4-view sheet back onto the mesh (lib.paint.project_paint)."""
import math

import bmesh
import bpy
import numpy as np
from mathutils import Vector

from . import paint as PT
from . import render as RD

VIEWS = ["front", "side", "back", "side_mirror"]


def frame_for(obj, margin):
    """One orthographic framing for all views: centred on x = y = 0 (characters stand on the origin, which
    is what the projection's centre_x assumes), wide enough for the height and both horizontal extents."""
    M = obj.matrix_world
    co = np.array([tuple(M @ v.co) for v in obj.data.vertices])
    zlo, zhi = co[:, 2].min(), co[:, 2].max()
    span = max(zhi - zlo, 2 * np.abs(co[:, 0]).max(), 2 * np.abs(co[:, 1]).max())
    return {"center": [0.0, 0.0, float((zlo + zhi) / 2)], "extent": float(span * margin)}


def smooth_copy(obj, levels, crease_deg):
    """Evaluated copy with `levels` of subdivision; edges sharper than crease_deg (and open edges) fully
    creased, so only the soft facets round off. Not linked to the scene; caller removes it."""
    me = obj.data.copy()
    bm = bmesh.new()
    bm.from_mesh(me)
    cr = bm.edges.layers.float.get("crease_edge") or bm.edges.layers.float.new("crease_edge")
    lim = math.radians(crease_deg)
    for e in bm.edges:
        e[cr] = 1.0 if len(e.link_faces) != 2 or e.calc_face_angle(0.0) > lim else 0.0
    bm.to_mesh(me)
    bm.free()
    tmp = bpy.data.objects.new("_DepthSmooth", me)
    tmp.matrix_world = obj.matrix_world.copy()
    bpy.context.scene.collection.objects.link(tmp)
    mod = tmp.modifiers.new("sub", "SUBSURF")
    mod.levels = mod.render_levels = levels
    ev = tmp.evaluated_get(bpy.context.evaluated_depsgraph_get())
    out = bpy.data.objects.new("_DepthSmoothEval", bpy.data.meshes.new_from_object(ev))
    out.matrix_world = obj.matrix_world.copy()
    bpy.data.objects.remove(tmp)
    bpy.data.meshes.remove(me)
    return out


def render_guides(obj, out_dir, cfg):
    """Write init_/depth_/mask_<view>.png (natural camera orientation) and reference.json to out_dir.
    cfg: paint.ai. Returns (reference dict, frame)."""
    S = cfg["view_size"]
    frame = frame_for(obj, cfg["frame_margin"])
    cz, ext = frame["center"][2], frame["extent"]
    mpp = ext / S
    RD.VIEWS["side_mirror"] = (Vector((-1, 0, 0)), False)
    RD.render_views(out_dir, VIEWS, size=S, prefix="init", frame=frame, light="FLAT")

    def to_px(h, z):
        return S / 2 + h / mpp, S / 2 - (z - cz) / mpp

    dobj = smooth_copy(obj, cfg["depth_subsurf"], cfg["crease_deg"]) if cfg["depth_subsurf"] else obj
    try:
        for v in VIEWS:
            zb = PT.zbuffer(dobj, v, (S, S), to_px)
            zm = PT.zbuffer(obj, v, (S, S), to_px) if dobj is not obj else zb
            if v == "side_mirror":  # projection orientation (screen right = +Y) -> natural camera view
                zb, zm = zb[:, ::-1], zm[:, ::-1]
            fg = (zm > -8) & (zb > -8)  # real outline; the smoothed copy shrinks a little
            d = np.zeros((S, S))
            lo, hi = zb[fg].min(), zb[fg].max()
            d[fg] = 0.25 + 0.75 * (zb[fg] - lo) / max(hi - lo, 1e-6)
            RD.save_rgba(np.dstack([d, d, d, np.ones_like(d)]).astype(np.float32), out_dir / f"depth_{v}.png")
            m = (zm > -8).astype(np.float32)
            RD.save_rgba(np.dstack([m, m, m, np.ones_like(m)]), out_dir / f"mask_{v}.png")
    finally:
        if dobj is not obj:
            me = dobj.data
            bpy.data.objects.remove(dobj)
            bpy.data.meshes.remove(me)
    # the generated sheet is [front | side | back | side_mirror flipped back to projection orientation]
    ref = {"m_per_px": mpp, "floor_y": S / 2 + cz / mpp, "background": [c / 255 for c in cfg["background"]],
           "views": {v: {"center_x": S / 2 + i * S, "x_range": [i * S, (i + 1) * S]} for i, v in enumerate(VIEWS)}}
    return ref, frame
