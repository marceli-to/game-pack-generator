# Officer's peaked cap (tinfox, hero-m), fitted to specs/officer/reference: a black band round the head, a wide olive
# saucer crown tilted up at the front (front ~1.86 m, back ~1.73 m), a near-black peak sloping down to the front,
# a round brass badge on the crown's front.
def rr(z, sx, f, b, r, seg=3):
    return P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=seg)
def tilted(z, sx, f, b, r, s):
    """Ring at height z above the band top, sheared so its front (-y) rises by s per metre."""
    return [Vector((p.x, p.y, 1.69 + z + s * max(0.0, -p.y) - 0.4 * s * max(0.0, p.y))) for p in rr(0.0, sx, f, b, r)]
# band (black), slightly lower at the back
band = [Vector((p.x, p.y, p.z - 0.03 * p.y)) for p in rr(1.635, 0.14, -0.158, 0.184, 0.07)]
band2 = [Vector((p.x, p.y, p.z - 0.03 * p.y)) for p in rr(1.695, 0.143, -0.161, 0.187, 0.07)]
P.loft([band, band2], "secondary", cap_roles=("dark", "secondary"))
# crown: (height, half width, front, back, corner, shear)
crown = [(0.0, 0.141, -0.158, 0.184, 0.068, 0.0), (0.035, 0.18, -0.18, 0.2, 0.09, 0.12),
         (0.07, 0.21, -0.198, 0.222, 0.105, 0.22), (0.095, 0.208, -0.196, 0.22, 0.105, 0.26),
         (0.12, 0.17, -0.166, 0.186, 0.085, 0.28), (0.135, 0.1, -0.1, 0.11, 0.05, 0.3)]
P.loft([tilted(*c) for c in crown], "primary", cap_roles=("dark", "primary"))
# peak: a thick sheet from the band forward, sloping down to the front, rounded front edge
cols = [math.radians(a) for a in (-66, -44, -22, 0, 22, 44, 66)]
def peak_pt(t, reach, z):
    return Vector((0.138 * math.sin(t) * (1 - 0.6 * reach), -0.145 * math.cos(t) - reach * math.cos(t) ** 0.5, z))
P.shell([[peak_pt(t, 0.0, 1.68) for t in cols], [peak_pt(t, 0.045, 1.67) for t in cols],
         [peak_pt(t, 0.085, 1.652) for t in cols]], 0.012, "secondary")
# badge: brass disc on the crown's front, centred on the bulge above the band, leaning with it
c = Vector((0.0, -0.19, 1.776))
n = Vector((0, -1, -0.2)).normalized()   # follows the crown front, which leans forward
P.cylinder(c - n * 0.01, c + n * 0.008, 0.042, n=12, role="metal")
P.cylinder(c + n * 0.006, c + n * 0.013, 0.03, n=12, role="metal")
