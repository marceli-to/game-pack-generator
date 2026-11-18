# Hard hat (tinfox, hero-f), for specs/worker/reference: a white faceted dome on a wide brim that reaches furthest
# out at the front (peak), a raised crest from the front of the brim over the top to the back, a step at the dome's
# base. Sits on the brow; the ears show below it.
hb, ht = lm["head_base"].z, lm["head_top"].z
zb = ht - 0.115            # brim underside, just above the brows
def sring(z, sx, f, b, n=16, e=2.6):
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        s, c = math.sin(t), -math.cos(t)
        x = sx * math.copysign(abs(s) ** (2 / e), s)
        y = (f if c < 0 else b) * math.copysign(abs(c) ** (2 / e), c)
        pts.append(Vector((x, y, z)))
    return pts
# brim: a plate with a chamfered rim
P.loft([sring(zb, 0.186, 0.21, 0.19), sring(zb + 0.01, 0.196, 0.224, 0.2), sring(zb + 0.022, 0.196, 0.224, 0.2),
        sring(zb + 0.03, 0.18, 0.205, 0.184)], "secondary")
# dome (with a small step at the base)
dome = [(zb + 0.02, 0.168, 0.152, 0.178), (zb + 0.04, 0.168, 0.152, 0.178), (zb + 0.042, 0.162, 0.146, 0.172),
        (zb + 0.12, 0.16, 0.143, 0.17), (zb + 0.189, 0.142, 0.124, 0.152), (zb + 0.235, 0.104, 0.088, 0.114),
        (zb + 0.256, 0.052, 0.044, 0.058)]
P.loft([sring(*d) for d in dome] + [[Vector((0, 0.008, zb + 0.26))]], "secondary")
# crest: front of the brim over the top to the back, along the dome's centre line
cp = [(-0.205, zb + 0.03), (-0.148, zb + 0.063), (-0.143, zb + 0.12), (-0.124, zb + 0.189), (-0.088, zb + 0.235),
      (-0.044, zb + 0.256), (0.008, zb + 0.263), (0.058, zb + 0.256), (0.114, zb + 0.235), (0.152, zb + 0.189),
      (0.17, zb + 0.12), (0.177, zb + 0.063), (0.19, zb + 0.03)]
path = [Vector((0, y, z)) for y, z in cp]
nrm = []
for k in range(len(path)):
    a, b = path[max(0, k - 1)], path[min(len(path) - 1, k + 1)]
    t = (b - a).normalized()
    nrm.append(Vector((1, 0, 0)).cross(t).normalized() * -1)
P.sweep(path, P.strap_profile(0.07, 0.014, 0.004, inset=0.01), "secondary", nrm)
