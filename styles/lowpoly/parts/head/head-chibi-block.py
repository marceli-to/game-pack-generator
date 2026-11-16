# Chibi head (lowpoly): rounded box with single 45-degree corner chamfers (8-sided rings), so it reads as
# big flat facets; tall oval dot eyes, a line smile (both `eyes`), block ears.
z0, z1 = lm["head_base"].z, lm["head_top"].z
# (z, half width, front y, back y, corner chamfer)
prof = [(z0, 0.11, -0.12, 0.08, 0.05), (0.85, 0.17, -0.17, 0.14, 0.07), (0.97, 0.19, -0.18, 0.165, 0.08),
        (1.08, 0.18, -0.172, 0.16, 0.08), (z1, 0.12, -0.11, 0.11, 0.05)]
P.loft([P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=1) for z, sx, f, b, r in prof], "skin")
eye = P.loft([P.ring((0.075, -0.166, 0.965), 0.019, 0.034, n=8, axis="y"),
              P.ring((0.075, -0.186, 0.965), 0.019, 0.034, n=8, axis="y")], "eyes")
P.mirror_x(eye)
xs = [-0.045, -0.022, 0.0, 0.022, 0.045]
P.sweep([Vector((x, -0.181, 0.9 + 10 * x * x)) for x in xs], P.strap_profile(0.011, 0.006, 0.002),
        "eyes", [Vector((0, -1, 0))] * len(xs))
ear = P.rbox((0.175, -0.035, 0.93), (0.235, 0.035, 1.04), "skin", r=0.02, bevel=0, seg=1, axis="x")
P.mirror_x(ear)
