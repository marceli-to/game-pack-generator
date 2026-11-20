# Greaved boots (lowpoly chibi), fitted to specs/shieldbearer/reference: dark chunky ankle boots (the low boots'
# foot, single chamfers) with a steel greave round the shin from the ankle to z 0.205, a raised lip at its top and
# bottom; the trousers end inside the greave.
a, t = lm["ankle.l"], lm["toes.l"]
x = a.x + 0.01
cy = a.y + 0.012
shaft = P.loft([P.rrect((x, cy, z), sx, sy, r, seg=1) for z, sx, sy, r in
                ((0.06, 0.09, 0.105, 0.04), (0.11, 0.088, 0.102, 0.04))], "dark")
greave = P.loft([P.rrect((x, cy, z), sx, sy, r, seg=1) for z, sx, sy, r in
                 ((0.075, 0.1, 0.116, 0.045), (0.09, 0.104, 0.12, 0.047), (0.1, 0.098, 0.113, 0.044),
                  (0.18, 0.094, 0.108, 0.042), (0.188, 0.104, 0.118, 0.047), (0.205, 0.104, 0.118, 0.047),
                  (0.212, 0.09, 0.104, 0.04))], "metal")
foot = P.loft([P.rrect((x, a.y + 0.142, 0.05), 0.094, 0.05, 0.03, seg=1, axis="y"),
               P.rrect((x, a.y + 0.13, 0.055), 0.098, 0.055, 0.035, seg=1, axis="y"),
               P.rrect((x, a.y - 0.07, 0.055), 0.098, 0.055, 0.035, seg=1, axis="y"),
               P.rrect((x, t.y + 0.05, 0.05), 0.095, 0.05, 0.035, seg=1, axis="y"),
               P.rrect((x, t.y + 0.025, 0.04), 0.08, 0.04, 0.03, seg=1, axis="y")], "dark")
P.mirror_x(shaft + greave + foot)
