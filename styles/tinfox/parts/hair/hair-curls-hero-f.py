# Big curly hair (tinfox, hero-f; player 4), from specs/player-4/reference: a rounded hair mass over the head plus
# ~34 chunky faceted curls (five-sided double pyramids, each turned differently) all round it: along the hairline
# over the forehead, big on the top and sides, framing the face in front of and behind the ears down to the jaw,
# over the nape at the back. Built in hero-m coordinates and moved onto the hero-f head at the end (as head-hero-f).
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
    p = P.rrect((0, (f + b) / 2, z), sx + o, (b - f) / 2 + o, r + o, seg=2)[j]
    return Vector((p.x, p.y, z))
ref = P.rrect((0, 0, 0), 1, 1, 0.5, seg=2)
def z_bottom(j):
    d = Vector((ref[j].x, ref[j].y, 0)).normalized()
    return 1.64 + 0.085 * max(0.0, -d.y) ** 2 - 0.1 * max(0.0, d.y) ** 1.5
N = 12
rings = [[pt(j, z, o) for j in range(N)] for z, o in ((1.826, -0.03), (1.8, 0.012), (1.75, 0.03))]
rings.append([pt(j, z_bottom(j), 0.024) for j in range(N)])
rings.append([pt(j, z_bottom(j) + 0.012, -0.012) for j in range(N)])
P.loft([[Vector((0, 0.01, 1.835))]] + rings, "hair")
# curls: (azimuth, elevation, radius); azimuth 0 = front (-Y), 90 = wearer's left; on an ellipsoid round the head
C, R = Vector((0, 0.012, 1.66)), (0.185, 0.185, 0.17)
CURLS = []
for el, n, r, skip in ((78, 3, 0.06, 0), (50, 7, 0.062, 0), (26, 9, 0.058, 0), (2, 8, 0.056, 62),
                       (-22, 6, 0.054, 78), (-44, 4, 0.05, 95)):
    for k in range(n):
        az = -180 + (360 / n) * (k + 0.5 * (el % 2 == 0)) + 11 * ((k * 7 + el) % 3 - 1)
        if abs(((az + 180) % 360) - 180) < skip:
            continue
        CURLS.append((az, el, r * (0.85 + 0.3 * ((k * 5 + el) % 4) / 3)))
# fringe curls over the forehead, just above the brows
CURLS += [(-26, 18, 0.046), (34, 17, 0.044)]
def ball(c, r, k):
    top, bot = Vector((0, 0, 1.0 * r)), Vector((0, 0, -1.0 * r))
    up = [Vector((0.9 * r * math.cos(2 * math.pi * i / 5), 0.9 * r * math.sin(2 * math.pi * i / 5), 0.4 * r)) for i in range(5)]
    dn = [Vector((0.9 * r * math.cos(2 * math.pi * (i + 0.5) / 5), 0.9 * r * math.sin(2 * math.pi * (i + 0.5) / 5), -0.4 * r))
          for i in range(5)]
    f = P.loft([[top], up, dn, [bot]], "hair")
    M = (Matrix.Translation(c) @ Matrix.Rotation(math.radians(37 * k), 4, "Z") @ Matrix.Rotation(math.radians(23 * k + 11), 4, "X"))
    P.transform(f, M)
for k, (az, el, r) in enumerate(CURLS):
    a, e = math.radians(az), math.radians(el)
    d = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
    c = C + Vector((R[0] * d.x, R[1] * d.y, R[2] * d.z)) - d * 0.012
    ball(c, r, k)
hb = lm["head_base"].z
P.transform(list(P.bm.faces), Matrix.Translation((0, 0, hb)) @ Matrix.Diagonal((0.95, 0.95, 1.0, 1.0))
            @ Matrix.Translation((0, 0, -1.47)))
