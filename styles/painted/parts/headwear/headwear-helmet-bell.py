# Bell helmet (painted chibi knight), v3 of the kettle helmet: same fitted dome, but chunky bevelled gold
# band and crest (P.sweep), thick cheek guards with bevelled gold frames, dome rivets, a broken hole.
ZR, H, RX, RY, YC = 1.08, 0.292, 0.262, 0.278, 0.006   # dome base z, dome height, radii, y centre
PROF = [(0.0, 1.0), (0.18, 0.985), (0.36, 0.93), (0.5, 0.86), (0.62, 0.77), (0.74, 0.64), (0.84, 0.49), (0.93, 0.3)]
N = 16
def band_z(phi):
    return 1.08 - 0.024 * math.sin(phi)
def rad(t):
    for (a, ra), (b, rb) in zip(PROF, PROF[1:]):
        if t <= b:
            return ra + (rb - ra) * (t - a) / (b - a)
    return PROF[-1][1] * max(0.0, (1 - t) / (1 - PROF[-1][0]))
def pt(phi, t, out=0.0):
    r = rad(t)
    return Vector(((r * RX + out) * math.cos(phi), (r * RY + out) * math.sin(phi) + YC, ZR + H * t))
def dome_n(p):
    """outward normal of the dome (ellipsoid-ish) at p"""
    d = p - Vector((0, YC, ZR))
    return Vector((d.x / RX ** 2, d.y / RY ** 2, max(d.z, 0) / H ** 2)).normalized()

# dome (metal outside, dark inside), lower rim hidden in the band
angs = [math.radians(-90 + 360 * i / N) for i in range(N)]
TS = [t for t, _ in PROF]
outer = [[pt(a, t) for a in angs] for t in TS]
outer[0] = [Vector((p.x, p.y, band_z(a) - 0.016)) for p, a in zip(outer[0], angs)]
inner = [[(p - Vector((0, YC, ZR + H * t))) * 0.9 + Vector((0, YC, ZR + H * t)) for p in ring] for ring, t in zip(outer, TS) if t in (0.0, 0.5, 0.84)]
top_o, top_i = Vector((0, YC, ZR + H)), Vector((0, YC, ZR + H - 0.025))
rings = [[top_o]] + outer[::-1] + inner + [[top_i]]
P.loft(rings, lambda b, i: "metal" if b <= len(outer) else "dark")

# band: bevelled strap around the dome base, V points hanging down at the brow and the back
M = 24
BW, BH, BB = 0.058, 0.03, 0.011          # width, thickness, bevel
def band_v(phi):
    x = abs((RX + 0.02) * math.cos(phi))
    if math.sin(phi) < 0:
        return 0.07 * max(0.0, 1 - x / 0.12)
    return 0.08 * max(0.0, 1 - x / 0.137)
bangs = [math.radians(-90 + 360 * i / M) for i in range(M)]
bpath = [Vector(((RX + 0.008) * math.cos(a), (RY + 0.01) * math.sin(a) + YC, band_z(a))) for a in bangs]
bnorm = [Vector((math.cos(a), math.sin(a), 0)) for a in bangs]
def band_prof(i):
    v, w, k = band_v(bangs[i]), BW / 2, BB   # side axis points down here
    return [(-0.012, -w), (BH - k, -w), (BH, -w + k), (BH, w - k + v), (BH - k, w + v), (-0.012, w + v)]
P.sweep(bpath, band_prof, "accent", bnorm, cyclic=True)

# crest: wide bevelled strap over the dome, front band to back band
ts = [0.02, 0.14, 0.28, 0.42, 0.56, 0.69, 0.81, 0.9]
cpath = [pt(-math.pi / 2, t) for t in ts] + [Vector((0, YC, ZR + H * 0.985))] + [pt(math.pi / 2, t) for t in reversed(ts)]
cnorm = [dome_n(p) for p in cpath]
P.sweep(cpath, P.strap_profile(0.08, 0.02, 0.009, inset=0.01), "accent", cnorm)

# cheek guards + neck skirt: thick horseshoe plate, flaring at the bottom
half = [(0.165, -0.085), (0.215, -0.09), (0.265, -0.05), (0.285, 0.02), (0.275, 0.1), (0.24, 0.175), (0.17, 0.235), (0.085, 0.255)]
prof = half + [(0.0, 0.26)] + [(-x, y) for x, y in reversed(half)]
SK = ((band_z(0) - 0.01, 1.0), (0.97, 1.015), (0.90, 1.035), (0.85, 1.06))
skirt = [[Vector((x * fl, y * fl + YC, z)) for x, y in prof] for z, fl in SK]
P.shell(skirt, -0.032, "metal")

# gold frame along each cheek guard's front edge, turning back along its lower edge
fpath, fnorm = [], []
for z, fl in SK:
    fpath.append(Vector((0.165 * fl + 0.004, -0.085 * fl + YC - 0.006, z)))
    fnorm.append(Vector((0.55, -0.83, 0)))
for x, y in half[1:4]:
    fl = SK[-1][1]
    fpath.append(Vector((x * fl, y * fl + YC, SK[-1][0] + 0.004)))
    fnorm.append(Vector((x, y, 0)).normalized())
fpath[3] = fpath[3] + Vector((0, 0, 0.012))       # corner: round it a little
frame = P.sweep(fpath, P.strap_profile(0.042, 0.014, 0.006, inset=0.012), "accent", fnorm)
P.mirror_x(frame)

# rivets: real domes on band, crest and frames
for i in range(12):
    a = math.radians(-90 + 360 * (i + 0.5) / 12)
    if abs(math.cos(a)) < 0.2:   # where the crest crosses the band
        continue
    p = Vector(((RX + 0.008 + BH) * math.cos(a), (RY + 0.01 + BH) * math.sin(a) + YC, band_z(a)))
    P.dome(p, (math.cos(a), math.sin(a), 0), 0.017, 0.013)
for t in (0.2, 0.42, 0.64):
    p = pt(-math.pi / 2, t)
    P.dome(p + dome_n(p) * 0.02, dome_n(p), 0.017, 0.013)
for t in (0.3, 0.6):
    p = pt(math.pi / 2, t)
    P.dome(p + dome_n(p) * 0.02, dome_n(p), 0.017, 0.013)
riv = []
for k in (1, 2):
    p = fpath[k] + fnorm[k] * 0.014
    riv += P.dome(p, fnorm[k], 0.014, 0.011)
P.mirror_x(riv)

# broken hole in the dome (upper front, the character's left): a dark jagged plate lying on the dome
# (a real hole would need booleans); its top is shallowly dished so the rim catches the light
hc_phi, hc_t = math.radians(-30), 0.6
c = pt(hc_phi, hc_t)
n = dome_n(c)
u = n.cross(Vector((0, 0, 1))).normalized()
w = n.cross(u)
jag = [0.095, 0.07, 0.088, 0.05, 0.075, 0.098, 0.062, 0.08, 0.052, 0.09, 0.072, 0.085, 0.058, 0.082]
def on_dome(q, out):
    phi = math.atan2((q.y - YC) / RY, q.x / RX)
    s = pt(phi, min(0.97, max(0.0, (q.z - ZR) / H)))
    return s + dome_n(s) * out
flat = [c + (u * math.cos(a) + w * math.sin(a) * 0.75) * r for a, r in
        zip([2 * math.pi * k / len(jag) for k in range(len(jag))], jag)]
lip = [on_dome(c + (q - c) * 0.8, 0.005) for q in flat]     # inner edge of the broken metal lip
ring_o = [on_dome(q, 0.007) for q in flat]
ring_i = [on_dome(c + (q - c) * 0.85, -0.012) for q in flat]
# bands: 0 = hole (dark, dished), 1 = lit metal lip, 2 = outer wall, 3 = underside
P.loft([[on_dome(c, -0.004)], lip, ring_o, ring_i, [on_dome(c, -0.02)]], lambda b, i: "metal" if b in (1, 2) else "dark")
