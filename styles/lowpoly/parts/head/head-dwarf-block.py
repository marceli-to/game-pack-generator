# Dwarf head (lowpoly, dwarf archetype): a wide rounded box with single chamfers (8-sided rings): cheeks and ears
# much wider than the chibi head, the same tall oval dot eyes (`eyes`), a line smile, block ears.
z0, z1 = lm["head_base"].z, lm["head_top"].z
# (z, half width, front y, back y, corner chamfer)
prof = [(z0, 0.2, -0.17, 0.13, 0.07), (0.66, 0.265, -0.228, 0.19, 0.1), (0.76, 0.275, -0.238, 0.2, 0.1),
        (0.86, 0.255, -0.222, 0.19, 0.1), (z1, 0.165, -0.15, 0.13, 0.06)]
P.loft([P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=1) for z, sx, f, b, r in prof], "skin")
eye = P.loft([P.ring((0.077, -0.228, 0.742), 0.02, 0.037, n=8, axis="y"),
              P.ring((0.077, -0.25, 0.742), 0.02, 0.037, n=8, axis="y")], "eyes")
P.mirror_x(eye)
xs = [-0.042, -0.021, 0.0, 0.021, 0.042]
P.sweep([Vector((x, -0.243, 0.695 + 10 * x * x)) for x in xs], P.strap_profile(0.011, 0.006, 0.002),
        "eyes", [Vector((0, -1, 0))] * len(xs))
ear = P.rbox((0.255, -0.04, 0.66), (0.315, 0.04, 0.78), "skin", r=0.02, bevel=0, seg=1, axis="x")
P.mirror_x(ear)
