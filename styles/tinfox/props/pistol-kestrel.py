# Kestrel 9 pistol (Tinfox weapon sheet 01). Measured off the sheet in cm: x from the back tip (muzzle at 30),
# z from the handle's bottom, y across (+y = the gun's left side). Lying along +X, top +Z (STYLE.md §9b).
K = 0.01   # cm -> m


def V(x, y, z):
    return Vector((x * K, y * K, z * K))


def xring(x, cz, hy, hz, ch, cy=0.0):
    """Chamfered rectangle (half sizes hy across, hz up) in the plane x = const."""
    return [V(x, cy + p.y / K, cz + p.z / K) for p in P.rect((0, 0, 0), hy * K, hz * K, ch * K, axis="x")]


def oct_x(x, r, cz=17.0):
    """Octagon (flat at the bottom) around the bore axis, in the plane x = const."""
    return [V(x, p.y / K, cz + p.z / K) for p in P.ring((0, 0, 0), r * K, n=8, axis="x")]


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


# --- body: chamfered block, octagon-ish cross-section, tapered at the back and the front top
BW, BZ0, BZ1, BCH = 4.6, 12.5, 21.9, 1.2
body = [
    xring(2.4, 17.1, 3.9, 3.4, 1.2),
    xring(4.0, (BZ0 + BZ1) / 2, BW, (BZ1 - BZ0) / 2, BCH),
    xring(20.6, (BZ0 + BZ1) / 2, BW, (BZ1 - BZ0) / 2, BCH),
    xring(22.4, 16.9, 4.0, 3.5, 1.2),
]
P.loft(body, "primary")

# --- rear cap (silver), sunk into the body
P.loft([xring(3.4, 16.8, 3.6, 3.0, 1.1), xring(1.0, 16.8, 3.6, 3.0, 1.1), xring(0.0, 16.8, 2.7, 2.1, 0.8)], "metal")

# --- barrel, black collar, orange emitter ring with a dark bore
# rings where the barrel leaves the body and enters the collar: vertex AO samples at vertices, and a tube whose
# only rings are buried comes out dark all over
P.loft([oct_x(21.5, 3.3), oct_x(22.7, 3.3), oct_x(24.5, 3.3), oct_x(26.2, 3.3), oct_x(26.8, 3.3)], "primary")
P.loft([oct_x(26.4, 3.75), oct_x(27.7, 3.75)], "secondary")
ring_bands = ["accent", "accent", "accent", "accent", "dark"]
P.loft([oct_x(27.4, 4.1), oct_x(27.9, 4.6), oct_x(29.5, 4.6), oct_x(30.0, 4.1), oct_x(30.0, 2.4), oct_x(28.6, 2.4)],
       ring_bands, cap_roles=("accent", "dark"))

# --- rear sight block (black; the sheet's silver post removed, Marcel)
prism_y([(4.4, 21.4), (6.6, 24.2), (10.9, 24.2), (12.6, 21.4)], -2.2, 2.2, "secondary", inset=0.12)

# --- per side: energy window, orange stripes, silver block under the barrel
side = []
for y in (1, -1):
    # silver rim standing out of the side, the blue glass flush in it (one shell; a recessed glass baked dark)
    def wring(yy, r):
        return [V(17.0 + p.x / K, yy * y, 17.2 + p.z / K) for p in P.ring((0, 0, 0), r * K, n=10, axis="y")]
    P.loft([wring(3.9, 2.55), wring(5.15, 2.55), wring(5.45, 2.2), wring(5.45, 1.65)],
           ["metal", "metal", "metal"], cap_roles=("metal", "special"))
    for x0 in (5.2, 8.3):
        poly = [(x0, 15.6), (x0 + 2.0, 15.6), (x0 + 4.8, 21.2), (x0 + 2.8, 21.2)]
        prism_y(poly, 4.3 * y, 4.7 * y, "accent")
    prism_y([(18.7, 12.7), (19.3, 11.6), (24.0, 11.6), (24.5, 12.2), (24.5, 15.3), (20.3, 15.3)],
            3.0 * y, 5.3 * y, "metal", inset=0.06)

# --- trigger guard (black loop) and trigger (orange)
# smaller loop than the sheet's (Marcel)
path = [(9.9, 13.2), (9.9, 10.9), (10.6, 9.0), (12.2, 7.9), (14.2, 7.6), (16.0, 8.2), (17.1, 10.0), (17.4, 13.2)]
prof = [(-0.9, -1.0), (0.9, -1.0), (0.9, 1.0), (-0.9, 1.0)]
P.sweep([V(x, 0, z) for x, z in path], [(o * K, s * K) for o, s in prof], "secondary",
        normals=[(0, 1, 0)] * len(path))
prism_y([(9.9, 12.8), (12.3, 12.8), (12.1, 10.4), (10.3, 10.2)], -0.6, 0.6, "accent")
prism_y([(10.3, 10.5), (12.1, 10.6), (12.6, 9.4), (11.5, 9.5)], -0.6, 0.6, "accent")

# --- handle (black), raked back ~9 degrees, with three grip ridges


def hx(z):
    return 4.4 + 2.5 * z / 12.5      # centre line of the handle


def hring(z, hxs, hy, ch):
    return xz_ring(hx(z), z, hxs, hy, ch)


def xz_ring(cx, z, hxs, hy, ch):
    return [V(cx + p.x / K, p.y / K, z) for p in P.rect((0, 0, 0), hxs * K, hy * K, ch * K, axis="z")]


P.loft([hring(0.0, 2.7, 2.0, 0.6), hring(0.6, 3.2, 2.45, 0.8), hring(13.0, 2.9, 2.45, 0.8)], "secondary")
for z0, z1 in ((1.5, 3.0), (4.3, 5.8), (7.1, 8.6)):
    P.loft([hring(z0, 3.25, 2.55, 0.8), hring(z0 + 0.25, 3.5, 2.8, 0.9), hring(z1 - 0.25, 3.5, 2.8, 0.9),
            hring(z1, 3.25, 2.55, 0.8)], "secondary")

# --- anchors: grip on the handle's centre line where the fist closes; muzzle at the bore's front
P.anchor("grip", V(hx(6.0), 0, 6.0))
P.anchor("muzzle", V(30.0, 0, 17.0))
