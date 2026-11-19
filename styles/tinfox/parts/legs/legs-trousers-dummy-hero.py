# Padded trousers (tinfox, hero-m), for the practice dummy: the guard's trousers in padded canvas (role armor) with a
# big quilted knee pad on each knee: a rounded square cushion standing ~4 cm proud, sharing thigh and shin (half
# each) like a kneecap so it rides the bent knee.
hip, kn = lm["hip.l"], lm["knee.l"]
x = hip.x
# facet pass (2026-11-19): the guard trousers' sections (legs-trousers-hero): chamfered rectangles, knee break at z 0.46
rows = [(0.95, 0.075, 0.08, 0.0), (hip.z, 0.105, 0.105, 0.0), (0.78, 0.13, 0.12, 0.0), (0.62, 0.13, 0.122, -0.005),
        (0.5, 0.126, 0.12, 0.0), (0.46, 0.134, 0.128, 0.008), (0.41, 0.112, 0.108, 0.018),
        (0.35, 0.1, 0.094, 0.04), (0.3, 0.082, 0.08, 0.05)]
dx = lambda z: 0.0 if z >= kn.z else 0.02 * min(1.0, (kn.z - z) / (kn.z - 0.3))
def sec(z, rx, ry, dy):
    return P.rrect((x + dx(z), dy, z), rx, ry, 0.38 * min(rx, ry), seg=1)
legs = P.loft([sec(*r) for r in rows], "armor")
pz = kn.z + 0.055
sq = lambda y, sx, sz, r: P.rrect((x, y, pz), sx, sz, r, seg=1, axis="y")
pad = P.loft([sq(-0.07, 0.085, 0.085, 0.04), sq(-0.14, 0.1, 0.098, 0.045), sq(-0.162, 0.094, 0.092, 0.042),
              sq(-0.17, 0.076, 0.074, 0.034)], "armor")
P.set_weights(pad, {"upperleg.l": 0.5, "lowerleg.l": 0.5})
P.mirror_x(legs + pad)
