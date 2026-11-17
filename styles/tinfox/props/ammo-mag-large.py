# SMG magazine (Tinfox sheet 06, bottom row), 0.24 m tall, slightly curved, standing on the floor. Pickup.
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

H0, H1 = 2.4, 20.6


def cx(z):
    """Centre line: leans forward 1.5 cm towards the top and bows back 1.6 cm in the middle (as drawn)."""
    t = (z - H0) / (H1 - H0)
    return 1.5 * t - 1.6 * math.sin(math.pi * t)


prism_y([(-4.9, 0.4), (-4.5, 0.0), (4.5, 0.0), (4.9, 0.4), (4.9, 2.6), (-4.9, 2.6)], -3.0, 3.0, "secondary",
        inset=0.05)
zs = [H0 + (H1 - H0) * i / 8 for i in range(9)]
P.loft([zring(cx(z), z, 4.4, 2.6, 0.6) for z in zs], "primary")
P.loft([zring(cx(H1) + 0.2, 20.4, 4.3, 2.45, 0.5), zring(cx(H1) + 0.2, 22.5, 4.3, 2.45, 0.5),
        zring(cx(H1) + 0.2, 22.8, 4.0, 2.2, 0.4)], "accent")
P.loft([zring(cx(H1) + 2.3, 22.6, 1.9, 2.2, 0.4), zring(cx(H1) + 2.3, 23.9, 1.9, 2.2, 0.4),
        zring(cx(H1) + 2.3, 24.2, 1.65, 1.95, 0.3)], "accent")
for zc in (6.0, 9.4, 12.8, 16.2):                                                     # grip notches, back edge
    x = cx(zc) - 4.4
    prism_y([(x - 0.7, zc - 0.7), (x + 0.6, zc - 0.7), (x + 0.6, zc + 0.7), (x - 0.7, zc + 0.7)], -2.3, 2.3, "primary")
# curved window on both broad sides: frame strip and glass strip swept along the centre line
wz = [4.6 + (18.6 - 4.6) * i / 7 for i in range(8)]
for s in (1, -1):
    path = [V(cx(z) + 0.6, 2.6 * s, z) for z in wz]
    P.sweep(path, [(-0.004, -0.0135), (0.0025, -0.0135), (0.0025, 0.0135), (-0.004, 0.0135)], "dark",
            normals=[(0, s, 0)] * len(path))
    path = [V(cx(z) + 0.6, 2.6 * s, z) for z in [5.1 + (18.1 - 5.1) * i / 7 for i in range(8)]]
    P.sweep(path, [(-0.002, -0.009), (0.003, -0.009), (0.003, 0.009), (-0.002, 0.009)], "special",
            normals=[(0, s, 0)] * len(path))
# window on the front (narrow) face, following the curve
fz = [5.6 + (17.6 - 5.6) * i / 6 for i in range(7)]
path = [V(cx(z) + 4.4, 0, z) for z in fz]
P.sweep(path, [(-0.004, -0.012), (0.0025, -0.012), (0.0025, 0.012), (-0.004, 0.012)], "dark", normals=[(1, 0, 0)] * len(path))
path = [V(cx(z) + 4.4, 0, z) for z in [6.1 + (17.1 - 6.1) * i / 6 for i in range(7)]]
P.sweep(path, [(-0.002, -0.0075), (0.003, -0.0075), (0.003, 0.0075), (-0.002, 0.0075)], "special", normals=[(1, 0, 0)] * len(path))
