"""Step 2 (AI texture spike, Blender): render generation guides.
blender -b workspace/knight-v3/character.blend -P spikes/ai-texture/guides.py -- spikes/ai-texture/guides .
Per view (front, side, back, side_mirror; 512 px, head framing): init_<v>.png (auto paint, unlit),
depth_<v>.png (near = white), mask_<v>.png. All in natural camera orientation.
Env GUIDE_SUBSURF=<levels> (default 2; 0 = raw mesh): depth from a subdivided copy (edges over 40° creased, so only the soft
facets round off). The depth ControlNet reads flat mesh segments as panels ("plank" lines on the dome)."""
import math
import os
import sys
from pathlib import Path

out, repo = Path(sys.argv[-2]), Path(sys.argv[-1])
sys.path.insert(0, str(repo / "jobs"))
import bpy
import numpy as np
from mathutils import Vector
from lib import paint as PT
from lib import render as RD

S, CZ, EXT = 512, 1.08, 0.75
MPP = EXT / S
out.mkdir(parents=True, exist_ok=True)
obj = bpy.data.objects["Character"]
bpy.data.objects["Armature"].data.pose_position = "REST"
RD.VIEWS["side_mirror"] = (Vector((-1, 0, 0)), False)
views = ["front", "side", "back", "side_mirror"]
RD.render_views(out, views, size=S, prefix="init", frame={"center": [0, 0, CZ], "extent": EXT}, light="FLAT")

def to_px(h, z):
    return S / 2 + h / MPP, S / 2 - (z - CZ) / MPP

def smooth_copy(obj, levels, crease_deg=40.0):
    import bmesh
    me = obj.data.copy()
    bm = bmesh.new()
    bm.from_mesh(me)
    cr = bm.edges.layers.float.get("crease_edge") or bm.edges.layers.float.new("crease_edge")
    for e in bm.edges:
        sharp = len(e.link_faces) != 2 or e.calc_face_angle(0.0) > math.radians(crease_deg)
        e[cr] = 1.0 if sharp else 0.0
    bm.to_mesh(me)
    bm.free()
    tmp = bpy.data.objects.new("DepthSmooth", me)
    tmp.matrix_world = obj.matrix_world.copy()
    bpy.context.scene.collection.objects.link(tmp)
    mod = tmp.modifiers.new("sub", "SUBSURF")
    mod.levels = mod.render_levels = levels
    dg = bpy.context.evaluated_depsgraph_get()
    ev = tmp.evaluated_get(dg)
    out = bpy.data.objects.new("DepthSmoothEval", bpy.data.meshes.new_from_object(ev))
    out.matrix_world = obj.matrix_world.copy()
    return out

subsurf = int(os.environ.get("GUIDE_SUBSURF", "2"))
dobj = smooth_copy(obj, subsurf) if subsurf else obj
for v in views:
    zb = PT.zbuffer(dobj, v, (S, S), to_px)
    zm = PT.zbuffer(obj, v, (S, S), to_px) if dobj is not obj else zb
    if v == "side_mirror":       # projection orientation (screen right = +Y) -> natural camera view
        zb, zm = zb[:, ::-1], zm[:, ::-1]
    fg = (zm > -8) & (zb > -8)   # mask = real mesh outline (the smoothed copy shrinks a little)
    d = np.zeros((S, S))
    lo, hi = zb[fg].min(), zb[fg].max()
    d[fg] = 0.25 + 0.75 * (zb[fg] - lo) / max(hi - lo, 1e-6)
    rgba = np.dstack([d, d, d, np.ones_like(d)]).astype(np.float32)
    RD.save_rgba(rgba, out / f"depth_{v}.png")
    m = (zm > -8).astype(np.float32)
    RD.save_rgba(np.dstack([m, m, m, np.ones_like(m)]), out / f"mask_{v}.png")
print("GUIDES OK", out)
