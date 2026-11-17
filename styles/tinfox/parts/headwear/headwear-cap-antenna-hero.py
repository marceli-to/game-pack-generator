# Field cap with radio antenna (tinfox, hero-m), fitted to specs/guard/reference: an olive band round the head and
# a soft crown that bulges a little over the band, a near-black peak, an orange earpiece disc on the wearer's left
# (+X) with a short antenna and a ball on top.
def rr(z, sx, f, b, r):
    return P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=3)
# (z front, z back, half width, front y, back y, corner): the crown is low and slopes down to the back
crown = [(1.69, 1.68, 0.128, -0.158, 0.168, 0.06), (1.735, 1.725, 0.132, -0.162, 0.172, 0.065),
         (1.74, 1.73, 0.138, -0.168, 0.178, 0.07), (1.81, 1.78, 0.142, -0.168, 0.18, 0.075),
         (1.85, 1.81, 0.12, -0.14, 0.15, 0.06), (1.862, 1.828, 0.07, -0.085, 0.09, 0.035)]
def tilted(zf, zb, sx, f, b, r):
    pts = rr(0.0, sx, f, b, r)
    return [Vector((p.x, p.y, zf + (zb - zf) * (p.y - f) / (b - f))) for p in pts]
P.loft([tilted(*c) for c in crown], "primary", cap_roles=("dark", "primary"))
# peak: a thick sheet from the band forward, tilted down a little, rounded front edge
cols = [math.radians(a) for a in (-62, -40, -20, 0, 20, 40, 62)]
def peak_pt(t, reach, z):
    return Vector((0.135 * math.sin(t) * (1 - 0.15 * reach), -0.155 * math.cos(t) - reach * math.cos(t) ** 0.5, z))
P.shell([[peak_pt(t, 0.0, 1.705) for t in cols], [peak_pt(t, 0.05, 1.7) for t in cols],
         [peak_pt(t, 0.095, 1.688) for t in cols]], 0.012, "secondary")
# earpiece + antenna (wearer's left)
P.cylinder(Vector((0.125, 0.0, 1.72)), Vector((0.168, 0.0, 1.72)), 0.04, n=8, role="accent")
P.cylinder(Vector((0.155, 0.01, 1.75)), Vector((0.16, 0.02, 1.86)), 0.008, n=6, role="accent")
c = Vector((0.16, 0.02, 1.875))
P.loft([[c + Vector((0, 0, -0.022))]] + [P.ring(c + Vector((0, 0, 0.02 * s)), 0.022 * k, n=8) for s, k in
                                         ((-0.6, 0.8), (0.0, 1.0), (0.6, 0.8))] + [[c + Vector((0, 0, 0.022))]], "accent")
