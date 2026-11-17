"""Automatic fit to the reference sheet (STYLE.md §7b): scale curves per body region + the arm angle of the
comparison pose, found by coordinate descent on the sheet's outline and colour classes.

args: { ref: <reference.json>, ref_dir, spec, out_dir, start?: {fit, arms_down_deg} }
Works on the assembled character (rest mesh, unfitted: `spec.fit` is ignored here, the search starts from
`start`). Saves nothing to the .blend; returns the fit for the spec and a sheet
(rows: sheet classes, before, after).
"""
import json
import math
import tempfile
from pathlib import Path

import bpy
import numpy as np

from compare_reference import hide_slots, pose_arms
from lib import fit as F
from lib import measure as M
from lib import overlap as O
from lib import render as RD
from lib import scene as SC
from lib import style as S

ID_COLOURS = [(0.9, 0.1, 0.1), (0.1, 0.8, 0.1), (0.1, 0.2, 0.9), (0.95, 0.85, 0.1), (0.8, 0.1, 0.8),
              (0.1, 0.85, 0.85), (0.95, 0.5, 0.1), (0.5, 0.25, 0.05), (0.55, 0.55, 0.55), (0.15, 0.15, 0.15),
              (0.6, 0.9, 0.5), (0.4, 0.4, 0.9)]


def _hex(c):
    return "#%02X%02X%02X" % tuple(int(round(x * 255)) for x in c)


def run(args):
    style = S.load()
    cfg = style["fit"]
    ref, ref_dir, spec = args["ref"], Path(args["ref_dir"]), args["spec"]
    out_dir = Path(args["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    size = cfg["size"]
    char = bpy.data.objects.get(style["skeleton"]["mesh_object"])
    arm = SC.main_armature()
    if char is None or arm is None:
        raise RuntimeError("no assembled character")
    hide_slots(char, (spec.get("compare") or {}).get("hide_slots", []))
    me = char.data
    slots, roles = style["slots"], style["roles"]

    # --- colour classes: palette colours used by the faces -> classes; an ID colour per class on the mesh
    role_f = M._int_face_attr(me, "role")
    colors = spec.get("colors") or {}
    pal = style["palette"]["colors"]
    used = sorted({colors[roles[r]] for r in set(role_f.tolist()) if roles[r] in colors})
    cls_of_col, lab = F.classes([pal[i] for i in used], cfg["colour_merge"])
    cls_of_pidx = {p: int(c) for p, c in zip(used, cls_of_col)}
    face_cls = np.array([cls_of_pidx.get(colors.get(roles[r]), 0) for r in role_f])
    ids = np.array(ID_COLOURS[:max(cls_of_col) + 1], dtype=np.float32)
    ca = me.color_attributes.get("FITID") or me.color_attributes.new("FITID", "BYTE_COLOR", "CORNER")
    loop_cls = np.repeat(face_cls, [len(p.vertices) for p in me.polygons])
    cols = np.ones((len(me.loops), 4), dtype=np.float32)
    cols[:, :3] = ids[loop_cls]
    ca.data.foreach_set("color_srgb", cols.ravel())   # byte colours: write the sRGB values the render shows
    me.color_attributes.active_color = ca

    # --- reference class maps per view
    views = list(ref["views"])
    ref_bg = ref["background"]
    ref_lab = {}
    for v in views:
        a = RD.resample(RD.load_rgba(ref_dir / ref["crops"][v]), size)
        fg = RD.mask(a, ref_bg)
        ref_lab[v] = F.classify(a[..., :3], fg, lab, cls_of_col)

    # --- render setup (flat ID colours, no antialiasing), same framing as compare_reference
    mpp, s, pad = ref["m_per_px"], ref["crop_px"], ref["pad_px"]
    RD.setup(size, "FLAT")
    sc = bpy.context.scene
    sc.display.shading.color_type = "VERTEX"
    sc.display.render_aa = "OFF"
    cam = RD._camera()
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = s * mpp
    centre = np.array([0.0, 0.0, (s / 2 - pad) * mpp])
    bg = np.array([c / 255 for c in bytes.fromhex(style["preview"]["background"].lstrip("#"))], dtype=np.float32)
    tmp = Path(tempfile.mkdtemp(prefix="gpg-fit-")) / "r.png"
    pal_ids = np.concatenate([ids, bg[None, :]], axis=0)

    def render_labels(view):
        d, _ = RD.VIEWS[view]
        cam.location = tuple(centre + np.array(d) * s * mpp * 3)
        cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = str(tmp)
        bpy.ops.render.render(write_still=True)
        img = RD.load_rgba(tmp)[..., :3]
        dist = ((img[:, :, None, :] - pal_ids[None, None]) ** 2).sum(-1)
        lab_ = np.argmin(dist, axis=2).astype(np.int32)
        lab_[lab_ == len(ids)] = -1
        return lab_

    # --- geometry: rest coordinates, groups
    tpl = json.loads(S.repo_path(style["archetypes"][spec.get("archetype", style["default_archetype"])]["template"]).read_text())
    orig = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get("co", orig)
    orig = orig.reshape(-1, 3)
    vslot = O.vertex_slots(me, M._int_face_attr(me, "slot"))
    fr = F.frames(orig, vslot, slots, cfg["groups"], tpl["landmarks"])
    skip = set((spec.get("compare") or {}).get("fit_exclude", []))   # regions kept as modelled (a deliberate change)
    gnames = [g for g in cfg["groups"] if g in fr and g not in skip]
    # a region's end that meets a region kept as modelled stays as modelled too (trousers inside locked boots)
    pinned = {(g, {"start": 0, "end": F.STATIONS - 1}[k]) for g in gnames
              for k, n in cfg["groups"][g].get("meets", {}).items() if n in skip or n not in fr}

    def set_pose(deg):
        for pb in arm.pose.bones:
            pb.matrix_basis.identity()
        arm.data.pose_position = "POSE"
        bpy.context.view_layer.update()
        pose_arms(arm, deg)

    lo_b, hi_b = (math.log(b) for b in cfg["bounds"])

    def evaluate(x, deg, labels=False):
        fit = {g: {"u": [math.exp(v) for v in x[g]["u"]], "v": [math.exp(v) for v in x[g]["v"]]} for g in gnames}
        co = F.apply(orig, fr, fit)
        me.vertices.foreach_set("co", co.ravel())
        me.update()
        set_pose(deg)
        per, maps = {}, {}
        for v in views:
            ren = render_labels(v)
            per[v] = F.score(ref_lab[v], ren, cfg["w_silhouette"])
            maps[v] = ren
        total = sum(p[2] for p in per.values()) / len(per)
        smooth = sum((a - b) ** 2 for g in gnames for k in ("u", "v") for a, b in zip(x[g][k], x[g][k][1:]))
        obj = total - cfg["smooth_penalty"] * smooth
        return (obj, per, maps) if labels else obj

    start = args.get("start") or {}
    sfit = start.get("fit") or {}
    x = {g: {k: [math.log(v) for v in sfit.get(g, {}).get(k, [1.0] * F.STATIONS)] for k in ("u", "v")}
         for g in gnames}
    deg = float(start.get("arms_down_deg") or (spec.get("compare") or {}).get("arms_down_deg") or 60)
    best, per0, maps0 = evaluate(x, deg, labels=True)
    first = (best, per0)
    evals = 1
    dmin, dmax = cfg["arms_down_range"]
    for step in cfg["steps"]:
        for _ in range(cfg["passes"]):
            improved = False
            # the comparison pose first (the arms' angle on the sheet), then every scale factor
            for dd in (cfg["arms_down_step"], -cfg["arms_down_step"]):
                nd = min(dmax, max(dmin, deg + dd))
                val = evaluate(x, nd)
                evals += 1
                if val > best + 1e-5:
                    best, deg, improved = val, nd, True
            for g in gnames:
                for k in ("u", "v"):
                    for i in range(F.STATIONS):
                        if (g, i) in pinned:
                            continue
                        for sgn in (1, -1):
                            old = x[g][k][i]
                            x[g][k][i] = min(hi_b, max(lo_b, old + sgn * step))
                            val = evaluate(x, deg)
                            evals += 1
                            if val > best + 1e-5:
                                best, improved = val, True
                                break
                            x[g][k][i] = old
            if not improved:
                break
    final, per1, maps1 = evaluate(x, deg, labels=True)

    # sheet: rows = sheet classes, before, after (class colours; grey = background)
    def colourise(lab_):
        img = np.ones(lab_.shape + (4,), dtype=np.float32)
        img[..., :3] = 0.92
        m = lab_ >= 0
        img[m, :3] = ids[lab_[m]]
        return img
    rows = [[colourise(ref_lab[v]) for v in views], [colourise(maps0[v]) for v in views],
            [colourise(maps1[v]) for v in views]]
    sheet = RD.save_rgba(np.concatenate([np.concatenate(r, axis=1) for r in rows], axis=0), out_dir / "fit_sheet.png")
    fit = {g: {k: [round(math.exp(v), 3) for v in x[g][k]] for k in ("u", "v")} for g in gnames}
    rnd = lambda per: {v: {"silhouette": round(p[0], 4), "colour": round(p[1], 4), "score": round(p[2], 4)}
                       for v, p in per.items()}
    return {"outputs": [sheet], "previews": [sheet],
            "stats": {"fit": fit, "arms_down_deg": deg, "evaluations": evals,
                      "before": {"score": round(first[0], 4), "views": rnd(first[1])},
                      "after": {"score": round(final, 4), "views": rnd(per1)},
                      "stations": {g: [round(t, 4) for t in fr[g]["stations"]] for g in gnames},
                      "classes": {str(p): int(c) for p, c in cls_of_pidx.items()},
                      "class_colours": [_hex(c) for c in ids.tolist()]}}
