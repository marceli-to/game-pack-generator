# Leather gloves (lowpoly chibi): the mitten fist (two-step corners, closed tip, thumb forward) in leather, with
# a wide flared gauntlet cuff over the wrist and the sleeve end.
wr = lm["wrist.l"]
z = wr.z - 0.0025
hand = [(-0.03, 0.05, 0.045, 0.03), (-0.005, 0.06, 0.054, 0.038), (0.075, 0.06, 0.054, 0.038),
        (0.1, 0.053, 0.047, 0.034), (0.116, 0.04, 0.035, 0.026), (0.124, 0.022, 0.019, 0.014)]
faces = P.loft([P.rrect((wr.x + dx, 0, z), sy, sz, r, seg=2, axis="x") for dx, sy, sz, r in hand], "leather")
tx, tz = wr.x + 0.03, z - 0.015
thumb = [(-0.035, 0.03, 0.028, 0.02), (-0.075, 0.03, 0.028, 0.02), (-0.094, 0.024, 0.022, 0.016),
         (-0.104, 0.013, 0.012, 0.008)]
faces += P.loft([P.rrect((tx, y, tz), sx, sz, r, seg=2, axis="y") for y, sx, sz, r in thumb], "leather")
faces += P.loft([P.rrect((wr.x + dx, 0, z), sy, sz, 0.03, seg=1, axis="x")
                 for dx, sy, sz in ((-0.05, 0.072, 0.068), (-0.005, 0.068, 0.064), (0.01, 0.062, 0.058))], "leather")
P.mirror_x(faces)
