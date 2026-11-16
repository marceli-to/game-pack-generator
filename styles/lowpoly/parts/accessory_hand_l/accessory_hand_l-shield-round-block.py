# Round shield (lowpoly): WEAPON grip on the left hand, strapped over the back of the fist: in the T-pose the
# face looks up (+Z), so with the arms hanging it faces outward. 10 sides, gold rim, steel boss, leather back.
hs = lm["handslot.l"]
c = Vector((hs.x - 0.01, 0, 0))
def ring(z, r):
    return P.ring((c.x, c.y, z), r, n=10)
P.loft([ring(0.79, 0.16), ring(0.8, 0.178), ring(0.82, 0.178), ring(0.826, 0.158), ring(0.832, 0.148),
        [Vector((c.x, c.y, 0.842))]], ["accent", "accent", "accent", "accent", "primary"], cap_roles=("leather", None))
P.dome((c.x, c.y, 0.84), (0, 0, 1), 0.052, 0.035, n=8, role="metal")
P.rbox((hs.x - 0.03, -0.022, hs.z - 0.01), (hs.x + 0.03, 0.022, 0.795), "leather", r=0.008, bevel=0, seg=1)
