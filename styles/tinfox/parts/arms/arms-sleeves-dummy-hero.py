# Padded sleeves (tinfox, hero-m), for the practice dummy: the guard's bulky sleeves in padded canvas (role armor),
# down to inside the glove's cuff (no bare wrist), and a chunky octagonal elbow pad round each elbow that shares
# upper arm and forearm (half each), so it rides the bend.
sh, el, wr = lm["shoulder.l"], lm["elbow.l"], lm["wrist.l"]
zc = sh.z
xs = [0.14, sh.x + 0.02, el.x - 0.04, el.x + 0.02, wr.x - 0.12, wr.x - 0.02]
rs = [0.095, 0.1, 0.092, 0.086, 0.08, 0.064]
faces = P.loft([P.ring((x, 0, zc), r, n=14, axis="x") for x, r in zip(xs, rs)], "armor", cap_roles=("armor", "dark"))
oc = lambda x, r: P.ring((x, 0.0, zc), r, r * 0.96, n=8, axis="x", phase=22.5)
pad = P.loft([oc(el.x - 0.1, 0.094), oc(el.x - 0.08, 0.118), oc(el.x + 0.07, 0.118), oc(el.x + 0.09, 0.094)], "armor")
P.set_weights(pad, {"upperarm.l": 0.5, "lowerarm.l": 0.5})
P.mirror_x(faces + pad)
