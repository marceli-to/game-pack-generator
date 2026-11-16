# Dwarf axe (lowpoly): WEAPON grip, handle along the handslot bone axis (-Y in the T-pose), the single blade
# pointing outward along the forearm (-X for the right hand), so it leads in a chop. Gold pommel cap, leather
# grip wrap, wooden haft, steel head with a short poll. 0.6 m overall (the sheet's 0.84 m would stick far out
# in front of a 1 m dwarf with this grip).
hs = lm["handslot.r"]
def at(y, u=0.0, v=0.0):
    return Vector((hs.x + u, y, hs.z + v))
P.cylinder(at(0.085), at(0.06), 0.03, n=6, role="accent")
P.cylinder(at(0.062), at(-0.12), 0.022, n=6, role="leather")
P.cylinder(at(-0.118), at(-0.53), 0.02, n=6, role="primary", r_end=0.018)
P.cylinder(at(-0.4), at(-0.415), 0.024, n=6, role="metal")
yc = -0.47
P.loft([P.rect(at(yc, 0.045), 0.032, 0.02, chamfer=0.01, axis="x"), P.rect(at(yc, 0.0), 0.05, 0.024, chamfer=0.012, axis="x"),
        P.rect(at(yc, -0.06), 0.05, 0.02, chamfer=0.012, axis="x"), P.rect(at(yc, -0.13), 0.085, 0.012, chamfer=0.01, axis="x"),
        P.rect(at(yc, -0.17), 0.11, 0.005, chamfer=0.004, axis="x")], "metal")
