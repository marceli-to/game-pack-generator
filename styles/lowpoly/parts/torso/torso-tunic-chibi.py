# Tunic (lowpoly chibi): 10 facets, collar and hem in `secondary`, flaring to mid-thigh; brown belt, and a leather
# bandolier strap running diagonally round the body (right shoulder to left hip, where the satchel hangs). Legs are a separate part.
rings = [(0.77, 0.075, 0.07), (0.755, 0.15, 0.12), (0.72, 0.198, 0.148), (0.62, 0.2, 0.155), (0.52, 0.188, 0.148),
         (0.47, 0.192, 0.15), (0.40, 0.212, 0.163), (0.30, 0.232, 0.178), (0.28, 0.235, 0.18)]
P.loft([P.ring((0, 0, z), rx, ry, n=10) for z, rx, ry in rings],
       ["secondary"] + ["primary"] * 6 + ["secondary"], cap_roles=("secondary", "dark"))
P.loft([P.rrect((0, 0, 0.455), 0.2, 0.156, 0.06, seg=1), P.rrect((0, 0, 0.53), 0.2, 0.156, 0.06, seg=1)], "leather")
P.rbox((-0.03, -0.17, 0.465), (0.03, -0.15, 0.52), "accent", r=0.008, bevel=0, seg=1, axis="y")
def size(z):
    for (z1, a1, b1), (z0, a0, b0) in zip(rings, rings[1:]):
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0)
            return a0 + (a1 - a0) * t, b0 + (b1 - b0) * t
    return rings[-1][1:]
path, nrm = [], []
for k in range(16):
    ph = 2 * math.pi * k / 16
    x = 0.2 * math.cos(ph)
    for _ in range(3):
        z = 0.6 - 0.85 * x
        rx, ry = size(z)
        rx, ry = rx + 0.004, ry + 0.004
        x = rx * math.cos(ph)
    path.append(Vector((x, ry * math.sin(ph), z)))
    nrm.append(Vector((math.cos(ph) / rx, math.sin(ph) / ry, 0)).normalized())
P.sweep(path, P.strap_profile(0.04, 0.012, 0.004), "leather", nrm, cyclic=True)
