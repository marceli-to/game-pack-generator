# Suit legs, striped variant (tinfox, hero-f; player 4, specs/player-4/reference): legs-suit-hero-f with a white
# stripe (role `secondary`) down the outer front of each thigh from the hip to above the knee. legs-suit-hero-f: slim fitted legs, one 12-sided tube per
# leg from inside the suit top into the boot shaft; full at the hip, tapering thigh, a faceted knee, a slim shin
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
legs = P.loft([P.ring((x + dx(z), dy, z), rx, ry, n=12) for z, rx, ry, dy in rows], "primary")
def leg_at(z):
    for a, b in zip(rows, rows[1:]):
        if b[0] <= z <= a[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return [u + (v - u) * t for u, v in zip(a, b)]
a = math.radians(32)
path, nrm = [], []
for z in (0.86, 0.8, 0.74, 0.68, 0.62, 0.57):
    _, rx, ry, dy = leg_at(z)
    path.append(Vector((x + dx(z) + rx * math.cos(a), dy - ry * math.sin(a), z)))
    nrm.append(Vector((math.cos(a) / rx, -math.sin(a) / ry, 0)).normalized())
legs += P.sweep(path, P.strap_profile(0.028, 0.004, 0.0012), "secondary", nrm)
P.mirror_x(legs)
