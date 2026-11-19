# Overall legs (tinfox, hero-f), for specs/worker/reference: chamfered-rectangle sections per leg from inside the overalls top
# into the boot shaft; full thighs, a wide faceted knee, the shin tapering back and out into the boot shaft.
hip, kn = lm["hip.l"], lm["knee.l"]
x = hip.x
rows = [(0.93, 0.07, 0.075, 0.0), (hip.z, 0.1, 0.1, 0.0), (0.74, 0.112, 0.108, 0.0), (0.6, 0.116, 0.11, -0.004),
        (kn.z + 0.07, 0.122, 0.112, -0.01), (kn.z + 0.02, 0.122, 0.112, -0.014), (kn.z - 0.04, 0.104, 0.098, 0.006),
        (0.3, 0.085, 0.08, 0.045)]
dx = lambda z: 0.0 if z >= kn.z else 0.02 * min(1.0, (kn.z - z) / (kn.z - 0.3))
# facet pass (2026-11-19): chamfered-rectangle sections (broad front/side planes), not 12-sided rings
def sec(z, rx, ry, dy):
    return P.rrect((x + dx(z), dy, z), rx, ry, 0.38 * min(rx, ry), seg=1)
legs = P.loft([sec(*r) for r in rows], "primary")
P.mirror_x(legs)
