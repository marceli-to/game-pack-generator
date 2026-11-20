# Berserker arms (lowpoly chibi), from specs/berserker/reference: bare muscular arms along the T-pose arm (+X, 8
# sides, skin) with a bulging upper arm; a long leather bracer over the forearm with a raised lip at each end and a
# steel plate on its outer side (+Z in the T-pose = outward with the arms down); a grey-brown fur tuft over each
# shoulder (`secondary`, one shell over the top with a jagged outer edge), joining the torso's fur mantle.
# Starts inside the torso at x 0.06.
sh, el, wr = lm["shoulder.l"], lm["elbow.l"], lm["wrist.l"]
zc = sh.z
xs = [0.06, sh.x + 0.03, el.x - 0.015, el.x + 0.02, wr.x - 0.01]
rs = [0.078, 0.088, 0.074, 0.066, 0.058]
left = P.loft([P.ring((x, 0, zc), r, n=8, axis="x") for x, r in zip(xs, rs)], "skin")
# bracer: leather over the forearm, lips at both ends
bx = [wr.x - 0.14, wr.x - 0.135, wr.x - 0.123, wr.x - 0.03, wr.x - 0.018, wr.x - 0.012]
br = [0.076, 0.088, 0.084, 0.08, 0.09, 0.084]
left += P.loft([P.ring((x, 0, zc), r, n=8, axis="x") for x, r in zip(bx, br)], "leather")
left += P.rbox((wr.x - 0.1, -0.035, zc + 0.078), (wr.x - 0.05, 0.035, zc + 0.098), "metal", r=0.008, bevel=0.004,
               seg=1, axis="z")
# shoulder fur: rows along the arm, 7 columns from front to back over the top; outer edge jagged
ANG = [-115 + 230 * k / 6 for k in range(7)]
def pt(x, r, a, dz=0.012):
    return Vector((x, r * math.sin(math.radians(a)), zc + dz + r * math.cos(math.radians(a))))
rows = [[pt(0.1, 0.115, a) for a in ANG], [pt(0.17, 0.14, a) for a in ANG], [pt(0.24, 0.145, a) for a in ANG],
        [pt(0.3 + (0.035 if k % 2 == 0 else 0.0), 0.13 if k % 2 == 0 else 0.135, a) for k, a in enumerate(ANG)]]
left += P.shell(rows, -0.03, "secondary")
P.mirror_x(left)
