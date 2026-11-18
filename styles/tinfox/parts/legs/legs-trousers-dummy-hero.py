# Padded trousers (tinfox, hero-m), for the practice dummy: the guard's trousers in padded canvas (role armor) with a
# big quilted knee pad on each knee: a rounded square cushion standing ~4 cm proud, sharing thigh and shin (half
# each) like a kneecap so it rides the bent knee.
hip, kn = lm["hip.l"], lm["knee.l"]
x = hip.x
rows = [(0.95, 0.075, 0.08, 0.0), (hip.z, 0.1, 0.1, 0.0), (0.78, 0.118, 0.108, 0.0), (0.66, 0.125, 0.112, -0.005), (kn.z + 0.08, 0.112, 0.104, -0.01),
        (kn.z + 0.03, 0.116, 0.11, -0.018), (kn.z - 0.03, 0.108, 0.102, 0.004), (kn.z - 0.07, 0.096, 0.09, 0.026),
        (0.3, 0.082, 0.08, 0.05)]
dx = lambda z: 0.0 if z >= kn.z else 0.02 * min(1.0, (kn.z - z) / (kn.z - 0.3))
legs = P.loft([P.ring((x + dx(z), dy, z), rx, ry, n=14) for z, rx, ry, dy in rows], "armor")
pz = kn.z + 0.055
sq = lambda y, sx, sz, r: P.rrect((x, y, pz), sx, sz, r, seg=2, axis="y")
pad = P.loft([sq(-0.07, 0.085, 0.085, 0.04), sq(-0.14, 0.1, 0.098, 0.045), sq(-0.162, 0.094, 0.092, 0.042),
              sq(-0.17, 0.076, 0.074, 0.034)], "armor")
P.set_weights(pad, {"upperleg.l": 0.5, "lowerleg.l": 0.5})
P.mirror_x(legs + pad)
