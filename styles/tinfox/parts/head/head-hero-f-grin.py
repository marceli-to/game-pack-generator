# Hero-f head with a grin (tinfox, hero-f; player 4, specs/player-4/reference): head-hero-f with head-hero-grin's
# open grin (dark D-plate, role `eyes`, white teeth, role `secondary`) instead of the smile line. head-hero-f: the guard's head (head-hero-square) with a softer face:
# narrower jaw and a smaller chin, a smaller nose, thinner arched brows, a symmetric smile. Built in hero-m
# coordinates (same head size: the worker's face is drawn as wide as the guard's) and moved down onto the hero-f head
# joint at the end, 5 % narrower and shallower (head 0.28 m).
z1 = 1.80   # built in hero-m coordinates, moved onto hero-f at the end
N = 20   # v6: more points round the face for the chin and jaw
def ring(z, sx, fy, by, bump, n=3.2):
    pts = []
    for k in range(N):
        t = 2 * math.pi * k / N
        s, c = math.sin(t), -math.cos(t)          # t = 0: front (-Y)
        x = sx * math.copysign(abs(s) ** (2 / n), s)
        r = fy if c < 0 else by
        y = r * math.copysign(abs(c) ** (2 / n), c)
        y -= bump * max(0.0, -c) ** 6               # centre-front profile
        pts.append(Vector((x, y, z)))
    return pts
P.loft([P.ring((0, 0.01, 1.38), 0.075, 0.07, n=8), P.ring((0, 0.01, 1.48), 0.08, 0.075, n=8)], "skin")
# (z, half width, front, back, centre-front bump)
prof = [(1.443, 0.06, 0.098, 0.05, 0.0), (1.455, 0.075, 0.112, 0.07, 0.016), (1.472, 0.09, 0.122, 0.088, 0.02),
        (1.49, 0.106, 0.13, 0.1, 0.016), (1.51, 0.119, 0.134, 0.115, 0.008), (1.535, 0.13, 0.136, 0.13, 0.002), (1.575, 0.132, 0.139, 0.145, 0.01), (1.615, 0.127, 0.139, 0.152, 0.0),
        (1.66, 0.124, 0.137, 0.156, 0.02), (1.7, 0.119, 0.13, 0.156, 0.005), (1.75, 0.108, 0.118, 0.146, 0.0),
        (z1, 0.08, 0.085, 0.112, 0.0)]
P.loft([[Vector((0, 0.0, 1.44))]] + [ring(*p) for p in prof] + [[Vector((0, 0.012, z1 + 0.006))]], "skin")
def face_y(x, z, out=0.0):
    """Front surface y at (x, z), from the ring profile (approximate, for placing features)."""
    for a, b in zip(prof, prof[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            sx, fy = a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t
            u = min(0.999, abs(x) / sx)
            return -fy * (1 - u ** 3.2) ** (1 / 3.2) - out
    return -0.1
eye = P.loft([P.ring((0.05, face_y(0.05, 1.615) + 0.004, 1.615), 0.016, 0.027, n=10, axis="y"),
              P.ring((0.05, face_y(0.05, 1.615) - 0.007, 1.615), 0.015, 0.026, n=10, axis="y")], "eyes")
bx = [0.016, 0.042, 0.07, 0.094]
bz = [1.66, 1.672, 1.676, 1.666]
brow = P.sweep([Vector((x, face_y(x, z) - 0.006, z)) for x, z in zip(bx, bz)],
               P.strap_profile(0.018, 0.01, 0.003), "hair", [Vector((0, -1, 0))] * 4)
# ears (v6): a rounded rim (helix) swept round a C open at the front, a recessed bowl inside it, an earlobe; the
# whole ear angled out 15 deg at the back so it catches its own light against the side of the head
ex, ey, ez, ery, erz = 0.132, 0.012, 1.615, 0.031, 0.051
angs = [math.radians(a) for a in range(-140, 161, 20)]          # 0 = back (+Y), positive = up
path = [Vector((ex + 0.006, ey + ery * math.cos(a), ez + erz * math.sin(a))) for a in angs]
# the rim starts 4 cm inside the head (strap inset) so it stays attached when the ear is angled out
ear = P.sweep(path, P.strap_profile(0.017, 0.022, 0.004, inset=0.04), "skin", [Vector((1, 0, 0))] * len(path))
# bowl, with a root reaching 3.5 cm into the head so the angled ear stays attached all round
ear += P.loft([P.ring((ex - 0.035, ey - 0.002, ez), 0.026, 0.044, n=10, axis="x"),
               P.ring((ex + 0.012, ey - 0.002, ez), 0.024, 0.041, n=10, axis="x")], "skin")
ear += P.rbox((ex - 0.03, ey - 0.03, ez - 0.07), (ex + 0.02, ey + 0.004, ez - 0.035), "skin", r=0.012, bevel=0, seg=2,
              axis="x")
# 70 % size (Marcel: ears massive), scaled about where the ear meets the side of the head
root = Vector((0.125, 0.012, 1.615))
P.transform(ear, Matrix.Translation(root) @ Matrix.Diagonal((0.7, 0.7, 0.7, 1.0)) @ Matrix.Translation(-root))
piv = Vector((0.115, -0.03, 1.615))
M = (Matrix.Translation(piv) @ Matrix.Rotation(math.radians(-15), 4, "Z") @ Matrix.Rotation(math.radians(-8), 4, "Y")
     @ Matrix.Translation(-piv))
P.transform(ear, M)
P.mirror_x(eye + brow + ear)
# nose (v6): a rounded 8-sided loft from the bridge between the brows to a broad tip, back into the face under it;
# a broad tip (no nostril wings: Marcel)
# each ring spans from the nose's front back to 1 cm inside the face, so the nose is solid against it (v6: a
# tube of round rings floated up to 9 mm in front of the face and showed a gap from the side)
def nose_ring(z, front, rx, back=-0.13):
    return P.ring((0, (front + back) / 2, z), rx, (back - front) / 2, n=8)
P.loft([nose_ring(z, f, rx) for z, f, rx in ((1.655, -0.141, 0.008), (1.625, -0.152, 0.01), (1.6, -0.161, 0.015),
                                           (1.586, -0.165, 0.02), (1.573, -0.16, 0.018), (1.566, -0.146, 0.014))],
       "skin")
# grin: as head-hero-grin, a little smaller (top edge almost straight, corners up, a deep U of teeth, thin dark rim)
def bump_at(z):
    for a, b in zip(prof, prof[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return a[4] + (b[4] - a[4]) * t, a[1] + (b[1] - a[1]) * t
    return 0.0, 0.13
def fy(x, z, out):
    bmp, sx = bump_at(z)
    return face_y(x, z, out) - bmp * max(0.0, 1 - (x / sx) ** 2) ** 3
MW = 0.056
zt = lambda x: 1.54 + 0.012 * (x / MW) ** 4
zb = lambda x: zt(x) - 0.036 * max(0.0, 1 - (x / MW) ** 2) ** 0.6 - 0.002
xs = [MW * k / 4 for k in range(-4, 5)]
mid = lambda x: (zt(x) + zb(x)) / 2
rows = [[Vector((x, fy(x, f(x), 0.004), f(x))) for x in xs] for f in (zt, mid, zb)]
P.shell(rows, -0.016, "eyes")
TW = MW - 0.004
xt = [TW * k / 4 for k in range(-4, 5)]
top = lambda x: zt(x) - 0.0035
bot = lambda x: min(top(x) - 0.003, zb(x) + 0.004)
rows = [[Vector((x, fy(x, f(x), 0.0075), f(x))) for x in xt] for f in (top, lambda x: (top(x) + bot(x)) / 2, bot)]
P.shell(rows, -0.006, "secondary")
# onto hero-f: head joint 1.47 -> lm head_base, 5 % narrower/shallower
hb = lm["head_base"].z
P.transform(list(P.bm.faces), Matrix.Translation((0, 0, hb)) @ Matrix.Diagonal((0.95, 0.95, 1.0, 1.0))
            @ Matrix.Translation((0, 0, -1.47)))
