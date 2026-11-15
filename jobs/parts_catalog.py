"""Preview sheet of library parts: one row per part (front, side, 3/4), in the preview colours.

args: { parts: ["<slot>-<variant>", ...], out_dir, size? }
"""
from pathlib import Path

import bpy
import numpy as np

from lib import palette as PAL
from lib import parts as PT
from lib import render as RD
from lib import scene as SC
from lib import shading as SH
from lib import style as S


def run(args):
    out_dir = Path(args["out_dir"])
    size = args.get("size", 256)
    colors = S.load()["parts"]["preview_colors"]
    rows, order = [], []
    for part in args["parts"]:
        SC.empty_scene()
        obj = PT.load_part(part)
        PAL.apply_roles(obj, colors)
        SH.apply(obj.data)
        views, _ = RD.render_views(out_dir / "views", ["front", "side", "three_quarter"], size=size, prefix=part)
        rows.append(np.concatenate([RD.load_rgba(p) for p in views], axis=1))
        order.append(part)
    if not rows:
        raise RuntimeError("no parts to show")
    sheet = RD.save_rgba(np.concatenate(rows, axis=0), out_dir / "catalog.png")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return {"outputs": [sheet], "previews": [sheet], "stats": {"rows": order}}
