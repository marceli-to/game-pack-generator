# Head: rounded box with 30-degree corner steps (16-point rings, so it shades round under the 40-degree
# smoothing rule), full cheeks, domed top; ears and a small nose.
z0, z1 = lm["head_base"].z, lm["head_top"].z
rings = [(z0, 0.135, 0.145, 0.06), (z0 + 0.04, 0.15, 0.16, 0.07), (1.66, 0.16, 0.17, 0.075),
         (z1 - 0.025, 0.138, 0.148, 0.07), (z1, 0.09, 0.10, 0.05)]
P.loft([P.rrect((0, 0, z), sx, sy, r, seg=3) for z, sx, sy, r in rings], "skin")
ear = P.box((0.152, -0.03, 1.50), (0.19, 0.045, 1.60), "skin")
P.mirror_x(ear)
P.rbox((-0.024, -0.205, 1.51), (0.024, -0.15, 1.57), "skin", r=0.012, bevel=0, seg=1, axis="y")  # nose
