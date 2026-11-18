# Terminal (Tinfox props sheet 13), game box 0.90 x 1.30 x 0.60 m (X x Z up x Y deep); the screen faces -Y.
# Players walk up to it and use it. Dark grey cabinet: lower body with a grooved panel, slanted light grey
# control desk (buttons, big orange push button), tower with a light grey bezel and a blue screen, side vents,
# black feet. Sheet front view 0.179 cm/px across, 0.168 up; side view 0.156 / 0.168 (front on the left).
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

YF, YB = -27.5, 30.0          # lower body front / back
# lower body with grooved panels on the front and both sides (dark groove = the recess walls)
GROOVE = dict(depth=0.8, bevel=0.5, role="metal", wall="leather")
ZL0, ZL1 = 4.5, 51.0
ZM = (ZL0 + ZL1) / 2
pbox((-41.0, YF, ZL0), (41.0, YB, ZL1), "metal", panels={
    "-y": dict(hu=32.0, hv=17.5, ch=3.0, cv=29.5 - ZM, **GROOVE),
    "+x": dict(hu=20.5, hv=18.0, ch=3.0, cu=3.5, cv=29.0 - ZM, **GROOVE),
    "-x": dict(hu=20.5, hv=18.0, ch=3.0, cu=-3.5, cv=29.0 - ZM, **GROOVE),
})
# wedge under the control desk, and the tower (top chamfered at the front corners and the back)
# upper body in one loft: cheeks flaring to +-45 beside the desk (the box width), the tower above, its top
# chamfered at the front corners and the back; the front follows the desk's underside
P.loft([[V(x, y, z) for x, y in ((-w, yf), (w, yf), (w, YB), (-w, YB))] for z, w, yf in (
    (ZL1 - 0.5, 41.0, YF), (52.5, 45.0, YF), (62.0, 45.0, -6.4), (68.6, 43.0, 5.5), (75.0, 41.0, 5.5),
    (123.0, 41.0, 5.5))] + [[V(x, y, 130.0) for x, y in ((-35, 5.5), (35, 5.5), (35, 22), (-35, 22))]], "metal")
# bezel, dark rim, screen and its pale graphics (ring + three lines)
slab("y", (0, 100.0), 35.0, 23.0, 3.5, 5.5, -0.5, "secondary", bev1=1.0)
slab("y", (0, 100.75), 29.8, 16.0, 2.8, 0.0, -0.8, "leather")
slab("y", (0, 100.75), 29.0, 15.25, 2.4, 0.0, -1.0, "special")
annulus_y(-14.0, 100.75, 10.0, 6.0, -1.25, -0.9, "skin")
for xc, hu, zc in ((12.0, 12.0, 107.75), (11.0, 11.0, 100.75), (8.0, 8.0, 93.75)):
    slab("y", (xc, zc), hu, 1.75, 1.2, -0.9, -1.25, "skin")
for xs in (-29.5, 29.5):
    for zs in (82.0, 118.5):
        bolt("y", -1, (xs, zs), -0.5, 1.3, 0.4, "leather")
# control desk: slanted light grey slab between the cheeks, wider at the front lip (+-42) than at the back (+-38)
SIN, COS = 18.0 / 38.91, 34.5 / 38.91          # slope 27.6 degrees
POLY = [(-30.0, 51.8), (-27.6, 50.2), (5.5, 68.6), (5.5, 75.0), (-29.2, 57.0), (-30.0, 56.2)]


def xh(y):
    return 42.0 - (y + 30.0) / 35.5 * 4.0


P.loft([[V(-xh(y), y, z) for y, z in POLY], [V(xh(y), y, z) for y, z in POLY]], "secondary")


def on_desk(u, s, h):
    """Point on the desk top: u across (x), s up the slope from the front edge, h out of the surface."""
    return V(u, -29.2 + s * COS - h * SIN, 57.0 + s * SIN + h * COS)


def key(uc, sc, hu, hs, ch, h, role):
    pts = [(p.x / K, p.y / K) for p in P.rect((0, 0, 0), hu * K, hs * K, ch * K)]
    P.loft([[on_desk(uc + a, sc + b, hh) for a, b in pts] for hh in (-0.5, h - 0.5)] +
           [[on_desk(uc + a * 0.85, sc + b * 0.85, h) for a, b in pts]], role)


for uc, top, bottom in ((-24.5, "accent", "eyes"), (-12.5, "accent", "eyes"), (0.0, "leather", "leather")):
    key(uc, 29.2, 4.5, 4.9, 1.2, 2.0, top)
    key(uc, 14.6, 4.5, 4.6, 1.2, 2.0, bottom)


def disc(uc, sc, r, h0, h1, role, n=12):
    ring = [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    P.loft([[on_desk(uc + a * k, sc + b * k, hh) for a, b in ring] for hh, k in ((h0, 1), (h1 - 0.6, 1), (h1, 0.88))],
           role)


disc(21.5, 19.5, 8.5, -0.5, 1.0, "leather", n=10)     # black collar
disc(21.5, 19.5, 6.3, 0.5, 3.8, "accent")              # big orange button
# side vents on the tower
for sx in (-1, 1):
    for zc in (108.75, 103.0, 97.0):
        P.loft([[V(sx * x, 18.0 + u, zc + w) for u, w in ((-6.6, 0), (-5.4, -1.6), (5.4, -1.6), (6.6, 0), (5.4, 1.6), (-5.4, 1.6))]
                for x in (40.7, 41.3)], "dark")
# screws: lower front panel and the side panels
for xs in (-27.0, 27.0):
    for zs in (16.0, 41.0):
        bolt("y", -1, (xs, zs), YF, 1.4, 0.5, "leather")
for sx in (-1, 1):
    for ys in (-11.0, 19.0):
        for zs in (15.0, 43.0):
            bolt("x", sx, (ys, zs), sx * 41.0, 1.4, 0.5, "leather")
# feet
for xc in (-27.5, 27.5):
    for yc in (-20.0, 23.0):
        slab("z", (xc, yc), 9.0, 7.0, 0, 4.7, 0.0, "leather", bev1=1.5)
