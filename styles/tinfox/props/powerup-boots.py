# Zoom Boots (Tinfox power-up sheet 24), about 0.40 m tall; pickup. Toe faces -Y (the sheet's FRONT view).
# Measured in cm off the sheet's side view (0.40 m / 470 px); y = the side view's x (toe at -y), z up.
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
# --- Tinfox depot kit helpers (pasted in by run.py after _lib.py / _kit.py; cm, z up from the floor, front = -Y).


def _ring(axis, c, a, hu, hv, ch):
    """Rectangle (half sizes hu, hv; chamfer ch) in the plane axis = a, centred c in the other two axes
    (axis y: c = (x, z); x: (y, z); z: (x, y))."""
    ctr = {"y": (c[0], a, c[1]), "x": (a, c[0], c[1]), "z": (c[0], c[1], a)}[axis]
    return P.rect(V(*ctr), hu * K, hv * K, ch * K, axis=axis)


def slab(axis, c, hu, hv, ch, a0, a1, role, bev0=0.0, bev1=0.0, side=None):
    """Prism along `axis` from a0 to a1 with a (chamfered) rectangular section; bev0 / bev1 bevel the a0 / a1
    end by that much (45 degrees). side = role of the straight walls (default: role)."""
    sg = 1 if a1 > a0 else -1
    rings, roles = [], []
    if bev0:
        rings.append(_ring(axis, c, a0, hu - bev0, hv - bev0, max(0.3, ch - bev0 * 0.6) if ch else 0))
        rings.append(_ring(axis, c, a0 + sg * bev0, hu, hv, ch))
        roles.append(role)
    else:
        rings.append(_ring(axis, c, a0, hu, hv, ch))
    rings.append(_ring(axis, c, a1 - sg * bev1, hu, hv, ch))
    roles.append(side or role)
    if bev1:
        rings.append(_ring(axis, c, a1, hu - bev1, hv - bev1, max(0.3, ch - bev1 * 0.6) if ch else 0))
        roles.append(role)
    return P.loft(rings, roles)


def bx(x0, y0, z0, x1, y1, z1, role, ch=0.0):
    """Axis box in cm (vertical edges chamfered by ch)."""
    return P.box(V(min(x0, x1), min(y0, y1), min(z0, z1)), V(max(x0, x1), max(y0, y1), max(z0, z1)), role,
                 chamfer=ch * K)


def prism_x2(poly, x0, x1, role, side=None):
    """Convex YZ polygon (cm, CCW or CW) extruded along X from x0 to x1."""
    return P.loft([[V(x0, y, z) for y, z in poly], [V(x1, y, z) for y, z in poly]], side or role,
                  cap_roles=(role, role))


def bolt(axis, sgn, c, a, r, h, role, n=6):
    """Small hexagonal bolt head on a face: axis = the face normal axis, sgn its direction, c = centre in the
    other two axes, a = the face's coordinate; stands h proud."""
    a0 = 30 if n == 6 else 45
    pts = [(r * math.cos(math.radians(a0 + 360 / n * i)), r * math.sin(math.radians(a0 + 360 / n * i))) for i in range(n)]

    def ring(t, k):
        out = []
        for u, w in pts:
            u, w = c[0] + u * k, c[1] + w * k
            out.append({"y": V(u, t, w), "x": V(t, u, w), "z": V(u, w, t)}[axis])
        return out
    return P.loft([ring(a - sgn * 0.3, 1), ring(a + sgn * h, 0.75)], role)


def annulus_y(cx, cz, ro, ri, y0, y1, role, n=10):
    """Flat ring (washer) facing -Y between y0 (front) and y1 (back), as one closed shell."""
    bm = P.bm
    def pt(r, i, y):
        t = 2 * math.pi * i / n
        return bm.verts.new(V(cx + r * math.cos(t), y, cz + r * math.sin(t)))
    O0 = [pt(ro, i, y0) for i in range(n)]; I0 = [pt(ri, i, y0) for i in range(n)]
    O1 = [pt(ro, i, y1) for i in range(n)]; I1 = [pt(ri, i, y1) for i in range(n)]
    faces = []
    for i in range(n):
        j = (i + 1) % n
        for q in ((O0[i], O0[j], I0[j], I0[i]), (O1[i], I1[i], I1[j], O1[j]),
                  (O0[i], O1[i], O1[j], O0[j]), (I0[i], I0[j], I1[j], I1[i])):
            faces.append(bm.faces.new(q))
    P.set_role(faces, role)
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return faces
# --- end of depot helpers


def rr(z, yf, yb, sx, r, seg=2, zf=None):
    """Rounded footprint ring at height z (cm) from yf (toe) to yb (heel), half width sx; zf(y) lifts points."""
    sy = (yb - yf) / 2
    pts = P.rrect(V(0, (yf + yb) / 2, z), sx * K, sy * K, min(r, sx - 0.1, sy - 0.1) * K, seg, axis="z")
    if zf:
        for p in pts:
            p.z = zf(p.y / K) * K
    return pts


def heel_up(base):
    return lambda y: base + max(0.0, min(1.0, (y - 3.0) / 8.0)) * 5.5


# sole: dark tread under a white midsole whose top rises at the heel
P.loft([rr(0.0, -20.6, 16.6, 11.1, 6), rr(5.0, -21.6, 17.6, 12.1, 6.5)], "dark")
P.loft([rr(4.6, -22.3, 18.3, 12.7, 6.5), rr(0, -22.3, 18.3, 12.7, 6.5, zf=heel_up(9.6)),
        rr(0, -21.6, 17.6, 12.0, 6, zf=heel_up(10.6))], "secondary")

# yellow upper: toe box with a flat top, then the shaft leaning back, the collar open (dark inside)
up = [(9.0, -21.0, 16.0, 11.0), (15.6, -21.3, 16.2, 11.2), (17.5, -13.2, 15.8, 10.7),
      (25.0, -8.6, 15.5, 10.5), (33.0, -3.6, 13.2, 10.0), (35.6, -2.6, 11.6, 9.0)]
rings = [rr(z, yf, yb, sx, 6) for z, yf, yb, sx in up]
rings += [rr(36.0, -0.8, 10.0, 7.0, 4.5), rr(31.0, -0.6, 9.4, 6.4, 4.0)]
P.loft(rings, ["primary"] * 6 + ["dark"], cap_roles=("primary", "dark"))

# pull tab (orange) at the top of the tongue
P.box(V(-4.0, -5.4, 33.0), V(4.0, -1.4, 39.6), "accent")


def front_y(z):
    for (z0, y0, _, _), (z1, y1, _, _) in zip(up, up[1:]):
        if z0 <= z <= z1:
            return y0 + (y1 - y0) * (z - z0) / (z1 - z0)
    return up[-1][1]


# three arched dark laces across the tongue
for zc in (20.6, 25.0, 29.4):
    yf = front_y(zc)
    path = []
    for x in (-7.4, -2.6, 2.6, 7.4):
        path.append(V(x, yf + 0.3 + max(0.0, abs(x) - 4.4) ** 2 / 9.0, zc + 1.3 * (1 - (x / 7.4) ** 2)))
    prof = [(o * K, s * K) for o, s in ((-0.8, -1.4), (1.6, -1.6), (2.8, -0.7), (2.8, 0.7), (1.6, 1.6), (-0.8, 1.4))]
    P.sweep(path, prof, "dark", normals=[(0, -1, 0)] * len(path))

# white lightning bolt on both sides of the shaft (two overlapping prisms make the Z)
for poly in ([(3.0, 27.6), (7.4, 27.9), (4.2, 19.4), (-0.9, 19.0)], [(0.6, 21.0), (8.4, 21.3), (-0.2, 12.4)]):
    f = prism_x2(poly, 9.9, 11.0, "secondary")
    P.mirror_x(f)

# orange heel patch on the midsole, both sides
f = prism_x2([(9.4, 6.6), (16.2, 6.6), (16.2, 12.6), (12.4, 12.6)], 11.6, 12.95, "accent")
P.mirror_x(f)

# white wings at the heel: two feathers each, turned outwards
for poly in ([(8.4, 31.5), (17.5, 37.6), (21.9, 37.9), (22.1, 35.0), (17.0, 31.0), (9.0, 27.2)],
             [(9.0, 28.0), (17.0, 30.3), (20.6, 29.4), (19.6, 26.0), (13.0, 22.4), (9.0, 22.4)]):
    f = prism_x2(poly, 9.4, 10.9, "secondary")
    piv = V(10.0, 9.0, 0.0)   # turned outward about the root, so the wings read broad from the front too
    P.transform(f, Matrix.Translation(piv) @ Matrix.Rotation(math.radians(-25), 4, "Z") @ Matrix.Translation(-piv))
    P.mirror_x(f)
