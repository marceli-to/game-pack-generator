# Padded sleeves (tinfox, hero-m), fitted to specs/guard/reference. Facet pass (2026-11-19): sections are chamfered
# rectangles (broad front/top planes) measured on the sheet: bulky upper arm, a kink at the elbow, a narrower forearm,
# then a broad 14 cm rolled cuff with a clear step; bare wrist into the glove. Starts inside the torso (pads on the torso).
sh, el, wr = lm["shoulder.l"], lm["elbow.l"], lm["wrist.l"]
zc = sh.z
# (x, half depth (y), half height (z))
rows = [(0.14, 0.09, 0.095), (sh.x + 0.02, 0.1, 0.1), (el.x - 0.07, 0.096, 0.096), (el.x - 0.01, 0.085, 0.088),
        (el.x + 0.03, 0.08, 0.082), (wr.x - 0.205, 0.08, 0.082), (wr.x - 0.2, 0.106, 0.106), (wr.x - 0.075, 0.104, 0.104),
        (wr.x - 0.068, 0.09, 0.09)]
def sec(xx, a, b):
    return P.rrect((xx, 0, zc), a, b, 0.38 * min(a, b), seg=1, axis="x")
faces = P.loft([sec(*r) for r in rows], ["primary"] * (len(rows) - 1), cap_roles=("primary", "dark"))
faces += P.loft([P.ring((wr.x - 0.075, 0, zc), 0.05, n=8, axis="x"), P.ring((wr.x + 0.02, 0, zc), 0.048, n=8, axis="x")],
                "skin")
P.mirror_x(faces)
