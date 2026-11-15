# Long robe from the collar to above the ankles, 19 points per ring with a gold front strip
# (between -95 and -85 degrees), gold collar and hem; flares in a curve. Belt with a buckle.
ANG = [-85, -65, -45, -25, -5, 15, 35, 55, 75, 90, 105, 125, 145, 165, 185, 205, 225, 245, 265]
STRIP = len(ANG) - 1
rings = [  # (z, rx, ry, y-offset)
    (1.40, 0.080, 0.075, 0.0), (1.37, 0.120, 0.100, 0.0), (1.34, 0.165, 0.120, 0.0),
    (1.29, 0.195, 0.135, 0.0), (1.12, 0.182, 0.132, 0.0), (1.00, 0.165, 0.125, 0.0),
    (0.85, 0.200, 0.150, 0.005), (0.69, 0.240, 0.190, 0.01), (0.52, 0.290, 0.225, 0.015),
    (0.36, 0.345, 0.255, 0.02), (0.30, 0.355, 0.260, 0.02),
]
pts = [P.ring((0, dy, z), rx, ry, angles=ANG) for z, rx, ry, dy in rings]
last = len(rings) - 2
P.loft(pts, lambda b, i: "accent" if (i == STRIP or b in (0, last)) else "primary", cap_roles=("accent", "dark"))
P.loft([P.rrect((0, 0, 0.955), 0.185, 0.142, 0.08), P.rrect((0, 0, 1.045), 0.19, 0.147, 0.08)], "leather")
P.rbox((-0.045, -0.172, 0.948), (0.045, -0.135, 1.052), "metal", r=0.012, bevel=0, seg=1, axis="y")
P.box((-0.022, -0.176, 0.972), (0.022, -0.168, 1.028), "leather")
