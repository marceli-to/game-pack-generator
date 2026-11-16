# Wizard beard (face slot): a thick (solid-looking) sheet hugging the face from sideburn to sideburn (in front of the ears,
# up to the hat brim), covering the cheeks from just under the smile, ending in a V on the chest.
N = 15
rows = []
for i in range(7):
    v = i / 6
    row = []
    for j in range(N):
        th = math.radians(-90 + 180 * j / (N - 1))         # 0 = front (-Y); sideburns end at the ears
        s = abs(math.sin(th))  # by x, so the V edges are straight in front view
        z_top = 0.878 + 0.05 * min(s / 0.7, 1.0) ** 1.5 + 0.17 * max(0.0, (s - 0.75) / 0.25) ** 1.2  # cheeks, then sideburns
        z_bot = 0.675 + 0.15 * s                           # V: pointed in front, shorter at the sides
        z = z_top + (z_bot - z_top) * v
        rx = 0.207 + 0.012 * math.sin(math.pi * v)
        ry = 0.2 + 0.035 * math.sin(math.pi * min(1.0, v * 1.3)) - 0.03 * v
        row.append(Vector((rx * math.sin(th), -ry * math.cos(th) + 0.008, z)))
    rows.append(row)
P.shell(rows, -0.09, "hair")                               # thick: reads as a solid wedge from the side
