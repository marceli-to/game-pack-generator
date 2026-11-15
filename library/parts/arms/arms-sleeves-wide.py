# Wide wizard sleeves along the T-pose arm (+X), 12 sides, flaring in a curve to a gold cuff;
# dark inner opening. Two edge loops at the shoulder and the elbow.
sh, el, wr = lm["shoulder.l"], lm["elbow.l"], lm["wrist.l"]
zc = sh.z
xs = [0.14, sh.x + 0.01, el.x - 0.03, el.x + 0.03, wr.x - 0.18, wr.x - 0.11, wr.x - 0.09, wr.x - 0.035]
rs = [0.095, 0.10, 0.097, 0.10, 0.115, 0.135, 0.145, 0.15]
rings = [P.ring((x, 0, zc), r, n=12, axis="x") for x, r in zip(xs, rs)]
left = P.loft(rings, ["primary"] * 6 + ["accent"], cap_roles=("primary", "dark"))
P.mirror_x(left)
