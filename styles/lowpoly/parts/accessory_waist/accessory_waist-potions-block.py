# Potion belt (lowpoly): two small flasks (`special` liquid, leather stoppers) in a leather holder hung high on the
# belt at the wearer's right front (-X; pouches sit on +X), above where a hem rises in run (about 0.42).
P.rbox((-0.18, -0.205, 0.452), (-0.055, -0.168, 0.49), "leather", r=0.01, bevel=0, seg=1)
for cx, h in ((-0.088, 0.0), (-0.145, -0.012)):
    c = (cx, -0.2, 0.0)
    P.loft([P.ring((cx, c[1], z), r, n=6) for z, r in ((0.44, 0.022), (0.455, 0.03), (0.5 + h, 0.03),
                                                        (0.515 + h, 0.014), (0.53 + h, 0.012))], "special")
    P.loft([P.ring((cx, c[1], z), r, n=6) for z, r in ((0.525 + h, 0.016), (0.548 + h, 0.014))], "leather")
