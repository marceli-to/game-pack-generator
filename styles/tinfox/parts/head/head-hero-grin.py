# Hero head (tinfox, hero-m), v6 face pass (ears, nose, chin; v5: profile, eyes, brows), fitted to specs/guard/reference: a rounded-square head (12 points per
# ring, superellipse, flat front face) with a face profile pushed forward down the centre line: brow ridge, cheeks/nose base, a recess
# at the mouth, a square chin jutting forward; a short neck into the collar. Face as geometry: big tall eyes, thick
# stern eyebrows (hair colour), a nose wedge with a bridge, a lopsided smirk (higher on the wearer's left), big
# rounded ears with a raised inner rim.
z1 = lm["head_top"].z
N = 12   # facet pass (2026-11-19): 12 points, few broad planes like the sheet (v6 had 20)
def ring(z, sx, fy, by, bump, n=3.2):
    pts = []
    for k in range(N):
        t = 2 * math.pi * (k + 0.5) / N   # a flat face at the front, not a centre ridge
        s, c = math.sin(t), -math.cos(t)          # t = 0: front (-Y)
        x = sx * math.copysign(abs(s) ** (2 / n), s)
        r = fy if c < 0 else by
        y = r * math.copysign(abs(c) ** (2 / n), c)
        y -= bump * max(0.0, -c) ** 6               # centre-front profile
        pts.append(Vector((x, y, z)))
    return pts
# thick neck, about jaw-wide (player sheet)
P.loft([P.ring((0, 0.012, 1.36), 0.09, 0.084, n=10), P.ring((0, 0.012, 1.48), 0.094, 0.088, n=10)], "skin")
# (z, half width, front, back, centre-front bump)
# player: the jaw narrows in straight planes to a flat chin (the guard's round lower face showed above the open collar)
prof = [(1.445, 0.06, 0.1, 0.05, 0.0), (1.457, 0.074, 0.114, 0.07, 0.03), (1.474, 0.088, 0.124, 0.088, 0.036),
        (1.492, 0.102, 0.13, 0.1, 0.03), (1.512, 0.116, 0.134, 0.115, 0.014), (1.535, 0.13, 0.136, 0.13, 0.002), (1.575, 0.132, 0.139, 0.145, 0.01), (1.615, 0.127, 0.139, 0.152, 0.0),
        (1.66, 0.124, 0.137, 0.156, 0.02), (1.7, 0.119, 0.13, 0.156, 0.005), (1.75, 0.108, 0.118, 0.146, 0.0),
        (z1, 0.08, 0.085, 0.112, 0.0)]
P.loft([[Vector((0, 0.0, 1.44))]] + [ring(*p) for p in prof] + [[Vector((0, 0.012, z1 + 0.006))]], "skin")
def face_y(x, z, out=0.0):
    """Front surface y at (x, z) on the actual facets (polygon incl. the centre-front bump, not the analytic
    superellipse), so features sit on the planes."""
    def on_ring(p):
        pts = sorted((q for q in ring(*p) if q.y < 0), key=lambda q: q.x)
        ax = abs(x)
        for a, b in zip(pts, pts[1:]):
            if a.x <= ax <= b.x or a.x <= -ax <= b.x:
                xx = ax if a.x <= ax <= b.x else -ax
                return a.y + (b.y - a.y) * (xx - a.x) / max(1e-9, b.x - a.x)
        return pts[len(pts) // 2].y
    for a, b in zip(prof, prof[1:]):
        if a[0] <= z <= b[0]:
            s = (z - a[0]) / (b[0] - a[0])
            return on_ring(a) + (on_ring(b) - on_ring(a)) * s - out
    return -0.1
eye = P.loft([P.ring((0.05, face_y(0.05, 1.615) + 0.004, 1.615), 0.016, 0.027, n=10, axis="y"),
              P.ring((0.05, face_y(0.05, 1.615) - 0.007, 1.615), 0.015, 0.026, n=10, axis="y")], "eyes")
bx = [0.016, 0.042, 0.07, 0.094]
bz = [1.655, 1.664, 1.672, 1.668]
brow = P.sweep([Vector((x, face_y(x, z) - 0.006, z)) for x, z in zip(bx, bz)],
               P.strap_profile(0.024, 0.012, 0.004), "hair", [Vector((0, -1, 0))] * 4)
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
P.loft([nose_ring(z, f, rx) for z, f, rx in ((1.655, -0.143, 0.009), (1.625, -0.162, 0.012), (1.6, -0.174, 0.019),
                                           (1.584, -0.18, 0.027), (1.568, -0.175, 0.025), (1.561, -0.156, 0.02))],
       "skin")
# grin (players, specs/player-1/reference): wide, the top edge almost straight with the corners just turned up, a
# deep U below, filled with white teeth (role `secondary`) and only a thin dark rim (role `eyes`) round them
def bump_at(z):
    for a, b in zip(prof, prof[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return a[4] + (b[4] - a[4]) * t, a[1] + (b[1] - a[1]) * t
    return 0.0, 0.13
def fy(x, z, out):
    """face_y plus the centre-front profile bump (chin, mouth recess)."""
    bmp, sx = bump_at(z)
    return face_y(x, z, out)   # facet pass: face_y already follows the bump on the facets
MW = 0.062
zt = lambda x: 1.538 + 0.012 * (x / MW) ** 4
zb = lambda x: zt(x) - 0.042 * max(0.0, 1 - (x / MW) ** 2) ** 0.6 - 0.002
xs = [MW * k / 6 for k in range(-6, 7)]
mid = lambda x: (zt(x) + zb(x)) / 2
rows = [[Vector((x, fy(x, f(x), 0.004), f(x))) for x in xs] for f in (zt, mid, zb)]
P.shell(rows, -0.01, "eyes")   # facet pass: 1.6 cm turned the plate inside-out at its thin ends on the flat face
TW = MW - 0.004
xt = [TW * k / 6 for k in range(-6, 7)]
top = lambda x: zt(x) - 0.0035
bot = lambda x: min(top(x) - 0.003, zb(x) + 0.004)
rows = [[Vector((x, fy(x, f(x), 0.0075), f(x))) for x in xt] for f in (top, lambda x: (top(x) + bot(x)) / 2, bot)]
P.shell(rows, -0.006, "secondary")
