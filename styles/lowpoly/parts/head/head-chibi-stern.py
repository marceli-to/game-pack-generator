# Stern head (lowpoly chibi): the chibi block head with heavy brows slanting down to the nose and a flat mouth
# turning down at the ends (warriors, guards, grumpy villagers). Brows and mouth are raised straps (`eyes`).
z0, z1 = lm["head_base"].z, lm["head_top"].z
prof = [(z0, 0.11, -0.12, 0.08, 0.05), (0.85, 0.17, -0.17, 0.14, 0.07), (0.97, 0.19, -0.18, 0.165, 0.08),
        (1.08, 0.18, -0.172, 0.16, 0.08), (z1, 0.12, -0.11, 0.11, 0.05)]
P.loft([P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=1) for z, sx, f, b, r in prof], "skin")
eye = P.loft([P.ring((0.075, -0.166, 0.965), 0.019, 0.034, n=8, axis="y"),
              P.ring((0.075, -0.186, 0.965), 0.019, 0.034, n=8, axis="y")], "eyes")
P.mirror_x(eye)
xs = [-0.04, -0.02, 0.0, 0.02, 0.04]
P.sweep([Vector((x, -0.181, 0.9 - 8 * x * x)) for x in xs], P.strap_profile(0.011, 0.006, 0.002),
        "eyes", [Vector((0, -1, 0))] * len(xs))
brow = P.sweep([Vector((0.035, -0.18, 1.012)), Vector((0.075, -0.179, 1.03)), Vector((0.108, -0.177, 1.042))],
               P.strap_profile(0.016, 0.009, 0.003), "eyes", [Vector((0, -1, 0))] * 3)
ear = P.rbox((0.175, -0.035, 0.93), (0.235, 0.035, 1.04), "skin", r=0.02, bevel=0, seg=1, axis="x")
P.mirror_x(brow + ear)
