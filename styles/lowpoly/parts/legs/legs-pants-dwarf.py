# Dwarf trousers (lowpoly, dwarf archetype): one 8-sided tube per leg from inside the torso into the boot shaft,
# loops around the knee; visible only between the jerkin hem (0.2) and the boots (0.11).
hip = lm["hip.l"]
x = hip.x + 0.005
k = lm["knee.l"].z
legs = P.loft([P.ring((x - 0.01, 0, 0.3), 0.085, n=8), P.ring((x, 0, hip.z), 0.095, n=8),
               P.ring((x, 0, k + 0.015), 0.09, n=8), P.ring((x, 0, k - 0.015), 0.088, n=8),
               P.ring((x + 0.005, 0.01, 0.06), 0.085, n=8)], "dark")
P.mirror_x(legs)
