# Dwarf body (lowpoly, dwarf archetype): a barrel torso of 10 facets, leather jerkin (`primary`) open over a steel
# chest plate (the two front facets, `metal`), flaring into a short skirt to the hem at 0.2; a wide belt with a big
# gold buckle. Legs are a separate part.
rings = [(0.6, 0.1, 0.09), (0.585, 0.2, 0.15), (0.54, 0.25, 0.18), (0.45, 0.262, 0.2), (0.35, 0.27, 0.21),
         (0.33, 0.275, 0.212), (0.27, 0.288, 0.222), (0.2, 0.3, 0.232)]
front = (6, 7)
P.loft([P.ring((0, 0, z), rx, ry, n=10) for z, rx, ry in rings],
       lambda b, i: "metal" if (b <= 3 and i in front) else "primary", cap_roles=("metal", "dark"))
P.loft([P.rrect((0, 0, 0.262), 0.292, 0.226, 0.08, seg=1), P.rrect((0, 0, 0.338), 0.292, 0.226, 0.08, seg=1)],
       "leather")
P.rbox((-0.075, -0.244, 0.225), (0.075, -0.224, 0.35), "accent", r=0.012, bevel=0, seg=1, axis="y")
P.rbox((-0.038, -0.252, 0.26), (0.038, -0.24, 0.315), "leather", r=0.006, bevel=0, seg=1, axis="y")
