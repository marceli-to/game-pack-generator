# Horned dwarf helmet (lowpoly, dwarf archetype), fitted to specs/dwarf/reference: a round dome with a thick rim,
# tilted back 14 degrees (rim at the brow in front, at the nape behind), a ridge from brow to nape, and two cream
# horns curving out and up (bisector-oriented rings, checked against folding).
def rr(z, sx, f, b, r):
    return P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=1)
prof = [(0.775, 0.276, -0.25, 0.28, 0.1), (0.785, 0.284, -0.258, 0.288, 0.1), (0.83, 0.284, -0.258, 0.288, 0.1),
        (0.84, 0.268, -0.244, 0.274, 0.1), (0.92, 0.255, -0.23, 0.26, 0.1), (0.99, 0.215, -0.19, 0.22, 0.085),
        (1.04, 0.15, -0.13, 0.16, 0.06), (1.07, 0.07, -0.055, 0.085, 0.03)]
faces = P.loft([rr(*p) for p in prof], "metal", cap_roles=("dark", "metal"))
mid = [(-0.25, 0.84), (-0.232, 0.92), (-0.19, 0.99), (-0.12, 1.045), (0.015, 1.077), (0.15, 1.045),
       (0.22, 0.99), (0.262, 0.92), (0.28, 0.84)]
c = Vector((0, 0.015, 0.8))
path = [Vector((0, y, z)) for y, z in mid]
faces += P.sweep(path, P.strap_profile(0.065, 0.014, 0.005), "metal", [(p - c).normalized() for p in path])
piv = Vector((0, 0.015, 0.8))
P.transform(faces, Matrix.Translation(piv) @ Matrix.Rotation(math.radians(-14), 4, "X") @ Matrix.Translation(-piv))
N = 6
REF = Vector((0, -1, 0))
def oring(c, t, r):
    t = t.normalized()
    u = (REF - t * REF.dot(t)).normalized()
    w = t.cross(u)
    return [c + r * (math.cos(a) * u + math.sin(a) * w) for a in (math.radians(30 + 60 * k) for k in range(N))]
spine = [(Vector((0.2, 0.02, 0.9)), 0.058), (Vector((0.265, 0.02, 0.925)), 0.05), (Vector((0.31, 0.025, 0.965)), 0.04),
         (Vector((0.325, 0.03, 1.02)), 0.028), (Vector((0.31, 0.035, 1.06)), 0.017)]
rings = []
for k, (c, r) in enumerate(spine):
    prv = spine[k - 1][0] if k else c - Vector((0.06, 0, 0))
    nxt = spine[k + 1][0] if k + 1 < len(spine) else c + (c - prv)
    rings.append(oring(c, (c - prv).normalized() + (nxt - c).normalized(), r))
rings.append([Vector((0.29, 0.038, 1.095))])
P.mirror_x(P.loft(rings, "secondary"))
