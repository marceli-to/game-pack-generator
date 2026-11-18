# Spiky messy hair (tinfox, hero-m; player 1, specs/player-1/reference): the short-hair cap below + chunky
# five-sided spikes: a fringe pointing up and forward, a crown standing up, tufts out at the sides and down
# over the nape (slightly asymmetric, messy). Cap from the short hair: a closed loft over the head 1.6 cm out (12 columns), its lower edge
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
# v2 (Marcel: forehead): the mass itself is jagged, as on the sheet: 24 columns, every other column pushed out (and
# up near the crown) as a point, the points shifting one column per ring so they twist into faceted shards; at the
# front the lower edge dips into fringe points over the forehead; a little irregular (messy)
SEG = 5
N = 4 * (SEG + 1)
ref = P.rrect((0, 0, 0), 1, 1, 0.4, seg=SEG)
def pt(j, z, o):
    sx, f, b, r = dims(z)
    p = P.rrect((0, (f + b) / 2, z), sx + o, (b - f) / 2 + o, r + 0.4 * o, seg=SEG)[j]
    return Vector((p.x, p.y, z))
def hdir(j):
    return Vector((ref[j].x, ref[j].y, 0)).normalized()
def z_bottom(j):
    d = hdir(j)
    return 1.645 + 0.065 * max(0.0, -d.y) ** 2 - 0.08 * max(0.0, d.y) ** 1.5   # hairline 1.71, nape 1.565
def messy(j, i):
    return 0.6 + 0.8 * ((j * 37 + i * 11) % 7) / 6
def jag(i, z, o, out, up):
    ring = []
    for j in range(N):
        q = pt(j, z, o)
        if (j + i) % 2 == 0:
            m = messy(j, i)
            q = q + hdir(j) * (out * m) + Vector((0, 0, up * m))
        ring.append(q)
    return ring
rings = [jag(0, 1.835, 0.0, 0.0, 0.05), jag(1, 1.81, 0.008, 0.026, 0.04), jag(2, 1.775, 0.04, 0.03, 0.018),
         jag(3, 1.74, 0.044, 0.03, -0.004)]
mid = [pt(j, 1.74 + (z_bottom(j) - 1.74) * 0.5, 0.032) for j in range(N)]
rings.append([q + hdir(j) * (0.014 * messy(j, 4)) if j % 2 else q for j, q in enumerate(mid)])
def fringe_dip(j):
    d = hdir(j)
    return (0.05 * messy(j, 5) * max(0.0, -d.y) ** 3) if j % 2 == 0 else 0.0
rings.append([pt(j, z_bottom(j) - fringe_dip(j), 0.018) for j in range(N)])
rings.append([pt(j, z_bottom(j) + 0.012, -0.012) for j in range(N)])
P.loft([[Vector((0, 0.01, 1.85))]] + rings, "hair")
side = P.rbox((0.112, -0.052, 1.575), (0.128, -0.024, 1.68), "hair", r=0.006, bevel=0, seg=1, axis="z")
P.mirror_x(side)

# locks: flat shards (a flattened diamond tapering to a point), lying along the hair and lifting off it, so they
# read as big planes like the sheet's, not cones.
# (base azimuth, base elevation, pointing azimuth, pointing elevation, width, length); azimuth 0 = front (-Y),
# 90 = wearer's left (+X); elevation from the horizontal
C, R = Vector((0, 0.005, 1.67)), (0.165, 0.18, 0.175)
def on_hair(az, el):
    az, el = math.radians(az), math.radians(el)
    return C + Vector((R[0] * math.sin(az) * math.cos(el), -R[1] * math.cos(az) * math.cos(el), R[2] * math.sin(el)))
def direction(az, el):
    az, el = math.radians(az), math.radians(el)
    return Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
LOCKS = [
    # a few big shards on top of the jagged mass: two up and forward over the fringe, two up and back on the crown
    (-10, 45, -15, 70, 0.12, 0.08), (25, 45, 35, 68, 0.11, 0.07),
    (150, 60, 165, 62, 0.12, 0.07), (-155, 60, -170, 60, 0.11, 0.065)]
for baz, bel, paz, pel, w, L in LOCKS:
    d = direction(paz, pel)
    b0 = on_hair(baz, bel)
    nrm = (b0 - C).normalized()
    nrm = (nrm - d * nrm.dot(d)).normalized()       # thickness direction: off the hair surface
    side = d.cross(nrm)
    base = b0 - d * 0.03 - nrm * 0.012
    ring_ = [base + side * (w / 2), base + nrm * 0.018, base - side * (w / 2), base - nrm * 0.012]
    tip = base + d * (L + 0.03) + nrm * 0.004
    P.loft([ring_, [tip]], "hair")
