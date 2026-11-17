# Tunic (lowpoly chibi, v2 detail pass, fitted to specs/rogue/reference): 10 facets flaring to mid-thigh, collar in
# `secondary`, a thick leather hem band standing proud of the cloth, a slit up the front (dark wedge); brown belt
# with a bevelled gold buckle frame and prong; a leather mantle round the shoulders (under a hood its top tucks in);
# a leather bandolier strap running diagonally round the body (right shoulder to left hip, where the satchel hangs).
# Legs are a separate part.
rings = [(0.77, 0.075, 0.07), (0.755, 0.15, 0.12), (0.72, 0.198, 0.148), (0.62, 0.2, 0.155), (0.52, 0.188, 0.148),
         (0.47, 0.192, 0.15), (0.40, 0.212, 0.163), (0.315, 0.229, 0.176), (0.31, 0.24, 0.186), (0.275, 0.244, 0.19),
         (0.27, 0.235, 0.181)]
P.loft([P.ring((0, 0, z), rx, ry, n=10) for z, rx, ry in rings],
       ["secondary"] + ["primary"] * 6 + ["secondary"] * 3, cap_roles=("secondary", "dark"))
P.loft([P.rrect((0, 0, 0.455), 0.2, 0.156, 0.06, seg=1), P.rrect((0, 0, 0.53), 0.2, 0.156, 0.06, seg=1)], "leather")
# buckle: bevelled gold frame on the belt front with a prong across it
yb, zb, hw, hh, ch = -0.16, 0.4925, 0.04, 0.034, 0.01
frame = [(hw - ch, -hh), (hw, -hh + ch), (hw, hh - ch), (hw - ch, hh), (-hw + ch, hh), (-hw, hh - ch),
         (-hw, -hh + ch), (-hw + ch, -hh)]
P.sweep([Vector((x, yb, zb + z)) for x, z in frame], [(-0.004, -0.007), (0.01, -0.007), (0.01, 0.007),
        (-0.004, 0.007)][::-1], "accent", [Vector((0, -1, 0))] * 8, cyclic=True)
P.rbox((-0.01, yb - 0.01, zb - 0.006), (0.024, yb + 0.004, zb + 0.006), "accent", r=0.004, bevel=0, seg=1, axis="y")
# front slit: a dark wedge lying on the cloth from the hem band up to 0.37
def front_y(z):
    for (z1, a1, b1), (z0, a0, b0) in zip(rings, rings[1:]):
        if z0 <= z <= z1:
            return b0 + (b1 - b0) * (z - z0) / (z1 - z0)
    return rings[-1][2]
P.shell([[Vector((-0.002, -front_y(0.37) - 0.002, 0.37)), Vector((0.002, -front_y(0.37) - 0.002, 0.37))],
         [Vector((-0.022, -front_y(0.316) - 0.002, 0.316)), Vector((0.022, -front_y(0.316) - 0.002, 0.316))],
         [Vector((-0.024, -0.192, 0.31)), Vector((0.024, -0.192, 0.31))],
         [Vector((-0.028, -0.192, 0.272)), Vector((0.028, -0.192, 0.272))]], 0.003, "dark")
# leather mantle round the shoulders: top tucked under the collar/hood, rising over the shoulder balls at the sides,
# a shallow point at the front and back
cols = [2 * math.pi * k / 16 for k in range(16)]
def mrow(rx, ry, zf, zs, drop=0.0, pw=2):
    out = []
    for t in cols:
        s, c = math.sin(t), math.cos(t)
        z = zf + (zs - zf) * abs(s) ** pw - drop * abs(c) ** 6
        out.append(Vector((rx * s, -ry * c, z)))
    return out
# closed loft: top (tucked in at the neck) -> upper face -> outer edge (2 cm thick) -> underside back into the body
# (front/back hang down onto the chest below a hood's rim; the sides stay above the T-pose sleeve tops, z 0.78)
P.loft([mrow(0.12, 0.105, 0.79, 0.79), mrow(0.2, 0.168, 0.75, 0.805), mrow(0.272, 0.205, 0.655, 0.805, 0.015, 4),
        mrow(0.266, 0.197, 0.632, 0.787, 0.015, 4), mrow(0.19, 0.155, 0.69, 0.76)], "leather")
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
