# Range target (Tinfox prop sheet 04): round board on a post. Front faces -Y. Units cm (V), z up from the floor.
# Main mesh = base + post + saddle; piece "board" (board, clamp, hinge barrel) is a child of the anchor `hinge`
# on the board's bottom back edge, so the game tips it backwards (+Y) about X without crossing the post: every
# board vertex lies at y <= HY and z >= HZ except the barrel, which is round about the hinge axis.
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

N = 16
HZ, HY = 90.0, 3.0          # hinge: board bottom edge (z), board back face (y)
YF, YM = -7.0, -3.0         # board front face, navy front plate / cream back plate
A = 45.0                    # board apothem (0.90 m across flats)
C = HZ + A                  # board centre height


def ring_y(y, a, cz=C):
    """16-gon in the plane y (flat top and bottom) with apothem a: ring shares are measured to the flats, so the
    scoring circle (share x 0.45 m) lies inside each coloured ring."""
    return ngon_y(0, cz, y, a / math.cos(math.pi / N), n=N)


def rect_z(z, h, ch):
    return zring(0, z, h, h, ch)


# --- base: black slab, grey sloped plinth with orange corner marks, top plate
P.loft([rect_z(0, 23.0, 2.0), rect_z(0.6, 23.5, 2.2), rect_z(5.5, 23.5, 2.2)], "dark")
def ph(z):   # plinth half width at z
    return 23.0 - (z - 6.5) * 4.5 / 8.0
def pc(z):
    return 3.0 - (z - 6.5) * 0.5 / 8.0
P.loft([rect_z(5.3, 23.0, 3.0), rect_z(6.5, 23.0, 3.0), rect_z(14.5, ph(14.5), pc(14.5))], "primary")
P.loft([rect_z(14.3, 11.0, 1.0), rect_z(15.0, 11.0, 1.0), rect_z(15.8, 10.4, 0.8)], "primary")
for sx in (1, -1):
    for sy in (1, -1):
        rows = []
        for z in (8.3, 14.2):
            h, c = ph(z) + 0.25, pc(z)
            pts = [(13.0, h), (h - c, h), (h, h - c), (h, 13.0)]
            rows.append([V(sx * a, sy * b, z) for a, b in pts])
        if sx * sy < 0:
            rows = [r[::-1] for r in rows]
        P.shell(rows, -0.005, "leather")

# --- post with two diagonal orange stripes (each face on its own, rising to the right as seen from outside)
P.loft([rect_z(15.0, 6.5, 0.8), rect_z(80.5, 6.5, 0.8)], "primary")
P.loft([rect_z(80.0, 7.5, 1.0), rect_z(84.0, 7.5, 1.0)], "hair")
faces = [lambda u, z, o: V(u, -o, z), lambda u, z, o: V(o, u, z), lambda u, z, o: V(-u, o, z), lambda u, z, o: V(-o, -u, z)]
for zl in (35.5, 49.5):                      # lower edge at the left end of each face; 10.5 tall, rises 7 / 13
    for f in faces:
        rows = [[f(u, zl + dz + (u + 6.5) * 7 / 13, 6.6) for u in (-5.7, 0.0, 5.7)] for dz in (0.0, 10.5)]
        P.shell(rows, -0.004, "leather")
# saddle under the hinge (stays below the board's bottom edge)
prism_y([(-12, 84), (12, 84), (13, 85), (13, 88.5), (12.5, 89.2), (-12.5, 89.2), (-13, 88.5), (-13, 85)],
        -7.0, 7.0, "hair", inset=0.04)

# --- board piece
P.anchor("hinge", V(0, HY, HZ))
P.piece("board", parent="hinge")
# cream back plate
P.loft([ring_y(YM - 0.5, A), ring_y(HY - 1.0, A), ring_y(HY, A - 1.0)], "secondary")
# front plate: navy side + chamfer, then the rings flush on the front face (apothem shares of the diameter)
shares = [0.90, 0.68, 0.48, 0.28]
rings = [ring_y(YM, A), ring_y(YF + 1.0, A), ring_y(YF, A - 1.0)] + [ring_y(YF, s * A) for s in shares] + \
        [[V(0, YF, C)]]
P.loft(rings, ["special", "special", "special", "secondary", "accent", "secondary", "accent"],
       cap_roles=("special", "accent"))
P.anchor("board_centre", V(0, YF, C), piece="board")
# clamp over the board's bottom edge (front of it 1.5 cm proud of the rings)
prism_y([(-13, HZ), (13, HZ), (13, 103), (10, 106), (-10, 106), (-13, 103)], -8.5, HY - 1.0, "primary", inset=0.04)
P.dome(V(0, -8.5, 97.5), (0, -1, 0), 0.035, 0.012, n=8, role="metal")
# hinge barrel round the axis + pin caps
P.loft([[V(x, HY + p.y / K, HZ + p.z / K) for p in P.ring((0, 0, 0), 2.8 * K, n=8, axis="x")] for x in (-13.5, 13.5)],
       "hair")
for s in (1, -1):
    P.loft([[V(x, HY + p.y / K, HZ + p.z / K) for p in P.ring((0, 0, 0), 2.2 * K, n=8, axis="x")]
            for x in (s * 13.0, s * 14.5)], "metal")
