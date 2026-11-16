# Low boots (lowpoly chibi), fitted to specs/knight-lowpoly/reference: wide chunky ankle boots with a turned-down
# cuff (0.12-0.165) and a raised rounded toe; single chamfers (8-point rings) so they read as big facets. For
# characters whose trousers show between hem and boot (the trousers end inside the shaft at 0.15).
a, t = lm["ankle.l"], lm["toes.l"]
x = a.x + 0.01
cy = a.y + 0.012
shaft = P.loft([P.rrect((x, cy, z), sx, sy, r, seg=1) for z, sx, sy, r in
                ((0.06, 0.09, 0.105, 0.04), (0.118, 0.086, 0.1, 0.04), (0.12, 0.097, 0.112, 0.045),
                 (0.165, 0.097, 0.112, 0.045), (0.168, 0.077, 0.09, 0.035))], "leather")
foot = P.loft([P.rrect((x, a.y + 0.142, 0.05), 0.094, 0.05, 0.03, seg=1, axis="y"),
               P.rrect((x, a.y + 0.13, 0.055), 0.098, 0.055, 0.035, seg=1, axis="y"),
               P.rrect((x, a.y - 0.07, 0.055), 0.098, 0.055, 0.035, seg=1, axis="y"),
               P.rrect((x, t.y + 0.05, 0.05), 0.095, 0.05, 0.035, seg=1, axis="y"),
               P.rrect((x, t.y + 0.025, 0.04), 0.08, 0.04, 0.03, seg=1, axis="y")], "leather")
P.mirror_x(shaft + foot)
