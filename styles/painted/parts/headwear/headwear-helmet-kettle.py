# Kettle helmet (painted chibi knight): pointed dome, gold rim band tilted down to the back, a
# horseshoe skirt whose cheek guards end beside the face (gold front edges), gold crest, rivets.
# v2: band, skirt and gold frame fitted to the knight sheet (overlay in workspace/knight-spike).
ZR, H, RX, RY, YC = 1.08, 0.292, 0.262, 0.278, 0.006   # dome base z, dome height, radii, y centre
# dome profile: relative height -> relative radius (measured on the front view: pointed, not round)
PROF = [(0.0, 1.0), (0.18, 0.985), (0.36, 0.93), (0.5, 0.86), (0.62, 0.77), (0.74, 0.64), (0.84, 0.49), (0.93, 0.3)]
N = 16
def band_z(phi):
    """centre height of the rim band (front higher than the back)"""
    return 1.08 - 0.024 * math.sin(phi)
def rad(t):
    for (a, ra), (b, rb) in zip(PROF, PROF[1:]):
        if t <= b:
            return ra + (rb - ra) * (t - a) / (b - a)
    return PROF[-1][1] * max(0.0, (1 - t) / (1 - PROF[-1][0]))
def pt(phi, t, out=0.0):
    r = rad(t)
    return Vector(((r * RX + out) * math.cos(phi), (r * RY + out) * math.sin(phi) + YC, ZR - 0.05 * (t == 0) + H * t))
angs = [math.radians(-90 + 360 * i / N) for i in range(N)]
TS = [t for t, _ in PROF]
outer = [[pt(a, t) for a in angs] for t in TS]
# the dome's lower rim follows the tilted band (hidden inside it), so no purple lip shows under it
outer[0] = [Vector((p.x, p.y, band_z(a) - 0.016)) for p, a in zip(outer[0], angs)]
# inner surface (hidden, painted dark): fewer rings than the outside
inner = [[(p - Vector((0, YC, ZR + H * t))) * 0.9 + Vector((0, YC, ZR + H * t)) for p in ring] for ring, t in zip(outer, TS) if t in (0.0, 0.5, 0.84)]
top_o, top_i = Vector((0, YC, ZR + H)), Vector((0, YC, ZR + H - 0.025))
rings = [[top_o]] + outer[::-1] + inner + [[top_i]]
nb = len(rings) - 1
P.loft(rings, lambda b, i: "metal" if b <= len(outer) else "dark")

# rim band (fitted to the sheet): 5 cm tall, tilted 4.8 cm down to the back, with a V point hanging
# down at the front (brow, to z 1.005) and at the back (to z 0.944)
M = 28
BAND_H = 0.026
def band_v(phi):
    x = abs((RX + 0.025) * math.cos(phi))
    if math.sin(phi) < 0:
        return 0.073 * max(0.0, 1 - x / 0.12)
    return 0.086 * max(0.0, 1 - x / 0.137)
bangs = [math.radians(-90 + 360 * i / M) for i in range(M)]
band = []
for dz in (BAND_H, -BAND_H):
    band.append([Vector(((RX + 0.025) * math.cos(a), (RY + 0.03) * math.sin(a) + YC,
                         band_z(a) + dz - (band_v(a) if dz < 0 else 0.0))) for a in bangs])
band.insert(1, [Vector((p.x * 1.02, (p.y - YC) * 1.02 + YC, (p.z + q.z) / 2)) for p, q in zip(*band)])
P.shell(band, -0.035, "accent", cyclic=True)

# skirt: horseshoe cross-section (front edges beside the face), from under the band down to z 0.85
half = [(0.165, -0.085), (0.215, -0.09), (0.265, -0.05), (0.285, 0.02), (0.275, 0.1), (0.24, 0.175), (0.17, 0.235), (0.085, 0.255)]
prof = half + [(0.0, 0.26)] + [(-x, y) for x, y in reversed(half)]
skirt = []
for z, fl in ((band_z(0) - 0.01, 1.0), (0.97, 1.01), (0.90, 1.025), (0.85, 1.04)):
    skirt.append([Vector((x * fl, y * fl + YC, z)) for x, y in prof])
sk = P.shell(skirt, -0.025, "metal")
gold = [f for f in sk if f.calc_center_median().y < -0.06 and abs(f.calc_center_median().x) < 0.225]  # gold frame, ~5 cm
P.set_role(gold, "accent")

# crest: gold strip over the dome from the band (front) to the band (back)
def crest_pt(side, t, w):
    r = rad(t) * RX + 0.012
    d = max(-1.0, min(1.0, w / max(r, 1e-4)))
    phi = (-math.pi / 2 + math.asin(d)) if side == "front" else (math.pi / 2 - math.asin(d))
    return pt(phi, t, out=0.012)
ts = [0.05, 0.25, 0.45, 0.62, 0.76, 0.88]
rows = [[crest_pt("front", t, w) for w in (0.04, 0.0, -0.04)] for t in ts]
rows += [[crest_pt("back", t, w) for w in (0.04, 0.0, -0.04)] for t in reversed(ts)]
P.shell(rows, -0.014, "accent")

# rivets: little 6-sided domes on the crest, the band and the cheek guards
def rivet(p, n, r=0.014):
    n = n.normalized()
    q = Vector((0, 0, 1)).rotation_difference(n)
    ring = [p + q @ v for v in P.ring((0, 0, 0), r, n=6)]
    return P.loft([[x - n * 0.003 for x in ring], [p + n * 0.011]], "accent")
for t in (0.3, 0.6):
    for side in ("front", "back"):
        c = crest_pt(side, t, 0.0)
        rivet(c, c - Vector((0, YC, ZR + H * t * 0.4)))
for i in range(10):
    a = math.radians(-90 + 360 * (i + 0.5) / 10)
    c = Vector(((RX + 0.027) * math.cos(a), (RY + 0.032) * math.sin(a) + YC, band_z(a)))
    rivet(c, Vector((math.cos(a), math.sin(a), 0)))
for z in (0.95, 0.88):
    P.mirror_x(rivet(Vector((0.19, -0.094, z)), Vector((0.1, -1, 0)), r=0.011))
