# Combat helmet with earcups and radio antenna (tinfox, hero-m), for specs/rifle-guard/reference: a rounded olive
# dome 2.5-3 cm over the hair, its rim low at the back (neck guard) and over the ears at the sides; a black visor
# strip across the brow standing a little proud; a wide orange stripe from the brow over the top to the nape;
# olive earcups over the ears (P.covers: ears); an orange earpiece on the wearer's left cup with an antenna and a
# ball on top, as on the guard's cap.
P.covers = ["ears"]
def rr(z, sx, f, b, r):
    return P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=3)
def tilted(zf, zb, sx, f, b, r):
    pts = rr(0.0, sx, f, b, r)
    return [Vector((p.x, p.y, zf + (zb - zf) * (p.y - f) / (b - f))) for p in pts]
# (z front, z back, half width, front y, back y, corner)
# v2 (fit: the sheet's helmet is lower and rounder on top): top 1.84, narrowing from 1.76 up
dome = [(1.69, 1.55, 0.158, -0.166, 0.192, 0.075), (1.715, 1.6, 0.164, -0.172, 0.2, 0.08),
        (1.76, 1.7, 0.154, -0.162, 0.19, 0.078), (1.8, 1.77, 0.126, -0.136, 0.162, 0.066),
        (1.828, 1.815, 0.082, -0.09, 0.112, 0.042), (1.842, 1.838, 0.036, -0.04, 0.05, 0.017)]
P.loft([tilted(*d) for d in dome], "primary", cap_roles=("dark", "primary"))
# centre stripe: front brow over the top to the back rim, on the dome's centre profile
prof = [(d[3], d[0]) for d in dome] + [(0.005, 1.845)] + [(d[4], d[1]) for d in reversed(dome)]
path = [Vector((0, y, z)) for y, z in prof[1:]]
nrm = []
for i, p in enumerate(path):
    a, b = path[max(0, i - 1)], path[min(len(path) - 1, i + 1)]
    t = (b - a).normalized()
    nrm.append(Vector((0, t.z, -t.y)) if Vector((0, t.z, -t.y)).dot(p - Vector((0, 0.01, 1.7))) > 0 else Vector((0, -t.z, t.y)))
P.sweep(path, P.strap_profile(0.07, 0.005, 0.002), "accent", nrm)
# visor strip across the brow: a band round the front, standing out at the bottom edge
cols = [math.radians(a) for a in range(-75, 76, 15)]
def vpt(a, z, out):
    return Vector(((0.168 + out) * math.sin(a), -(0.174 + out) * math.cos(a) ** 0.8, z - 0.035 * (1 - math.cos(a))))
P.shell([[vpt(a, 1.675, 0.03) for a in cols], [vpt(a, 1.7, 0.022) for a in cols], [vpt(a, 1.745, 0.008) for a in cols]],
        0.022, "secondary")
# earcups over the ears (head ears at x 0.13-0.16, z 1.58-1.65)
cups = P.rbox((0.135, -0.05, 1.555), (0.198, 0.06, 1.69), "primary", r=0.03, bevel=0.012, seg=2, axis="x")
P.mirror_x(cups)
# earpiece + antenna (wearer's left)
P.cylinder(Vector((0.19, 0.005, 1.625)), Vector((0.218, 0.005, 1.625)), 0.038, n=10, role="accent")
P.cylinder(Vector((0.19, 0.03, 1.68)), Vector((0.19, 0.04, 1.86)), 0.008, n=6, role="accent")
c = Vector((0.19, 0.04, 1.877))
P.loft([[c + Vector((0, 0, -0.02))]] + [P.ring(c + Vector((0, 0, 0.018 * s)), 0.02 * k, n=8) for s, k in
                                        ((-0.6, 0.8), (0.0, 1.0), (0.6, 0.8))] + [[c + Vector((0, 0, 0.02))]], "accent")
