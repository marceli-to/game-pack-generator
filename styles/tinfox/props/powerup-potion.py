# Shrink Ray (Tinfox power-up sheet 29), 0.40 m tall; pickup. A round purple bottle (12 sides), a pale lilac neck
# and lip, a brown cork, a raised white downward arrow on the front (-Y) and the back.
# cm, z up from the bottom; measured off the sheet's front view (0.40 m / 631 px).
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

P.loft([ngon_z(0, z, r, 12) for z, r in ((0.0, 6.8), (3.0, 10.9), (9.4, 13.9), (17.0, 13.9), (22.2, 10.9), (24.6, 6.4))],
       "primary")
P.loft([ngon_z(0, z, r, 12) for z, r in ((23.8, 4.8), (29.2, 4.8), (29.2, 6.2), (29.8, 6.8), (32.4, 6.8), (33.0, 6.2),
                                          (33.0, 4.4))], "secondary")
P.loft([ngon_z(0, z, r, 12) for z, r in ((32.4, 4.0), (38.9, 5.1), (40.0, 4.3))], "leather")

# raised white arrow pointing down, front and back, lying on the belly's facets: every vertex sits 0.8 cm off the
# 12-gon surface (pieces split where the facets fold, so each face stays on one facet)
BELLY = ((0.0, 6.8), (3.0, 10.9), (9.4, 13.9), (17.0, 13.9), (22.2, 10.9), (24.6, 6.4))


def surf(x, z):
    """Distance from the axis to the belly's front surface (|y|) at (x, z)."""
    for (z0, r0), (z1, r1) in zip(BELLY, BELLY[1:]):
        if z0 <= z <= z1:
            a = (r0 + (r1 - r0) * (z - z0) / (z1 - z0)) * math.cos(math.radians(15))
            break
    best = None
    for k in (-1, 0, 1):
        nx, ny = math.sin(math.radians(30 * k)), math.cos(math.radians(30 * k))
        d = (a - x * nx) / ny
        best = d if best is None else min(best, d)
    return best


def label(poly, s, out=0.8, back=1.4):
    bm = P.bm
    F = [bm.verts.new(V(x, s * (surf(x, z) + out), z)) for x, z in poly]
    B = [bm.verts.new(V(x, s * (surf(x, z) - back), z)) for x, z in poly]
    n = len(poly)
    faces = [bm.faces.new(F), bm.faces.new(B[::-1])]
    faces += [bm.faces.new((F[i], B[i], B[(i + 1) % n], F[(i + 1) % n])) for i in range(n)]
    P.set_role(faces, "accent")
    bmesh.ops.recalc_face_normals(bm, faces=faces)


for s in (-1, 1):
    label([(-2.7, 14.4), (2.7, 14.4), (2.7, 17.2), (-2.7, 17.2)], s)
    label([(-2.7, 16.9), (2.7, 16.9), (2.7, 21.8), (-2.7, 21.8)], s)
    label([(-3.5, 14.9), (3.5, 14.9), (3.5, 11.3), (0.0, 7.4), (-3.5, 11.3)], s)
    for m in (-1, 1):
        label([(m * 3.35, 14.9), (m * 7.3, 14.9), (m * 3.35, 11.15)], s)
