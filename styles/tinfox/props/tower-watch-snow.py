# Watchtower (Tinfox Snowfort sheet 37), world prop, the game's box 2.40 x 8.08 (high) x 2.40 m, door side = front (-Y).
# One closed block with straight sides: concrete base with a metal door, olive middle with a narrow window per side,
# a lookout cabin (tapered underside, orange band, dark window band, overhanging roof with snow), a searchlight and an
# antenna on the roof. The sheet draws the tower slim (base 1.7 m of 2.4); the game's collider is the full box, so the
# sections are widened (base 2.2 m) and the sheet's three-section rhythm is kept at ~2.4 m per section.
# cm, z up from the floor.
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


def sq(z, h, ch=0.0, c=(0, 0)):
    return [V(c[0] + p.x / K, c[1] + p.y / K, z) for p in P.rect((0, 0, 0), h * K, h * K, ch * K)]


def block(z0, z1, h, role, bev=0.0, h_top=None, ch=0.0, c=(0, 0)):
    """Square block z0..z1 (half size h; h_top: half size at the top), the top edge bevelled by bev."""
    ht = h if h_top is None else h_top
    rings = [sq(z0, h, ch, c)]
    if bev:
        rings += [sq(z1 - bev, ht, ch, c), sq(z1, ht - bev, max(0.0, ch - bev * 0.6) if ch else 0.0, c)]
    else:
        rings += [sq(z1, ht, ch, c)]
    return P.loft(rings, role)


# Big faces get an extra vertex ring 3 cm from where they meet a ledge: the corner vertices there are shaded by the
# ledge (vertex AO) and would darken the whole face in a gradient.
def column(z0, z1, h, role, d=3.0, c=(0, 0)):
    P.loft([sq(z, h, c=c) for z in (z0, z0 + d, z1 - d, z1)], role)


def window_y(sgn, x, z, hu, hv, face, out=2.5):
    """Window on a +-Y face: a dark frame standing `out` proud, the glass flush with its front (4-point rings)."""
    def r(y, a, b):
        return [V(x + u, y, z + w) for u, w in ((a, -b), (-a, -b), (-a, b), (a, b))]
    P.loft([r(face - sgn * 1.0, hu, hv), r(face + sgn * out, hu, hv), r(face + sgn * out, hu - 3, hv - 3)],
           "dark", cap_roles=("dark", "special"))


def window_x(sgn, y, z, hu, hv, face, out=2.5):
    def r(x, a, b):
        return [V(x, y + u, z + w) for u, w in ((a, -b), (-a, -b), (-a, b), (a, b))]
    P.loft([r(face - sgn * 1.0, hu, hv), r(face + sgn * out, hu, hv), r(face + sgn * out, hu - 3, hv - 3)],
           "dark", cap_roles=("dark", "special"))


# --- base: plinth, concrete body with the door, ledge + snow
block(0, 22, 118, "primary", bev=3)
column(21, 239, 110, "primary")
# door: a metal slab 2.5 cm proud (rings near its ends: vertex AO), orange plate, handle
P.loft([[V(x, y, z) for x, y in ((43, -109), (-43, -109), (-43, -112.5), (43, -112.5))] for z in (21, 24, 213, 216)],
       "metal")
bx(-19, -111, 186, 19, -114, 199, "accent")
bx(26, -111, 100, 31, -115, 132, "dark")
block(238, 250, 116, "primary")
block(250, 262, 115, "leather", bev=3)

# --- middle: olive cladding, a narrow window per side, corner bolts
column(261, 479, 102, "secondary")
for sg in (1, -1):
    window_y(sg, 0, 370, 15, 46, sg * 102)
    window_x(sg, 0, 370, 15, 46, sg * 102)


def stud(axis, sgn, c, a, r=3.2, h=1.8):
    """Three-sided pyramid bolt head (4 tris) on a face."""
    pts = [(r, -r * 0.6), (0, r), (-r, -r * 0.6)]

    def at(t, u, w):
        return {"y": V(u, t, w), "x": V(t, u, w)}[axis]
    P.loft([[at(a - sgn * 0.3, c[0] + u, c[1] + w) for u, w in pts], [at(a + sgn * h, c[0], c[1])]], "dark")


for u in (-84, 84):
    for z in (282, 458):
        stud("y", -1, (u, z), -102)
        stud("x", 1, (u, z), 102)
        stud("y", 1, (u, z), 102)
        stud("x", -1, (u, z), -102)
block(478, 490, 108, "primary")
block(490, 500, 107, "leather", bev=3)

# --- cabin: tapered underside, orange band, window band flaring out (glass with dark corners), roof + snow
P.loft([sq(499, 93, 10), sq(503, 94.5, 10), sq(549, 106, 12)], "primary")
P.loft([sq(547, 108, 12), sq(547, 110, 12), sq(579, 110, 12), sq(579, 108, 12)], "accent")
P.loft([sq(578, 106, 12), sq(586, 108, 13), sq(672, 114, 14), sq(680, 112, 14)],
       lambda b, i: "dark" if b != 1 or i % 2 == 0 else "special")
# mullions on the front (three panes, as on the sheet's front view; the back stays one pane like the sides)
for sy in (-1,):
    for x in (-38, 38):
        y0, y1 = 108 * sy, 114 * sy
        P.loft([[V(x - 3, y0 + 1.2 * sy, 586), V(x + 3, y0 + 1.2 * sy, 586), V(x + 3, y0 - 3 * sy, 586), V(x - 3, y0 - 3 * sy, 586)],
                [V(x - 3, y1 + 1.2 * sy, 672), V(x + 3, y1 + 1.2 * sy, 672), V(x + 3, y1 - 3 * sy, 672), V(x - 3, y1 - 3 * sy, 672)]],
               "dark")
# roof slab (the 2.40 m box), snow on it
P.loft([sq(679, 111, 14), sq(684, 120, 16), sq(708, 120, 16), sq(712, 117, 15)], "primary")
P.loft([sq(711, 116, 15), sq(724, 116, 15), sq(730, 110, 13)], "leather")

# --- searchlight (front left, facing the front): yoke on a post, octagonal housing, orange rim, white lens
SX, SY = -48, -30
bx(SX - 10, SY - 10, 729, SX + 10, SY + 10, 742, "metal")
bx(SX - 24, SY - 5, 741, SX + 24, SY + 5, 754, "metal")
for sx in (-1, 1):
    bx(SX + sx * 21, SY - 5, 754, SX + sx * 25, SY + 5, 778, "metal")
LZ, R = 780, 19
P.loft([ngon_y(SX, LZ, SY + 20, R), ngon_y(SX, LZ, SY - 8, R),
        ngon_y(SX, LZ, SY - 9, R + 4), ngon_y(SX, LZ, SY - 17, R + 4), ngon_y(SX, LZ, SY - 17, R - 2)],
       ["metal", "accent", "accent", "accent"], cap_roles=("metal", "leather"))

# --- antenna (right, a little back): dark base with an orange band, thin mast, orange ball on top
AX, AY = 60, 16
A = (AX, AY)
block(729, 741, 13, "metal", c=A)
block(741, 747, 9, "accent", c=A)
P.loft([sq(746, 2.2, c=A), sq(796, 2.2, c=A)], "dark")
P.loft([[V(AX, AY, 794)], ngon_z(AX, 801, 5.5, n=4, cy=AY), [V(AX, AY, 808)]], "accent")
