# Wizard hair (lowpoly hair slot): white sheet behind the ears from under the brim to a V at the nape.
N, R = 7, 3
rows = []
for i in range(R):
    v = i / (R - 1)
    row = []
    for j in range(N):
        th = math.radians(95 + 170 * j / (N - 1))
        back = (1 - math.cos(th)) / 2
        z_bot = 0.86 - 0.13 * ((back - 0.54) / 0.46) ** 1.5
        z = 1.13 + (z_bot - 1.13) * v
        r = 0.205 + 0.02 * v * v
        row.append(Vector((r * math.sin(th), -r * 0.92 * math.cos(th) - 0.005, z)))
    rows.append(row)
P.shell(rows, -0.04, "hair")
