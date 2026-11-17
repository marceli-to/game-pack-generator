# Vireo SMG (Tinfox weapon sheet 03), 0.60 m. Lying along +X, top +Z (STYLE.md §9b). Two-handed: grip_l on the
# front grip.
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

CZ = 22.5   # bore axis

# --- folding stock: black butt with an orange insert, silver strut, black brace, silver hinge
prism_y([(1.0, 13.0), (2.0, 12.0), (5.8, 12.0), (5.8, 26.5), (4.8, 27.2), (1.8, 27.2), (1.0, 26.2)], -3.0, 3.0,
        "secondary", inset=0.08)
both_sides([(2.0, 15.0), (3.6, 15.0), (3.6, 23.6), (2.0, 23.6)], 2.85, 3.3, "accent")
P.box(V(5.0, -1.5, 20.6), V(15.0, 1.5, 24.4), "metal")
prism_y([(5.5, 18.0), (14.8, 16.4), (14.8, 18.4), (5.5, 19.9)], -1.1, 1.1, "secondary")
P.loft([ngon_y(16.2, 22.5, -3.4, 2.4), ngon_y(16.2, 22.5, -2.9, 3.0), ngon_y(16.2, 22.5, 2.9, 3.0),
        ngon_y(16.2, 22.5, 3.4, 2.4)], "metal")

# --- body
P.loft([xring(15.0, 21.5, 3.8, 5.0, 1.4), xring(16.8, 21.0, 4.6, 7.0, 1.6), xring(35.0, 21.2, 4.6, 6.8, 1.6),
        xring(53.5, 21.5, 4.6, 6.5, 1.6), xring(55.6, 22.0, 3.8, 5.0, 1.4)], "primary")

# --- top rail with teeth, rear and front sight (silver)
P.box(V(19.0, -2.5, 27.6), V(52.0, 2.5, 29.3), "secondary")
for i in range(12):
    x = 20.2 + i * 2.62
    P.box(V(x, -2.5, 29.2), V(x + 1.3, 2.5, 30.3), "secondary")
prism_y([(22.3, 29.0), (22.9, 32.2), (25.0, 32.2), (25.5, 29.0)], -1.5, 1.5, "metal", inset=0.08)
prism_y([(48.3, 29.0), (49.0, 33.4), (51.8, 33.4), (52.3, 29.0)], -1.7, 1.7, "metal", inset=0.08)

# --- barrel collar and emitter ring
tube_x([54.5, 55.6, 57.2], 3.4, CZ, "secondary")
emitter(56.8, 60.0, 4.1, 2.2, CZ)

# --- sides: long energy window, two stripes, silver side panels
window(41.3, 23.0, 9.3, 2.6, 2.2, 4.0, 4.95)
for x0 in (24.5, 27.6):
    both_sides([(x0, 20.4), (x0 + 1.8, 20.4), (x0 + 5.4, 26.0), (x0 + 3.6, 26.0)], 4.3, 4.75, "accent")
both_sides([(31.2, 16.5), (32.5, 15.0), (40.0, 15.0), (41.3, 16.5), (41.3, 19.3), (40.0, 20.6), (32.5, 20.6),
            (31.2, 19.3)], 3.8, 5.4, "metal", inset=0.05)
both_sides([(46.5, 17.0), (53.5, 17.0), (54.2, 17.8), (54.2, 19.8), (53.5, 20.5), (46.5, 20.5)], 3.8, 5.4, "metal",
           inset=0.05)


# --- pistol grip (raked ~20 degrees), trigger guard, trigger
def hx(z):
    return 19.0 + (z - 2.0) * 4.5 / 12.0


handle(hx, 2.0, 15.0, 4.2, 2.6, [(3.4, 4.9), (6.1, 7.6), (8.8, 10.3)])
guard_loop([(25.4, 14.6), (25.4, 12.0), (26.6, 10.6), (28.8, 10.1), (30.8, 10.6), (31.9, 12.0), (32.1, 14.6)],
           half_t=0.8, half_w=0.9)
prism_y([(24.8, 14.5), (26.6, 14.5), (26.4, 12.6), (25.0, 12.4)], -0.6, 0.6, "accent")
prism_y([(25.0, 12.6), (26.4, 12.7), (26.9, 11.4), (25.9, 11.4)], -0.6, 0.6, "accent")

# --- box magazine (role leather: silver as drawn; the pickups' dark grey is one spec colour away)
P.loft([zring(36.7, 2.8, 4.4, 2.3, 0.6), zring(36.7, 15.5, 4.2, 2.3, 0.6)], "leather")
for xa in (32.6, 35.6, 38.4):
    both_sides([(xa, 4.6), (xa + 1.4, 4.6), (xa + 1.4, 13.2), (xa, 13.2)], 2.1, 2.45, "primary")
prism_y([(31.8, 2.0), (32.4, 1.4), (41.0, 1.4), (41.6, 2.0), (41.6, 3.2), (31.8, 3.2)], -2.8, 2.8, "accent",
        inset=0.04)


# --- front grip with ridges
def fx(z):
    return 50.3


handle(fx, 2.0, 17.5, 2.9, 2.4, [(3.3, 4.8), (5.8, 7.3), (8.3, 9.8), (10.8, 12.3)])

P.anchor("grip", V(hx(8.0), 0, 8.0))
P.anchor("grip_l", V(50.3, 0, 10.0))
P.anchor("muzzle", V(60.0, 0, CZ))
