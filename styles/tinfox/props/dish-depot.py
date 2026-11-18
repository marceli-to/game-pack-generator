# Satellite dish (Tinfox depot sheet 31), world prop, the game's box 1.38 (x) x 4.34 (high) x 2.08 (deep): a concrete
# pad, a light grey mast with braces, a dark motor housing with orange stripes and a light-blue status light, a
# 16-facet light grey dish facing -Y tilted up 45 degrees, a feed arm with an orange receiver. The sheet draws a short
# mast under a big dish; the game's box asks for a tall mast and a 1.38 m dish, so the parts follow the sheet and the
# proportions follow the box. Metres, z up from the floor, the dish centre at y = 0.

def Vm(x, y, z):
    return Vector((x, y, z))


def ring(c, u, v, r, n, ph=0.0):
    return [c + u * (r * math.cos(ph + 2 * math.pi * i / n)) + v * (r * math.sin(ph + 2 * math.pi * i / n)) for i in range(n)]


def zr(z, hx, hy, ch, cy=0.0):
    return [p + Vector((0, cy, 0)) for p in P.rect(Vm(0, 0, z), hx, hy, ch)]


YM = 0.645                     # mast centre, behind the dish centre
# concrete pad (1.1 x 1.89) with dark bolts
P.loft([zr(0.0, 0.55, 0.945, 0.04, YM), zr(0.20, 0.55, 0.945, 0.04, YM), zr(0.24, 0.51, 0.905, 0.03, YM)], "secondary")
for sx in (1, -1):
    for sy in (1, -1):
        P.dome(Vm(sx * 0.43, YM + sy * 0.80, 0.24), (0, 0, 1), 0.04, 0.03, n=6, role="dark")

# mast: flange, chamfered square column, braces from the pad, collar under the housing
X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
P.loft([ring(Vm(0, YM, z), X, Y, r, 8, math.pi / 8) for z, r in ((0.22, 0.36), (0.34, 0.36), (0.34, 0.26), (0.40, 0.26))],
       ["dark", "dark", "dark"])
P.loft([zr(z, 0.21, 0.21, 0.06, YM) for z in (0.38, 1.2, 2.88)], "primary")
for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
    foot = Vm(sx * 0.42, YM + sy * 0.42, 0.24)
    P.box(foot - Vector((0.06, 0.06, 0.0)), foot + Vector((0.06, 0.06, 0.07)), "metal")
    P.cylinder(foot + Vector((0, 0, 0.04)), Vm(sx * 0.17, YM + sy * 0.17, 1.15), 0.05, n=4, role="metal")
P.loft([ring(Vm(0, YM, z), X, Y, r, 8, math.pi / 8) for z, r in ((2.84, 0.30), (2.96, 0.30))], "metal")

# motor housing with two orange stripes, a light-blue light on the front, pivot hubs on the sides
P.loft([zr(2.94, 0.35, 0.33, 0.07, YM), zr(3.42, 0.35, 0.33, 0.07, YM), zr(3.52, 0.29, 0.27, 0.05, YM)], "dark")
for z0, z1 in ((3.02, 3.08), (3.12, 3.18)):
    P.loft([zr(z0, 0.362, 0.342, 0.072, YM), zr(z1, 0.362, 0.342, 0.072, YM)], "accent")
P.box(Vm(-0.08, YM - 0.355, 3.26), Vm(0.08, YM - 0.32, 3.34), "special")
PIV = Vm(0, 0.318, 3.512)
for s in (1, -1):
    P.cylinder(Vm(s * 0.28, PIV.y, PIV.z), Vm(s * 0.42, PIV.y, PIV.z), 0.14, n=8, role="dark")

# the dish: axis a points forward and up (45 deg); rim at the dish centre C, bowl recessed behind it
C = Vm(0, 0.0, 3.83)
a = Vector((0, -math.cos(math.radians(45)), math.sin(math.radians(45))))
v = Vector((0, math.sin(math.radians(45)), math.cos(math.radians(45))))
R, N, PH = 0.69, 16, math.pi / 16
rings = [[C - a * 0.27]]
for r, d in ((0.24, 0.235), (0.48, 0.15), (0.67, 0.02)):
    rings.append(ring(C - a * d, X, v, r, N, PH))
rings.append(ring(C + a * 0.005, X, v, R, N, PH))               # rim lip
rings.append(ring(C - a * 0.04, X, v, R, N, PH))
for r, d in ((0.48, 0.20), (0.22, 0.30)):
    rings.append(ring(C - a * d, X, v, r, N, PH))
rings.append([C - a * 0.33])
P.loft(rings, ["primary"] * 4 + ["metal"] * 4)
# mount from the dish back to the pivot, feed arm and receiver
P.cylinder(C - a * 0.30, PIV, 0.09, n=8, role="dark")
P.cylinder(C - a * 0.26, C + a * 0.52, 0.022, n=6, role="metal")
rc = C + a * 0.56
P.loft([ring(rc - a * 0.07, X, v, 0.065, 8, PH * 2), ring(rc - a * 0.04, X, v, 0.08, 8, PH * 2),
        ring(rc + a * 0.04, X, v, 0.08, 8, PH * 2), ring(rc + a * 0.07, X, v, 0.065, 8, PH * 2)], "accent")

# to the game's box: exactly 1.38 (x) x 2.08 (y) x 4.34 (z) m
vs = P.bm.verts
lo = Vector([min(q.co[i] for q in vs) for i in range(3)])
hi = Vector([max(q.co[i] for q in vs) for i in range(3)])
want = (1.38, 2.08, 4.34)
for q in vs:
    for i in range(3):
        q.co[i] = (q.co[i] - (lo[i] if i == 2 else (lo[i] + hi[i]) / 2)) * want[i] / (hi[i] - lo[i])
