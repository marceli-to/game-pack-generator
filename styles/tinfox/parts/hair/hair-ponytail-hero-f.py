# Ponytail hair (tinfox, hero-f), for specs/worker/reference (under a hard hat): a closed loft over the head 1.6 cm
# out (as hair-short-hero), its lower edge under the hat brim in front, above the ears at the sides and down to the
# nape at the back, tucked into the head; a fringe swept from the wearer's left down across the right brow; a lock in
# front of each ear flicking out at the jaw; a ponytail out of a grey band at the back of the head.
# Built in hero-m coordinates (the head-hero-f head is the guard's, moved and scaled at the end the same way).
prof = [(1.52, 0.118, -0.14, 0.13, 0.055), (1.56, 0.12, -0.145, 0.142, 0.055), (1.65, 0.124, -0.146, 0.157, 0.06),
        (1.73, 0.115, -0.135, 0.153, 0.06), (1.80, 0.085, -0.095, 0.115, 0.045)]
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
    return 1.65 + 0.05 * max(0.0, -d.y) ** 2 - 0.12 * max(0.0, d.y) ** 1.5
N = 12
rings = [[pt(j, z, o) for j in range(N)] for z, o in ((1.79, 0.008), (1.76, 0.016))]
for v in (0.5, 1.0):
    rings.append([pt(j, 1.76 + (z_bottom(j) - 1.76) * v, 0.016) for j in range(N)])
rings.append([pt(j, z_bottom(j) + 0.012, -0.012) for j in range(N)])
P.loft([[Vector((0, 0.01, 1.805))]] + rings, "hair")
# head front surface (head-hero-square's profile) for the fringe
hp = [(1.535, 0.13, 0.136), (1.575, 0.132, 0.139), (1.615, 0.127, 0.139), (1.66, 0.124, 0.137), (1.7, 0.119, 0.13),
      (1.75, 0.108, 0.118)]
def face_y(x, z):
    for a, b in zip(hp, hp[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            sx, fy = a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t
            u = min(0.999, abs(x) / sx)
            return -fy * (1 - u ** 3.2) ** (1 / 3.2)
    return -0.1
fr = [(0.1, 1.715), (0.06, 1.7), (0.02, 1.682), (-0.02, 1.664), (-0.055, 1.65), (-0.085, 1.645), (-0.108, 1.655)]
path = [Vector((x, face_y(x, z) - 0.008, z)) for x, z in fr]
nrm = [Vector((x * 0.6, -1, 0)).normalized() for x, z in fr]
P.sweep(path, P.strap_profile(0.04, 0.016, 0.005, inset=0.012), "hair", nrm)
# locks in front of the ears, flicking out at the jaw
lock = P.loft([P.rrect((0.112 + dx, -0.035, z), sx, sy, min(sx, sy) * 0.5, seg=1) for z, dx, sx, sy in
               ((1.7, 0.0, 0.02, 0.03), (1.62, 0.004, 0.022, 0.032), (1.55, 0.006, 0.022, 0.03),
                (1.5, 0.018, 0.017, 0.024), (1.475, 0.034, 0.008, 0.012))], "hair")
P.mirror_x(lock)
# ponytail: a grey band on the back of the head, the tail out and down
def frame_rings(path, radii, n=8):
    out = []
    for k, (c, r) in enumerate(zip(path, radii)):
        a = path[max(0, k - 1)]; b = path[min(len(path) - 1, k + 1)]
        t = (b - a).normalized()
        u = Vector((1, 0, 0))
        w = t.cross(u).normalized()
        out.append([c + u * (r * math.cos(2 * math.pi * i / n)) + w * (r * math.sin(2 * math.pi * i / n))
                    for i in range(n)])
    return out
band = [Vector((0, 0.13, 1.6)), Vector((0, 0.165, 1.592)), Vector((0, 0.19, 1.586))]
P.loft(frame_rings(band, [0.034, 0.038, 0.036]), "metal")
tail = [Vector((0, 0.186, 1.588)), Vector((0, 0.22, 1.585)), Vector((0, 0.262, 1.56)), Vector((0, 0.282, 1.51)),
        Vector((0, 0.272, 1.46)), Vector((0, 0.245, 1.425))]
P.loft(frame_rings(tail, [0.042, 0.05, 0.054, 0.045, 0.03, 0.014]) + [[Vector((0, 0.232, 1.405))]], "hair")
hb = lm["head_base"].z
P.transform(list(P.bm.faces), Matrix.Translation((0, 0, hb)) @ Matrix.Diagonal((0.95, 0.95, 1.0, 1.0))
            @ Matrix.Translation((0, 0, -1.47)))
