# Drone guidance console (Tinfox props sheet 14), the mission target. Game box 1.40 x 1.20 x 0.70 m
# (X x Z up x Y deep); the screens face -Y. Dark grey base with grooved panels, slanted light grey control desk
# across the full width (keys, two levers, big orange push button), housing above with a round radar screen in
# an orange/black hazard frame between two small bar-graph screens, orange corner caps, side vents, antenna with
# an orange light, three black cables from the back into a floor plate. Sheet front view 0.215 cm/px across,
# 0.157 up; side view 0.156 deep (front on the left): the sheet is drawn taller than the box, sizes per axis.
# Y = sheet side-view depth - 35.
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

GROOVE = dict(depth=0.8, bevel=0.5, role="metal", wall="dark")
# --- lower base with grooved panels on the front and both sides
ZB0, ZB1 = 3.6, 33.0
ZBM = (ZB0 + ZB1) / 2
pbox((-65.5, -31.5, ZB0), (65.5, 20.0, ZB1), "metal", panels={
    "-y": dict(hu=52.0, hv=10.5, ch=3.0, cv=19.5 - ZBM, **GROOVE),
    "+x": dict(hu=13.5, hv=10.5, ch=0, cu=-0.5, cv=19.5 - ZBM, **GROOVE),
    "-x": dict(hu=13.5, hv=10.5, ch=0, cu=0.5, cv=19.5 - ZBM, **GROOVE),
})
# behind the desk: the base rises to the housing
prism_x2([(-31.5, 32.5), (20.0, 32.5), (20.0, 55.5), (0.0, 55.5)], -65.5, 65.5, "metal")
# --- housing (its bottom at the desk's back edge, overhanging the desk by 10 cm): wings across the full width, the raised centre (screen) 1 cm proud; backs chamfered at the top
def hpoly(hw, z0, ztop, ch):
    return [(-hw, z0), (hw, z0), (hw, ztop - ch), (hw - ch, ztop), (-hw + ch, ztop), (-hw, ztop - ch)]


def housing(hw, ztop, ch, yf, role):
    rings = [[V(x, y, z) for x, z in hpoly(hw, 55.5, zt, ch)] for y, zt in ((yf, ztop), (18.0, ztop), (21.5, ztop - 3.5))]
    return P.loft(rings, role)


housing(63.0, 100.0, 7.0, -10.0, "metal")
housing(31.0, 103.5, 4.0, -11.0, "metal")
# orange caps: the wings' top outer corners (front half) and the lower outer corners above the desk
caps = prism_y([(50.0, 96.0), (63.6, 86.0), (63.6, 93.3), (56.3, 100.6), (50.0, 100.6)], -10.6, 7.0, "accent")
caps += prism_y([(57.0, 55.0), (63.6, 55.0), (63.6, 60.5), (60.6, 63.5), (57.0, 63.5)], -10.6, 0.0, "accent")
P.mirror_x(caps)
# side vents on the wings (dark slots)
for sx in (-1, 1):
    for zc in (76.0, 81.0, 86.0):
        P.loft([[V(sx * x, 7.5 + u, zc + w) for u, w in ((-6.5, -1.4), (6.5, -1.4), (6.5, 1.4), (-6.5, 1.4))]
                for x in (62.7, 63.3)], "dark")
# --- radar screen: orange frame, black stripes, dark backing, blue screen with pale rings and sweep line
ZS = 79.5
slab("y", (0, ZS), 29.0, 20.5, 7.0, -11.0, -12.5, "accent", bev1=0.6)
slab("y", (0, ZS), 21.5, 16.0, 6.0, -12.0, -13.0, "leather")


def stripe(poly):
    P.loft([[V(x, y, z) for x, z in poly] for y in (-12.3, -12.75)], "leather")


for x0 in (-17.0, -7.0, 3.0):                      # top and bottom bands, slanting /
    stripe([(x0, 95.6), (x0 + 3.0, 95.6), (x0 + 6.6, 99.3), (x0 + 3.6, 99.3)])
    stripe([(x0 - 1.0, 59.7), (x0 + 2.0, 59.7), (x0 + 5.6, 63.4), (x0 + 2.6, 63.4)])
for sx in (-1, 1):                                  # side bands
    for z0 in (68.0, 78.0):
        stripe([(sx * 21.6, z0), (sx * 21.6, z0 + 3.0), (sx * 28.3, z0 + 9.0), (sx * 28.3, z0 + 6.0)])
P.loft([ngon_y(0, ZS, y, 15.5, n=16) for y in (-12.8, -13.5)], "special")
annulus_y(0, ZS, 11.0, 9.6, -13.9, -13.3, "skin", n=10)
annulus_y(0, ZS, 5.6, 4.4, -13.9, -13.3, "skin", n=8)
P.loft([ngon_y(0, ZS, y, 2.0, n=6) for y in (-13.3, -13.9)], "skin")
# sweep line, from the centre up and to the right
P.loft([[V(x, y, z) for x, z in ((1.0, ZS + 0.3), (1.6, ZS + 1.2), (9.8, ZS + 11.5), (9.2, ZS + 10.6))]
        for y in (-13.3, -13.9)], "skin")
# --- small screens with bar graphs, grey bezels
for sx in (-1, 1):
    cx = sx * 46.5
    slab("y", (cx, 72.0), 11.5, 9.0, 2.0, -10.0, -11.6, "secondary")
    slab("y", (cx, 72.0), 8.5, 6.3, 1.5, -11.3, -12.0, "special")
    for dx, h in ((-3.6, 4.2), (0.0, 7.0), (3.6, 3.6)):
        slab("y", (cx + dx, 67.4 + h / 2), 1.3, h / 2, 0, -11.8, -12.3, "skin")
# --- control desk: slanted light grey slab, +-70 at the front lip, +-63 at the back
POLY = [(-33.0, 32.3), (-35.0, 34.3), (-35.0, 38.5), (0.0, 55.5), (0.0, 51.0), (-31.5, 32.3)]
SIN, COS = 17.0 / 38.91, 35.0 / 38.91          # slope 25.9 degrees


def xh(y):
    return 70.0 - (y + 35.0) / 35.0 * 7.0


P.loft([[V(-xh(y), y, z) for y, z in POLY], [V(xh(y), y, z) for y, z in POLY]], "secondary")


def on_desk(u, s, h):
    """Point on the desk top: u across (x), s up the slope from the front edge, h out of the surface."""
    return V(u, -35.0 + s * COS - h * SIN, 38.5 + s * SIN + h * COS)


def key(uc, sc, hu, hs, h, role, top=0.85):
    pts = [(-hu, -hs), (hu, -hs), (hu, hs), (-hu, hs)]
    P.loft([[on_desk(uc + a, sc + b, -0.5) for a, b in pts], [on_desk(uc + a * top, sc + b * top, h) for a, b in pts]],
           role)


for uc in (-52.0, -41.0, -30.0):
    key(uc, 23.0, 4.4, 4.6, 2.0, "accent")
    key(uc, 10.5, 4.4, 4.6, 2.0, "eyes")
key(31.0, 10.5, 4.0, 4.6, 2.0, "leather")
for uc in (42.0, 53.0):
    key(uc, 10.5, 4.4, 4.6, 2.0, "eyes")
# levers: black base with a dark slot, shaft leaning forward, orange handle across
for uc in (-9.0, 9.0):
    key(uc, 13.0, 5.2, 7.5, 1.6, "leather", top=0.92)
    key(uc, 13.0, 1.4, 4.8, 1.7, "dark", top=1.0)
    b = on_desk(uc, 14.5, 1.0)
    t = V(uc, -28.5, 55.0)
    sq = ((-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0))
    P.loft([[b + V(a, c, 0) for a, c in sq], [t + V(a, c, 0) for a, c in sq]], "leather")
    slab("x", (-28.5, 56.0), 1.9, 1.9, 0.6, uc - 6.5, uc + 6.5, "accent")


def disc(uc, sc, r, h0, h1, role, n=10, top=0.88, rings=3):
    ring = [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    hs = ((h0, 1), (h1, top)) if rings == 2 else ((h0, 1), (h1 - 0.6, 1), (h1, top))
    P.loft([[on_desk(uc + a * k, sc + b * k, hh) for a, b in ring] for hh, k in hs], role)


disc(41.0, 24.0, 7.2, -0.5, 1.0, "leather", n=8, top=0.95, rings=2)   # black collar
disc(41.0, 24.0, 5.4, 0.5, 4.2, "accent", n=8)                      # big orange button
# --- antenna with the orange light (Y 3..13 on the side view)
bx(-6.5, 3.0, 103.0, 6.5, 13.0, 106.5, "leather", ch=1.0)
P.loft([ngon_z(0, z, r, n=6, cy=8.0) for z, r in ((106.0, 1.8), (112.5, 1.8))], "leather")
P.loft([ngon_z(0, z, r, n=8, cy=8.0) for z, r in ((114.0, 3.6), (117.6, 3.6), (120.0, 2.0))], "accent")
# --- feet
for xc in (-48.5, 48.5):
    for yc, hy in ((-21.25, 6.25), (11.0, 6.0)):
        slab("z", (xc, yc), 9.0, hy, 0, ZB0 + 0.4, 0.0, "leather")
# --- cables: three black tubes out of the back, arcing down into a floor plate (Y 21..35)


def tube_path(path, r, role, n=6):
    pts = [V(*p) for p in path]
    xa = Vector((1, 0, 0))
    rings = []
    for i, c in enumerate(pts):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, len(pts) - 1)]
        t = (b - a).normalized()
        nrm = t.cross(xa).normalized()
        rings.append([c + (xa * math.cos(2 * math.pi * k / n) + nrm * math.sin(2 * math.pi * k / n)) * (r * K)
                      for k in range(n)])
    return P.loft(rings, role)


for xc in (24.0, 30.5, 37.0):
    tube_path([(xc, 18.0, 38.0), (xc, 27.0, 37.5), (xc, 31.0, 31.0), (xc, 31.0, 2.0)], 2.3, "leather", n=5)
bx(16.5, 21.0, 0.0, 44.5, 35.0, 3.0, "metal")
# (screws dropped: the 1,500 tris budget)
