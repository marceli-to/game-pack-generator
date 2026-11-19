# Healer robe (lowpoly chibi), fitted to specs/healer/reference (sheet scaled from the head: chin -> 0.79 m).
# A long cream robe (12 facets, a flat facet at the front) to just above the boots with a raised gold hem band;
# a gold V at the neck; a team-coloured stole (role `secondary`, Heerschar swaps that palette cell per team)
# lying over the shoulders and hanging down the front in two strips with pointed gold-trimmed ends and gold
# crosses; a soft hood lying on the shoulders and the upper back; a rope belt (leather) with a knot and two ends.
# th: 0 = front (-Y), 90 = +X (wearer's left).
TH = [15 + 30 * k for k in range(12)]
rings = [  # (z, rx, ry, y offset)
    (0.778, 0.07, 0.066, 0.0), (0.764, 0.15, 0.12, 0.0), (0.726, 0.19, 0.142, 0.0), (0.62, 0.186, 0.145, 0.0),
    (0.52, 0.18, 0.145, 0.0), (0.40, 0.19, 0.158, 0.004), (0.28, 0.222, 0.174, 0.008), (0.192, 0.24, 0.184, 0.01),
    (0.188, 0.252, 0.194, 0.01), (0.152, 0.256, 0.198, 0.01),
]
def pt(th, rx, ry, dy, z):
    t = math.radians(th)
    return Vector((rx * math.sin(t), -ry * math.cos(t) + dy, z))
HEM = len(rings) - 2
P.loft([[pt(th, rx, ry, dy, z) for th in TH] for z, rx, ry, dy in rings],
       lambda b, i: "accent" if b == HEM else "primary", cap_roles=("primary", "dark"))

def size(z):
    """Robe ring (rx, ry, dy) at height z (linear between the rings above the hem)."""
    body = rings[:HEM]
    for (z1, a1, b1, d1), (z0, a0, b0, d0) in zip(body, body[1:]):
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0)
            return a0 + (a1 - a0) * t, b0 + (b1 - b0) * t, d0 + (d1 - d0) * t
    return body[0][1:] if z > body[0][0] else body[-1][1:]

def surf(th, z, out=0.0):
    """Point on the faceted robe surface (on the facet chord at angle th), pushed out along the facet normal."""
    rx, ry, dy = size(z)
    th = th % 360
    k = int(((th - 15) % 360) // 30)
    a0 = 15 + 30 * k
    a, b = pt(a0, rx, ry, dy, z), pt(a0 + 30, rx, ry, dy, z)
    f = ((th - a0) % 360) / 30
    p = a.lerp(b, f)
    e = b - a
    n = Vector((e.y, -e.x, 0)).normalized()  # outward for counter-clockwise (front -> +X) order
    if n.dot(Vector((p.x, p.y - dy, 0))) < 0:
        n = -n
    return p + n * out

# gold V at the neck: two bevelled straps from the collar down to a point on the front facet
for s in (1, -1):
    path = [surf(s * 22, 0.774, 0.0) + Vector((0, 0, 0.0)), surf(s * 11, 0.722, 0.0), surf(0, 0.672, 0.0)]
    P.sweep(path, P.strap_profile(0.022, 0.008, 0.003), "accent", [Vector((0, -1, 0.3))] * len(path))

# stole: one strip per side, (z, inner th, outer th) per row; the strip lies on the facets 2 cm proud
OUT = 0.014
stole_rows = [(0.772, 20, 62), (0.745, 17, 66), (0.70, 15, 66), (0.60, 15, 62), (0.48, 15, 58), (0.36, 16, 55),
              (0.30, 16, 54)]
def stole(s):
    grid = []
    for z, a, b in stole_rows:
        m = (a + b) / 2
        grid.append([surf(s * a, z, OUT), surf(s * m, z, OUT), surf(s * b, z, OUT)])
    za, zm = 0.30, 0.262  # red ends in a V; the gold band below it, 3 mm further out
    a, b = stole_rows[-1][1:]
    m = (a + b) / 2
    red = grid + [[surf(s * a, za - 0.008, OUT), surf(s * m, zm, OUT), surf(s * b, za - 0.008, OUT)]]
    if s < 0:
        red = [r[::-1] for r in red]
    P.shell(red, 0.012, "secondary")
    gold = [[surf(s * a, za - 0.004, OUT + 0.003), surf(s * m, zm + 0.004, OUT + 0.003), surf(s * b, za - 0.004, OUT + 0.003)],
            [surf(s * a, 0.258, OUT + 0.003), surf(s * m, 0.214, OUT + 0.003), surf(s * b, 0.258, OUT + 0.003)]]
    if s < 0:
        gold = [r[::-1] for r in gold]
    P.shell(gold, 0.012, "accent")
    # gold cross on the strip
    cz, ct = 0.345, m
    def plate(t0, t1, z0, z1):
        g = [[surf(s * t0, z1, OUT + 0.004), surf(s * t1, z1, OUT + 0.004)],
             [surf(s * t0, z0, OUT + 0.004), surf(s * t1, z0, OUT + 0.004)]]
        if s < 0:
            g = [r[::-1] for r in g]
        P.shell(g, 0.008, "accent")
    plate(ct - 3.2, ct + 3.2, cz - 0.045, cz + 0.045)
    plate(ct - 10, ct - 3.4, cz - 0.014, cz + 0.014)
    plate(ct + 3.4, ct + 10, cz - 0.014, cz + 0.014)
stole(1)
stole(-1)

# hood lying on the shoulders: a thick sheet from the neck roll down the upper back to a soft point
def edge_z(th):  # lower edge of the hood per angle (180 = back centre)
    d = abs(((th - 180) + 180) % 360 - 180) / 130.0  # 0 at the back, 1 at th 50 / 310
    return 0.60 + (0.755 - 0.60) * min(1.0, d) ** 0.8
cols = [50 + 260 * k / 12 for k in range(13)]
hood = []
for t, bulge in ((0.0, 0.012), (0.3, 0.03), (0.65, 0.036), (1.0, 0.016)):
    row = []
    for th in cols:
        z = 0.785 + (edge_z(th) - 0.785) * t
        if t == 0.0:
            rx, ry, dy = 0.088, 0.084, 0.006
            row.append(pt(th, rx, ry, dy, z))
        else:
            row.append(surf(th, z, bulge + 0.012))
    hood.append(row)
P.shell(hood, 0.016, "primary", edge_role="primary")

# rope belt: a thin round band with a knot at the front and two hanging ends
BZ = 0.528
rx, ry, dy = size(BZ)
P.loft([P.ring((0, dy, z), rx + o, ry + o, n=12, phase=0) for z, o in ((BZ - 0.012, 0.0), (BZ - 0.005, 0.012),
                                                                           (BZ + 0.005, 0.012), (BZ + 0.012, 0.0))],
       "leather")
fy = -ry + dy - 0.016
knot = Vector((0.012, fy - 0.006, BZ))
P.loft([[knot + Vector((0, 0, -0.024))]] + [P.ring(knot + Vector((0, 0, h)), r, r * 0.8, n=6) for h, r in
                                             ((-0.014, 0.022), (0.0, 0.028), (0.014, 0.022))]
       + [[knot + Vector((0, 0, 0.024))]], "leather")
for x0, x1, z1 in ((0.0, -0.022, 0.415), (0.02, 0.03, 0.44)):
    a = Vector((x0, fy - 0.004, BZ - 0.01))
    b = Vector((x1, surf(0, z1).y - 0.014, z1))
    P.cylinder(a, b, 0.009, n=5, role="leather")
    P.loft([[b + Vector((0, 0, 0.012))], P.ring(b, 0.013, n=5), [b + Vector((0, 0, -0.018))]], "leather")
