# Banner (Tinfox Snowfort sheet 38), world prop, the game's box 0.75 x 2.60 (high) x 0.05 m, hangs flat on a wall.
# Origin at the bottom centre (the swallowtail points); the emblem side faces the front (-Y), the back (+Y) is flat.
# Olive cloth with orange borders down both long sides and a swallowtail, dark grey hexagonal end caps at the top
# (no visible pole: the cloth top runs between them), a white round badge with a drone over a mountain peak.
# The sheet is drawn 1.5 m tall; the box asks for 2.6, so the cloth is longer and the badge stays round. cm, z up.
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

W, WI = 27.8, 23.2            # half width of the cloth (outer border edge) and of the olive field
TOP, NOTCH = 256.0, 30.0       # cloth top, swallowtail notch apex
YB = 2.4                       # cloth back (the wall side)


def vz(x):                     # bottom edge of the cloth (the V of the swallowtail) at x
    return NOTCH * (1 - abs(x) / W)


# olive field: one prism with the swallowtail notch (a concave 5-gon front and back; overlapping convex pieces
# shaded each other's corners dark: vertex AO)
outline = [(-WI, TOP), (-WI, vz(WI)), (0.0, NOTCH), (WI, vz(WI)), (WI, TOP)]
F = [P.bm.verts.new(V(x, 0.9, z)) for x, z in outline]
B = [P.bm.verts.new(V(x, YB, z)) for x, z in outline]
fs = [P.bm.faces.new(F[::-1]), P.bm.faces.new(B)]
for i in range(5):
    j = (i + 1) % 5
    fs.append(P.bm.faces.new([F[i], F[j], B[j], B[i]]))
P.set_role(fs, "primary")
bmesh.ops.recalc_face_normals(P.bm, faces=fs)
# orange borders down to the points, 1 mm behind the cloth's front (proud, they would shade its corners dark:
# vertex AO) and tucked 2 mm under its edge
for s in (1, -1):
    pts = [(s * WI - s * 0.2, vz(WI)), (s * W, 0.0), (s * W, TOP), (s * WI - s * 0.2, TOP)]
    prism_y(pts if s > 0 else pts[::-1], 1.0, YB + 0.05, "accent")
# end caps: hexagonal prisms along X, flat at the front and back (2.5 cm), taller than deep
for s in (1, -1):
    ring = lambda x: [V(x, p.y / K, 255.0 + p.z / K) for p in P.ring((0, 0, 0), 2.887 * K, 5.0 * K, n=6, axis="x")]
    P.loft([ring(s * (W - 0.5)), ring(s * 37.5)], "metal")

# badge: white disc, olive disc on it (a white ring shows), mountain peaks and a drone in white
CZ = 186.0
P.loft([ngon_y(0, CZ, 1.0, 23.0), ngon_y(0, CZ, 0.4, 23.0)], "secondary")
P.loft([ngon_y(0, CZ, 0.5, 20.6), ngon_y(0, CZ, 0.15, 20.6)], "primary")
prism_y([(-10, 168.5), (15, 168.5), (2, 183.5)], 0.2, -0.25, "secondary")
prism_y([(-16, 168.5), (-2, 168.5), (-7.6, 177.5)], 0.2, -0.2, "secondary")
prism_y([(-15.5, 196.5), (15.5, 196.5), (15.5, 199.0), (-15.5, 199.0)], 0.2, -0.25, "secondary")
prism_y([(-4.0, 186.5), (4.0, 186.5), (8.0, 197.0), (-8.0, 197.0)], 0.2, -0.25, "secondary")
for s in (1, -1):                # rotor pods under the arm ends
    prism_y([(s * 11.0, 193.0), (s * 15.0, 193.0), (s * 15.0, 197.0), (s * 11.0, 197.0)][::s], 0.2, -0.25, "secondary")

# to the game's box: exactly 0.75 (x) x 0.05 (y) x 2.60 (z), origin at the bottom centre
vs = P.bm.verts
lo = Vector([min(q.co[i] for q in vs) for i in range(3)])
hi = Vector([max(q.co[i] for q in vs) for i in range(3)])
want = (0.75, 0.05, 2.60)
for q in vs:
    for i in range(3):
        q.co[i] = (q.co[i] - (lo[i] if i == 2 else (lo[i] + hi[i]) / 2)) * want[i] / (hi[i] - lo[i])
