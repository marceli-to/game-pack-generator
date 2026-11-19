# Cloth sleeves with a wide cloth cuff (lowpoly chibi), fitted to specs/archer/reference: arms-sleeves-slim-chibi's
# 8-sided sleeve along the T-pose arm (+X), ending in a broad turned-back cuff of the same cloth over the forearm
# (two steps, as on the archer sheet). Starts inside the torso at x 0.06; edge loops at the shoulder and the elbow.
sh, el, wr = lm["shoulder.l"], lm["elbow.l"], lm["wrist.l"]
zc = sh.z
xs = [0.06, sh.x + 0.01, el.x - 0.03, el.x + 0.03, wr.x - 0.112, wr.x - 0.104, wr.x - 0.06, wr.x - 0.054,
      wr.x - 0.048, wr.x - 0.012, wr.x - 0.004]
rs = [0.068, 0.072, 0.067, 0.067, 0.068, 0.088, 0.088, 0.08, 0.084, 0.086, 0.074]
left = P.loft([P.ring((x, 0, zc), r, n=8, axis="x") for x, r in zip(xs, rs)], "primary",
              cap_roles=("primary", "dark"))
P.mirror_x(left)
