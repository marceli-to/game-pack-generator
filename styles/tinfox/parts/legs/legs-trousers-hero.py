# Uniform trousers (tinfox, hero-m), fitted to specs/guard/reference: one 10-sided tube per leg from inside the
# jacket down into the boot shaft; full thighs, a faceted knee, the shin into the boot. Edge loops at the knee.
hip, kn = lm["hip.l"], lm["knee.l"]
x = hip.x
rows = [(0.95, 0.075, 0.08, 0.0), (hip.z, 0.1, 0.1, 0.0), (0.78, 0.118, 0.108, 0.0), (0.66, 0.125, 0.112, -0.005), (kn.z + 0.08, 0.112, 0.104, -0.01),
        (kn.z + 0.03, 0.116, 0.11, -0.018), (kn.z - 0.03, 0.108, 0.102, 0.004), (kn.z - 0.07, 0.096, 0.09, 0.026),
        (0.3, 0.082, 0.08, 0.05)]
# v3: the shin runs back and out into the boot shaft's centre (the shaft sits 3.5 cm behind the leg bone and 2 cm
# further out, so the foot can reach forward under a wide stance)
dx = lambda z: 0.0 if z >= kn.z else 0.02 * min(1.0, (kn.z - z) / (kn.z - 0.3))
legs = P.loft([P.ring((x + dx(z), dy, z), rx, ry, n=14) for z, rx, ry, dy in rows], "primary")
P.mirror_x(legs)
