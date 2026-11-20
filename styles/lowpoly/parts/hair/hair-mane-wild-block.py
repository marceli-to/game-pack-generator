# Wild mane (lowpoly chibi, bare heads), from specs/berserker/reference: a core cap over the crown following the
# head's facets 2.5 cm out (12 columns), its lower edge at the hairline in front (1.065), above the ears at the sides
# and down to the nape at the back, tucked into the head; on it ~30 broad pointed tufts (4-sided, flattened, bent
# upwards and back), in rings: a crown pointing up and back, an upper ring up and out, a middle ring out at the sides
# and back (the mane's width beside the face), a lower ring out and down behind the ears to z ~0.8, and short
# tufts at the hairline pointing up. Not for headwear.
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
    return 1.0 + 0.065 * max(0.0, -d.y) ** 2 - 0.17 * max(0.0, d.y)
def thin(j):
    """the core stands off less at the front, so the hairline reads as an edge, not a brim"""
    d = Vector((ref[j].x, ref[j].y, 0)).normalized()
    return 0.35 if d.y < -0.5 else 1.0
rings = [[pt(j, z, o * (1 if z > 1.2 else thin(j))) for j in range(N)] for z, o in ((1.215, 0.02), (1.165, 0.04), (1.1, 0.045))]
for v in (0.55, 1.0):
    rings.append([pt(j, 1.1 + (z_bottom(j) - 1.1) * v, (0.045 - 0.01 * v) * thin(j)) for j in range(N)])
rings.append([pt(j, z_bottom(j) + 0.012, -0.015) for j in range(N)])
P.loft([[Vector((0, 0, 1.25))]] + rings, "hair")
# tufts: broad flat leaves lying on the mane, flowing up and back like flames; each 4-sided, bulging out at the
# middle. (azimuth deg, 0 = front, + towards the wearer's left; elevation deg; length; half width; flow)
C = Vector((0, 0.02, 1.02))
R = Vector((0.215, 0.205, 0.2))
UPBACK = Vector((0, 0.8, 0.6))
def tuft(az, el, L, w, flow=UPBACK, lift=0.5):
    a, e = math.radians(az), math.radians(el)
    d = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
    base = C + Vector((d.x * R.x, d.y * R.y, d.z * R.z))
    f = Vector(flow) - d * Vector(flow).dot(d)
    out = (d * lift + (f.normalized() if f.length > 1e-3 else d)).normalized()
    t = d.cross(out).normalized()
    n = out.cross(t).normalized()
    if n.dot(d) < 0: n = -n
    def ring(c, s):
        return [c + t * w * s, c + n * w * 0.35 * s, c - t * w * s, c - n * w * 0.35 * s]
    mid = base + out * L * 0.45 + n * 0.025
    tip = base + out * L + n * 0.01
    return P.loft([ring(base - out * 0.02, 1.0), ring(mid, 0.85), [tip]], "hair")
for az in (-90, 0, 90, 180):                                       # crown
    tuft(az, 68, 0.17, 0.085)
for az in (-140, -95, -50, 50, 95, 140, 180):                      # upper ring
    tuft(az, 38, 0.18, 0.09)
for az in (-155, -115, -75, 75, 115, 155):                         # middle ring: out beside the face, and back
    sx = math.copysign(1, az)
    tuft(az, 8, 0.17, 0.09, Vector((0.7 * sx, 0.6, 0.15)), 0.9)
for az in (-145, -100, 100, 145, 180):                             # lower ring: out and down behind the ears
    sx = math.copysign(1, az) if az != 180 else 0
    tuft(az, -25, 0.15, 0.085, Vector((0.5 * sx, 0.5, -0.6)), 0.9)
for az in (-28, 28):                                               # hairline: standing up
    tuft(az, 50, 0.12, 0.075, Vector((0.3 * math.copysign(1, az), 0, 1.0)), 0.8)
tuft(0, 55, 0.14, 0.08, Vector((0, 0.1, 1.0)), 0.8)
tuft(0, 30, 0.07, 0.05, Vector((0, -0.2, -1.0)), 0.3)          # widow's peak: a V over the forehead
