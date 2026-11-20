# Shieldbearer arms (lowpoly chibi), fitted to specs/shieldbearer/reference: dark grey padded sleeves along the
# T-pose arm (+X, 8 sides), a wide steel bracer over the forearm with a raised lip at each end; a big rounded steel
# pauldron over each shoulder in two plates: a cap and a wider lower plate stepping out from under it.
# Starts inside the torso at x 0.06.
sh, el, wr = lm["shoulder.l"], lm["elbow.l"], lm["wrist.l"]
zc = sh.z
xs = [0.06, sh.x + 0.01, el.x - 0.03, el.x + 0.03, wr.x - 0.12, wr.x - 0.01]
rs = [0.074, 0.078, 0.07, 0.07, 0.068, 0.064]
left = P.loft([P.ring((x, 0, zc), r, n=8, axis="x") for x, r in zip(xs, rs)], "dark", cap_roles=("dark", "dark"))
# bracer: a steel sleeve over the forearm, lips at both ends
bx = [wr.x - 0.125, wr.x - 0.12, wr.x - 0.108, wr.x - 0.03, wr.x - 0.018, wr.x - 0.012]
br = [0.082, 0.09, 0.086, 0.086, 0.094, 0.088]
left += P.loft([P.ring((x, 0, zc), r, n=8, axis="x") for x, r in zip(bx, br)], "metal")
# pauldron: two shells over the shoulder (rows along the arm, 7 columns from front to back over the top)
ANG = [-112 + 224 * k / 6 for k in range(7)]
def pt(x, r, a, dz=0.014):
    return Vector((x, r * math.sin(math.radians(a)), zc + dz + r * math.cos(math.radians(a))))
cap = [(0.115, 0.1), (0.17, 0.136), (0.225, 0.152), (0.262, 0.146)]
lame = [(0.235, 0.158), (0.29, 0.17), (0.33, 0.145)]
left += P.shell([[pt(x, r, a) for a in ANG] for x, r in cap], 0.02, "metal")
left += P.shell([[pt(x, r, a, 0.0) for a in ANG] for x, r in lame], 0.02, "metal")
P.mirror_x(left)
