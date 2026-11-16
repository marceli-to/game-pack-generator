# Short beard (lowpoly chibi face slot): the wizard beard's sheet cut short: sideburn to sideburn under the
# smile, the chin just below the head (z 0.77), 7 columns, 3 bands, 5 cm thick.
N, R = 7, 3
rows = []
for i in range(R):
    v = i / (R - 1)
    row = []
    for j in range(N):
        th = math.radians(-90 + 180 * j / (N - 1))
        s = abs(math.sin(th))
        z_top = 0.875 + 0.05 * min(s / 0.7, 1.0) + 0.14 * max(0.0, (s - 0.75) / 0.25)
        z_bot = 0.77 + 0.1 * s
        z = z_top + (z_bot - z_top) * v
        rx = 0.2 + 0.012 * math.sin(math.pi * v)
        ry = 0.19 + 0.02 * math.sin(math.pi * v)
        row.append(Vector((rx * math.sin(th), -ry * math.cos(th) + 0.01, z)))
    rows.append(row)
P.shell(rows, -0.05, "hair")
