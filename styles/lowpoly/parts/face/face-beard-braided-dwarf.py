# Huge dwarf beard (lowpoly face slot, dwarf archetype), fitted to specs/dwarf/reference: a thick faceted sheet
# from the sideburns (up to the helmet rim), bulging forward and narrowing to a point on the chest, a two-lobed moustache under the smile,
# bushy brows, and two braids hanging from the jaw with gold rings.
N, R = 9, 5
rows = []
for i in range(R):
    v = i / (R - 1)
    row = []
    for j in range(N):
        th = math.radians(-90 + 180 * j / (N - 1))
        s = abs(math.sin(th))
        z_top = 0.665 + 0.05 * min(s / 0.6, 1.0) + 0.1 * max(0.0, (s - 0.8) / 0.2)
        z_bot = 0.425 + 0.13 * s ** 2.5
        z = z_top + (z_bot - z_top) * v
        rx = 0.272 + 0.02 * math.sin(math.pi * v) - 0.04 * v * v
        ry = 0.25 + 0.06 * math.sin(math.pi * min(1.0, v * 1.2)) + 0.03 * v
        row.append(Vector((rx * math.sin(th), -ry * math.cos(th) + 0.01, z)))
    rows.append(row)
P.shell(rows, -0.11, "hair")
mo = P.rbox((0.006, -0.3, 0.625), (0.14, -0.232, 0.692), "hair", r=0.03, bevel=0.012, seg=1, axis="y")
mo += P.rbox((0.04, -0.252, 0.795), (0.15, -0.222, 0.845), "hair", r=0.015, bevel=0, seg=1, axis="y")
P.mirror_x(mo)
br = []
x, y = 0.18, -0.3
for z, r in ((0.6, 0.045), (0.55, 0.034), (0.515, 0.045), (0.47, 0.034), (0.435, 0.045), (0.4, 0.034),
             (0.36, 0.034), (0.33, 0.042)):
    br.append(P.ring((x, y, z), r, n=6))
br.append([Vector((x, y, 0.29))])
braid = P.loft(br, "hair")
braid += P.cylinder((x, y, 0.37), (x, y, 0.41), 0.05, n=6, role="accent")
P.mirror_x(braid)
