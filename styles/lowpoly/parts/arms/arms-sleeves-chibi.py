# Wide sleeves (lowpoly chibi) along the T-pose arm (+X), 8 sides, widening to a gold cuff; dark inside.
# Starts inside the robe at x 0.06 so the shoulder has no gap under the beard.
# Edge loops at the shoulder and the elbow.
sh, el, wr = lm["shoulder.l"], lm["elbow.l"], lm["wrist.l"]
zc = sh.z
xs = [0.06, sh.x + 0.01, el.x - 0.03, el.x + 0.03, wr.x - 0.09, wr.x - 0.045, wr.x - 0.005]
rs = [0.075, 0.08, 0.08, 0.083, 0.095, 0.1, 0.1]
left = P.loft([P.ring((x, 0, zc), r, n=8, axis="x") for x, r in zip(xs, rs)],
              ["primary"] * 5 + ["accent"], cap_roles=("primary", "dark"))
P.mirror_x(left)
