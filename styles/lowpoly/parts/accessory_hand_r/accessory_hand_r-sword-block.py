# Arming sword (lowpoly): WEAPON grip, along the handslot bone axis (-Y in the T-pose); the edges lie along the
# forearm (X). Faceted pommel, leather grip through the fist, gold crossguard just past the thumb, diamond blade.
hs = lm["handslot.r"]
def at(y, u=0.0, v=0.0):
    return Vector((hs.x + u, y, hs.z + v))
P.loft([[at(0.088)], P.ring(at(0.072), 0.024, n=6, axis="y"), P.ring(at(0.054), 0.024, n=6, axis="y"),
        [at(0.04)]], "accent")
P.cylinder(at(0.058), at(-0.108), 0.016, n=6, role="leather")
P.rbox((hs.x - 0.08, -0.128, hs.z - 0.018), (hs.x + 0.08, -0.106, hs.z + 0.018), "accent", r=0.009, bevel=0,
       seg=1, axis="y")
dia = lambda y, w, t: P.ring(at(y), w, t, axis="y", angles=[0, 90, 180, 270])
P.loft([dia(-0.12, 0.034, 0.011), dia(-0.42, 0.03, 0.01), [at(-0.49)]], "metal")
