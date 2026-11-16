# Cuffed boots (lowpoly chibi): the chunky boot (shaft to 0.25 so robes and the knee blend work as with
# feet-boots-chibi) with a turned-down cuff round the top (`secondary`), a dark sole and a slightly upturned toe.
a, t = lm["ankle.l"], lm["toes.l"]
x = a.x + 0.01
cy = a.y + 0.0175
shaft = P.loft([P.rrect((x, cy, z), sx, sy, 0.045, seg=2)
                for z, sx, sy in ((0.06, 0.09, 0.1), (0.12, 0.09, 0.1), (0.17, 0.09, 0.1),
                                  (0.199, 0.089, 0.099), (0.25, 0.084, 0.092))], "leather")
cuff = P.loft([P.rrect((x, cy, z), sx, sy, 0.05, seg=1)
               for z, sx, sy in ((0.18, 0.1, 0.11), (0.24, 0.1, 0.11), (0.255, 0.094, 0.104))],
              "secondary")
foot = P.loft([P.rrect((x, a.y + 0.13, 0.045), 0.1, 0.045, 0.03, seg=2, axis="y"),
               P.rrect((x, a.y - 0.06, 0.05), 0.1, 0.05, 0.035, seg=2, axis="y"),
               P.rrect((x, t.y + 0.045, 0.044), 0.094, 0.04, 0.03, seg=2, axis="y"),
               P.rrect((x, t.y + 0.005, 0.05), 0.07, 0.024, 0.018, seg=2, axis="y")], "leather")
sole = P.rbox((x - 0.103, t.y - 0.0, 0.0), (x + 0.103, a.y + 0.14, 0.018), "dark", r=0.03, bevel=0, seg=1)
P.mirror_x(shaft + cuff + foot + sole)
