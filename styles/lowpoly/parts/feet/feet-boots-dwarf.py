# Big dwarf boots (lowpoly, dwarf archetype), fitted to specs/dwarf/reference (0.27 wide, 0.39 long): a short shaft
# with a turned-down cuff to 0.12 and a long, low rounded foot. Single chamfers (blocky, as on the sheet).
a = lm["ankle.l"]
x = a.x + 0.012
cy = a.y + 0.03
shaft = P.loft([P.rrect((x, cy, z), sx, sy, 0.05, seg=1)
                for z, sx, sy in ((0.05, 0.12, 0.13), (0.1, 0.12, 0.13), (0.1, 0.13, 0.14), (0.125, 0.13, 0.14),
                                  (0.13, 0.12, 0.13))], "leather")
foot = P.loft([P.rrect((x, 0.2, 0.05), 0.11, 0.05, 0.035, seg=1, axis="y"),
               P.rrect((x, 0.175, 0.058), 0.132, 0.058, 0.042, seg=1, axis="y"),
               P.rrect((x, -0.07, 0.058), 0.135, 0.058, 0.042, seg=1, axis="y"),
               P.rrect((x, -0.15, 0.05), 0.13, 0.05, 0.036, seg=1, axis="y"),
               P.rrect((x, -0.19, 0.036), 0.1, 0.036, 0.026, seg=1, axis="y")], "leather")
P.mirror_x(shaft + foot)
