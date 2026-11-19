# "Pelican" orb blaster (Tinfox weapon sheet 07), 0.90 m (1.2 x the prompt's 75 cm). Lying along +X, top +Z
# (STYLE.md §9b). Two-handed: grip_l on the front handle under the nozzle. The revolving drum turns about the
# item's side axis (Y), as the sheet's side view draws it: six orbs show on each side.
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

CZ = 37.5            # nozzle / drum axis height
DX = 63.0            # drum centre along X


def ball(cx, cy, cz, r, n=8):
    """Orb: faceted ball, olive with an orange band round its middle (axis up)."""
    pts = [V(cx, cy, cz - r)]
    rings = [ngon_z(cx, cz + f * r, k * r, n, cy) for f, k in ((-0.72, 0.69), (-0.26, 0.97), (0.26, 0.97),
                                                               (0.72, 0.69))]
    P.loft([pts] + rings + [[V(cx, cy, cz + r)]], ["armor", "armor", "accent", "armor", "armor"])


# --- shoulder rest: orange back plate, black pad, two silver rods into the body
P.loft([xring(0.0, 36.0, 7.6, 12.8, 2.4), xring(0.8, 36.0, 8.5, 14.0, 2.8), xring(4.6, 36.0, 8.5, 14.0, 2.8)],
       "accent")
P.loft([xring(4.4, 36.0, 8.3, 13.4, 2.8), xring(9.4, 36.0, 8.0, 12.6, 2.8), xring(11.8, 36.0, 5.6, 10.0, 2.4)],
       "secondary")
P.box(V(10.5, -4.2, 38.0), V(19.0, 4.2, 42.2), "metal")
P.box(V(10.5, -4.2, 32.6), V(19.0, 4.2, 36.8), "metal")

# --- body (boxy, rounded), running into the drum
P.loft([xring(17.5, 37.0, 7.0, 8.0, 2.5), xring(19.2, 37.3, 9.0, 11.6, 3.0), xring(23.0, 37.5, 9.5, 13.5, 3.2),
        xring(36.0, 37.5, 9.5, 13.5, 3.2), xring(49.0, 37.5, 9.5, 13.5, 3.2), xring(55.0, 37.5, 9.0, 12.5, 3.0)],
       "primary")

# sides: two orange stripes, light blue window, silver plate
for x0 in (23.5, 29.0):
    both_sides([(x0, 40.5), (x0 + 3.0, 40.5), (x0 + 7.0, 47.5), (x0 + 4.0, 47.5)], 9.2, 9.75, "accent")
window(39.3, 39.5, 6.7, 3.0, 2.6, 9.0, 10.0)
both_sides([(33.0, 26.7), (34.3, 25.4), (45.7, 25.4), (47.0, 26.7), (47.0, 30.3), (45.7, 31.6), (34.3, 31.6),
            (33.0, 30.3)], 9.0, 10.8, "metal", inset=0.05)

# --- top: black base plate, silver hinge, flip-up sight frame
prism_y([(36.5, 50.0), (37.6, 53.6), (48.4, 53.6), (49.5, 50.0)], -5.0, 5.0, "secondary", inset=0.06)
P.loft([ngon_y(44.5, 56.0, -4.6, 2.3), ngon_y(44.5, 56.0, -4.1, 2.8), ngon_y(44.5, 56.0, 4.1, 2.8),
        ngon_y(44.5, 56.0, 4.6, 2.3)], "metal")
P.box(V(47.5, -5.0, 54.5), V(49.7, 5.0, 60.8), "metal", chamfer=0.003)
P.box(V(47.5, -5.0, 60.5), V(49.7, -3.2, 66.5), "metal")
P.box(V(47.5, 3.2, 60.5), V(49.7, 5.0, 66.5), "metal")
P.box(V(47.55, -4.9, 64.6), V(49.65, 4.9, 66.4), "metal")

# --- revolving drum (axis Y): fat disc with chamfered faces, silver hub, six sockets with orbs per side
RD, HW = 17.0, 14.5
P.loft([ngon_y(DX, CZ, -HW, 12.6, 16), ngon_y(DX, CZ, -HW + 1.8, 15.6, 16), ngon_y(DX, CZ, -6.5, RD, 16),
        ngon_y(DX, CZ, 6.5, RD, 16), ngon_y(DX, CZ, HW - 1.8, 15.6, 16), ngon_y(DX, CZ, HW, 12.6, 16)], "primary")
for s in (1, -1):
    P.loft([ngon_y(DX, CZ, s * (HW - 0.5), 4.6, 10), ngon_y(DX, CZ, s * (HW + 1.0), 4.6, 10),
            ngon_y(DX, CZ, s * (HW + 1.6), 3.8, 10), ngon_y(DX, CZ, s * (HW + 1.6), 2.4, 10),
            ngon_y(DX, CZ, s * (HW + 1.1), 2.4, 10)], "metal")
    for a in (90, 30, -30, -90, -150, 150):
        t = math.radians(a)
        ox, oz = DX + 10.2 * math.cos(t), CZ + 11.2 * math.sin(t)
        P.loft([ngon_y(ox, oz, s * (HW - 1.6), 5.15, 8), ngon_y(ox, oz, s * (HW + 0.35), 5.15, 8)], "dark")
        ball(ox, s * (HW - 1.2), oz, 4.7)
    # silver plate over the drum's top (top view)
    arc = [math.radians(a) for a in range(64, 117, 8)]
    P.sweep([V(DX + RD * math.cos(t), s * 9.8, CZ + RD * math.sin(t)) for t in arc],
            P.strap_profile(3.6 * K, 1.2 * K, 0.4 * K, inset=0.6 * K), "metal",
            normals=[(math.cos(t), 0, math.sin(t)) for t in arc])

# --- nozzle: grey neck, wide orange ring with a stepped dark bore
tube_x([76.0, 80.0, 84.0], 11.8, CZ, "primary", n=12)
P.loft([ngon_x(83.0, 13.9, CZ, 16), ngon_x(84.0, 14.9, CZ, 16), ngon_x(89.0, 14.9, CZ, 16),
        ngon_x(90.0, 13.7, CZ, 16), ngon_x(90.0, 10.2, CZ, 16), ngon_x(89.0, 8.6, CZ, 16),
        ngon_x(89.0, 7.0, CZ, 16), ngon_x(86.0, 7.0, CZ, 16)],
       ["accent", "accent", "accent", "accent", "accent", "accent", "dark"], cap_roles=("accent", "dark"))


# --- rear pistol grip (raked, curving back into the body), trigger guard, orange trigger
def hx(z):
    return 21.5 + (z - 0.5) * 0.2 if z < 15 else 24.4 - (z - 15) * 0.2


P.loft([zring(hx(0.5), 0.5, 5.5, 3.9, 0.7), zring(hx(1.2), 1.2, 6.2, 4.5, 1.0), zring(hx(15), 15.0, 5.4, 4.5, 1.0),
        zring(hx(21), 21.0, 6.2, 4.5, 1.0), zring(hx(28), 28.0, 6.8, 4.5, 1.0)], "secondary")
for za, zb in ((3.0, 5.0), (6.4, 8.4), (9.8, 11.8)):
    P.loft([zring(hx(za), za, 6.25, 4.55, 1.0), zring(hx(za + 0.3), za + 0.3, 6.65, 4.95, 1.1),
            zring(hx(zb - 0.3), zb - 0.3, 6.65, 4.95, 1.1), zring(hx(zb), zb, 6.25, 4.55, 1.0)], "secondary")
guard_loop([(28.6, 25.0), (28.6, 20.0), (30.0, 17.6), (32.6, 17.2), (34.6, 18.6), (35.4, 21.0), (35.4, 25.0)],
           half_t=0.8, half_w=1.1)
prism_y([(29.4, 24.6), (31.8, 24.6), (31.4, 21.2), (30.6, 19.0), (29.6, 19.2), (29.8, 21.6)], -0.7, 0.7, "accent")

# --- front handle under the nozzle, on a silver bracket
P.loft([xring(69.5, 22.2, 4.2, 2.2, 0.8), xring(70.5, 22.4, 4.6, 2.6, 0.9), xring(79.0, 22.4, 4.6, 2.6, 0.9),
        xring(80.4, 22.6, 4.0, 2.2, 0.8)], "metal")


def fx(z):
    return 74.3


handle(fx, 0.5, 21.0, 4.6, 4.0, [(2.4, 4.6), (5.9, 8.1), (9.4, 11.6), (12.9, 15.1)])

P.anchor("grip", V(hx(8.0), 0, 8.0))
P.anchor("grip_l", V(74.3, 0, 10.0))
P.anchor("muzzle", V(90.0, 0, CZ))
