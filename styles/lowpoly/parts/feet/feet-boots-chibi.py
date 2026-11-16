# Chunky boots (lowpoly chibi): rounded shaft (two-step corners) from inside the foot up past the knee, well inside
# the robe (hem 0.19, knee 0.199): the boots are the visible legs; with the knee joint blend the part above the knee
# follows the thigh (and the robe), so a bent knee never opens a gap or swings the shaft top out over the hem.
# A longer rounded foot with a lower toe.
a, t = lm["ankle.l"], lm["toes.l"]
x = a.x + 0.01
cy = a.y + 0.0175
shaft = P.loft([P.rrect((x, cy, z), sx, sy, 0.045, seg=2)
                for z, sx, sy in ((0.06, 0.092, 0.1025), (0.12, 0.092, 0.1025), (0.17, 0.092, 0.1025),
                                  (0.199, 0.091, 0.1015), (0.23, 0.088, 0.097), (0.25, 0.082, 0.09))], "leather")
foot = P.loft([P.rrect((x, a.y + 0.13, 0.042), 0.1, 0.042, 0.03, seg=2, axis="y"),
               P.rrect((x, a.y + 0.11, 0.048), 0.1, 0.048, 0.035, seg=2, axis="y"),
               P.rrect((x, a.y - 0.06, 0.048), 0.1, 0.048, 0.035, seg=2, axis="y"),
               P.rrect((x, t.y + 0.04, 0.04), 0.096, 0.04, 0.03, seg=2, axis="y"),
               P.rrect((x, t.y + 0.005, 0.03), 0.075, 0.026, 0.02, seg=2, axis="y")], "leather")
P.mirror_x(shaft + foot)
