# Work gloves (tinfox, hero-f), for specs/worker/reference: big brown mitten fist (two-step corners, closed rounded
# tip) with a separate thumb and a wide flared gauntlet cuff over the wrist (the sheet's gloves are drawn large).
wr = lm["wrist.l"]
z = wr.z - 0.004
hand = [(0.0, 0.066, 0.052, 0.036), (0.025, 0.074, 0.058, 0.042), (0.12, 0.074, 0.058, 0.042),
        (0.15, 0.066, 0.052, 0.038), (0.172, 0.05, 0.04, 0.03), (0.183, 0.028, 0.022, 0.016)]
faces = P.loft([P.rrect((wr.x + dx, 0, z), sy, sz, r, seg=2, axis="x") for dx, sy, sz, r in hand], "leather")
tx, tz = wr.x + 0.05, z - 0.02
thumb = [(-0.04, 0.036, 0.032, 0.023), (-0.095, 0.036, 0.032, 0.023), (-0.118, 0.029, 0.025, 0.019),
         (-0.13, 0.015, 0.014, 0.01)]
faces += P.loft([P.rrect((tx, y, tz), sx, sz, r, seg=2, axis="y") for y, sx, sz, r in thumb], "leather")
faces += P.loft([P.rrect((wr.x + dx, 0, z), sy, sz, 0.03, seg=1, axis="x")
                 for dx, sy, sz in ((-0.065, 0.08, 0.072), (-0.06, 0.086, 0.078), (-0.01, 0.08, 0.068),
                                    (0.015, 0.072, 0.06))], "leather")
P.mirror_x(faces)
