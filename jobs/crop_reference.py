"""Cut a turnaround sheet into square, same-scale view crops (front / side / back).

args: { image, out_dir, top_y, floor_y, height_m, extent_m, size,
        views: {view: {center_x, x_range?: [x0, x1]}} }
Scale: (floor_y - top_y) px = height_m (the body height, floor to skull top). Each crop is
extent_m wide and tall, its bottom `pad` below the floor, centred on the view's body axis.
Pixels outside x_range (neighbouring views) and the floor line are filled with the background.
"""
from pathlib import Path

import numpy as np

from lib import render as RD


def crop_geometry(args):
    mpp = args["height_m"] / (args["floor_y"] - args["top_y"])
    s = int(round(args["extent_m"] / mpp))
    pad = int(round(0.04 * s))
    return mpp, s, pad


def run(args):
    out_dir = Path(args["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    src = RD.load_rgba(args["image"])
    h, w = src.shape[:2]
    bg = src[2, 2].copy()
    mpp, s, pad = crop_geometry(args)
    floor_y = args["floor_y"]
    y0 = floor_y + pad - s
    outs = {}
    for view, v in args["views"].items():
        cx = int(round(v["center_x"]))
        x0 = cx - s // 2
        canvas = np.empty((s, s, 4), dtype=np.float32)
        canvas[:] = bg
        xr = v.get("x_range", [0, w])
        for yy in range(s):
            sy = y0 + yy
            if sy < 0 or sy >= h or sy >= floor_y - 1:
                continue
            lo, hi = max(x0, xr[0], 0), min(x0 + s, xr[1], w)
            if hi > lo:
                canvas[yy, lo - x0:hi - x0] = src[sy, lo:hi]
        crop = RD.resample(canvas, args["size"])
        outs[view] = RD.save_rgba(crop, out_dir / f"{view}.png")
    sheet = np.concatenate([RD.load_rgba(outs[v]) for v in args["views"]], axis=1)
    sheet_path = RD.save_rgba(sheet, out_dir / "reference_sheet.png")
    return {"outputs": list(outs.values()) + [sheet_path], "previews": [sheet_path],
            "stats": {"m_per_px": mpp, "crop_px": s, "pad_px": pad, "background": [round(float(x), 4) for x in bg[:3]],
                      "crops": outs}}
