# Mitten hands (palm down in the T-pose), bevelled, with a thumb on the front side.
wr = lm["wrist.l"]
z = wr.z
hand = P.rbox((wr.x - 0.05, -0.062, z - 0.047), (wr.x + 0.125, 0.062, z + 0.042), "skin", r=0.03, bevel=0.018, axis="x")
thumb = P.rbox((wr.x - 0.005, -0.098, z - 0.038), (wr.x + 0.065, -0.035, z + 0.012), "skin", r=0.015, bevel=0, seg=1, axis="x")
P.mirror_x(hand + thumb)
