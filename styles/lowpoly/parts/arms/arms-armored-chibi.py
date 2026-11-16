# Armoured arms (lowpoly chibi), fitted to specs/knight-lowpoly/reference: steel sleeves along the T-pose arm (+X),
# 8 sides, a wide gold band on the forearm; a rounded steel pauldron cap with a raised gold rim over each shoulder.
# Starts inside the torso at x 0.06; loops at shoulder and elbow.
sh, el, wr = lm["shoulder.l"], lm["elbow.l"], lm["wrist.l"]
zc = sh.z
xs = [0.06, sh.x + 0.01, el.x - 0.03, el.x + 0.03, wr.x - 0.09, wr.x - 0.085, wr.x - 0.02, wr.x - 0.005]
rs = [0.072, 0.074, 0.068, 0.07, 0.074, 0.084, 0.086, 0.08]
left = P.loft([P.ring((x, 0, zc), r, n=8, axis="x") for x, r in zip(xs, rs)],
              ["metal"] * 4 + ["accent"] * 3, cap_roles=("metal", "dark"))
# pauldron: a rounded steel cap over the shoulder (4 rows along the arm, 7 columns from front to back over the
# top), with a raised 4-sided gold strap swept along its front, outer and back edges
AX = [0.14, 0.2, 0.265, 0.315]
RR = [0.09, 0.124, 0.128, 0.1]
ANG = [-102 + 34 * k for k in range(7)]
def pt(x, r, a):
    return Vector((x, r * math.sin(math.radians(a)), zc + 0.012 + r * math.cos(math.radians(a))))
left += P.shell([[pt(x, r, a) for a in ANG] for x, r in zip(AX, RR)], 0.016, "metal")
path = [pt(x, r + 0.004, -102) for x, r in zip(AX[1:], RR[1:])]
path += [pt(AX[-1] + 0.002, RR[-1] + 0.004, a) for a in ANG[1:-1]]
path += [pt(x, r + 0.004, 102) for x, r in reversed(list(zip(AX[1:], RR[1:])))]
nrm = []
for p_ in path:
    radial = Vector((0, p_.y, p_.z - zc - 0.012)).normalized()
    nrm.append((radial + Vector((0.9, 0, 0))).normalized() if p_.x > AX[-1] - 0.01 else radial)
left += P.sweep(path, [(-0.004, -0.014), (0.014, -0.014), (0.014, 0.014), (-0.004, 0.014)], "accent", nrm)
P.mirror_x(left)
