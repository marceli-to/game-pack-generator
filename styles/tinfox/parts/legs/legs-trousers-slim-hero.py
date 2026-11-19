# Slim uniform trousers (tinfox, hero-m), for long coats and tall boots (specs/officer/reference): slim inside the
# coat (thighs clear of its skirt), full at the knee where they show between hem and boot top, tapering into the
# boot shaft below the knee (which sits behind and outside the leg bone). Edge loops at the knee.
hip, kn = lm["hip.l"], lm["knee.l"]
x = hip.x
# (z, rx, ry, dy)
rows = [(0.95, 0.075, 0.08, 0.0), (hip.z, 0.085, 0.088, 0.0), (0.74, 0.082, 0.088, 0.0), (0.6, 0.092, 0.094, -0.005),
        (kn.z + 0.09, 0.1, 0.1, -0.01), (kn.z + 0.04, 0.104, 0.104, -0.015), (kn.z, 0.098, 0.096, 0.0),
        (kn.z - 0.03, 0.085, 0.082, 0.02), (0.33, 0.075, 0.072, 0.035), (0.26, 0.07, 0.068, 0.04)]
dx = lambda z: 0.0 if z >= kn.z else 0.015 * min(1.0, (kn.z - z) / (kn.z - 0.3))
# facet pass (2026-11-19): chamfered-rectangle sections
def sec(z, rx, ry, dy):
    return P.rrect((x + dx(z), dy, z), rx, ry, 0.38 * min(rx, ry), seg=1)
legs = P.loft([sec(*r) for r in rows], "primary")
P.mirror_x(legs)
