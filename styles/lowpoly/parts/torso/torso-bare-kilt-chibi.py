# Berserker body (lowpoly chibi), from specs/berserker/reference: a bare muscular chest (skin, 12 sides, raised pec
# slabs) down to the belt; two dark leather straps crossing over the chest and the back (right shoulder -> left hip and
# left shoulder -> right hip) with a steel ring on the left one; a dark belt with a big steel G buckle; two leather
# pouches with flaps on the hips; a kilt in the team colour (`primary`) flaring to a jagged hem (pleat points, the
# front centre lowest); a grey-brown fur mantle (`secondary`) round the neck, over the shoulders and down the upper
# back with a jagged edge. Shoulder fur over the arms is in the arms part. Legs are a separate part.
N = 12
BODY = [(0.775, 0.085, 0.08), (0.76, 0.168, 0.13), (0.725, 0.214, 0.16), (0.665, 0.226, 0.17),
        (0.6, 0.216, 0.164), (0.53, 0.198, 0.152), (0.45, 0.2, 0.154), (0.44, 0.198, 0.152)]
KILT = [(0.475, 0.198, 0.152), (0.45, 0.212, 0.164), (0.34, 0.232, 0.182), (0.22, 0.252, 0.198)]
def rad(z, prof=BODY):
    for (z0, x0, y0), (z1, x1, y1) in zip(prof, prof[1:]):
        if z1 <= z <= z0:
            t = (z0 - z) / (z0 - z1)
            return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
    return prof[-1][1:] if z < prof[-1][0] else prof[0][1:]
def on(z, a, out=0.0, prof=BODY):
    """point on the body at height z, angle a (deg, 0 = front, + towards the wearer's left), pushed `out`"""
    rx, ry = rad(z, prof)
    t = math.radians(a)
    return Vector(((rx + out) * math.sin(t), -(ry + out) * math.cos(t), z))
def nrm(a):
    t = math.radians(a)
    return Vector((math.sin(t), -math.cos(t), 0))
P.loft([[on(z, 360 * k / N) for k in range(N)] for z, _, _ in BODY], "skin")
# pecs: a raised slab each side of the breastbone
for s in (1, -1):
    P.shell([[on(z, s * a, 0.012) for a in (5, 30, 55)][::s] for z in (0.685, 0.64, 0.585)], 0.016, "skin")
# kilt: flaring to a jagged hem, a bottom cap in dark (the legs pass through it)
hem = [0.22 if k == 0 else (0.235 if k % 2 else 0.255) for k in range(N)]
krings = [[on(z, 360 * k / N, prof=KILT) for k in range(N)] for z, _, _ in KILT[:-1]]
krings.append([on(hem[k], 360 * k / N, prof=KILT) for k in range(N)])
P.loft(krings, "primary", cap_roles=("primary", "dark"))
# straps: front and back, each from under the fur down to the belt; the second one 6 mm further out where they cross
def strap(a0, a1, out, back=False):
    zs = [0.74, 0.63, 0.53, 0.455]
    pts, ns = [], []
    for i, z in enumerate(zs):
        a = a0 + (a1 - a0) * i / (len(zs) - 1)
        a = 180 - a if back else a
        pts.append(on(z, a, out)); ns.append(nrm(a))
    return P.sweep(pts, [(-0.004, -0.025), (0.012, -0.022), (0.012, 0.022), (-0.004, 0.025)], "dark", ns)
strap(-38, 58, 0.004); strap(38, -58, 0.012)
strap(-38, 58, 0.004, back=True); strap(38, -58, 0.012, back=True)
# steel ring on the left strap (from the left shoulder), high on the chest
zr, ar = 0.655, 14
c = on(zr, ar, 0.022)
nr = nrm(ar)
side = Vector((0, 0, 1)).cross(nr).normalized()
ring = [c + side * 0.042 * math.cos(math.radians(22.5 + 45 * k)) + Vector((0, 0, 0.042 * math.sin(math.radians(22.5 + 45 * k))))
        for k in range(8)]
P.sweep(ring, [(-0.006, -0.009), (0.008, -0.009), (0.008, 0.009), (-0.006, 0.009)][::-1], "metal", [nr] * 8, cyclic=True)
# belt: thick, bevelled top and bottom
def bring(z, out):
    return [on(z, 360 * k / N, out) for k in range(N)]
P.loft([bring(0.43, 0.022), bring(0.438, 0.03), bring(0.5, 0.03), bring(0.508, 0.022)], "dark",
       cap_roles=("dark", "dark"))
# G buckle: a steel frame open at the right, with the inner bar
yb, zb = -rad(0.465)[1] - 0.04, 0.458
G = [(0.058, 0.03), (0.045, 0.048), (-0.045, 0.048), (-0.058, 0.035), (-0.058, -0.035), (-0.045, -0.048),
     (0.045, -0.048), (0.058, -0.035), (0.058, 0.0), (0.012, 0.0)]
P.sweep([Vector((x, yb, zb + z)) for x, z in G], [(-0.004, -0.009), (0.012, -0.009), (0.012, 0.009),
        (-0.004, 0.009)][::-1], "metal", [Vector((0, -1, 0))] * len(G))
# pouches: a box with a flap on each hip, hanging from the belt
for s in (1, -1):
    a = s * 58
    M = Matrix.Translation(on(0.37, a, 0.04)) @ Matrix.Rotation(math.radians(-a), 4, "Z")
    pf = P.rbox((-0.055, -0.03, -0.06), (0.055, 0.03, 0.055), "leather", r=0.012, bevel=0, seg=1, axis="y")
    pf += P.box((-0.06, -0.038, 0.0), (0.06, 0.018, 0.065), "leather")
    P.transform(pf, M)
# fur mantle: round the neck, over the shoulders and down the back, jagged edge; 16 columns
M16 = 12
def fur_hem(k):
    a = 360 * k / M16
    back = (1 - math.cos(math.radians(a))) / 2                    # 0 front, 1 back
    return 0.73 - 0.1 * back + (0.035 if k % 2 else 0.0)
rows = [[Vector((0.13 * math.sin(math.radians(360 * k / M16)), -0.12 * math.cos(math.radians(360 * k / M16)) + 0.01, 0.815))
         for k in range(M16)],
        [on(0.76, 360 * k / M16, 0.05) for k in range(M16)],
        [on(0.5 * (0.76 + fur_hem(k)), 360 * k / M16, 0.055) for k in range(M16)],
        [on(fur_hem(k), 360 * k / M16, 0.04) for k in range(M16)]]
P.shell(rows, -0.035, "secondary", cyclic=True)
