"""Step 2 (AI texture spike, Blender): render generation guides.
blender -b workspace/knight-v3/character.blend -P spikes/ai-texture/guides.py -- spikes/ai-texture/guides .
Per view (front, side, back, side_mirror; 512 px, head framing): init_<v>.png (auto paint, unlit),
depth_<v>.png (near = white), mask_<v>.png. All in natural camera orientation."""
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

for v in views:
    zb = PT.zbuffer(obj, v, (S, S), to_px)
    if v == "side_mirror":       # projection orientation (screen right = +Y) -> natural camera view
        zb = zb[:, ::-1]
    fg = zb > -8
    d = np.zeros((S, S))
    lo, hi = zb[fg].min(), zb[fg].max()
    d[fg] = 0.25 + 0.75 * (zb[fg] - lo) / max(hi - lo, 1e-6)
    rgba = np.dstack([d, d, d, np.ones_like(d)]).astype(np.float32)
    RD.save_rgba(rgba, out / f"depth_{v}.png")
    m = fg.astype(np.float32)
    RD.save_rgba(np.dstack([m, m, m, np.ones_like(m)]), out / f"mask_{v}.png")
print("GUIDES OK", out)
