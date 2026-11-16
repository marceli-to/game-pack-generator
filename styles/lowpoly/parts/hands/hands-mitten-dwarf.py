# Dwarf fists (lowpoly, dwarf archetype): the chibi mitten made 20 % bigger with single chamfers: rounded
# rectangles tapering to a closed tip along the T-pose arm (+X), thumb forward (-Y).
wr = lm["wrist.l"]
z = wr.z - 0.003
k = 1.2
hand = [(-0.03, 0.05, 0.045, 0.03), (-0.005, 0.06, 0.054, 0.038), (0.075, 0.06, 0.054, 0.038),
        (0.1, 0.053, 0.047, 0.034), (0.116, 0.04, 0.035, 0.026), (0.124, 0.022, 0.019, 0.014)]
faces = P.loft([P.rrect((wr.x + k * dx, 0, z), k * sy, k * sz, k * r, seg=1, axis="x") for dx, sy, sz, r in hand],
               "skin")
tx, tz = wr.x + k * 0.03, z - k * 0.015
thumb = [(-0.035, 0.03, 0.028, 0.02), (-0.075, 0.03, 0.028, 0.02), (-0.094, 0.024, 0.022, 0.016),
         (-0.104, 0.013, 0.012, 0.008)]
faces += P.loft([P.rrect((tx, k * y, tz), k * sx, k * sz, k * r, seg=1, axis="y") for y, sx, sz, r in thumb], "skin")
P.mirror_x(faces)
