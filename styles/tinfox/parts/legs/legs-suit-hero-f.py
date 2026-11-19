# Suit legs (tinfox, hero-f; players 2 and 4), from specs/player-2/reference: slim fitted legs, chamfered-rectangle
# sections per leg from inside the suit top into the boot shaft; full at the hip, tapering thigh, a faceted knee, a slim shin
# running back and out into the boot shaft (as legs-overalls-hero-f, slimmer).
hip, kn = lm["hip.l"], lm["knee.l"]
x = hip.x
# v2 (Marcel: legs should bend at the top to look connected): the upper thigh angles in towards the crotch and a
# little forward, fuller at the front, so it covers the suit top's lower front and flows up into the belt instead of
# hanging as a straight tube under a separate hip shape
rows = [(0.94, 0.08, 0.1, -0.008), (hip.z, 0.104, 0.124, -0.004), (0.74, 0.1, 0.11, -0.002), (0.6, 0.088, 0.094, -0.004),
        (kn.z + 0.07, 0.09, 0.092, -0.008), (kn.z + 0.02, 0.092, 0.094, -0.012), (kn.z - 0.04, 0.082, 0.084, 0.006),
        (0.3, 0.074, 0.074, 0.045)]
dx = lambda z: (-0.026 * min(1.0, (z - 0.7) / (0.94 - 0.7)) if z > 0.7 else 0.0) + \
    (0.0 if z >= kn.z else 0.02 * min(1.0, (kn.z - z) / (kn.z - 0.3)))
# facet pass (2026-11-19): chamfered-rectangle sections (broad front/side planes), not 12-sided rings
def sec(z, rx, ry, dy):
    return P.rrect((x + dx(z), dy, z), rx, ry, 0.38 * min(rx, ry), seg=1)
legs = P.loft([sec(*r) for r in rows], "primary")
P.mirror_x(legs)
