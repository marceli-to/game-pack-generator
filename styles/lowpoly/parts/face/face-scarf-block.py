# Face scarf (lowpoly chibi): a thick band from cheek to cheek over the mouth and chin, just under the eyes,
# hanging to a point in front over the mantle (v2: longer, to the chest like the rogue sheet).
# the bottom edge drops to a point at the front over the chest
rows = []
for z, rx, ry, drop in ((0.925, 0.222, 0.21, 0.0), (0.86, 0.205, 0.198, 0.02), (0.8, 0.165, 0.195, 0.05),
                        (0.76, 0.13, 0.205, 0.11)):
    rows.append([Vector((rx * math.sin(math.radians(a)), -ry * math.cos(math.radians(a)) - 0.004,
                         z - drop * max(0.0, math.cos(math.radians(a))) ** 6))
                 for a in (-100, -70, -42, -14, 14, 42, 70, 100)])
# bottom row: the two front points close in to a tip
rows[-1][3].x *= 0.25
rows[-1][4].x *= 0.25
P.shell(rows, 0.016, "dark")
