# Cargo container (Tinfox props sheet 07), game box 2.90 x 1.41 x 1.55 m (X x Z up x Y deep); cover, flat top.
# Front = a long side (-Y); the doors on the -X end (the sheet's end view; its top view shows the lock bars there).
# Measured off the sheet (long side 0.383 cm/px across, 0.401 cm/px up; end view 0.387 cm/px).
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
# --- Tinfox cover/depot kit helpers (pasted in by run.py after _lib.py; cm, z up from the floor, front = -Y).
# Low budgets (cover <= 400 tris): one closed box mesh whose faces carry recessed chamfered panels, corner caps.

FACES = {  # face: (normal, u, v) with u x v = normal (CCW seen from outside); -y = the front, u = +x, v = +z
    "+x": ((1, 0, 0), (0, 1, 0), (0, 0, 1)), "-x": ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
    "+y": ((0, 1, 0), (-1, 0, 0), (0, 0, 1)), "-y": ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
    "+z": ((0, 0, 1), (1, 0, 0), (0, 1, 0)), "-z": ((0, 0, -1), (1, 0, 0), (0, -1, 0)),
}


def octa(hu, hv, ch, cu=0.0, cv=0.0):
    """Chamfered rectangle in face coordinates, CCW from the bottom edge (8 points)."""
    return [(cu - hu + ch, cv - hv), (cu + hu - ch, cv - hv), (cu + hu, cv - hv + ch), (cu + hu, cv + hv - ch),
            (cu + hu - ch, cv + hv), (cu - hu + ch, cv + hv), (cu - hu, cv + hv - ch), (cu - hu, cv - hv + ch)]


def pbox(lo, hi, role, panels=None, skip=()):
    """Closed box lo..hi (cm) as one shell. panels = {face: dict(hu, hv, ch, cu=0, cv=0, depth, bevel, role,
    wall=role)}: a chamfered panel recessed `depth` into that face, its walls sloping in by `bevel`.
    Faces in `skip` are still closed (plain quads). Returns the faces."""
    bm = P.bm
    lo, hi = Vector(lo) * K, Vector(hi) * K
    c, h = (lo + hi) / 2, (hi - lo) / 2
    corners = {}

    def corner(s):
        if s not in corners:
            corners[s] = bm.verts.new(Vector((c.x + s[0] * h.x, c.y + s[1] * h.y, c.z + s[2] * h.z)))
        return corners[s]
    faces = []

    def face(vs, r):
        f = bm.faces.new(vs)
        P.set_role([f], r)
        faces.append(f)
    for name, (n, u, v) in FACES.items():
        n, u, v = Vector(n), Vector(u), Vector(v)
        hn = abs(n.dot(h)); hu = abs(u.dot(h)); hv = abs(v.dot(h))
        fc = c + n * hn

        def sgn(su, sv):
            p = n * hn + u * (su * hu) + v * (sv * hv)
            return tuple(1 if p[i] > 0 else -1 for i in range(3))
        C = [corner(sgn(-1, -1)), corner(sgn(1, -1)), corner(sgn(1, 1)), corner(sgn(-1, 1))]
        pn = (panels or {}).get(name)
        if not pn:
            face(C, role)
            continue
        d, b = pn["depth"] * K, pn.get("bevel", 0.0)
        cu, cv = pn.get("cu", 0.0), pn.get("cv", 0.0)
        if pn["ch"] <= 0:              # plain rectangle: cheaper (18 tris instead of 34)
            def rq(a, bb):
                return [(cu - a, cv - bb), (cu + a, cv - bb), (cu + a, cv + bb), (cu - a, cv + bb)]
            O = [bm.verts.new(fc + u * (x * K) + v * (y * K)) for x, y in rq(pn["hu"], pn["hv"])]
            I = [bm.verts.new(fc - n * d + u * (x * K) + v * (y * K)) for x, y in rq(pn["hu"] - b, pn["hv"] - b)]
            for k in range(4):
                face([C[k], C[(k + 1) % 4], O[(k + 1) % 4], O[k]], role)
                face([O[k], O[(k + 1) % 4], I[(k + 1) % 4], I[k]], pn.get("wall", role))
            face(I, pn["role"])
            continue
        o_pts = octa(pn["hu"], pn["hv"], pn["ch"], cu, cv)
        i_pts = octa(pn["hu"] - b, pn["hv"] - b, max(0.2, pn["ch"] - b * 0.4), cu, cv)
        O = [bm.verts.new(fc + u * (a * K) + v * (bb * K)) for a, bb in o_pts]
        I = [bm.verts.new(fc - n * d + u * (a * K) + v * (bb * K)) for a, bb in i_pts]
        for k in range(4):            # border: a quad per side, a triangle per corner
            face([C[k], C[(k + 1) % 4], O[2 * k + 1], O[2 * k]], role)
            face([C[(k + 1) % 4], O[(2 * k + 2) % 8], O[2 * k + 1]], role)
        for k in range(8):
            face([O[k], O[(k + 1) % 8], I[(k + 1) % 8], I[k]], pn.get("wall", role))
        for q in ([I[0], I[1], I[2], I[3]], [I[0], I[3], I[4], I[5]], [I[0], I[5], I[6], I[7]]):
            face(q, pn["role"])
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return faces


def cap(sx, sy, sz, bx, by, zf, out, a, hgt, role, bev=1.2, bev_in=True, bev_out=True, wedge=False):
    """Corner cap on the box corner (signs sx, sy, sz); box half sizes bx, by; zf = the box's top (sz > 0) or
    bottom (sz < 0) z. The block stands `out` proud of the faces, reaches `a` along the x/y faces and is `hgt`
    tall from its outer face; edges bevelled by `bev` at the inner end (bev_in) and the outer face (bev_out)."""
    z_out = zf + sz * out
    z_in = z_out - sz * hgt

    def ring(zz, k):
        xo, yo = sx * (bx + out - k), sy * (by + out - k)
        xi, yi = sx * (bx - a + k), sy * (by - a + k)
        if wedge:   # 3 points: the diagonal runs inside the box, the ends show as 45-degree cuts
            return [V(x, y, zz) for x, y in ((sx * (bx - a), sy * (by + out - k)), (sx * (bx + out - k), sy * (by - a)),
                                              (sx * (bx + out - k), sy * (by + out - k)))]
        return [V(x, y, zz) for x, y in ((xi, yi), (xo, yi), (xo, yo), (xi, yo))]
    zs = []
    if bev_in:
        zs += [(z_in, bev), (z_in + sz * bev, 0)]
    else:
        zs += [(z_in, 0)]
    if bev_out:
        zs += [(z_out - sz * bev, 0), (z_out, bev)]
    else:
        zs += [(z_out, 0)]
    return P.loft([ring(zz, k) for zz, k in sorted(zs, key=lambda q: q[0])], role)
# --- end of kit helpers

HX, HY, H = 145.0, 77.5, 141.0
PX, PY = 23.0, 19.0                # corner posts: reach along the long side / the end
WI = 5.0                           # walls set back from the posts' faces


def frustum(lo, hi, axis, sign, shrink, role):
    """Box lo..hi (cm) whose face on the `sign` side of `axis` is shrunk by `shrink` (a bevelled plate)."""
    a = "xyz".index(axis)
    o = [i for i in range(3) if i != a]

    def ring(t, k):
        q = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        pts = []
        for s0, s1 in q:
            p = [0.0, 0.0, 0.0]
            p[a] = t
            p[o[0]] = (lo[o[0]] + hi[o[0]]) / 2 + s0 * ((hi[o[0]] - lo[o[0]]) / 2 - k)
            p[o[1]] = (lo[o[1]] + hi[o[1]]) / 2 + s1 * ((hi[o[1]] - lo[o[1]]) / 2 - k)
            pts.append(V(*p))
        return pts
    back, front = (lo[a], hi[a]) if sign > 0 else (hi[a], lo[a])
    return P.loft([ring(back, 0.0), ring(front, shrink)], role)


# walls + roof: one box set back from the frame
P.box(V(-HX + WI, -HY + WI, 4.0), V(HX - WI, HY - WI, H - 3.0), "primary")
# corner posts, bevelled at the top and the bottom
for sx in (1, -1):
    for sy in (1, -1):
        def pr(z, k):
            x0, x1 = sorted((sx * (HX - PX + k), sx * (HX - k)))
            y0, y1 = sorted((sy * (HY - PY + k), sy * (HY - k)))
            return [V(x0, y0, z), V(x1, y0, z), V(x1, y1, z), V(x0, y1, z)]
        P.loft([pr(0.0, 2.0), pr(3.0, 0.0), pr(H - 3.0, 0.0), pr(H, 2.0)], "metal")
# orange top rails: tall along the long sides, thin across the ends
for sy in (1, -1):
    y0, y1 = sorted((sy * (HY - 18.0), sy * (HY - 0.4)))
    P.box(V(-HX + PX - 1.0, y0, H - 22.0), V(HX - PX + 1.0, y1, H - 0.4), "accent")
for sx in (1, -1):
    x0, x1 = sorted((sx * (HX - 9.0), sx * (HX - 0.6)))
    P.box(V(x0, -HY + PY - 1.0, H - 8.0), V(x1, HY - PY + 1.0, H - 0.6), "accent")
# six raised ribs on each long side
for sy in (1, -1):
    for xc in (-96.0, -57.6, -19.2, 19.2, 57.6, 96.0):
        y0, y1 = sorted((sy * (HY - WI - 1.0), sy * (HY - 1.5)))
        frustum((xc - 10.0, y0, 22.4), (xc + 10.0, y1, 110.6), "y", sy, 2.4, "secondary")
# doors on the -X end: two plates, a black lock bar on each with a handle
for y0, y1 in ((-58.0, -1.0), (1.0, 58.0)):
    frustum((-HX + 2.0, y0, 9.0), (-HX + WI + 1.0, y1, H - 24.0), "x", -1, 2.0, "secondary")
for yb in (-35.0, 15.6):
    P.box(V(-HX, yb - 2.2, 7.0), V(-HX + 3.5, yb + 2.2, H - 10.0), "dark")
    P.box(V(-HX, yb - 5.5, 58.0), V(-HX + 3.2, yb + 5.5, 66.0), "dark")
