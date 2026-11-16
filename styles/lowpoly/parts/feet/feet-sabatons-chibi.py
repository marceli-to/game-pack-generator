# Sabatons (lowpoly chibi, armour): steel greave shaft to 0.25 (like the boots, for the knee blend) with a gold
# band at the top, single chamfers (hard faceted metal), and a foot of overlapping plates stepping down to the toe.
a, t = lm["ankle.l"], lm["toes.l"]
x = a.x + 0.01
cy = a.y + 0.0175
shaft = P.loft([P.rrect((x, cy, z), sx, sy, 0.04, seg=1)
                for z, sx, sy in ((0.06, 0.094, 0.104), (0.12, 0.094, 0.104), (0.17, 0.094, 0.104),
                                  (0.199, 0.093, 0.103), (0.25, 0.088, 0.096))], "metal")
band = P.loft([P.rrect((x, cy, z), sx, sy, 0.045, seg=1)
               for z, sx, sy in ((0.215, 0.097, 0.107), (0.255, 0.093, 0.101))], "accent")
# (y, half width, half height): pairs at the same y are the plate steps
plates = [(a.y + 0.13, 0.1, 0.042), (a.y + 0.11, 0.1, 0.05), (-0.03, 0.1, 0.05), (-0.03, 0.094, 0.045),
          (-0.095, 0.094, 0.045), (-0.095, 0.088, 0.039), (-0.155, 0.086, 0.036), (t.y + 0.005, 0.07, 0.024)]
# each plate's ring sits 4 mm higher than the one behind it, so the step faces keep some height at the sole
foot = P.loft([P.rrect((x, y, sz + 0.004 * (0, 0, 0, 1, 1, 2, 2, 2)[i]), sx, sz, min(0.022, sz - 0.002), seg=1, axis="y")
               for i, (y, sx, sz) in enumerate(plates)], "metal")
P.mirror_x(shaft + band + foot)
