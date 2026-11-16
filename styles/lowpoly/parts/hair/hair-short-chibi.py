# Short hair (lowpoly chibi, bare heads): one closed loft over the crown following the head's facets 1.8 cm out
# (12 columns); the lower edge drops from a jagged fringe over the brow (tufts to z 1.03) to the sides (0.99,
# over the ear tops) and the nape (0.9), then tucks 1.5 cm into the head so no rim shows. Not for headwear.
prof = [(lm["head_base"].z, 0.11, -0.12, 0.08, 0.05), (0.85, 0.17, -0.17, 0.14, 0.07), (0.97, 0.19, -0.18, 0.165, 0.08),
        (1.08, 0.18, -0.172, 0.16, 0.08), (lm["head_top"].z, 0.12, -0.11, 0.11, 0.05)]
N = 12
def dims(z):
    z = max(prof[0][0], min(prof[-1][0], z))
    for a, b in zip(prof, prof[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return [u + (v - u) * t for u, v in zip(a[1:], b[1:])]
def pt(j, z, o):
    sx, f, b, r = dims(z)
    p = P.rrect((0, (f + b) / 2, z), sx + o, (b - f) / 2 + o, r + 0.4 * o, seg=2)[j]
    return Vector((p.x, p.y, z))
ref = P.rrect((0, 0, 0), 1, 1, 0.4, seg=2)
def z_bottom(j):
    d = Vector((ref[j].x, ref[j].y, 0)).normalized()
    z = 0.99 + 0.075 * max(0.0, -d.y) ** 2 - 0.09 * max(0.0, d.y)
    if j in (8, 9):      # fringe: two tufts on the brow, notches beside them (mirror pairs 8/9, 7/10)
        z -= 0.03
    elif j in (7, 10):
        z += 0.012
    return z
rings = [[pt(j, z, o) for j in range(N)] for z, o in ((1.215, 0.01), (1.165, 0.018), (1.1, 0.02))]
for v in (0.55, 1.0):
    rings.append([pt(j, 1.1 + (z_bottom(j) - 1.1) * v, 0.02 + 0.006 * v) for j in range(N)])
rings.append([pt(j, z_bottom(j) + 0.012, -0.015) for j in range(N)])
P.loft([[Vector((0, 0, 1.23))]] + rings, "hair")
