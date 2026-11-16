# Mitten hands (lowpoly chibi): big fists lofted along the T-pose arm (+X) from rounded rectangles that taper
# and close at the fingertips (no flat cut); thumb lofted forward (-Y), also closing in a rounded tip.
wr = lm["wrist.l"]
z = wr.z - 0.0025
# (x offset from the wrist, half depth y, half height z, corner radius)
hand = [(-0.03, 0.05, 0.045, 0.03), (-0.005, 0.06, 0.054, 0.038), (0.075, 0.06, 0.054, 0.038),
        (0.1, 0.053, 0.047, 0.034), (0.116, 0.04, 0.035, 0.026), (0.124, 0.022, 0.019, 0.014)]
faces = P.loft([P.rrect((wr.x + dx, 0, z), sy, sz, r, seg=2, axis="x") for dx, sy, sz, r in hand], "skin")
tx, tz = wr.x + 0.03, z - 0.015
thumb = [(-0.035, 0.03, 0.028, 0.02), (-0.075, 0.03, 0.028, 0.02), (-0.094, 0.024, 0.022, 0.016),
         (-0.104, 0.013, 0.012, 0.008)]
faces += P.loft([P.rrect((tx, y, tz), sx, sz, r, seg=2, axis="y") for y, sx, sz, r in thumb], "skin")
P.mirror_x(faces)
