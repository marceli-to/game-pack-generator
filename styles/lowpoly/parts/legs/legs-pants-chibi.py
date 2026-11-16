# Pants (lowpoly chibi): one 8-sided tube per leg from inside the torso (0.42) down into the boot shaft (0.15),
# slightly narrowing; edge loops around the knee. Visible only between the tunic hem and the boots.
hip = lm["hip.l"]
x = hip.x - 0.005
k = lm["knee.l"].z
legs = P.loft([P.ring((x - 0.01, 0, 0.42), 0.07, n=8), P.ring((x, 0, hip.z), 0.08, n=8),
               P.ring((x, 0, 0.29), 0.079, n=8), P.ring((x, 0, k + 0.015), 0.075, n=8),
               P.ring((x, 0, k - 0.015), 0.074, n=8), P.ring((x + 0.005, 0.01, 0.15), 0.07, n=8)], "dark")
P.mirror_x(legs)
