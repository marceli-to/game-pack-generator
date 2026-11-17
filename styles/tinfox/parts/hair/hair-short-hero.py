# Short hair (tinfox, hero-m) for capped heads: a closed loft over the head 1.6 cm out (12 columns), its lower edge
# at the cap band in front (hidden under it), above the ears at the sides and down to the nape at the back, then
# tucked 1.2 cm into the head so no rim shows; short sideburns in front of the ears.
prof = [(1.56, 0.116, -0.145, 0.14, 0.055), (1.65, 0.12, -0.146, 0.155, 0.06), (1.73, 0.115, -0.135, 0.152, 0.06),
        (lm["head_top"].z, 0.085, -0.095, 0.115, 0.045)]
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
    return 1.64 + 0.06 * max(0.0, -d.y) ** 2 - 0.09 * max(0.0, d.y) ** 1.5
N = 12
rings = [[pt(j, z, o) for j in range(N)] for z, o in ((1.79, 0.008), (1.76, 0.016))]
for v in (0.5, 1.0):
    rings.append([pt(j, 1.76 + (z_bottom(j) - 1.76) * v, 0.016) for j in range(N)])
rings.append([pt(j, z_bottom(j) + 0.012, -0.012) for j in range(N)])
P.loft([[Vector((0, 0.01, 1.805))]] + rings, "hair")
side = P.rbox((0.112, -0.052, 1.575), (0.128, -0.024, 1.68), "hair", r=0.006, bevel=0, seg=1, axis="z")
P.mirror_x(side)
