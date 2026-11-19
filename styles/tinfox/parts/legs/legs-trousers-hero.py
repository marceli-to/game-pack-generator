# Uniform trousers (tinfox, hero-m), fitted to specs/guard/reference. Facet pass (2026-11-19): sections are chamfered
# rectangles (broad front and side planes, narrow chamfers) measured on the sheet: full thigh, widest at the knee
# break (z 0.46, bulging at the back), a narrower shin running back and out into the boot shaft's centre.
hip, kn = lm["hip.l"], lm["knee.l"]
x = hip.x
# (z, half width, half depth, y offset)
rows = [(0.95, 0.075, 0.08, 0.0), (hip.z, 0.105, 0.105, 0.0), (0.78, 0.13, 0.12, 0.0), (0.62, 0.13, 0.122, -0.005),
        (0.5, 0.126, 0.12, 0.0), (0.46, 0.134, 0.128, 0.008), (0.41, 0.112, 0.108, 0.018),
        (0.35, 0.1, 0.094, 0.04), (0.3, 0.082, 0.08, 0.05)]
dx = lambda z: 0.0 if z >= kn.z else 0.02 * min(1.0, (kn.z - z) / (kn.z - 0.3))
def sec(z, rx, ry, dy):
    return P.rrect((x + dx(z), dy, z), rx, ry, 0.38 * min(rx, ry), seg=1)
legs = P.loft([sec(*r) for r in rows], "primary")
P.mirror_x(legs)
