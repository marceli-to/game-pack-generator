# Skull head (painted chibi): cranium hidden under the helmet, big face with a protruding jaw,
# angry eye sockets with glowing eyes, nose hole, two rows of teeth over a dark mouth.
# v2: nose and teeth raised ~1.5 cm and widened to match the knight sheet.
z0, z1 = lm["head_base"].z, lm["head_top"].z
# (z, half width, front y, back y, corner radius)
prof = [(z0, 0.09, -0.17, 0.05, 0.04), (0.83, 0.11, -0.19, 0.08, 0.05), (0.88, 0.125, -0.195, 0.12, 0.055),
        (0.935, 0.155, -0.19, 0.16, 0.065), (0.99, 0.165, -0.185, 0.17, 0.07), (1.07, 0.163, -0.175, 0.17, 0.07),
        (1.15, 0.14, -0.145, 0.15, 0.065), (z1, 0.085, -0.085, 0.09, 0.04)]
P.loft([P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=3) for z, sx, f, b, r in prof], "skin")

def tilted(lo, hi, role, deg, r=0.012):
    f = P.rbox(lo, hi, role, r=r, bevel=0, seg=1, axis="y")
    c = (Vector(lo) + Vector(hi)) / 2
    P.transform(f, Matrix.Translation(c) @ Matrix.Rotation(math.radians(deg), 4, "Y") @ Matrix.Translation(-c))
    return f

# eye sockets (dark, slanted down towards the nose = angry) + glowing eyes
sock = tilted((0.03, -0.20, 0.985), (0.13, -0.165, 1.055), "dark", 14, r=0.02)
eye = tilted((0.052, -0.212, 1.002), (0.108, -0.19, 1.036), "special", 14, r=0.012)
P.mirror_x(sock + eye)
# nose hole: small inverted triangle
P.loft([[Vector((x, y, z)) for x, z in ((0.0, 0.945), (0.026, 0.985), (-0.026, 0.985))] for y in (-0.165, -0.2)], "dark")
# mouth + teeth
P.rbox((-0.12, -0.2, 0.84), (0.12, -0.15, 0.945), "dark", r=0.02, bevel=0, seg=1, axis="y")
for row, (zb, zt) in enumerate(((0.897, 0.943), (0.846, 0.891))):
    n = 7 if row == 0 else 6
    w = 0.23 / n
    for i in range(n):
        x = -0.115 + w * (i + 0.5)
        P.rbox((x - w * 0.42, -0.214, zb), (x + w * 0.42, -0.17, zt), "skin", r=0.006, bevel=0, seg=1, axis="y")
# cheekbones
cb = P.rbox((0.10, -0.195, 0.935), (0.158, -0.13, 0.98), "skin", r=0.02, bevel=0.008, seg=1, axis="y")
P.mirror_x(cb)
