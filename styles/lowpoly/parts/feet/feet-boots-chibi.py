# Chunky boots (lowpoly chibi): rounded shaft (two chamfer steps) up under the robe hem, a longer rounded foot
# with a lower toe.
a, t = lm["ankle.l"], lm["toes.l"]
x = a.x + 0.01
shaft = P.rbox((x - 0.092, a.y - 0.085, 0.06), (x + 0.092, a.y + 0.12, 0.2), "leather", r=0.045, bevel=0, seg=2)
foot = P.loft([P.rrect((x, a.y + 0.13, 0.042), 0.1, 0.042, 0.03, seg=2, axis="y"),
               P.rrect((x, a.y + 0.11, 0.048), 0.1, 0.048, 0.035, seg=2, axis="y"),
               P.rrect((x, a.y - 0.06, 0.048), 0.1, 0.048, 0.035, seg=2, axis="y"),
               P.rrect((x, t.y + 0.04, 0.04), 0.096, 0.04, 0.03, seg=2, axis="y"),
               P.rrect((x, t.y + 0.005, 0.03), 0.075, 0.026, 0.02, seg=2, axis="y")], "leather")
P.mirror_x(shaft + foot)
