# Knight's round shield (lowpoly) as its own GLB: the geometry of accessory_hand_l-shield-round-block (the knight's
# in-mesh shield, sized to specs/knight-lowpoly/reference), moved into the hand slot's frame. SHIELD prop (root
# STYLE.md §9b): face towards -Y (glTF +Z = handslot.l +Z, KayKit's shields), the fist (the chibi handslot.l) at the
# origin behind it, the strap along Z. Board on the team cell (`primary`) with a gold rim and a steel boss.
lm = {"handslot.l": Vector((0.5702, 0.0, 0.6777))}
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
# into the slot frame: the T-pose face direction (+Z) becomes -Y, the forearm (X) becomes +Z
R = Matrix(((0, -1, 0, 0), (0, 0, -1, 0), (1, 0, 0, 0), (0, 0, 0, 1)))
P.transform(list(P.bm.faces), R @ Matrix.Translation(-Vector(hs)))
P.anchor("grip", (0, 0, 0))
