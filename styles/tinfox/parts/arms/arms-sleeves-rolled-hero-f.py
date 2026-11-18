# Rolled-up sleeves (tinfox, hero-f), for specs/worker/reference: short teal sleeves from inside the torso to a thick
# rolled cuff over the elbow, bare forearms down into the gloves.
sh, el, wr = lm["shoulder.l"], lm["elbow.l"], lm["wrist.l"]
zc = sh.z
xs = [0.12, sh.x + 0.01, el.x - 0.07, el.x - 0.045]
rs = [0.08, 0.082, 0.072, 0.07]
faces = P.loft([P.ring((x, 0, zc), r, n=12, axis="x") for x, r in zip(xs, rs)], "primary")
faces += P.loft([P.ring((x, 0, zc), r, n=12, axis="x") for x, r in
                 ((el.x - 0.05, 0.078), (el.x - 0.045, 0.086), (el.x + 0.06, 0.086), (el.x + 0.065, 0.076))],
                "primary", cap_roles=("primary", "dark"))
faces += P.loft([P.ring((el.x + 0.04, 0, zc), 0.052, n=10, axis="x"), P.ring((el.x + 0.15, 0, zc), 0.046, n=10, axis="x"),
                 P.ring((wr.x - 0.01, 0, zc), 0.04, n=10, axis="x"), P.ring((wr.x + 0.02, 0, zc), 0.038, n=10, axis="x")],
                "skin")
P.mirror_x(faces)
