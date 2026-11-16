# Baggy trousers (lowpoly chibi): wide 8-sided tubes from inside the torso, bloused out over the boot tops
# (z 0.25-0.29) and tucked back in under them; edge loops at the knee. Visible between a short hem and the boots.
hip = lm["hip.l"]
x = hip.x - 0.005
legs = P.loft([P.ring((x - 0.01, 0, 0.42), 0.072, n=8), P.ring((x, 0, hip.z), 0.088, n=8),
               P.ring((x, -0.003, 0.32), 0.095, n=8), P.ring((x + 0.004, -0.006, 0.285), 0.102, n=8),
               P.ring((x + 0.006, -0.004, 0.25), 0.096, n=8), P.ring((x + 0.008, 0.005, 0.225), 0.078, n=8),
               P.ring((x + 0.01, 0.012, 0.15), 0.07, n=8)], "secondary")
P.mirror_x(legs)
