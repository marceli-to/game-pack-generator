"""Automatic fit to the reference sheet (STYLE.md §7b, core.json `fit`).

The fit changes no part script: it scales body regions (`fit.groups`: head group, torso, arms + hands, legs +
feet) across their main axis, with a width and a depth curve per region (scale factors at three stations along
the axis: start, middle, end; linear in between). `spec.fit` stores the factors; `assemble` applies them to the
joined rest mesh, so the spec hash covers them. Pure numpy, no bpy: used by the `assemble` and `fit_reference`
jobs and by the tests.
"""
import math

import numpy as np

STATIONS = 3


def _group_of(vslot, slots, groups):
    """Vertex -> group name (None if its slot is in no group)."""
    out = np.full(len(vslot), -1, dtype=np.int32)
    names = list(groups)
    for gi, g in enumerate(names):
        for s in groups[g]["slots"]:
            if s in slots:
                out[vslot == slots.index(s)] = gi
    return out, names


def frames(co, vslot, slots, groups, landmarks):
    """Per group: which vertices, the coordinate along the axis (`t`), the two radial coordinates' centres and
    the stations (min / mid / max of `t` over the group's vertices in the unfitted mesh)."""
    gid, names = _group_of(vslot, slots, groups)
    out = {}
    for gi, g in enumerate(names):
        idx = np.nonzero(gid == gi)[0]
        if not len(idx):
            continue
        cfg = groups[g]
        p = co[idx]
        side = np.where(p[:, 0] >= 0, 1.0, -1.0)
        if cfg["axis"] == "x":            # arms: along |x| in the T-pose, radial = y and z about the arm line
            t = np.abs(p[:, 0])
            cu = np.zeros(len(idx))
            cv = np.full(len(idx), float(landmarks[cfg["centre"]][2]))
            ucol, vcol = 1, 2
        else:                             # vertical: along z, radial = x and y about a vertical line
            t = p[:, 2]
            cx = abs(float(landmarks[cfg["centre"]][0])) if cfg.get("centre") else 0.0
            cu = side * cx
            cv = np.zeros(len(idx))
            ucol, vcol = 0, 1
        lo, hi = float(t.min()), float(t.max())
        out[g] = {"idx": idx, "t": t, "cu": cu, "cv": cv, "ucol": ucol, "vcol": vcol,
                  "stations": [lo, (lo + hi) / 2, hi]}
    return out


def _curve(t, stations, values):
    return np.interp(t, stations, values)


def apply(co, fr, fit):
    """Fitted copy of `co` (N x 3 rest coordinates). `fit` = {group: {"u": [3], "v": [3]}} scale factors
    (u: width across the axis, v: depth; arms: u = front-back, v = up-down)."""
    out = co.copy()
    for g, f in (fit or {}).items():
        if g not in fr:
            continue
        F = fr[g]
        su = _curve(F["t"], F["stations"], f.get("u", [1.0] * STATIONS))
        sv = _curve(F["t"], F["stations"], f.get("v", [1.0] * STATIONS))
        p = out[F["idx"]]
        p[:, F["ucol"]] = F["cu"] + (p[:, F["ucol"]] - F["cu"]) * su
        p[:, F["vcol"]] = F["cv"] + (p[:, F["vcol"]] - F["cv"]) * sv
        out[F["idx"]] = p
    return out


# --- colour classes ------------------------------------------------------------------------------------------
def srgb_to_lab(rgb):
    """sRGB 0..1 (... x 3) -> CIE Lab (D65)."""
    c = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def classes(colors_hex, merge):
    """Palette colours used by the character -> classes: colours closer than `merge` (Lab, lightness weighted
    as in `classify`) share one class (a black glove and a dark-grey belt are not told apart on a shaded sheet).
    Returns (class of each colour, Lab of each colour)."""
    rgb = np.array([[int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)] for h in colors_hex])
    lab = srgb_to_lab(rgb)
    cls = list(range(len(lab)))
    for i in range(len(lab)):
        for j in range(i):
            if _dist(lab[i], lab[j]) < merge and cls[i] == i:
                cls[i] = cls[j]
    return np.array(cls), lab


def _dist(a, b, lw=0.5):
    d = a - b
    return float(math.sqrt((lw * d[0]) ** 2 + d[1] ** 2 + d[2] ** 2))


def classify(rgb, fg, lab, cls, lw=0.5):
    """Sheet pixels -> class of the nearest palette colour (lightness weighted down: the sheet is shaded);
    background -> -1."""
    L = srgb_to_lab(rgb[fg])
    d = (lw * (L[:, None, 0] - lab[None, :, 0])) ** 2 + (L[:, None, 1] - lab[None, :, 1]) ** 2 + \
        (L[:, None, 2] - lab[None, :, 2]) ** 2
    out = np.full(fg.shape, -1, dtype=np.int32)
    out[fg] = cls[np.argmin(d, axis=1)]
    return out


def score(ref_lab, ren_lab, w_sil):
    """Silhouette IoU and class agreement (both over the union of the two outlines) -> (sil, cls, total)."""
    a, b = ref_lab >= 0, ren_lab >= 0
    union = np.logical_or(a, b).sum()
    if not union:
        return 0.0, 0.0, 0.0
    sil = np.logical_and(a, b).sum() / union
    agree = (np.logical_and(a, b) & (ref_lab == ren_lab)).sum() / union
    return float(sil), float(agree), float(w_sil * sil + (1 - w_sil) * agree)
