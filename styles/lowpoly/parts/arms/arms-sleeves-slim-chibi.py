# Slim cloth sleeves (lowpoly chibi) along the T-pose arm (+X), 8 sides, with leather bracers on the forearm.
# Start inside the torso at x 0.06; edge loops at the shoulder and the elbow.
sh, el, wr = lm["shoulder.l"], lm["elbow.l"], lm["wrist.l"]
zc = sh.z
xs = [0.06, sh.x + 0.01, el.x - 0.03, el.x + 0.03, wr.x - 0.1, wr.x - 0.092, wr.x - 0.012, wr.x - 0.005]
rs = [0.068, 0.07, 0.063, 0.063, 0.065, 0.073, 0.073, 0.066]
left = P.loft([P.ring((x, 0, zc), r, n=8, axis="x") for x, r in zip(xs, rs)],
              ["primary"] * 4 + ["leather"] * 3, cap_roles=("primary", "dark"))
P.mirror_x(left)
