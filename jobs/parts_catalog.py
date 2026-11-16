"""Preview sheet of library parts: one row per slot, one 3/4 tile per part, in the preview colours.
Mirrored pairs (arms, hands, legs, feet) are framed on the left (+X) side so they are not tiny.
Also writes catalog.html (tiles with part names, archetypes and tris), since the sheet has no labels.

args: { parts: ["<slot>-<variant>", ...], out_dir, size? }
"""
import html
import json
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

from lib import palette as PAL
from lib import parts as PT
from lib import render as RD
from lib import scene as SC
from lib import shading as SH
from lib import style as S

PAIRED = {"arms", "hands", "legs", "feet"}


def _frame(obj, slot):
    pts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    if slot in PAIRED:
        pts = [p for p in pts if p.x >= -0.005] or pts
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return {"center": list((lo + hi) / 2), "extent": max(hi - lo) * 1.25}


def run(args):
    out_dir = Path(args["out_dir"])
    size = args.get("size", 256)
    colors = S.load()["parts"]["preview_colors"]
    by_slot = {}
    for part in args["parts"]:
        slot, _ = PT.split_part_name(part)
        SC.empty_scene()
        obj = PT.load_part(part)
        PAL.apply_roles(obj, colors)
        SH.apply(obj.data)
        views, _ = RD.render_views(out_dir / "views", ["three_quarter"], size=size, prefix=part,
                                   frame=_frame(obj, slot))
        meta_p = Path(PT.part_path(part, ".json"))
        meta = json.loads(meta_p.read_text()) if meta_p.exists() else {}
        by_slot.setdefault(slot, []).append((part, views[0], meta))
    if not by_slot:
        raise RuntimeError("no parts to show")
    cols = max(len(v) for v in by_slot.values())
    sheet = np.full((size * len(by_slot), size * cols, 4), 0.92, dtype=np.float32)
    sheet[..., 3] = 1.0
    grid, cells = {}, []
    for r, (slot, items) in enumerate(by_slot.items()):
        grid[slot] = [p for p, _, _ in items]
        cells.append(f"<h2>{html.escape(slot)}</h2><div class=row>")
        for c, (part, img, meta) in enumerate(items):
            px = RD.load_rgba(img)
            a = px[..., 3:4]
            sheet[r * size:(r + 1) * size, c * size:(c + 1) * size, :3] = \
                px[..., :3] * a + sheet[r * size:(r + 1) * size, c * size:(c + 1) * size, :3] * (1 - a)
            rel = Path(img).relative_to(out_dir).as_posix()
            info = f"{', '.join(meta.get('archetypes', []))} · {meta.get('tris', '?')} tris"
            cells.append(f"<figure><img src='{rel}'><figcaption><b>{html.escape(part)}</b><br>"
                         f"{html.escape(info)}</figcaption></figure>")
        cells.append("</div>")
    out = RD.save_rgba(sheet, out_dir / "catalog.png")
    page = out_dir / "catalog.html"
    page.write_text(
        "<!DOCTYPE html><meta charset=utf-8><title>Parts catalog</title><style>"
        "body{font:13px system-ui;background:#eee;margin:20px}h2{margin:18px 0 6px;font-size:15px}"
        ".row{display:flex;flex-wrap:wrap;gap:10px}figure{margin:0;background:#e6e6e6;padding:4px;width:"
        f"{size}px}}img{{width:{size}px;height:{size}px}}figcaption{{font-size:11px;word-break:break-all}}</style>"
        + "".join(cells))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return {"outputs": [out, str(page)], "previews": [out], "stats": {"rows": grid, "columns": cols}}
