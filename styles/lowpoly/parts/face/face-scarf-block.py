# Face scarf (lowpoly chibi): a thick band from cheek to cheek over the mouth and chin, just under the eyes,
# hanging to a point in front.
# the bottom edge drops to a point at the front over the chest
rows = []
for z, rx, ry, drop in ((0.925, 0.222, 0.21, 0.0), (0.86, 0.205, 0.198, 0.02), (0.8, 0.18, 0.19, 0.05)):
    rows.append([Vector((rx * math.sin(math.radians(a)), -ry * math.cos(math.radians(a)) - 0.004,
                         z - drop * max(0.0, math.cos(math.radians(a))) ** 2))
                 for a in (-100, -70, -42, -14, 14, 42, 70, 100)])
P.shell(rows, 0.016, "dark")
