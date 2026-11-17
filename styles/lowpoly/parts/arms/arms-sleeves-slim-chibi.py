# Slim cloth sleeves (lowpoly chibi) along the T-pose arm (+X), 8 sides, with leather cuffs on the forearm.
# Start inside the torso at x 0.06; edge loops at the shoulder and the elbow.
sh, el, wr = lm["shoulder.l"], lm["elbow.l"], lm["wrist.l"]
zc = sh.z
# v2 detail pass (rogue/villager sheets): a thick turned-back leather cuff in two steps over the forearm.
xs = [0.06, sh.x + 0.01, el.x - 0.03, el.x + 0.03, wr.x - 0.112, wr.x - 0.106, wr.x - 0.064, wr.x - 0.058,
      wr.x - 0.052, wr.x - 0.012, wr.x - 0.004]
rs = [0.068, 0.072, 0.067, 0.067, 0.068, 0.086, 0.086, 0.078, 0.081, 0.081, 0.07]
left = P.loft([P.ring((x, 0, zc), r, n=8, axis="x") for x, r in zip(xs, rs)],
              ["primary"] * 4 + ["leather"] * 6, cap_roles=("primary", "dark"))
P.mirror_x(left)
