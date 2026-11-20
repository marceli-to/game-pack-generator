# Shieldbearer helmet (lowpoly chibi), fitted to specs/shieldbearer/reference: a plain steel kettle/sallet, the
# knight helmet's dome and cheek/neck guard without gold band and crest, a little wider and taller (+-0.255, top
# 1.30); a raised steel ridge running from the brow over the top to the back; the brow edge juts forward with a
# shallow V over the nose; a round riveted disc on each side at the temple. All steel (`metal`).
P.covers = ["ears"]
def rr(z, sx, f, b, r, seg=2):
    return P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=seg)
# (z, half width, front y, back y, corner radius); the first ring is an inner flange that closes the rim towards
# the brow so the band never shows its underside above the face
prof = [(0.997, 0.2, -0.19, 0.2, 0.09), (1.003, 0.252, -0.25, 0.26, 0.12), (1.06, 0.252, -0.256, 0.262, 0.12),
        (1.12, 0.228, -0.238, 0.25, 0.115), (1.18, 0.19, -0.205, 0.222, 0.1), (1.23, 0.135, -0.155, 0.175, 0.07),
        (1.27, 0.07, -0.09, 0.105, 0.035), (1.295, 0.03, -0.035, 0.045, 0.015)]
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
    ear = min(1.0, max(0.0, 1 - (abs(abs(a) - 90) - 30) / 20)) * min(1.0, max(0.0, (z - 0.86) / 0.03))
    if ear > 0:
        need = 0.235 + gap + 0.006
        if abs(p.x) < need:
            p.x = math.copysign(abs(p.x) + (need - abs(p.x)) * ear, p.x)
    return p

# brow lip: a bevelled steel strip round the front half, its lower edge dipping to a shallow V over the nose
AN = [-96 + 96 * k / 4 for k in range(9)]
def lip_z(a):
    return 1.0 + 0.012 * min(1.0, abs(a) / 60) - 0.028 * max(0.0, 1 - abs(a) / 22)
path = [surf(a, lip_z(a) + 0.024, 0.004) for a in AN]
nrm = [Vector((math.sin(math.radians(a)), -math.cos(math.radians(a)), 0)) for a in AN]
def lprof(i):
    h = 0.024 + 0.012 * max(0.0, 1 - abs(AN[i]) / 22)
    return [(-0.006, -h), (0.012, -h), (0.02, -h + 0.01), (0.02, h - 0.006), (0.012, h), (-0.006, h)][::-1]
P.sweep(path, lprof, "metal", nrm)

# ridge: a raised flat strip from the brow over the top down the back
C = Vector((0, 0.01, 1.0))
pts = [surf(0, z, 0.0) for z in (1.05, 1.12, 1.18, 1.23, 1.27)] + [Vector((0, 0.005, 1.296))] + \
      [surf(180, z, 0.0) for z in (1.27, 1.23, 1.18, 1.12, 1.05)]
nrm = [(p - C).normalized() for p in pts]
P.sweep(pts, P.strap_profile(0.07, 0.02, 0.008)[::-1], "metal", nrm)

# cheek + neck guard (as the knight's): one shell round the sides and back, hugging the head at the cheeks
rows = []
for i, (z, a0, flare) in enumerate(((1.012, 44, 0.0), (0.94, 48, 0.008), (0.88, 52, 0.02), (0.83, 56, 0.04))):
    cols = [a0 + (360 - 2 * a0) * k / 12 for k in range(13)]
    row = []
    for a in cols:
        back = max(0.0, -math.cos(math.radians(a)))
        shell_p = surf(a, 1.012, 0.004 + flare * back)
        shell_p.z = z
        tight = hug(a, z, 0.014)
        w = (0.55 if i == 0 else 1.0) * (1 - back ** 0.7)
        row.append(shell_p.lerp(tight, w))
    rows.append(row)
P.shell(rows, 0.024, "metal")

# side discs at the temples: a flat ring with a raised boss, standing on the dome's side
for s in (1, -1):
    p = surf(90 * s, 1.03, 0.0) + Vector((0, 0.07, 0))
    p.x = s * (abs(p.x) + 0.004)
    n = Vector((s, 0, 0))
    P.loft([P.ring(p - n * 0.01, 0.048, n=8, axis="x"), P.ring(p + n * 0.008, 0.048, n=8, axis="x"),
            P.ring(p + n * 0.012, 0.03, n=8, axis="x"), P.ring(p + n * 0.024, 0.024, n=8, axis="x")], "metal")
