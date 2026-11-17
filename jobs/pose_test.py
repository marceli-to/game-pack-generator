"""Pose test (STYLE.md §8a): play every clip on the assembled character, check it, render a sheet.

args: { spec: {...}, out_dir, clips?: [names], step?: frames, columns?: frames per clip in the sheet, size?: px }
Checks per clip, on the skinned mesh (sampled every `step` frames, plus the last frame):
  - penetration: vertices of one part that end up inside another part's closed shell although they were
    outside it in the rest pose, deeper than `pose_test.penetration_tolerance`; `visible` when a viewer above
    the horizon can see where the part goes in (lib/overlap.py). Only visible ones deeper than
    `visible_tolerance` become findings.
  - floor: lowest point per slot below -foot_contact_tolerance
  - foot contact (walk/run): each foot's lowest point over the cycle within ±foot_contact_tolerance
Sheet: one row per clip, `columns` evenly spaced frames, front view then side view.
"""
import math
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

from lib import anim as A
from lib import measure as M
from lib import overlap as O
from lib import render as RD
from lib import scene as SC
from lib import style as S

def _frames(action, step):
    f0, f1 = (int(round(x)) for x in action.frame_range)
    fr = list(range(f0, f1 + 1, step))
    if fr[-1] != f1:
        fr.append(f1)
    return fr


def _render_tile(cam, view, center, extent, path):
    d, _ = RD.VIEWS[view]
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = extent
    cam.data.clip_end = extent * 12
    cam.location = center + d * extent * 3
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def run(args):
    style = S.load()
    pt = style["pose_test"]
    tol_floor = style["foot_contact_tolerance"]
    tol_pen = pt["penetration_tolerance"]
    step = args.get("step", pt["step"])
    columns = args.get("columns", pt["columns"])
    size = args.get("size", pt["tile_size"])
    slots = style["slots"]
    arm = SC.main_armature()
    char = bpy.data.objects.get(style["skeleton"]["mesh_object"])
    if arm is None or char is None:
        raise RuntimeError("no assembled character")
    names = [c["name"] for c in style["animations"]["clips"]]
    wanted = args.get("clips") or names
    acts = [bpy.data.actions[n] for n in wanted if n in bpy.data.actions]
    missing = [n for n in wanted if n not in bpy.data.actions]
    if not acts:
        raise RuntimeError("the character has no clips; run apply_animations first")

    mesh = char.data
    slot_face = M._int_face_attr(mesh, "slot")
    if slot_face is None:
        raise RuntimeError("mesh has no `slot` attribute (assemble_from_parts sets it)")
    vslot = O.vertex_slots(mesh, slot_face)
    shells = O.Shells(mesh, slot_face)
    dirs = O.view_dirs()

    arm.data.pose_position = "REST"
    bpy.context.view_layer.update()
    rest = O.coords(char)
    rest_inside = set(shells.inside(rest, vslot))
    feet = slots.index("feet")
    foot_side = {"l": np.nonzero((vslot == feet) & (rest[:, 0] > 0))[0],
                 "r": np.nonzero((vslot == feet) & (rest[:, 0] < 0))[0]}
    height = float(rest[:, 2].max())

    arm.data.pose_position = "POSE"
    sc = bpy.context.scene
    upright = A.upright_slots(args.get("spec") or {})
    held = set(style["skinning"]["upright_held_clips"])
    report, findings = {}, []
    for a in acts:
        SC.assign_action(arm, a)
        pen = {}      # (vertex slot, shell slot) -> {depth, frame, verts}
        lowest = {}   # slot -> (z, frame)
        foot_low = {s: (9.0, None) for s in foot_side}
        tilt = {b: 0.0 for b in upright.values()}
        for f in _frames(a, step):
            sc.frame_set(f)
            co = O.coords(char)
            for b in tilt:   # angle between the slot's posed and rest orientation (armature space)
                q = arm.pose.bones[b].matrix.to_quaternion().rotation_difference(
                    arm.data.bones[b].matrix_local.to_quaternion())
                tilt[b] = max(tilt[b], abs(math.degrees(q.angle)) % 360)
            ins = shells.inside(co, vslot)
            groups = {}   # (vertex slot, island) -> [vertices deeper than the tolerance]
            for (v, k), depth in ins.items():
                if (v, k) in rest_inside or depth <= tol_pen:
                    continue
                groups.setdefault((int(vslot[v]), k), []).append(v)
            allb = O.scene_bvh(co, shells.polys) if groups else None
            for (vs_, k), verts in groups.items():
                key = (slots[vs_], slots[shells.islands[k]["slot"]])
                e = pen.setdefault(key, {"depth": 0.0, "frame": f, "verts": set(), "visible_depth": 0.0,
                                         "visible_frame": None, "visible_points": 0})
                e["verts"].update(verts)
                depth = max(ins[(v, k)] for v in verts)
                if depth > e["depth"]:
                    e["depth"], e["frame"] = depth, f
                # visible: where the part goes in, can anyone see it? (boots entering a skirt through its
                # underside are hidden; an arm through a beard is not)
                # depth of what shows: the inside vertices next to a visible crossing (an armpit seam is
                # shallow even where the sleeve's hidden inner end lies deep in the torso)
                seen = [v for p, v in shells.crossings(co, ins, verts, k)
                        if O.visible(allb, p, dirs, spread_deg=pt["visible_cone_deg"])]
                if seen:
                    e["visible_points"] += len(seen)
                    vd = max(ins[(v, k)] for v in seen)
                    if vd > e["visible_depth"]:
                        e["visible_depth"], e["visible_frame"] = vd, f
            for s in np.unique(vslot[vslot >= 0]):
                z = float(co[vslot == s, 2].min())
                if z < lowest.get(slots[s], (9.0, None))[0]:
                    lowest[slots[s]] = (z, f)
            for side, idx in foot_side.items():
                z = float(co[idx, 2].min()) if len(idx) else 9.0
                if z < foot_low[side][0]:
                    foot_low[side] = (z, f)
        r = {"frames": int(round(a.frame_range[1] - a.frame_range[0])), "penetrations": [], "below_floor": [],
             "feet_lowest": {s: round(z, 4) for s, (z, _) in foot_low.items()},
             "upright_tilt_deg": {b: round(min(t, 360 - t), 2) for b, t in tilt.items()}}
        for b, t in r["upright_tilt_deg"].items():
            if a.name not in held and t > pt["max_upright_tilt_deg"]:
                findings.append(f"{a.name}: {b} tilts {t:.0f}° although the grip is upright")
        for (va, sb), e in sorted(pen.items(), key=lambda kv: -kv[1]["depth"]):
            vis = e["visible_points"] > 0
            r["penetrations"].append({"part": va, "into": sb, "depth_m": round(e["depth"], 4),
                                      "frame": e["frame"], "verts": len(e["verts"]), "visible": vis,
                                      **({"visible_depth_m": round(e["visible_depth"], 4),
                                          "visible_frame": e["visible_frame"],
                                          "visible_points": e["visible_points"]} if vis else {})})
            if vis and e["visible_depth"] > pt["visible_tolerance"]:
                # hidden overlaps (boots inside a skirt) and shallow visible seams at joints (a sleeve meeting
                # the torso at the armpit) stay in the report, not in the findings
                findings.append(f"{a.name}@{e['visible_frame']}: {va} {e['visible_depth'] * 100:.1f} cm inside {sb}, "
                                f"visible ({e['visible_points']} crossing points seen)")
        for s, (z, f) in lowest.items():
            if z < -tol_floor:
                r["below_floor"].append({"slot": s, "z": round(z, 4), "frame": f})
                findings.append(f"{a.name}@{f}: {s} {-z * 100:.1f} cm below the floor")
        if a.name in pt["foot_contact_clips"]:
            for side, (z, f) in foot_low.items():
                if abs(z) > tol_floor:
                    findings.append(f"{a.name}: foot.{side} never touches the floor (lowest {z * 100:.1f} cm)")
            r["foot_contact"] = all(abs(z) <= tol_floor for z, _ in foot_low.values())
        report[a.name] = r

    # sheet: one row per clip, `columns` frames x (front, side)
    out = Path(args["out_dir"])
    tiles = out / "tiles"
    tiles.mkdir(parents=True, exist_ok=True)
    RD.setup(size)
    cam = RD._camera()
    rows = []
    for a in acts:
        SC.assign_action(arm, a)
        f0, f1 = a.frame_range
        frs = [int(round(f0 + (f1 - f0) * i / max(columns - 1, 1))) for i in range(columns)]
        report[a.name]["sheet_frames"] = frs
        # framing per clip: the box over its sheet frames, square, floor near the bottom edge
        boxes = []
        for f in frs:
            sc.frame_set(f)
            co = O.coords(char)
            boxes.append((co.min(axis=0), co.max(axis=0)))
        lo = np.min([b[0] for b in boxes], axis=0)
        hi = np.max([b[1] for b in boxes], axis=0)
        extent = max(height, *(hi - lo)) * pt["frame_scale"]
        zc = max((lo[2] + hi[2]) / 2, extent / 2 - pt["floor_margin"] * extent)
        row = []
        for view in ("front", "side"):
            for f in frs:
                sc.frame_set(f)
                p = tiles / f"{a.name}_{view}_{f:03d}.png"
                c = Vector(((lo[0] + hi[0]) / 2 if view == "front" else 0, (lo[1] + hi[1]) / 2 if view == "side" else 0, zc))
                _render_tile(cam, view, c, extent, p)
                row.append(RD.load_rgba(p))
        rows.append(np.concatenate(row, axis=1))
    sheet = np.concatenate(rows, axis=0)
    sheet_path = RD.save_rgba(sheet, out / "pose_test.png")
    arm.data.pose_position = "POSE"
    return {"outputs": [sheet_path], "previews": [sheet_path],
            "stats": {"clips": report, "findings": findings, "missing_clips": missing,
                      "sheet_layout": f"rows: {[a.name for a in acts]}; columns: {columns} frames front, "
                                      f"then the same frames from the side"},
            "warnings": [f"no clip {n!r}" for n in missing]}
