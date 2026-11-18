# Explosive barrel (Tinfox props sheet 01), 0.90 m tall, ~0.545 m across. Level prop: front faces -Y.
# Measured off the sheet's front view at 0.1141 cm/px (floor y 864, centre x 293.5); cm, z up from the floor.
# --- Tinfox weapon helpers (pasted into each prop script by run.py; measured in cm off the sheets:
# x along the barrel (muzzle +X), z up from the item's bottom, y across (+y = the item's left side))
K = 0.01   # cm -> m


def V(x, y, z):
    return Vector((x * K, y * K, z * K))


def xring(x, cz, hy, hz, ch, cy=0.0):
    """Chamfered rectangle (half sizes hy across, hz up) in the plane x = const."""
    return [V(x, cy + p.y / K, cz + p.z / K) for p in P.rect((0, 0, 0), hy * K, hz * K, ch * K, axis="x")]


def zring(cx, z, hx, hy, ch, cy=0.0):
    """Chamfered rectangle (half sizes hx along, hy across) in the plane z = const."""
    return [V(cx + p.x / K, cy + p.y / K, z) for p in P.rect((0, 0, 0), hx * K, hy * K, ch * K, axis="z")]


def ngon_x(x, r, cz, n=8):
    """Regular polygon (flat at the bottom) around an axis along X at height cz."""
    return [V(x, p.y / K, cz + p.z / K) for p in P.ring((0, 0, 0), r * K, n=n, axis="x")]


def ngon_z(cx, z, r, n=8, cy=0.0):
    return [V(cx + p.x / K, cy + p.y / K, z) for p in P.ring((0, 0, 0), r * K, n=n, axis="z")]


def ngon_y(cx, cz, y, r, n=8):
    return [V(cx + p.x / K, y, cz + p.z / K) for p in P.ring((0, 0, 0), r * K, n=n, axis="y")]


def tube_x(xs, r, cz, role, n=8):
    """Tube along X through the stations xs (extra stations give vertex AO samples in the open)."""
    return P.loft([ngon_x(x, r, cz, n) for x in xs], role)


def prism_y(poly, y0, y1, role, inset=0.0):
    """Extrude a convex XZ polygon (cm) from y0 to y1; `inset` chamfers both faces towards the centroid."""
    cx = sum(p[0] for p in poly) / len(poly)
    cz = sum(p[1] for p in poly) / len(poly)

    def ring(y, k):
        return [V(cx + (x - cx) * k, y, cz + (z - cz) * k) for x, z in poly]
    if inset:
        sgn = 1 if y1 > y0 else -1
        rings = [ring(y0, 1 - inset), ring(y0 + sgn * 0.3, 1), ring(y1 - sgn * 0.3, 1), ring(y1, 1 - inset)]
    else:
        rings = [ring(y0, 1), ring(y1, 1)]
    return P.loft(rings, role)


def both_sides(poly, y0, y1, role, inset=0.0):
    """The same prism on the left (+y) and the right (-y) side."""
    prism_y(poly, y0, y1, role, inset)
    prism_y(poly, -y0, -y1, role, inset)


def emitter(x0, x1, r, bore, cz, n=8):
    """Orange emitter ring with chamfered edges and a dark bore recess (one shell)."""
    c = min(0.5, (x1 - x0) / 5)
    P.loft([ngon_x(x0, r - c, cz, n), ngon_x(x0 + c, r, cz, n), ngon_x(x1 - c, r, cz, n), ngon_x(x1, r - c, cz, n),
            ngon_x(x1, bore, cz, n), ngon_x(x1 - 1.4, bore, cz, n)],
           ["accent", "accent", "accent", "accent", "dark"], cap_roles=("accent", "dark"))


def handle(hx, z0, z1, half_x, half_y, ridges, role="secondary", ridge_out=0.35):
    """Raked handle: horizontal chamfered rings centred on hx(z), from z0 (bottom) up into the body at z1;
    `ridges` = [(za, zb), ...] grip bands standing out by ridge_out."""
    P.loft([zring(hx(z0), z0, half_x - 0.5, half_y - 0.45, 0.6), zring(hx(z0 + 0.6), z0 + 0.6, half_x, half_y, 0.8),
            zring(hx(z1), z1, half_x - 0.3, half_y, 0.8)], role)
    o = ridge_out
    for za, zb in ridges:
        P.loft([zring(hx(za), za, half_x + 0.05, half_y + 0.1, 0.8),
                zring(hx(za + 0.25), za + 0.25, half_x + o, half_y + o, 0.9),
                zring(hx(zb - 0.25), zb - 0.25, half_x + o, half_y + o, 0.9),
                zring(hx(zb), zb, half_x + 0.05, half_y + 0.1, 0.8)], role)


def guard_loop(path, half_t=0.9, half_w=1.0, role="secondary"):
    """Trigger guard: a square section swept along an XZ path (cm), both ends buried in the body."""
    prof = [(-half_w, -half_t), (half_w, -half_t), (half_w, half_t), (-half_w, half_t)]
    P.sweep([V(x, 0, z) for x, z in path], [(o * K, s * K) for o, s in prof], role, normals=[(0, 1, 0)] * len(path))


def window(cx, cz, sx, sz, r, y_in, y_out, frame="metal", glass="special", inset=0.6, seg=2):
    """Rounded-rectangle window on both sides: a frame standing out to y_out with the glass flush in it
    (a recessed glass bakes dark: vertex AO)."""
    for s in (1, -1):
        def rr(y, ax, az, rad):
            return [V(p.x / K, y * s, p.z / K) for p in P.rrect((cx * K, 0, cz * K), ax * K, az * K, rad * K, seg, axis="y")]
        P.loft([rr(y_in, sx, sz, r), rr(y_out, sx, sz, r), rr(y_out + 0.25, sx - 0.25, sz - 0.25, max(0.1, r - 0.25)),
                rr(y_out + 0.25, sx - inset, sz - inset, max(0.1, r - inset))],
               [frame, frame, frame], cap_roles=(frame, glass))
# --- end of helpers

N = 16                      # sides; a flat facet faces the front (-Y), so the flame sits on a flat face
HALF = 180.0 / N
DA = 360.0 / N


def dring(z, a, turn=0.0):
    """16-gon with apothem `a` (= the front view's half width) at height z; `turn` in columns."""
    R = a / math.cos(math.radians(HALF))
    return [V(R * math.cos(math.radians(-90 + HALF + (i + turn) * DA)),
              R * math.sin(math.radians(-90 + HALF + (i + turn) * DA)), z) for i in range(N)]


# (z, apothem, role of the band up to the next ring); "S" = hazard stripes
PROFILE = [
    (0.0, 18.4, "metal"), (0.7, 19.2, "metal"), (3.9, 19.8, "primary"),          # black-grey skirt
    (3.9, 20.5, "primary"), (5.2, 21.7, "primary"), (9.5, 23.0, "primary"),       # lower body
    (12.3, 24.2, "primary"), (13.2, 26.1, "primary"), (18.2, 26.3, "primary"),    # lower rim
    (18.9, 25.0, "primary"), (20.6, 24.8, "primary"), (24.0, 25.6, "primary"),
    (27.2, 26.4, "primary"),
    (27.2, 26.75, "S"), (34.8, 26.8, "S"), (42.4, 26.75, "primary"),            # hazard band
    (42.4, 26.5, "primary"), (46.0, 26.9, "primary"), (50.0, 27.2, "primary"),
    (54.0, 26.2, "primary"), (58.5, 24.9, "primary"), (62.6, 23.7, "primary"),
    (63.6, 25.8, "primary"), (69.2, 25.9, "primary"), (70.4, 24.2, "primary"),   # upper rim
    (71.0, 22.9, "secondary"),                                                    # lid
    (75.2, 22.4, "secondary"), (77.6, 20.4, "secondary"), (79.2, 18.0, None),
]
STRIPE_BANDS = [i for i, p in enumerate(PROFILE) if p[2] == "S"]
turns, t = [], 0.0
for i, p in enumerate(PROFILE):
    turns.append(t)
    if p[2] == "S":
        t += 0.5          # stripes rise to the right ("/") seen from the front: +1 column over the band


def body_role(b, i):
    r = PROFILE[b][2]
    if r == "S":
        return "accent" if i % 2 == 0 else "dark"
    return r


P.loft([dring(z, a, tu) for (z, a, _), tu in zip(PROFILE, turns)], body_role,
       cap_roles=("metal", "secondary"))


def apothem(z):
    for (z0, a0, _), (z1, a1, _) in zip(PROFILE, PROFILE[1:]):
        if z0 <= z <= z1 and z1 > z0:
            return a0 + (a1 - a0) * (z - z0) / (z1 - z0)
    return PROFILE[-1][1]


def surf_y(x, z):
    """Front surface of the body (y < 0) at (x, z): the 16-gon's facets facing forward."""
    a = apothem(z)
    best = -1e9
    for k in range(N):
        th = math.radians(-90 + k * DA)       # facet normals (the front facet at -90)
        s = math.sin(th)
        if s < -1e-6:
            best = max(best, (a - x * math.cos(th)) / s)
    return best


def hull(pts):
    pts = sorted(set(pts))
    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2 and ((h[-1][0] - h[-2][0]) * (p[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0])) <= 0:
                h.pop()
            h.append(p)
        return h
    lo, up = half(pts), half(pts[::-1])
    return lo[:-1] + up[:-1]


def sheet(dx, dy):
    """Flame crop pixel (2x zoom of sheet x 200.., y 260..) -> cm on the front (x right, z up)."""
    return ((200 + dx / 2 - 293.5) * 0.1141, (864 - (260 + dy / 2)) * 0.1141)


def decal(poly_px, proud, role, side, back=1.5):
    """Convex symbol piece hugging the body front (side -1) or back (+1): front face `proud` cm off the
    surface, back face 1.5 cm inside."""
    poly = hull([sheet(*p) for p in poly_px])
    z0, z1 = min(p[1] for p in poly), max(p[1] for p in poly)
    def ring(off):
        out = []
        for x, z in poly:
            xx = x if side < 0 else -x                  # the back's symbol as seen from behind
            # deepest body point over the piece's height: the body bulges between the outline's corners
            # and would poke through a face that followed it only at the corners
            y = min(surf_y(x, zz) for zz in [z0 + (z1 - z0) * j / 12 for j in range(13)])
            out.append(V(xx, (y - off) * (1 if side < 0 else -1), z))
        return out
    P.loft([ring(proud), ring(-back)], role)


FLAME = [   # convex pieces of the yellow flame (crop px), then the red inner flame
    [(190, 428), (120, 402), (70, 350), (52, 290), (68, 245), (115, 222), (270, 222), (328, 290), (312, 352), (265, 402)],
    [(115, 224), (150, 160), (205, 75), (240, 125), (268, 224)],
    [(62, 262), (95, 185), (125, 232)],
    [(262, 240), (295, 190), (330, 282)],
]
INNER = [(207, 222), (236, 275), (248, 330), (240, 380), (222, 408), (190, 416), (155, 404), (130, 368), (130, 318), (158, 266)]
for side in (-1, 1):
    for k, poly in enumerate(FLAME):
        decal(poly, 0.5 + 0.12 * k, "accent", side, back=1.5 + 0.3 * k)   # no shared points: merge distance
    decal(INNER, 1.1, "primary", side, back=2.8)

# valve on the lid: octagonal base, housing, glowing light on top with a window at the front
P.loft([ngon_z(0, 78.6, 7.6), ngon_z(0, 81.8, 7.6), ngon_z(0, 82.7, 6.7)], "metal")
P.loft([ngon_z(0, 82.4, 5.7), ngon_z(0, 88.3, 5.7)], "metal")
P.loft([ngon_z(0, 84.0, 4.3), ngon_z(0, 88.9, 4.3), ngon_z(0, 89.6, 3.5)], "special")
win = [(-3.4, 84.4), (3.4, 84.4), (3.4, 87.9), (-3.4, 87.9)]
P.loft([[V(x, -4.6, z) for x, z in win], [V(x, -5.4, z) for x, z in win]], "special")
