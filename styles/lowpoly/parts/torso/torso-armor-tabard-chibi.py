# Knight body (lowpoly chibi), fitted to specs/knight-lowpoly/reference: 10 facets; gold collar, steel cuirass down to the belt, a short tabard skirt
# (primary) flaring to mid-thigh with a gold hem; brown belt with a gold buckle. Legs are a separate part.
rings = [  # (z, rx, ry)
    (0.77, 0.075, 0.07), (0.755, 0.15, 0.12), (0.72, 0.2, 0.15), (0.62, 0.205, 0.16), (0.52, 0.19, 0.15),
    (0.47, 0.195, 0.152), (0.40, 0.215, 0.165), (0.30, 0.235, 0.18), (0.28, 0.238, 0.182)]
P.loft([P.ring((0, 0, z), rx, ry, n=10) for z, rx, ry in rings],
       ["accent", "metal", "metal", "metal", "metal", "primary", "primary", "accent"], cap_roles=("accent", "dark"))
P.loft([P.rrect((0, 0, 0.455), 0.203, 0.158, 0.06, seg=1), P.rrect((0, 0, 0.53), 0.203, 0.158, 0.06, seg=1)],
       "leather")
P.rbox((-0.035, -0.172, 0.46), (0.035, -0.15, 0.525), "accent", r=0.008, bevel=0, seg=1, axis="y")
# dark gorget under the chin, a gold collar with a V point at the front, a breastplate with a centre ridge
P.loft([P.ring((0, -0.005, 0.735), 0.105, 0.095, n=10), P.ring((0, -0.005, 0.8), 0.1, 0.09, n=10)], "dark")
def size(z):
    for (z1, a1, b1), (z0, a0, b0) in zip(rings, rings[1:]):
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0)
            return a0 + (a1 - a0) * t, b0 + (b1 - b0) * t
    return rings[0][1:]
def on(th, z, out):
    rx, ry = size(z)
    return Vector(((rx + out) * math.sin(th), -(ry + out) * math.cos(th), z))
cols = [math.radians(360 * k / 12) for k in range(12)]
P.shell([[on(t, 0.768, 0.012) for t in cols],
         [on(t, 0.735 - 0.045 * max(0.0, math.cos(t)) ** 6, 0.014) for t in cols]], 0.014, "accent", cyclic=True)
pl = [math.radians(a) for a in (-60, -30, 0, 30, 60)]
P.shell([[on(t, z, 0.008 + 0.012 * math.cos(t) ** 2) for t in pl] for z in (0.705, 0.55)], 0.012, "metal")
