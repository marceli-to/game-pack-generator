# Round chibi head (painted): soft rounded box (30-degree corner steps), full cheeks; tall oval dot eyes,
# a small smile, little ears. The top is hidden under headwear on the wizard.
z0, z1 = lm["head_base"].z, lm["head_top"].z
# (z, half width, front y, back y, corner radius)
prof = [(z0, 0.10, -0.12, 0.08, 0.05), (0.83, 0.15, -0.16, 0.12, 0.06), (0.89, 0.18, -0.178, 0.15, 0.07),
        (0.97, 0.19, -0.18, 0.165, 0.078), (1.06, 0.184, -0.175, 0.165, 0.078), (1.14, 0.155, -0.15, 0.14, 0.068),
        (z1, 0.095, -0.09, 0.09, 0.045)]
P.loft([P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=3) for z, sx, f, b, r in prof], "skin")
# eyes: tall ovals, slightly proud of the face
eye = P.loft([P.ring((0.078, -0.166, 0.965), 0.019, 0.035, n=10, axis="y"),
              P.ring((0.078, -0.186, 0.965), 0.019, 0.035, n=10, axis="y")], "eyes")
P.mirror_x(eye)
# smile: a thin bevelled strap along a shallow U
xs = [-0.046, -0.031, -0.015, 0.0, 0.015, 0.031, 0.046]
P.sweep([Vector((x, -0.18, 0.9 + 9 * x * x)) for x in xs], P.strap_profile(0.01, 0.006, 0.002),
        "dark", [Vector((0, -1, 0))] * len(xs))
ear = P.rbox((0.175, -0.03, 0.94), (0.232, 0.035, 1.04), "skin", r=0.02, bevel=0, seg=1, axis="x")
P.mirror_x(ear)
