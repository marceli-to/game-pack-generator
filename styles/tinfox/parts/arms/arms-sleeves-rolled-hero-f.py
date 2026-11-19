# Rolled-up sleeves (tinfox, hero-f), for specs/worker/reference: short teal sleeves from inside the torso to a thick
# rolled cuff over the elbow, bare forearms down into the gloves.
sh, el, wr = lm["shoulder.l"], lm["elbow.l"], lm["wrist.l"]
zc = sh.z
# facet pass (2026-11-19): chamfered-square sections (broad front/top planes), not round rings
def sq(x, r):
    return P.rrect((x, 0, zc), r, r, 0.38 * r, seg=1, axis="x")
xs = [0.12, sh.x + 0.01, el.x - 0.07, el.x - 0.045]
rs = [0.08, 0.082, 0.072, 0.07]
faces = P.loft([sq(x, r) for x, r in zip(xs, rs)], "primary")
faces += P.loft([sq(x, r) for x, r in
                 ((el.x - 0.05, 0.078), (el.x - 0.045, 0.086), (el.x + 0.06, 0.086), (el.x + 0.065, 0.076))],
                "primary", cap_roles=("primary", "dark"))
faces += P.loft([sq(el.x + 0.04, 0.052), sq(el.x + 0.15, 0.046),
                 sq(wr.x - 0.01, 0.04), sq(wr.x + 0.02, 0.038)],
                "skin")
P.mirror_x(faces)
