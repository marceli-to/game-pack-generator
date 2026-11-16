# Armoured legs (lowpoly chibi): dark trousers (as legs-pants-chibi) under steel cuisses round the thighs that
# flare over the boot / greave tops (z 0.245), with a gold rim at the lower edge.
hip = lm["hip.l"]
x = hip.x - 0.005
legs = P.loft([P.ring((x - 0.01, 0, 0.42), 0.07, n=8), P.ring((x, 0, hip.z), 0.08, n=8),
               P.ring((x, 0, 0.29), 0.079, n=8), P.ring((x + 0.005, 0.01, 0.15), 0.07, n=8)], "dark")
cuisse = P.loft([P.ring((x, 0, 0.385), 0.084, n=8), P.ring((x, -0.004, 0.33), 0.092, n=8),
                 P.ring((x + 0.006, -0.006, 0.262), 0.1, n=8)], "metal")
rim = P.loft([P.ring((x + 0.006, -0.006, 0.27), 0.103, n=8), P.ring((x + 0.007, -0.006, 0.245), 0.105, n=8)], "accent")
P.mirror_x(legs + cuisse + rim)
