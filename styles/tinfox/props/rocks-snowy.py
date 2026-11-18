# Snowy rocks (Tinfox props sheet 35), game box 0.70 x 0.40 x 0.60 m (X x Z up x Y deep), ground decoration.
# One big faceted granite rock at the back, two smaller lighter ones leaning on it in front, snow on their tops,
# three tufts of straw-yellow grass. Front faces -Y. Measured off the sheet's front and top views (~0.11 cm/px).
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

N = 8
JIT = [1.0, 0.9, 1.06, 0.94, 1.08, 0.88, 1.02, 0.95]      # irregular facets, fixed


def rring(cx, cy, z, rx, ry, k, rot=0.0, wave=0.0, sh=0):
    out = []
    for i in range(N):
        a = math.radians(-90 + 180.0 / N + rot + i * 360.0 / N)
        j = JIT[(i + sh) % N]
        out.append(V(cx + rx * k * j * math.cos(a), cy + ry * k * j * math.sin(a), z + (wave if i % 2 else -wave)))
    return out


def rock(cx, cy, rx, ry, h, role, rot, sh, lean=(0.0, 0.0)):
    """Faceted rock: wide foot, bulge, scalloped snow line, snow shoulder and a flattish snow top."""
    lx, ly = lean
    prof = [(0.0, 0.88, 0), (0.3, 1.0, 0), (0.7, 0.8, 0.07 * h), (0.88, 0.55, 0), (1.0, 0.22, 0)]
    rings = [rring(cx + lx * t, cy + ly * t, h * t, rx, ry, k, rot, w, sh) for t, k, w in prof]
    P.loft(rings, [role, role, "secondary", "secondary"])


rock(-2, 6, 25, 17, 42, "primary", 8, 0, lean=(2, 3))         # big rock, back
rock(-20, -12, 14, 13, 21, "metal", 20, 3, lean=(2, 3))       # small rocks, front left / right
rock(17, -11, 13, 12, 23, "metal", -10, 5, lean=(-2, 3))


def tuft(x, y, blades):
    """Grass tuft: chunky three-sided blades fanning out from one point (angle from vertical, heading, length),
    each with its own foot and a blunt tip."""
    for tilt, head, ln in blades:
        t, hd = math.radians(tilt), math.radians(head)
        d = Vector((math.sin(t) * math.cos(hd), math.sin(t) * math.sin(hd), math.cos(t)))
        fx, fy = x + 1.5 * math.cos(hd), y + 1.5 * math.sin(hd)
        tip = V(fx, fy, 0) + d * ln * K

        def tri(c, r):
            return [c + Vector((r * math.cos(hd + math.radians(a)), r * math.sin(hd + math.radians(a)), 0)) * K
                    for a in (90, 210, 330)]
        P.loft([tri(V(fx, fy, 0), 2.0), tri(tip, 1.3)], "accent")


tuft(-24, 9, [(34, 185, 15), (12, 150, 16), (30, 120, 13)])     # back left, beside the big rock
tuft(-2, -19, [(30, 200, 13), (4, 270, 15), (30, -20, 13)])     # front, between the small rocks

# to the game's box: exactly 0.70 (x) x 0.60 (y) x 0.40 (z) m
vs = P.bm.verts
lo = Vector([min(v.co[i] for v in vs) for i in range(3)])
hi = Vector([max(v.co[i] for v in vs) for i in range(3)])
want = (0.70, 0.60, 0.40)
for v in vs:
    for i in range(3):
        v.co[i] = (v.co[i] - (lo[i] if i == 2 else (lo[i] + hi[i]) / 2)) * want[i] / (hi[i] - lo[i])
