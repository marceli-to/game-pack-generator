# Knight helmet (lowpoly chibi), fitted to specs/knight-lowpoly/reference (v3, detail pass): a tall round dome
# (12-point rounded rings) flaring into a neck guard at the back; a thick bevelled gold brow band over the front
# half only, chevron-shaped (point up at the centre, dipping at the brow), sloping down towards the ears; a raised
# steel nose ridge from the band to the crest; slanted cheek guards close round the face; a chunky red crest that
# arches from the forehead over the top and hangs down behind.
def rr(z, sx, f, b, r, seg=2):
    return P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=seg)
# (z, half width, front y, back y, corner radius); the first ring is an inner flange that closes the rim towards
# the brow so the band never shows its underside above the face
prof = [(0.997, 0.19, -0.18, 0.19, 0.09), (1.003, 0.244, -0.222, 0.248, 0.115), (1.06, 0.243, -0.23, 0.247, 0.12),
        (1.12, 0.23, -0.224, 0.238, 0.115), (1.17, 0.205, -0.205, 0.222, 0.1), (1.22, 0.155, -0.155, 0.172, 0.075),
        (1.258, 0.095, -0.092, 0.11, 0.045), (1.276, 0.035, -0.03, 0.045, 0.015)]
P.loft([rr(*p) for p in prof], "metal", cap_roles=("dark", "metal"))

def ray(ring_def, a, z):
    """Distance from the ring centre to a rounded-rect ring (sx, f, b, r, seg) along angle a (deg, 0 = front)."""
    sx, f, b, r, seg = ring_def
    cy, hy = (f + b) / 2, (b - f) / 2
    d = Vector((math.sin(math.radians(a)), -math.cos(math.radians(a))))
    ring = P.rrect((0, cy, z), sx, hy, r, seg=seg)
    best = 0.0
    for q0, q1 in zip(ring, ring[1:] + ring[:1]):
        a0, e = Vector((q0.x, q0.y - cy)), Vector((q1.x - q0.x, q1.y - q0.y))
        den = d.x * e.y - d.y * e.x
        if abs(den) < 1e-12:
            continue
        t_ = (a0.x * e.y - a0.y * e.x) / den
        u_ = (a0.x * d.y - a0.y * d.x) / den
        if t_ > 0 and -1e-9 <= u_ <= 1 + 1e-9:
            best = t_
    return cy, d, best
def lerp_prof(pr, z):
    for (z0, *p0), (z1, *p1) in zip(pr, pr[1:]):
        if z <= z1 or (z0, *p0) == pr[-2]:
            t = min(1.0, max(0.0, (z - z0) / (z1 - z0)))
            return [u + (v - u) * t for u, v in zip(p0, p1)]
def surf(a, z, off=0.0):
    """Point on the dome at angle a (deg, 0 = front, + towards the wearer's left) and height z, pushed `off` out."""
    sx, f, b, r = lerp_prof(prof[1:], z)
    cy, d, t_ = ray((sx, f, b, r, 4), a, z)
    return Vector((0, cy, z)) + Vector((d.x, d.y, 0)) * (t_ + off)
# the head this helmet sits on (head-chibi-block: z, half width, front y, back y, chamfer), for the guards
HEAD = [(0.79, 0.11, -0.12, 0.08, 0.05), (0.85, 0.17, -0.17, 0.14, 0.07), (0.97, 0.19, -0.18, 0.165, 0.08),
        (1.08, 0.18, -0.172, 0.16, 0.08), (1.2, 0.12, -0.11, 0.11, 0.05)]
def hug(a, z, gap):
    """Point `gap` outside the head at angle a and height z; clears the ears (x 0.235, z 0.93-1.04, |y| < 0.035)."""
    sx, f, b, r = lerp_prof(HEAD, z)
    cy, d, t_ = ray((sx, f, b, r, 1), a, z)
    p = Vector((0, cy, z)) + Vector((d.x, d.y, 0)) * (t_ + gap)
    a = (a + 180) % 360 - 180   # the guard runs 46..314 deg: the wearer's right ear is at 270 = -90
    # full clearance from 60 to 120 deg (the ear spans ~80-100), fading out by 40 / 140
    ear = min(1.0, max(0.0, 1 - (abs(abs(a) - 90) - 30) / 20)) * min(1.0, max(0.0, (z - 0.9) / 0.03))
    if ear > 0:
        need = 0.235 + gap + 0.006
        if abs(p.x) < need:
            p.x = math.copysign(abs(p.x) + (need - abs(p.x)) * ear, p.x)
    return p

# brow band: a bevelled block swept round the front, 13 points from -98 to 98 deg; bottom edge from 0.985 at
# the front down to 0.93 at the ends, top edge rising to a chevron point (1.135) at the centre
AN = [-98 + 98 * k / 7 for k in range(15)]
def band_z(a):   # bottom edge: rises from the ears to the brow, a small dip at the centre
    s = min(1.0, max(0.0, (abs(a) - 18) / 80))
    return 1.022 - 0.062 * s ** 1.5 - 0.016 * max(0.0, 1 - abs(a) / 16)
def band_h(a):    # even height, a chevron point at the centre
    return 0.062 + 0.078 * max(0.0, 1 - abs(a) / 32) ** 1.2
def band_off(a):  # clear the cheek guards at the sides
    return 0.016 * min(1.0, max(0.0, (abs(a) - 40) / 30))
path = [surf(a, band_z(a) + band_h(a) / 2, band_off(a)) for a in AN]
nrm = [Vector((math.sin(math.radians(a)), -math.cos(math.radians(a)), 0)) for a in AN]
def bprof(i):
    h, k = band_h(AN[i]) / 2, 0.012
    return [(-0.006, -h), (0.018, -h), (0.028, -h + k), (0.028, h - k), (0.018, h), (-0.006, h)][::-1]
P.sweep(path, bprof, "accent", nrm)

# nose ridge: a raised steel strip from the chevron point up over the dome towards the crest
rz = [1.12, 1.16, 1.195, 1.228]
path = [surf(0, z, 0.0) for z in rz]
nrm = [Vector((0, -1, 0.25)), Vector((0, -1, 0.6)), Vector((0, -1, 1.0)), Vector((0, -0.6, 1.4))]
P.sweep(path, lambda i: P.strap_profile(0.062 - 0.008 * i, 0.022, 0.008)[::-1], "metal", nrm)

# cheek + neck guard: one shell round the sides and back below the dome; its inner surface hugs the head (1.2 cm
# out, clearing the ears) at the cheeks and sides, blending into the dome rim at the top and into a flared neck
# guard at the back; the front edge slants back towards the jaw
rows = []
for i, (z, a0, flare) in enumerate(((1.012, 46, 0.0), (0.94, 50, 0.006), (0.88, 55, 0.016), (0.835, 60, 0.034))):
    cols = [a0 + (360 - 2 * a0) * k / 12 for k in range(13)]
    row = []
    for a in cols:
        back = max(0.0, -math.cos(math.radians(a)))          # 0 at the sides/front, 1 at the back
        shell_p = surf(a, 1.012, 0.004 + flare * back)
        shell_p.z = z
        tight = hug(a, z, 0.012)
        w = (0.55 if i == 0 else 1.0) * (1 - back ** 0.7)
        row.append(shell_p.lerp(tight, w))
    rows.append(row)
P.shell(rows, 0.022, "metal")

# crest: sections across an arc in the YZ plane (centre y 0.06, z 1.1) from the forehead to behind the helmet;
# each section a chamfered block, narrow at the dome and widest near the top (a brush)
C = Vector((0, 0.06, 1.1))
def sec(t, rin, rout, w):
    tt = math.radians(t)
    rad, tan = Vector((0, math.sin(tt), math.cos(tt))), Vector((0, math.cos(tt), -math.sin(tt)))
    h = rout - rin
    xr = [(0.5 * w, rin), (w, rin + 0.35 * h), (w, rout - 0.22 * h), (0.6 * w, rout),
          (-0.6 * w, rout), (-w, rout - 0.22 * h), (-w, rin + 0.35 * h), (-0.5 * w, rin)]
    return [C + Vector((x, 0, 0)) + rad * r for x, r in xr]
st = [(-36, 0.15, 0.27, 0.045), (-22, 0.15, 0.31, 0.075), (-5, 0.15, 0.33, 0.1), (15, 0.15, 0.335, 0.105),
      (38, 0.15, 0.32, 0.1), (60, 0.15, 0.295, 0.085), (78, 0.15, 0.27, 0.065), (90, 0.16, 0.24, 0.04)]
P.loft([sec(*s) for s in st], "secondary")
