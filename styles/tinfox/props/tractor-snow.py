# Snow tractor (Tinfox props sheet 39), game box 2.60 x 1.80 x 1.80 m (X long x Z up x Y wide); full cover.
# Blade at the +X end (the sheet's front view), the sheet's side view lies along X. Modelled in cm at the sheet's
# proportions (side view 0.378 cm/px: 2.60 long, ~1.95 high), then scaled per axis to the game's box.
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


def plate_y(poly, y0, y1, role):
    """Convex XZ polygon (cm) extruded across Y from y0 to y1, on both sides (+y and -y)."""
    prism_y(poly, y0, y1, role)
    prism_y(poly, -y0, -y1, role)


# tracks: rounded side profile, dark grey; road wheels on the outside
for s in (1, -1):
    ring0 = [V(p.x / K, s * 56.0, p.z / K) for p in P.rrect((-32.5 * K, 0, 34.0 * K), 95.5 * K, 34.0 * K, 22 * K, 2, axis="y")]
    ring1 = [V(p.x / K, s * 87.0, p.z / K) for p in P.rrect((-32.5 * K, 0, 34.0 * K), 95.5 * K, 34.0 * K, 22 * K, 2, axis="y")]
    P.loft([ring0, ring1], "secondary")
    for wx in (36.0, -8.0, -52.0, -96.0):
        P.loft([ngon_y(wx, 30.0, s * 86.0, 19.0), ngon_y(wx, 30.0, s * 90.0, 17.5)], "metal")
bx(-120.0, -56.0, 12.0, 60.0, 56.0, 64.0, "dark")                 # hull between the tracks

# body: light grey, bevelled top edge; hood front at X +70
P.loft([zring(-24.0, 60.0, 102.0, 58.0, 8.0), zring(-24.0, 94.0, 102.0, 58.0, 8.0),
        zring(-24.0, 101.0, 98.0, 54.0, 6.0)], "primary")
# cab: windscreen leaning back, roof with snow
P.loft([zring(-57.0, 100.0, 65.0, 53.0, 5.0), zring(-63.5, 155.0, 58.5, 52.0, 5.0)], "primary")
P.loft([zring(-63.0, 154.0, 61.0, 55.0, 4.0), zring(-63.0, 160.0, 61.0, 55.0, 4.0),
        zring(-63.0, 164.0, 57.0, 51.0, 3.0)], "hair")
# windows: flush glass plates
def xf(z):                                                         # the cab front at height z
    return 8.0 - 13.0 * (z - 100.0) / 55.0
prism_y([(xf(108) - 1.0, 108), (xf(108) + 1.2, 108), (xf(150) + 1.2, 150), (xf(150) - 1.0, 150)], -44.0, 44.0, "special")
bx(-123.5, -42.0, 110.0, -120.0, 42.0, 150.0, "special")         # rear window
plate_y([(-50.0, 110.0), (xf(110) - 4.0, 110.0), (xf(150) - 4.0, 150.0), (-50.0, 150.0)], 51.0, 54.0, "special")
plate_y([(-114.0, 110.0), (-58.0, 110.0), (-58.0, 150.0), (-114.0, 150.0)], 51.0, 54.0, "special")
# mirrors on arms at the cab front corners
for s in (1, -1):
    bx(-2.0, s * 50.0, 120.0, 2.0, s * 62.0, 124.0, "dark")
    bx(-3.0, s * 61.0, 110.0, 3.0, s * 70.0, 136.0, "secondary")
# front: grille, headlights, orange corner markers
bx(76.0, -22.0, 64.0, 81.0, 22.0, 96.0, "dark")
for s in (1, -1):
    P.loft([[V(76.0, s * 37.0 + p.y / K, 82.0 + p.z / K) for p in P.ring((0, 0, 0), 10.0 * K, n=8, axis="x")],
            [V(82.0, s * 37.0 + p.y / K, 82.0 + p.z / K) for p in P.ring((0, 0, 0), 9.0 * K, n=8, axis="x")]], "skin")
    bx(70.0, s * 50.0, 80.0, 80.0, s * 60.0, 90.0, "accent")
    bx(-131.0, s * 46.0, 66.0, -122.0, s * 60.0, 98.0, "accent")   # rear corner bumpers
# orange stripes: two diagonal ones on the hood sides, one long one under the rear side window
for s in (1, -1):
    for x0 in (30.0, 46.0):
        prism_y([(x0, 66.0), (x0 + 8.0, 66.0), (x0 + 24.0, 94.0), (x0 + 16.0, 94.0)], s * 57.0, s * 59.5, "accent")
    prism_y([(-112.0, 80.0), (-56.0, 80.0), (-56.0, 90.0), (-112.0, 90.0)], s * 57.0, s * 59.5, "accent")
# roof rack, beacons, olive box
for s in (1, -1):
    bx(-118.0, s * 40.0, 163.0, -10.0, s * 44.0, 174.0, "dark")      # rails standing on the roof snow
for xx in (-104.0, -24.0):
    bx(xx - 2.0, -48.0, 170.5, xx + 2.0, 48.0, 173.5, "dark")
for xx in (-116.0, -12.0):
    for s in (1, -1):
        bx(xx - 4.0, s * 44.0, 172.0, xx + 4.0, s * 52.0, 180.0, "accent")
P.loft([zring(-64.0, 174.0, 30.0, 27.0, 4.0), zring(-64.0, 190.0, 30.0, 27.0, 4.0),
        zring(-64.0, 194.0, 27.0, 24.0, 3.0)], "leather")
# push arms and the blade (concave mouldboard facing +X, three convex pieces) with two ribs
for s in (1, -1):
    bx(58.0, s * 30.0, 20.0, 112.0, s * 40.0, 34.0, "dark")
for poly in ([(108.0, 0.0), (130.0, 0.0), (130.0, 5.0), (121.0, 24.0), (110.0, 24.0)],
             [(110.5, 23.0), (121.3, 23.0), (118.8, 49.0), (110.5, 49.0)],
             [(110.0, 48.0), (119.0, 48.0), (130.0, 67.0), (128.0, 72.0), (112.0, 72.0)]):
    prism_y(poly, -90.0, 90.0, "accent")
for s in (1, -1):
    bx(117.0, s * 27.0, 8.0, 123.0, s * 33.0, 64.0, "accent")

# to the game's box: exactly 2.60 (x) x 1.80 (y) x 1.80 (z) m, origin on the floor in the middle
vs = P.bm.verts
lo = Vector([min(v.co[i] for v in vs) for i in range(3)])
hi = Vector([max(v.co[i] for v in vs) for i in range(3)])
want = (2.60, 1.80, 1.80)
for v in vs:
    for i in range(3):
        v.co[i] = (v.co[i] - (lo[i] if i == 2 else (lo[i] + hi[i]) / 2)) * want[i] / (hi[i] - lo[i])
