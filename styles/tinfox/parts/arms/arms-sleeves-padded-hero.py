# Padded sleeves (tinfox, hero-m), fitted to specs/guard/reference: bulky olive sleeves along the T-pose arm (+X),
# 10 sides, starting inside the torso (the shoulder pads are on the torso: v2); a thick rolled cuff over the forearm, a bare wrist, the glove starts at the wrist.
sh, el, wr = lm["shoulder.l"], lm["elbow.l"], lm["wrist.l"]
zc = sh.z
xs = [0.14, sh.x + 0.02, el.x - 0.04, el.x + 0.02, wr.x - 0.17, wr.x - 0.165, wr.x - 0.075, wr.x - 0.068]
rs = [0.095, 0.1, 0.092, 0.084, 0.082, 0.1, 0.1, 0.09]
faces = P.loft([P.ring((x, 0, zc), r, n=14, axis="x") for x, r in zip(xs, rs)],
               ["primary"] * 7, cap_roles=("primary", "dark"))
# bare wrist into the glove
faces += P.loft([P.ring((wr.x - 0.075, 0, zc), 0.05, n=8, axis="x"), P.ring((wr.x + 0.02, 0, zc), 0.048, n=8, axis="x")],
                "skin")
P.mirror_x(faces)
