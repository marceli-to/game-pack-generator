# Wizard hair (hair slot): white sheet around the back of the head behind the ears, from under the hat brim
# down to a V at the nape, flaring out a little at the ends.
N = 13
rows = []
for i in range(5):
    v = i / 4
    row = []
    for j in range(N):
        th = math.radians(95 + 170 * j / (N - 1))          # 95..265 degrees around the back (0 = front)
        back = (1 - math.cos(th)) / 2                       # ~0.6 behind the ears, 1 at the back
        z_bot = 0.86 - 0.13 * ((back - 0.54) / 0.46) ** 1.5  # down past the ears, V at the nape
        z = 1.13 + (z_bot - 1.13) * v
        r = 0.2 + 0.02 * v * v
        row.append(Vector((r * math.sin(th), -r * 0.92 * math.cos(th) - 0.005, z)))
    rows.append(row)
P.shell(rows, -0.03, "hair")
