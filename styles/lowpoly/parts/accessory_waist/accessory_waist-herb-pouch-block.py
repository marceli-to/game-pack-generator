# Herb pouch + potion bottle (lowpoly chibi), hanging from the healer's rope belt (z 0.528) on the wearer's left
# front: a small leather pouch with a flap and a gold leaf on it, and a round purple potion (role `special`)
# with a cream cork (role `primary`) on a short cord. Hung high so a lifted thigh doesn't reach them.
# pouch body, flap, leaf
P.rbox((0.0, -0.205, 0.415), (0.09, -0.152, 0.505), "leather", r=0.014, bevel=0, seg=1)
P.rbox((-0.004, -0.214, 0.462), (0.094, -0.168, 0.512), "leather", r=0.012, bevel=0, seg=1)
leaf = [Vector((0.045, -0.222, 0.495)), Vector((0.062, -0.222, 0.48)), Vector((0.045, -0.222, 0.462)),
        Vector((0.028, -0.222, 0.48))]
P.loft([leaf, [p + Vector((0, 0.012, 0)) for p in leaf]], "accent")
# potion: an 8-sided ball, neck, cork
c, r = Vector((0.142, -0.17, 0.43)), 0.042
lat = [-55, -20, 20, 55]
P.loft([[c + Vector((0, 0, -r))]]
       + [P.ring(c + Vector((0, 0, r * math.sin(math.radians(b)))), r * math.cos(math.radians(b)), n=8) for b in lat]
       + [[c + Vector((0, 0, r))]], "special")
P.cylinder(c + Vector((0, 0, r * 0.8)), c + Vector((0, 0, r + 0.025)), 0.014, n=6, role="special")
P.cylinder(c + Vector((0, 0, r + 0.022)), c + Vector((0, 0, r + 0.045)), 0.018, n=6, role="primary")
# cord from the belt to the cork
P.cylinder(Vector((0.13, -0.158, 0.53)), c + Vector((0, 0, r + 0.04)), 0.006, n=4, role="leather")
