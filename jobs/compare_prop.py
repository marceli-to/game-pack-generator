"""Prop vs its sheet (STYLE.md §9b): each drawn view cropped, the same view rendered at the same metres per pixel,
both aligned by the centres of their outlines; rows: sheet / render / overlay (red = sheet only, blue = render only).

args: { image: <abs path>, length_m, views: {view: [x0, y0, x1, y1]}, out_dir, size? }
The scale comes from the item_side view: the outline's width there is `length_m`.
"""
from pathlib import Path

import numpy as np
from mathutils import Vector

from lib import render as RD
from lib import scene as SC
from lib import style as S


def bbox(mask):
    ys, xs = np.where(mask)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def run(args):
    style = S.load()
    size = int(args.get("size", 512))
    img = RD.load_rgba(args["image"])
    h, w = img.shape[:2]
    border = np.concatenate([img[:4].reshape(-1, 4), img[-4:].reshape(-1, 4), img[:, :4].reshape(-1, 4), img[:, -4:].reshape(-1, 4)])
    bg = np.median(border, axis=0)
    views = args["views"]
    if "item_side" not in views:
        raise RuntimeError("spec.reference.views needs item_side (its width sets the scale)")
    crops = {}
    for v, (x0, y0, x1, y1) in views.items():
        c = img[y0:y1, x0:x1]
        m = RD.mask(c, bg, threshold=0.16)
        crops[v] = (c, m, bbox(m))
    bx0, _, bx1, _ = crops["item_side"][2]
    mpp = float(args["length_m"]) / (bx1 - bx0)

    lo, hi = RD.world_bbox(SC.meshes())
    centre = (lo + hi) / 2
    render_bg = [c / 255 for c in bytes.fromhex(style["preview"]["background"].lstrip("#"))] + [1.0]
    out_dir = Path(args["out_dir"])
    rows, iou, dims = [[], [], []], {}, {}
    for v, (c, m, (x0, y0, x1, y1)) in crops.items():
        side_px = int(max(x1 - x0, y1 - y0) * 1.15)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        ref = np.ones((side_px, side_px, 4), dtype=np.float32)
        ref[...] = bg
        ox, oy = int(round(cx - side_px / 2)), int(round(cy - side_px / 2))
        sx0, sy0 = max(0, ox), max(0, oy)
        sx1, sy1 = min(c.shape[1], ox + side_px), min(c.shape[0], oy + side_px)
        ref[sy0 - oy:sy1 - oy, sx0 - ox:sx1 - ox] = c[sy0:sy1, sx0:sx1]
        ref = RD.resample(ref, size)
        paths, _ = RD.render_views(out_dir, [v], size=size, prefix="render",
                                   frame={"center": list(centre), "extent": side_px * mpp})
        b = RD.load_rgba(paths[0])
        ma, mb = RD.mask(ref, bg, threshold=0.16), RD.mask(b, render_bg)
        inter, union = np.logical_and(ma, mb).sum(), np.logical_or(ma, mb).sum()
        iou[v] = round(float(inter / union), 3) if union else None
        dims[v] = {"sheet_m": [round((x1 - x0) * mpp, 4), round((y1 - y0) * mpp, 4)]}
        if mb.any():
            bx = bbox(mb)
            k = side_px * mpp / size
            dims[v]["render_m"] = [round((bx[2] - bx[0]) * k, 4), round((bx[3] - bx[1]) * k, 4)]
        ov = np.ones_like(ref)
        ov[..., :3] = 0.97
        ov[ma & ~mb, :3] = (0.85, 0.2, 0.2)
        ov[mb & ~ma, :3] = (0.2, 0.35, 0.9)
        ov[ma & mb, :3] = 0.6
        rows[0].append(ref)
        rows[1].append(b)
        rows[2].append(ov)
    sheet = np.concatenate([np.concatenate(r, axis=1) for r in rows], axis=0)
    out = RD.save_rgba(sheet, out_dir / "compare_sheet.png")
    return {"outputs": [out], "previews": [out],
            "stats": {"iou": iou, "m_per_px": round(mpp, 7), "dims": dims, "views": list(crops)}}
