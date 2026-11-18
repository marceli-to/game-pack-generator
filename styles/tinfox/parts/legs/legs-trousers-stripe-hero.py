# Squad suit trousers (tinfox, hero-m; players), the guard trousers + a white stripe (role `secondary`) down the
# outer front of each thigh, from the belt to above the knee (specs/player-1/reference). Guard trousers: one 10-sided tube per leg from inside the
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
def leg_at(z):
    for a, b in zip(rows, rows[1:]):
        if b[0] <= z <= a[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return [u + (v - u) * t for u, v in zip(a, b)]
a = math.radians(30)     # outer side, turned 30 deg to the front
path, nrm = [], []
for z in (0.9, 0.84, 0.78, 0.72, 0.66, 0.6, 0.56):
    _, rx, ry, dy = leg_at(z)
    path.append(Vector((x + dx(z) + rx * math.cos(a), dy - ry * math.sin(a), z)))
    nrm.append(Vector((math.cos(a) / rx, -math.sin(a) / ry, 0)).normalized())
legs += P.sweep(path, P.strap_profile(0.03, 0.004, 0.0012), "secondary", nrm)
P.mirror_x(legs)
