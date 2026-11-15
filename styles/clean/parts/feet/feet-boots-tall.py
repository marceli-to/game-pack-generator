# Tall boots: bevelled shaft up under the robe hem, rounded foot with a raised, rounded toe.
# Boots sit 3.5 cm outside the ankle joints (the reference stands wider than the hip joints).
a, t = lm["ankle.l"], lm["toes.l"]
x = a.x + 0.035
heel = guides["foot_heel"]
w = guides["foot_width"] / 2 + 0.01
h = guides["foot_height"] + 0.02
shaft = P.rbox((x - 0.09, a.y - 0.07, 0.10), (x + 0.09, a.y + 0.10, 0.36), "secondary", r=0.04, bevel=0.015, seg=1)
yb, yt = a.y + heel + 0.04, t.y + 0.05
foot = P.loft([P.rrect((x, yb, h / 2), w - 0.03, h / 2 - 0.02, 0.025, seg=1, axis="y"),
               P.rrect((x, yb - 0.02, h / 2), w - 0.01, h / 2, 0.035, seg=1, axis="y"),
               P.rrect((x, a.y - 0.08, h / 2), w, h / 2, 0.035, seg=1, axis="y"),
               P.rrect((x, yt + 0.03, h * 0.45), w - 0.01, h * 0.45, 0.035, seg=1, axis="y"),
               P.rrect((x, yt, h * 0.42), w - 0.04, h * 0.36, 0.02, seg=1, axis="y")], "secondary")
P.mirror_x(shaft + foot)
