# Round shield (lowpoly, v2 detail pass, sized to specs/knight-lowpoly/reference): WEAPON grip on the left hand,
# strapped over the back of the fist: in the T-pose the face looks up (+Z), so with the arms hanging it faces
# outward. 12 sides: a thick bevelled gold rim, a slightly domed blue face, a faceted steel boss with a gold ring,
# leather back and strap.
hs = lm["handslot.l"]
c = Vector((hs.x - 0.01, 0, 0))
def ring(z, r, n=12):
    return P.ring((c.x, c.y, z), r, n=n)
P.loft([ring(0.79, 0.19), ring(0.8, 0.212), ring(0.822, 0.212), ring(0.83, 0.19), ring(0.832, 0.172),
        ring(0.842, 0.1), [Vector((c.x, c.y, 0.846))]], ["accent", "accent", "accent", "accent", "primary", "primary"],
       cap_roles=("leather", None))
P.loft([ring(0.84, 0.072, 8), ring(0.848, 0.072, 8), ring(0.852, 0.06, 8)], "accent")
P.loft([ring(0.85, 0.058, 8), ring(0.872, 0.046, 8), ring(0.884, 0.024, 8), [Vector((c.x, c.y, 0.888))]], "metal")
P.rbox((hs.x - 0.03, -0.022, hs.z - 0.01), (hs.x + 0.03, 0.022, 0.795), "leather", r=0.008, bevel=0, seg=1)
