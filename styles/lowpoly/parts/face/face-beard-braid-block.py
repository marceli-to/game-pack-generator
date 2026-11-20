# Big beard with a braided tip (lowpoly chibi face slot), from specs/berserker/reference: one thick shell from
# sideburn to sideburn, its top edge framing the open grin (under the mouth at the centre, rising past the mouth
# corners up the cheeks to the sideburns at z 0.99), bulging forward and coming to a point on the chest (z 0.685);
# a moustache over the top teeth; a steel ring and a short braided tuft hanging from the point.
N, R = 9, 4
rows = []
for i in range(R):
    v = i / (R - 1)
    row = []
    for j in range(N):
        th = math.radians(-90 + 180 * j / (N - 1))
        s = abs(math.sin(th))
        z_top = 0.822 + 0.06 * min(s / 0.5, 1.0) + 0.11 * max(0.0, (s - 0.6) / 0.4)
        z_bot = 0.685 + 0.11 * s ** 1.8
        z = z_top + (z_bot - z_top) * v
        bulge = math.sin(math.pi * min(1.0, v * 1.15))
        rx = 0.198 + 0.03 * bulge
        ry = 0.188 + 0.07 * bulge * (1 - s) + 0.02 * bulge
        if i == R - 1:
            ry -= 0.03 * (1 - s)                              # the point tucks back a little under the chin
        row.append(Vector((rx * math.sin(th), -ry * math.cos(th) + 0.012, z)))
    rows.append(row)
P.shell(rows, -0.055, "hair")
# moustache: a thick strap over the top teeth, dipping at the centre, ends drooping beside the mouth
mp = [(-0.098, 0.845), (-0.07, 0.874), (-0.03, 0.886), (0.0, 0.881), (0.03, 0.886), (0.07, 0.874), (0.098, 0.845)]
f = -0.177
P.sweep([Vector((x, f + 0.004 + 0.25 * (x * x), z)) for x, z in mp], P.strap_profile(0.024, 0.02, 0.007), "hair",
        [Vector((0, -1, 0))] * len(mp))
# braid: a steel ring under the point, then a faceted tuft tapering to a tip
yb, zb = -0.2, 0.69
P.loft([P.ring((0, yb, zb + 0.012), 0.024, n=8), P.ring((0, yb, zb + 0.004), 0.032, n=8),
        P.ring((0, yb, zb - 0.022), 0.032, n=8), P.ring((0, yb, zb - 0.03), 0.024, n=8)], "metal")
P.loft([P.ring((0, yb, zb - 0.026), 0.024, n=6), P.ring((0, yb - 0.004, zb - 0.06), 0.04, n=6),
        P.ring((0, yb - 0.004, zb - 0.09), 0.034, n=6), [Vector((0, yb + 0.004, zb - 0.125))]], "hair")
