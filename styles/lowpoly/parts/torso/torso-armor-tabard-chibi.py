# Knight body (lowpoly chibi), fitted to specs/knight-lowpoly/reference (v3, detail pass): a steel breastplate
# (12 sides) with a chest ridge at the front and a crease under the chest; dark gorget and a gold collar with a V
# point; a thick brown belt with a bevelled gold buckle frame and prong; a blue tabard split at the front (the slit
# widens towards the hem), gold trim running up both slit edges and round the hem.
# Legs are a separate part.
N = 12
def ring(z, rx, ry, bulge=0.0, flat=0.0):
    """12-point ring, vertex at the front centre; bulge pushes the front forward (chest ridge), flat pulls the
    back in a little."""
    pts = []
    for k in range(N):
        th = 2 * math.pi * k / N
        c, s = math.cos(th), math.sin(th)
        y = -ry * c - bulge * max(0.0, c) ** 3 + flat * max(0.0, -c)
        pts.append(Vector((rx * s, y, z)))
    return pts
# breastplate: neck -> shoulders -> chest (ridge) -> crease under the chest -> waist (inside the belt)
plate = [(0.772, 0.08, 0.075, 0, 0), (0.758, 0.15, 0.12, 0, 0), (0.725, 0.192, 0.145, 0.0, 0),
         (0.665, 0.2, 0.152, 0.045, 0.006), (0.61, 0.192, 0.148, 0.055, 0.006), (0.578, 0.172, 0.136, 0.006, 0.004),
         (0.535, 0.182, 0.144, 0.016, 0.004), (0.5, 0.182, 0.144, 0.01, 0.0)]
P.loft([ring(*p) for p in plate], "metal", cap_roles=("metal", "metal"))
# belt: thick, bevelled top and bottom
belt = [(0.442, 0.196, 0.156), (0.45, 0.204, 0.164), (0.52, 0.204, 0.164), (0.528, 0.196, 0.156)]
P.loft([ring(z, rx, ry) for z, rx, ry in belt], "leather", cap_roles=("leather", "leather"))
# buckle: a bevelled gold frame on the belt front (sweep round a chamfered rectangle) with a prong across it
yb, zb, hw, hh, ch = -0.172, 0.485, 0.05, 0.045, 0.012
frame = [(hw - ch, -hh), (hw, -hh + ch), (hw, hh - ch), (hw - ch, hh), (-hw + ch, hh), (-hw, hh - ch),
         (-hw, -hh + ch), (-hw + ch, -hh)]
P.sweep([Vector((x, yb, zb + z)) for x, z in frame], [(-0.004, -0.009), (0.012, -0.009), (0.012, 0.009),
        (-0.004, 0.009)][::-1], "accent", [Vector((0, -1, 0))] * 8, cyclic=True)
P.rbox((-0.012, yb - 0.012, zb - 0.008), (0.03, yb + 0.004, zb + 0.008), "accent", r=0.004, bevel=0, seg=1, axis="y")
# tabard: one sheet round the body from the right slit edge, round the back, to the left slit edge; the slit is
# 2 x 1.5 deg wide under the belt and 2 x 9 deg at the hem; the skirt flares out
rows_def = [(0.452, 0.198, 0.158, 2.0), (0.38, 0.21, 0.168, 4.0), (0.3, 0.226, 0.182, 7.0), (0.235, 0.236, 0.19, 9.0)]
def skirt_pt(z, rx, ry, a):
    t = math.radians(a)
    return Vector((rx * math.sin(t), -ry * math.cos(t) - 0.006 * max(0.0, math.cos(t)) ** 3, z))
rows, edges = [], []
for z, rx, ry, g in rows_def:
    cols = [g + (360 - 2 * g) * k / 14 for k in range(15)]
    rows.append([skirt_pt(z, rx, ry, a) for a in cols])
P.shell(rows, 0.012, "primary")
# gold trim: up the right slit edge, round the hem, up the left slit edge (one bevelled strip)
def off(p, d):
    n = Vector((p.x, p.y, 0)).normalized()
    return p + n * d
right = [skirt_pt(z, rx, ry, g + 2.2) for z, rx, ry, g in rows_def]       # wearer's left side of the slit (+X)
hem = [skirt_pt(rows_def[-1][0] + 0.016, rows_def[-1][1], rows_def[-1][2], rows_def[-1][3] + (360 - 2 * rows_def[-1][3]) * k / 14)
       for k in range(15)]
left = [skirt_pt(z, rx, ry, 360 - g - 2.2) for z, rx, ry, g in reversed(rows_def)]
path = right[:-1] + hem + left[1:]
nrm = [Vector((p.x, p.y, 0)).normalized() for p in path]
def tprof(i):
    w = 0.042 if len(right) - 1 <= i < len(right) - 1 + len(hem) else 0.03   # broader along the hem
    return [(-0.004, -w / 2), (0.022, -w / 2), (0.028, 0), (0.022, w / 2), (-0.004, w / 2)][::-1]
P.sweep(path, tprof, "accent", nrm)
# dark gorget under the chin, a gold collar with a V point at the front
P.loft([P.ring((0, -0.005, 0.735), 0.105, 0.095, n=10), P.ring((0, -0.005, 0.8), 0.1, 0.09, n=10)], "dark")
cols = [math.radians(360 * k / 12) for k in range(12)]
def on(th, z, out):
    return Vector(((0.15 + out) * math.sin(th), -(0.12 + out) * math.cos(th), z))
P.shell([[on(t, 0.772, 0.0) for t in cols],
         [on(t, 0.742 - 0.05 * max(0.0, math.cos(t)) ** 6, 0.03) for t in cols]], 0.016, "accent", cyclic=True)
