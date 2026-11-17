# Heron LR sniper rifle (Tinfox weapon sheet 04), 1.32 m. Lying along +X, top +Z (STYLE.md §9b). Two-handed:
# grip_l on the silver fore-end.
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

CZ = 28.0    # bore axis
SZ = 41.5    # scope axis

# --- stock: silver butt plate, grey stock rising to the receiver, black cheek rest, an orange stripe
prism_y([(0.0, 12.5), (0.8, 11.0), (4.5, 11.0), (4.5, 31.5), (1.5, 31.5), (0.0, 30.0)], -3.8, 3.8, "metal",
        inset=0.06)
P.loft([xring(4.0, 21.0, 3.6, 10.0, 1.0), xring(12.0, 21.0, 3.6, 10.0, 1.0), xring(17.5, 24.5, 3.6, 6.0, 1.0),
        xring(30.0, 24.5, 3.6, 6.0, 1.0), xring(36.5, 26.0, 3.6, 7.5, 1.0)], "primary")
both_sides([(7.5, 12.0), (9.7, 12.0), (14.8, 21.0), (12.6, 21.0)], 3.45, 3.95, "accent")
prism_y([(8.5, 30.0), (9.5, 33.6), (11.0, 34.8), (27.0, 34.8), (28.8, 33.4), (29.2, 30.0)], -3.3, 3.3,
        "secondary", inset=0.06)

# --- receiver and top rail
P.loft([xring(35.5, 26.0, 4.6, 7.5, 1.5), xring(37.5, 26.6, 4.6, 7.6, 1.5), xring(63.0, 27.1, 4.6, 7.1, 1.5),
        xring(89.5, 27.6, 4.6, 6.6, 1.5), xring(96.5, 28.0, 3.6, 4.0, 1.2)], "primary")
P.box(V(46.0, -2.6, 33.8), V(80.0, 2.6, 36.2), "secondary")
for i in range(8):
    x = 47.5 + i * 4.2
    P.box(V(x, -2.6, 36.0), V(x + 1.6, 2.6, 36.9), "secondary")

# --- scope: lenses at both ends, bells, two silver rings with mounts, a round boss and a turret
P.loft([ngon_x(36.4, 3.8, SZ, 10), ngon_x(37.1, 4.6, SZ, 10), ngon_x(38.6, 4.8, SZ, 10)], "special")
P.loft([ngon_x(38.4, 5.0, SZ, 10), ngon_x(45.0, 4.4, SZ, 10), ngon_x(51.5, 3.7, SZ, 10), ngon_x(60.0, 3.7, SZ, 10),
        ngon_x(69.5, 3.7, SZ, 10), ngon_x(77.0, 4.4, SZ, 10), ngon_x(84.6, 5.0, SZ, 10)], "primary")
P.loft([ngon_x(84.4, 4.8, SZ, 10), ngon_x(86.6, 4.6, SZ, 10), ngon_x(87.4, 3.8, SZ, 10)], "special")
for x0, x1 in ((51.0, 55.0), (66.5, 70.0)):
    P.loft([ngon_x(x0, 4.9, SZ, 10), ngon_x(x0 + 0.3, 5.2, SZ, 10), ngon_x(x1 - 0.3, 5.2, SZ, 10),
            ngon_x(x1, 4.9, SZ, 10)], "metal")
    P.box(V(x0 + 0.4, -2.0, 35.6), V(x1 - 0.4, 2.0, 38.0), "metal")
P.loft([ngon_y(60.5, SZ, -3.6, 3.8, 10), ngon_y(60.5, SZ, -3.2, 4.3, 10), ngon_y(60.5, SZ, 3.2, 4.3, 10),
        ngon_y(60.5, SZ, 3.6, 3.8, 10)], "primary")
prism_y([(57.5, 44.5), (58.0, 48.5), (65.5, 48.5), (66.0, 44.5)], -2.2, 2.2, "secondary", inset=0.06)

# --- sides: energy window, stripes, silver fore-end
both_sides([(66.0, 27.2), (67.6, 25.0), (86.5, 25.0), (88.0, 27.2), (86.5, 29.4), (67.6, 29.4)], 4.2, 4.95,
           "special")
for x0 in (52.5, 56.6):
    both_sides([(x0, 22.8), (x0 + 2.0, 22.8), (x0 + 5.6, 31.4), (x0 + 3.6, 31.4)], 4.3, 4.8, "accent")
both_sides([(74.5, 18.8), (75.8, 17.4), (89.4, 17.4), (91.2, 19.0), (91.2, 22.6), (76.6, 22.6)], 3.4, 5.0, "metal",
           inset=0.05)

# --- barrel: silver collar, long barrel, silver ring, emitter
tube_x([94.0, 95.0, 100.5, 101.5], 3.6, CZ, "metal")
tube_x([100.0, 102.0, 112.0, 121.0, 123.0], 2.8, CZ, "primary")
tube_x([122.2, 122.6, 125.4, 125.8], 3.6, CZ, "metal")
emitter(125.6, 132.0, 4.5, 2.3, CZ)


# --- pistol grip, trigger guard, trigger
def hx(z):
    return 38.0 + 4.0 * (z - 1.0) / 18.0


handle(hx, 1.0, 20.0, 4.0, 2.8, [(4.0, 6.0), (8.0, 10.0), (12.0, 14.0)], ridge_out=0.45)
guard_loop([(43.8, 20.0), (43.8, 17.2), (45.3, 15.0), (48.5, 14.2), (52.0, 14.7), (54.0, 16.6), (54.6, 20.0)])
prism_y([(45.6, 19.6), (48.0, 19.6), (47.8, 17.8), (46.0, 17.6)], -0.6, 0.6, "accent")
prism_y([(46.0, 17.9), (47.8, 18.0), (48.4, 16.4), (47.2, 16.4)], -0.6, 0.6, "accent")

# --- box magazine (role leather: silver as drawn), black base plate
P.loft([zring(63.0, 3.0, 7.5, 3.0, 0.8), zring(63.0, 20.5, 7.5, 3.0, 0.8)], "leather")
for xa in (57.8, 61.4, 65.0, 68.6):
    both_sides([(xa, 5.0), (xa + 1.2, 5.0), (xa + 1.2, 17.0), (xa, 17.0)], 2.8, 3.25, "dark")
prism_y([(55.0, 1.6), (55.6, 1.0), (70.4, 1.0), (71.0, 1.6), (71.0, 3.2), (55.0, 3.2)], -3.4, 3.4, "secondary",
        inset=0.04)

P.anchor("grip", V(hx(9.0), 0, 9.0))
P.anchor("grip_l", V(82.5, 0, 19.5))
P.anchor("muzzle", V(132.0, 0, CZ))
