# Dagger (lowpoly): WEAPON grip along the handslot bone axis (-Y in the T-pose), edges along the forearm (X).
# Small faceted pommel, leather grip through the fist, short gold guard past the thumb, diamond blade.
hs = lm["handslot.r"]
def at(y, u=0.0, v=0.0):
    return Vector((hs.x + u, y, hs.z + v))
P.loft([[at(0.078)], P.ring(at(0.064), 0.02, n=6, axis="y"), P.ring(at(0.05), 0.02, n=6, axis="y"),
        [at(0.038)]], "accent")
P.cylinder(at(0.052), at(-0.108), 0.015, n=6, role="leather")
P.rbox((hs.x - 0.05, -0.124, hs.z - 0.014), (hs.x + 0.05, -0.106, hs.z + 0.014), "accent", r=0.007, bevel=0,
       seg=1, axis="y")
dia = lambda y, w, t: P.ring(at(y), w, t, axis="y", angles=[0, 90, 180, 270])
P.loft([dia(-0.116, 0.028, 0.009), dia(-0.27, 0.024, 0.008), [at(-0.33)]], "metal")
