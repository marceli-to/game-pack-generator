# Double Blast (Tinfox power-up sheet 26), 0.40 m tall; pickup. A red 8-point burst with chamfered faces, a yellow
# star plate and a raised white "x2" on the front (-Y) and the back (+Y, mirrored so it reads from behind).
# cm, centre at z 20; measured off the sheet's front view (0.40 m / 530 px).
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

ZC = 20.0


def outline(r_tip, r_val, n=8, tip_w=7.0):
    """Burst outline (x, z): n points pointing up, each tip cut flat over tip_w degrees, valleys between."""
    pts = []
    for i in range(n):
        a = 90 + 360.0 * i / n
        for d in (-tip_w, tip_w):
            t = math.radians(a + d)
            pts.append((r_tip * math.cos(t), ZC + r_tip * math.sin(t)))
        t = math.radians(a + 180.0 / n)
        pts.append((r_val * math.cos(t), ZC + r_val * math.sin(t)))
    return pts


def plate(rings, role, cap_role=None):
    """Loft of star-shaped rings [(y, scale, pts)], capped with centre fans (the outline is concave)."""
    bm = P.bm
    vr = []
    for y, s, pts in rings:
        vr.append([bm.verts.new(V(x * s, y, ZC + (z - ZC) * s)) for x, z in pts])
    faces = []
    m = len(vr[0])
    for A, B in zip(vr, vr[1:]):
        for i in range(m):
            j = (i + 1) % m
            faces.append(bm.faces.new((A[i], A[j], B[j], B[i])))
    P.set_role(faces, role)
    caps = []
    for ring, (y, _, _) in ((vr[0], rings[0]), (vr[-1], rings[-1])):
        c = bm.verts.new(V(0, y, ZC))
        for i in range(m):
            caps.append(bm.faces.new((c, ring[i], ring[(i + 1) % m])))
    P.set_role(caps, cap_role or role)
    faces += caps
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return faces


body = outline(20.0, 14.3, tip_w=9.5)
plate([(-4.8, 0.9, body), (-3.4, 1.0, body), (3.4, 1.0, body), (4.8, 0.9, body)], "primary")
star = outline(15.6, 8.4, tip_w=3.0)
for s in (1, -1):
    plate([(s * 4.4, 1.0, star), (s * 5.6, 1.0, star)], "accent")


def x2(s):
    """White "x2" standing 2.2 cm off the yellow plate on side s (-1 front, +1 back); x mirrored on the back."""
    y0, y1 = s * 5.2, s * 7.8
    m = -s       # front: as drawn; back: x mirrored so it reads from behind

    def pr(poly):
        prism_y([(m * x, ZC + z) for x, z in poly], y0, y1, "secondary")
    w = 1.8      # half stroke
    for (xa, za), (xb, zb) in (((-9.6, -5.6), (-1.7, 4.0)), ((-9.6, 4.0), (-1.7, -5.6))):
        pr([(xa - w, za), (xa + w, za), (xb + w, zb), (xb - w, zb)] if za < zb else
           [(xa - w, za), (xb - w, zb), (xb + w, zb), (xa + w, za)])
    pr([(0.2, -5.6), (9.9, -5.6), (9.9, -2.2), (0.2, -2.2)])
    pr([(0.2, -3.4), (4.4, -3.4), (9.4, 2.4), (6.0, 3.8)])
    bowl = [(0.9, 3.2), (2.0, 6.0), (5.0, 7.3), (7.9, 6.1), (8.9, 2.9)]
    path = [V(m * x, (y0 + y1) / 2, ZC + z) for x, z in bowl]
    h = (y1 - y0) / 2
    P.sweep(path, [(-h * K, -w * K), (h * K, -w * K), (h * K, w * K), (-h * K, w * K)], "secondary",
            normals=[(0, s, 0)] * len(path))


x2(-1)
x2(1)
