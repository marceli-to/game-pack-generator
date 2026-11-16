# Gauntlets (lowpoly chibi): the mitten fist (rounded rectangles tapering to a closed tip, thumb forward) in steel,
# with a flared cuff over the wrist.
wr = lm["wrist.l"]
z = wr.z - 0.0025
hand = [(-0.03, 0.05, 0.045, 0.03), (-0.005, 0.06, 0.054, 0.038), (0.075, 0.06, 0.054, 0.038),
        (0.1, 0.053, 0.047, 0.034), (0.116, 0.04, 0.035, 0.026), (0.124, 0.022, 0.019, 0.014)]
faces = P.loft([P.rrect((wr.x + dx, 0, z), sy, sz, r, seg=1, axis="x") for dx, sy, sz, r in hand], "metal")
tx, tz = wr.x + 0.03, z - 0.015
thumb = [(-0.035, 0.03, 0.028, 0.02), (-0.075, 0.03, 0.028, 0.02), (-0.094, 0.024, 0.022, 0.016),
         (-0.104, 0.013, 0.012, 0.008)]
faces += P.loft([P.rrect((tx, y, tz), sx, sz, r, seg=1, axis="y") for y, sx, sz, r in thumb], "metal")
faces += P.loft([P.rrect((wr.x + dx, 0, z), sy, sz, 0.025, seg=1, axis="x")
                 for dx, sy, sz in ((-0.02, 0.07, 0.066), (0.03, 0.074, 0.07))], "metal")
# bigger mitts, like the sheet: scale the whole gauntlet round a point just behind the wrist
c = Vector((wr.x + 0.01, 0, z))
P.transform(faces, Matrix.Translation(c) @ Matrix.Diagonal((1.15, 1.28, 1.28, 1)) @ Matrix.Translation(-c))
P.mirror_x(faces)
