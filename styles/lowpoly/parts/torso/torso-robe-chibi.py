# Wizard robe (lowpoly chibi): collar to just above the boots, 10 facets plus a narrow gold front strip,
# gold collar and hem, flaring towards the hem; brown belt.
ANG = [-85, -50, -15, 20, 55, 90, 125, 160, 195, 230, 265]
STRIP = len(ANG) - 1
rings = [  # (z, rx, ry, y-offset)
    (0.765, 0.07, 0.065, 0.0), (0.752, 0.145, 0.115, 0.0), (0.715, 0.198, 0.142, 0.0), (0.62, 0.197, 0.146, 0.0),
    (0.52, 0.19, 0.145, 0.0), (0.40, 0.21, 0.16, 0.005), (0.27, 0.24, 0.18, 0.01), (0.235, 0.25, 0.188, 0.01),
    (0.19, 0.255, 0.193, 0.01),
]
pts = [P.ring((0, dy, z), rx, ry, angles=ANG) for z, rx, ry, dy in rings]
last = len(rings) - 2
P.loft(pts, lambda b, i: "accent" if (i == STRIP or b in (0, last)) else "primary", cap_roles=("accent", "dark"))
P.loft([P.rrect((0, 0, 0.465), 0.2, 0.155, 0.06, seg=1), P.rrect((0, 0, 0.535), 0.2, 0.155, 0.06, seg=1)], "leather")
