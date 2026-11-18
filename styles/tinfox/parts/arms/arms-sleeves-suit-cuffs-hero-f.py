# Suit sleeves, white-cuff variant (tinfox, hero-f; player 4, specs/player-4/reference): arms-sleeves-suit-hero-f with
# a white band (role `secondary`) coming out of the cuff. arms-sleeves-suit-hero-f: fitted sleeves from inside the torso
# (under the shoulder pads) past the elbow to a thick cuff band at mid-forearm, a short bare forearm into the glove.
sh, el, wr = lm["shoulder.l"], lm["elbow.l"], lm["wrist.l"]
zc = sh.z
faces = P.loft([P.ring((x, 0, zc), r, n=12, axis="x") for x, r in
                ((0.12, 0.075), (sh.x + 0.01, 0.078), (el.x - 0.04, 0.066), (el.x + 0.04, 0.062), (el.x + 0.09, 0.062))],
               "primary")
faces += P.loft([P.ring((x, 0, zc), r, n=12, axis="x") for x, r in
                 ((el.x + 0.085, 0.068), (el.x + 0.09, 0.076), (el.x + 0.17, 0.074), (el.x + 0.175, 0.064))],
                "primary", cap_roles=("primary", "dark"))
faces += P.loft([P.ring((x, 0, zc), r, n=12, axis="x") for x, r in
                 ((el.x + 0.16, 0.06), (el.x + 0.165, 0.064), (el.x + 0.215, 0.062), (el.x + 0.22, 0.056))], "secondary")
faces += P.loft([P.ring((el.x + 0.15, 0, zc), 0.046, n=10, axis="x"), P.ring((wr.x - 0.01, 0, zc), 0.04, n=10, axis="x"),
                 P.ring((wr.x + 0.02, 0, zc), 0.038, n=10, axis="x")], "skin")
P.mirror_x(faces)
