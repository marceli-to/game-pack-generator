# Suit sleeves (tinfox, hero-f; players 2 and 4), from specs/player-2/reference: fitted sleeves from inside the torso
# (under the shoulder pads) past the elbow to a thick cuff band at mid-forearm, a short bare forearm into the glove.
sh, el, wr = lm["shoulder.l"], lm["elbow.l"], lm["wrist.l"]
zc = sh.z
faces = P.loft([P.ring((x, 0, zc), r, n=12, axis="x") for x, r in
                ((0.12, 0.075), (sh.x + 0.01, 0.078), (el.x - 0.04, 0.066), (el.x + 0.04, 0.062), (el.x + 0.09, 0.062))],
               "primary")
faces += P.loft([P.ring((x, 0, zc), r, n=12, axis="x") for x, r in
                 ((el.x + 0.085, 0.068), (el.x + 0.09, 0.076), (el.x + 0.17, 0.074), (el.x + 0.175, 0.064))],
                "primary", cap_roles=("primary", "dark"))
faces += P.loft([P.ring((el.x + 0.15, 0, zc), 0.046, n=10, axis="x"), P.ring((wr.x - 0.01, 0, zc), 0.04, n=10, axis="x"),
                 P.ring((wr.x + 0.02, 0, zc), 0.038, n=10, axis="x")], "skin")
P.mirror_x(faces)
