# Elf head (lowpoly chibi): the chibi block head (8-sided rounded box, tall oval dot eyes, line smile) with long
# pointed ears swept up and back instead of the block ears: 6-sided lofts from the side of the head to a tip.
z0, z1 = lm["head_base"].z, lm["head_top"].z
prof = [(z0, 0.11, -0.12, 0.08, 0.05), (0.85, 0.17, -0.17, 0.14, 0.07), (0.97, 0.19, -0.18, 0.165, 0.08),
        (1.08, 0.18, -0.172, 0.16, 0.08), (z1, 0.12, -0.11, 0.11, 0.05)]
P.loft([P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=1) for z, sx, f, b, r in prof], "skin")
eye = P.loft([P.ring((0.075, -0.166, 0.965), 0.019, 0.034, n=8, axis="y"),
              P.ring((0.075, -0.186, 0.965), 0.019, 0.034, n=8, axis="y")], "eyes")
P.mirror_x(eye)
xs = [-0.045, -0.022, 0.0, 0.022, 0.045]
P.sweep([Vector((x, -0.181, 0.9 + 10 * x * x)) for x in xs], P.strap_profile(0.011, 0.006, 0.002),
        "eyes", [Vector((0, -1, 0))] * len(xs))
# (x, y, z, half depth y, half height z): base inside the head, flat blade towards the tip
ear = [(0.165, -0.01, 0.975, 0.035, 0.06), (0.215, 0.0, 0.99, 0.03, 0.05), (0.27, 0.025, 1.035, 0.018, 0.032)]
ear = P.loft([P.ring((x, y, z), sy, sz, n=6, axis="x") for x, y, z, sy, sz in ear] + [[Vector((0.325, 0.055, 1.105))]],
             "skin")
P.mirror_x(ear)
