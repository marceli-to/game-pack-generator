# Suit sleeves (tinfox, hero-f; players 2 and 4), from specs/player-2/reference: fitted sleeves from inside the torso
# (under the shoulder pads) past the elbow to a thick cuff band at mid-forearm, a short bare forearm into the glove.
sh, el, wr = lm["shoulder.l"], lm["elbow.l"], lm["wrist.l"]
zc = sh.z
# facet pass (2026-11-19): chamfered-square sections (broad front/top planes), not round rings
def sq(x, r):
    return P.rrect((x, 0, zc), r, r, 0.38 * r, seg=1, axis="x")
faces = P.loft([sq(x, r) for x, r in
                ((0.12, 0.075), (sh.x + 0.01, 0.078), (el.x - 0.04, 0.066), (el.x + 0.04, 0.062), (el.x + 0.09, 0.062))],
               "primary")
faces += P.loft([sq(x, r) for x, r in
                 ((el.x + 0.085, 0.068), (el.x + 0.09, 0.076), (el.x + 0.17, 0.074), (el.x + 0.175, 0.064))],
                "primary", cap_roles=("primary", "dark"))
faces += P.loft([sq(el.x + 0.15, 0.046), sq(wr.x - 0.01, 0.04),
                 sq(wr.x + 0.02, 0.038)], "skin")
P.mirror_x(faces)
