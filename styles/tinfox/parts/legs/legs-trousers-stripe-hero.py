# Squad suit trousers (tinfox, hero-m; players), the guard trousers + a white stripe (role `secondary`) down the
# outer front of each thigh, from the belt to above the knee (specs/player-1/reference). Guard trousers: chamfered-rectangle sections per leg from inside the
# jacket down into the boot shaft; full thighs, a faceted knee, the shin into the boot. Edge loops at the knee.
hip, kn = lm["hip.l"], lm["knee.l"]
x = hip.x
# facet pass (2026-11-19): the guard trousers' sections (legs-trousers-hero): chamfered rectangles, knee break at z 0.46
rows = [(0.95, 0.075, 0.08, 0.0), (hip.z, 0.105, 0.105, 0.0), (0.78, 0.13, 0.12, 0.0), (0.62, 0.13, 0.122, -0.005),
        (0.5, 0.126, 0.12, 0.0), (0.46, 0.134, 0.128, 0.008), (0.41, 0.112, 0.108, 0.018),
        (0.35, 0.1, 0.094, 0.04), (0.3, 0.082, 0.08, 0.05)]
# v3: the shin runs back and out into the boot shaft's centre (the shaft sits 3.5 cm behind the leg bone and 2 cm
# further out, so the foot can reach forward under a wide stance)
dx = lambda z: 0.0 if z >= kn.z else 0.02 * min(1.0, (kn.z - z) / (kn.z - 0.3))
def sec(z, rx, ry, dy):
    return P.rrect((x + dx(z), dy, z), rx, ry, 0.38 * min(rx, ry), seg=1)
legs = P.loft([sec(*r) for r in rows], "primary")
def leg_at(z):
    for a, b in zip(rows, rows[1:]):
        if b[0] <= z <= a[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return [u + (v - u) * t for u, v in zip(a, b)]
# facet pass: the stripe runs down the middle of the front-outer chamfer facet (normal 45 deg out and forward)
path, nrm = [], []
for z in (0.9, 0.84, 0.78, 0.72, 0.66, 0.6, 0.56):
    _, rx, ry, dy = leg_at(z)
    r = 0.38 * min(rx, ry)
    path.append(Vector((x + dx(z) + rx - r / 2, dy - ry + r / 2, z)))
    nrm.append(Vector((1, -1, 0)).normalized())
legs += P.sweep(path, P.strap_profile(0.03, 0.004, 0.0012), "secondary", nrm)
P.mirror_x(legs)
