# Black gloves (tinfox, hero-m): oversized mitten fist (two-step corners, closed rounded tip) with a separate
# thumb forward and a short flared cuff over the wrist. Mitten + thumb (Marcel, 2026-11-17); fingers only if the
# guard reads wrong in game.
wr = lm["wrist.l"]
z = wr.z - 0.004
hand = [(-0.005, 0.062, 0.05, 0.035), (0.02, 0.07, 0.056, 0.04), (0.11, 0.07, 0.056, 0.04),
        (0.14, 0.062, 0.05, 0.036), (0.16, 0.047, 0.038, 0.028), (0.17, 0.026, 0.021, 0.015)]
faces = P.loft([P.rrect((wr.x + dx, 0, z), sy, sz, r, seg=2, axis="x") for dx, sy, sz, r in hand], "leather")
tx, tz = wr.x + 0.045, z - 0.018
thumb = [(-0.04, 0.034, 0.03, 0.022), (-0.09, 0.034, 0.03, 0.022), (-0.112, 0.027, 0.024, 0.018),
         (-0.124, 0.014, 0.013, 0.009)]
faces += P.loft([P.rrect((tx, y, tz), sx, sz, r, seg=2, axis="y") for y, sx, sz, r in thumb], "leather")
faces += P.loft([P.rrect((wr.x + dx, 0, z), sy, sz, 0.03, seg=1, axis="x")
                 for dx, sy, sz in ((-0.045, 0.068, 0.062), (-0.005, 0.075, 0.066), (0.012, 0.07, 0.06))], "leather")
P.mirror_x(faces)
