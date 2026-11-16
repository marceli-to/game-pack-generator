# Dwarf arms (lowpoly, dwarf archetype): thick grey sleeves to the elbow, bare forearms, steel bracers at the
# wrist, and a flat steel shoulder pad with a gold edge and rivet. Starts inside the torso; loops at shoulder/elbow.
sh, el, wr = lm["shoulder.l"], lm["elbow.l"], lm["wrist.l"]
zc = sh.z
xs = [0.06, sh.x + 0.01, el.x - 0.015, el.x - 0.005, el.x + 0.03, wr.x - 0.09, wr.x - 0.085, wr.x - 0.01, wr.x - 0.005]
rs = [0.09, 0.092, 0.088, 0.075, 0.074, 0.074, 0.088, 0.088, 0.08]
left = P.loft([P.ring((x, 0, zc), r, n=8, axis="x") for x, r in zip(xs, rs)],
              ["metal", "metal", "metal", "skin", "skin", "metal", "metal", "metal"], cap_roles=("metal", "dark"))
rows = []
for x, r in ((0.2, 0.1), (0.26, 0.11), (0.32, 0.1)):
    rows.append([Vector((x, r * math.sin(math.radians(a)), zc + 0.01 + r * math.cos(math.radians(a))))
                 for a in (-110, -70, -35, 0, 35, 70, 110)])
left += P.shell(rows, 0.02, "metal", edge_role="accent")
left += P.dome((0.26, -0.06, zc + 0.104), (0, -0.5, 1), 0.022, 0.015, n=6, role="accent")
P.mirror_x(left)
