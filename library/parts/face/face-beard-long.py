# Beard corners in 30-degree steps (shades round). Eyes, brows, a drooping moustache and a full beard that tapers to a point over the collar.
for faces in (P.box((0.052, -0.177, 1.572), (0.092, -0.16, 1.632), "eyes"),
              P.box((0.035, -0.182, 1.648), (0.115, -0.16, 1.672), "hair")):
    P.mirror_x(faces)
m = P.rbox((0.0, -0.21, 1.475), (0.095, -0.165, 1.515), "hair", r=0.015, bevel=0, seg=1, axis="x")
c = Vector((0.0, -0.19, 1.495))
P.transform(m, Matrix.Translation(c) @ Matrix.Rotation(math.radians(14), 4, "Y") @ Matrix.Translation(-c))
P.mirror_x(m)
rings = [(1.53, -0.01, 0.168, 0.16, 0.07), (1.45, -0.03, 0.172, 0.165, 0.085), (1.36, -0.07, 0.12, 0.12, 0.07),
         (1.31, -0.10, 0.045, 0.05, 0.035)]
P.loft([P.rrect((0, y, z), sx, sy, r, seg=3) for z, y, sx, sy, r in rings], "hair")
