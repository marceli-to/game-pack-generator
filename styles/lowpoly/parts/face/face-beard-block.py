# Wizard beard (lowpoly face slot): thick faceted sheet from sideburn to sideburn, under the smile, ending in
# a V on the chest. 9 columns, 4 bands.
N, R = 9, 5
rows = []
for i in range(R):
    v = i / (R - 1)
    row = []
    for j in range(N):
        th = math.radians(-90 + 180 * j / (N - 1))
        s = abs(math.sin(th))
        z_top = 0.875 + 0.05 * min(s / 0.7, 1.0) + 0.17 * max(0.0, (s - 0.75) / 0.25)
        z_bot = 0.68 + 0.15 * s
        z = z_top + (z_bot - z_top) * v
        rx = 0.207 + 0.012 * math.sin(math.pi * v)
        ry = 0.2 + 0.035 * math.sin(math.pi * min(1.0, v * 1.3)) - 0.03 * v
        row.append(Vector((rx * math.sin(th), -ry * math.cos(th) + 0.008, z)))
    rows.append(row)
P.shell(rows, -0.09, "hair")
