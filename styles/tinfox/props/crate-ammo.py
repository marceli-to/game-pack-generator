# Ammo crate (Tinfox props sheet 03), 0.72 long (X) x 0.44 deep (Y) x 0.345 high incl. the windows; pickup on
# the floor. Front (latches) faces -Y. Measured in cm off the sheet's front view (0.72 / 633 px).
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


def yring(cx, y, cz, hx, hz, ch):
    """Chamfered rectangle (half sizes hx along X, hz up) in the plane y = const."""
    return [V(cx + p.x / K, y, cz + p.z / K) for p in P.rect((0, 0, 0), hx * K, hz * K, ch * K, axis="y")]


# plinth, body, lid with the recessed grey panel on top
P.loft([zring(0, 0.0, 32.0, 18.0, 3.0), zring(0, 1.8, 32.0, 18.0, 3.0)], "secondary")
P.loft([zring(0, 1.5, 34.2, 19.8, 3.0), zring(0, 2.0, 34.7, 20.3, 3.2), zring(0, 21.6, 34.7, 20.3, 3.2)], "primary")
P.loft([zring(0, 21.4, 35.6, 21.4, 4.0), zring(0, 21.8, 36.0, 21.8, 4.2), zring(0, 27.4, 36.0, 21.8, 4.2),
        zring(0, 29.6, 34.0, 19.8, 3.4), zring(0, 29.6, 31.5, 17.3, 5.5), zring(0, 29.3, 31.2, 17.0, 5.4)],
       ["accent", "accent", "accent", "accent", "primary"], cap_roles=("accent", "primary"))

# side panels: body-grey plates with wide chamfers (the bevels catch the light like the sheet's panel edges);
# a darker label slot between the latches on the front and back
for s in (1, -1):
    P.loft([yring(0, s * 20.0, 12.0, 26.5, 4.6, 2.6), yring(0, s * 20.5, 12.0, 26.5, 4.6, 2.6),
            yring(0, s * 21.0, 12.0, 25.6, 3.7, 2.0)], "primary")
    P.loft([yring(0, s * 20.8, 13.2, 8.0, 2.2, 0.8), yring(0, s * 21.25, 13.2, 7.8, 2.0, 0.7)], "dark")
    P.loft([xring(s * 34.4, 12.0, 15.0, 4.6, 2.6), xring(s * 34.9, 12.0, 15.0, 4.6, 2.6),
            xring(s * 35.4, 12.0, 14.1, 3.7, 2.0)], "primary")

# orange corner bumpers round the bottom corners
for sx in (1, -1):
    for sy in (1, -1):
        cx, cy = sx * 31.2, sy * 16.8
        P.loft([zring(cx, 0.4, 4.2, 4.2, 1.2, cy), zring(cx, 1.0, 4.6, 4.6, 1.5, cy),
                zring(cx, 8.2, 4.6, 4.6, 1.5, cy), zring(cx, 9.8, 3.4, 3.4, 1.0, cy)], "accent")

# two black latches on the front (v2, as on the sheet): a hinge plate starting on the lid band and a clasp below
# it with chamfered bottom corners, both standing ~2 cm proud of the lid so they show from above
for x0 in (-15.3, 15.3):
    prism_y([(x0 - 4.8, 23.9), (x0 - 3.6, 25.3), (x0 + 3.6, 25.3), (x0 + 4.8, 23.9), (x0 + 4.8, 19.0),
             (x0 - 4.8, 19.0)], -21.4, -23.6, "secondary", inset=0.05)
    prism_y([(x0 - 4.6, 19.3), (x0 + 4.6, 19.3), (x0 + 4.6, 13.6), (x0 + 2.4, 11.2), (x0 - 2.4, 11.2),
             (x0 - 4.6, 13.6)], -20.4, -24.0, "secondary", inset=0.05)

# carrying handles on the short ends (v2, as on the sheet): two mount blocks just under the lid and a thick
# square-section loop hanging from them, leaning out a little; its bar hangs at ~12.5 cm, ~4 cm past the lid
for sx in (1, -1):
    for sy in (1, -1):
        a, b = sorted((sx * 34.4, sx * 39.6))
        P.box(V(a, sy * 8.0 - 2.2, 20.2), V(b, sy * 8.0 + 2.2, 23.6), "secondary")
    pts = [(-8.0, 38.8, 21.4), (-8.0, 40.0, 14.2), (-6.8, 40.2, 12.9), (6.8, 40.2, 12.9), (8.0, 40.0, 14.2),
           (8.0, 38.8, 21.4)]
    path = [V(sx * x, y, z) for y, x, z in pts]
    P.sweep(path, [(-0.011, -0.011), (0.011, -0.011), (0.011, 0.011), (-0.011, 0.011)], "secondary",
            normals=[(sx, 0, 0)] * len(path))

# three energy windows on the lid: black base, rim, light-blue dome
for xc in (-17.0, 0.0, 17.0):
    P.loft([ngon_z(xc, 29.0, 8.0, 12), ngon_z(xc, 31.0, 8.0, 12), ngon_z(xc, 31.3, 7.6, 12),
            ngon_z(xc, 31.3, 6.4, 12), ngon_z(xc, 32.0, 6.1, 12)], "secondary")
    P.loft([ngon_z(xc, 31.6, 5.6, 12), ngon_z(xc, 32.4, 5.6, 12), ngon_z(xc, 33.6, 4.4, 12),
            ngon_z(xc, 34.3, 2.6, 12), [V(xc, 0, 34.5)]], "special")
