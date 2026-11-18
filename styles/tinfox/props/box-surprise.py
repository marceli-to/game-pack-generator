# Surprise box (Tinfox prop sheet 02): 0.80 m purple cube, gold corner caps, gold octagon frames with recessed
# dark panels and raised white question marks on four sides and the top, glowing seam under the lid.
# Front faces -Y. Measured off the sheet at 0.197 cm/px (front view 406 px = 80 cm).
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

B = 37.5          # body half size
LID0, LID1 = 64.4, 81.2
FZ = 35.3         # frame centre height on the sides


def rect_ring(z, h, c):
    return zring(0, z, h, h, c)


# body: slightly chamfered vertical edges, small bevel at the bottom
P.loft([rect_ring(1.0, B - 1.0, 2.0), rect_ring(2.0, B, 2.5), rect_ring(LID0 - 3.0, B, 2.5)], "primary")
# glowing seam under the lid
P.loft([rect_ring(LID0 - 4.0, 35.2, 2.0), rect_ring(LID0 + 1.0, 35.2, 2.0)], "special")
# lid band with a bevelled top edge
L = 38.6
P.loft([rect_ring(LID0, L - 1.0, 2.5), rect_ring(LID0 + 1.0, L, 3.0), rect_ring(LID1 - 3.2, L, 3.0),
        rect_ring(LID1, L - 3.2, 2.0), rect_ring(LID1, 31.5, 17.0)], "primary")   # inner ring: vertex AO samples


# corner caps: chunky chamfered blocks on the eight corners
def cap(sx, sy, z0, z1, bevel_bottom):
    h, c, e = 9.6, 3.6, 3.0
    cx, cy = sx * (40.0 - h), sy * (40.0 - h)
    rings = []
    if bevel_bottom:
        rings.append(zring(cx, z0, h - e, h - e, c - 1.0, cy))
        rings.append(zring(cx, z0 + e, h, h, c, cy))
    else:
        rings.append(zring(cx, z0, h, h, c, cy))
    rings += [zring(cx, z1 - e, h, h, c, cy), zring(cx, z1, h - e, h - e, c - 1.0, cy)]
    P.loft(rings, "accent")


for sx in (1, -1):
    for sy in (1, -1):
        cap(sx, sy, 0.0, 18.5, False)
        cap(sx, sy, LID0, LID1 + 0.8, True)   # stands proud of the lid top (no coplanar faces)


# --- face frames ------------------------------------------------------------------------------
def face(o, u, v, n):
    """Map (a, b, d) in face coordinates (cm; a right, b up, d out of the face) to a world point."""
    def f(a, b, d):
        return V(*(o[i] + u[i] * a + v[i] * b + n[i] * d for i in range(3)))
    return f


def octo(f, d, h, c):
    pts = [(h, -h + c), (h, h - c), (h - c, h), (-h + c, h), (-h, h - c), (-h, -h + c), (-h + c, -h), (h - c, -h)]
    return [f(a, b, d) for a, b in pts]


def offset_convex(poly, d):
    """Convex polygon (counter-clockwise or clockwise) offset inwards by d."""
    n = len(poly)
    area = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
    s = 1 if area > 0 else -1
    lines = []
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        dx, dy = x1 - x0, y1 - y0
        ln = math.hypot(dx, dy)
        nx, ny = -dy / ln * s, dx / ln * s   # inward normal
        lines.append(((x0 + nx * d, y0 + ny * d), (dx, dy)))
    out = []
    for i in range(n):
        (p, r), (q, t) = lines[i - 1], lines[i]
        den = r[0] * t[1] - r[1] * t[0]
        k = ((q[0] - p[0]) * t[1] - (q[1] - p[1]) * t[0]) / den
        out.append((p[0] + r[0] * k, p[1] + r[1] * k))
    return out


# question mark, face coordinates (cm) around the frame centre, as overlapping convex pieces
QM = [
    [(-13.6, 11.0), (-13.6, 14.5), (-9.5, 18.7), (10.0, 18.7), (15.4, 13.6), (15.4, 11.0)],   # top bar
    [(-13.6, 6.0), (-11.9, 4.3), (-4.0, 4.3), (-4.0, 11.4), (-13.6, 11.4)],                   # left stub
    [(5.5, 6.0), (5.5, 11.4), (15.4, 11.4), (15.4, 6.0)],                                    # right arm
    [(-3.9, -3.5), (-3.9, 1.0), (7.0, 8.0), (15.4, 8.0), (15.4, 4.5), (6.0, -3.5)],           # diagonal
    [(-3.9, -7.3), (-3.9, -3.0), (6.0, -3.0), (6.0, -6.0), (4.7, -7.3)],                      # stem
    [(-3.9, -16.4), (-3.9, -12.1), (-2.0, -10.2), (4.1, -10.2), (6.0, -12.1), (6.0, -16.4), (4.1, -18.3), (-2.0, -18.3)],  # dot
]


def frame(f):
    H, C, W = 27.4, 7.0, 4.8           # outer half size, corner chamfer, frame width
    hi, ci = H - W, C - 2.0
    P.loft([octo(f, -1.5, H, C), octo(f, 1.4, H, C), octo(f, 2.0, H - 0.6, C - 0.25),
            octo(f, 2.0, hi + 0.6, ci + 0.25), octo(f, 1.4, hi, ci), octo(f, 0.5, hi, ci),
            octo(f, 0.5, hi - 4.0, ci - 1.5)],   # inner ring: panel vertices away from the frame wall (vertex AO)
           "accent", cap_roles=("accent", "dark"))
    for poly in QM:
        top = offset_convex(poly, 0.55)
        P.loft([[f(a, b, 0.0) for a, b in poly], [f(a, b, 1.6) for a, b in poly], [f(a, b, 2.2) for a, b in top]],
               "secondary")


# sides: origin on the face plane at the frame centre; (u right, v up, n out) as seen from outside
for o, u, n in (((0, -B, FZ), (1, 0, 0), (0, -1, 0)), ((B, 0, FZ), (0, 1, 0), (1, 0, 0)),
                ((0, B, FZ), (-1, 0, 0), (0, 1, 0)), ((-B, 0, FZ), (0, -1, 0), (-1, 0, 0))):
    frame(face(o, u, (0, 0, 1), n))
# top: readable from the front (v towards the back)
frame(face((0, 0, LID1), (1, 0, 0), (0, 1, 0), (0, 0, 1)))
