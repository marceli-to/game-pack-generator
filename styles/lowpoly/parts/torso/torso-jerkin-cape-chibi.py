# Archer's tunic, jerkin and capelet (lowpoly chibi), fitted to specs/archer/reference: a moss-green tunic (10 facets)
# to below the hips with a short slit; over it a brown leather jerkin, open down the front so a strip of green shows,
# ending above the tunic hem; a leather belt with a big square gold buckle; a dark strap from the wearer's left
# shoulder (where the quiver hangs) to the right hip; a short team-red capelet round the shoulders, higher at the
# front, closed under the chin with a gold clasp. Legs are a separate part.
rings = [(0.77, 0.075, 0.07), (0.755, 0.15, 0.12), (0.72, 0.198, 0.148), (0.62, 0.2, 0.155), (0.52, 0.188, 0.148),
         (0.47, 0.192, 0.15), (0.40, 0.212, 0.163), (0.315, 0.229, 0.176), (0.25, 0.242, 0.188), (0.245, 0.232, 0.178)]
P.loft([P.ring((0, 0, z), rx, ry, n=10) for z, rx, ry in rings], "primary", cap_roles=("primary", "dark"))
def size(z):
    for (z1, a1, b1), (z0, a0, b0) in zip(rings, rings[1:]):
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0)
            return a0 + (a1 - a0) * t, b0 + (b1 - b0) * t
    return rings[-1][1:]
# front slit: a dark wedge on the cloth from the hem up to 0.3
def front_y(z):
    return -size(z)[1] * math.cos(math.pi / 10) - 0.002
P.shell([[Vector((-0.002, front_y(0.3), 0.3)), Vector((0.002, front_y(0.3), 0.3))],
         [Vector((-0.022, front_y(0.25), 0.25)), Vector((0.022, front_y(0.25), 0.25))]], 0.003, "dark")
# jerkin: an open sheet 1-2 cm over the tunic, from under the cape to above the hem, gap at the front
ths = [14 + (346 - 14) * k / 12 for k in range(13)]
def jrow(z, out=0.022, dz=0.0):
    rx, ry = size(z)
    return [Vector(((rx + out) * math.sin(math.radians(t)), -(ry + out) * math.cos(math.radians(t)), z + dz)) for t in ths]
P.shell([jrow(z) for z in (0.71, 0.61, 0.52, 0.44, 0.38, 0.335)], 0.012, "leather")
# belt + buckle
P.loft([P.rrect((0, 0, 0.41), 0.226, 0.18, 0.07, seg=1), P.rrect((0, 0, 0.485), 0.222, 0.177, 0.07, seg=1)], "leather")
yb, zb, hw, hh, ch = -0.196, 0.4475, 0.046, 0.042, 0.01
frame = [(hw - ch, -hh), (hw, -hh + ch), (hw, hh - ch), (hw - ch, hh), (-hw + ch, hh), (-hw, hh - ch),
         (-hw, -hh + ch), (-hw + ch, -hh)]
P.sweep([Vector((x, yb, zb + z)) for x, z in frame], [(-0.004, -0.009), (0.012, -0.009), (0.012, 0.009),
        (-0.004, 0.009)][::-1], "accent", [Vector((0, -1, 0))] * 8, cyclic=True)
# strap: wearer's left shoulder to right hip, round the body over the jerkin
path, nrm = [], []
for k in range(12):
    ph = 2 * math.pi * k / 12
    x = 0.2 * math.cos(ph)
    for _ in range(3):
        z = 0.6 + 0.8 * x
        rx, ry = size(min(0.72, max(0.25, z)))
        rx, ry = rx + 0.036, ry + 0.036
        x = rx * math.cos(ph)
    path.append(Vector((x, ry * math.sin(ph), z)))
    nrm.append(Vector((math.cos(ph) / rx, math.sin(ph) / ry, 0)).normalized())
P.sweep(path, P.strap_profile(0.04, 0.01, 0.003), "dark", nrm, cyclic=True)
# capelet: closed loft round the shoulders, top tucked in at the neck, outer edge highest at the front
cols = [2 * math.pi * k / 16 for k in range(16)]
def crow(rx, ry, zf, zs, zb):
    out = []
    for t in cols:
        s, c = math.sin(t), math.cos(t)
        wf, wb = max(0.0, c) ** 2, max(0.0, -c) ** 2
        out.append(Vector((rx * s, -ry * c, zs * s * s + zf * wf + zb * wb)))
    return out
P.loft([crow(0.12, 0.105, 0.815, 0.8, 0.8), crow(0.22, 0.2, 0.805, 0.79, 0.78), crow(0.355, 0.262, 0.71, 0.655, 0.625),
        crow(0.342, 0.25, 0.732, 0.68, 0.65), crow(0.19, 0.16, 0.765, 0.76, 0.74)], "secondary")
# clasp
P.rbox((-0.036, -0.238, 0.72), (0.036, -0.21, 0.79), "accent", r=0.008, bevel=0.004, seg=1, axis="y")
