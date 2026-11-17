# Dagger (lowpoly): WEAPON grip along the handslot bone axis (-Y in the T-pose), edges along the forearm (X).
# v2 (rogue sheet): faceted gold pommel, leather grip with a gold ferrule, gold crossguard with flared ends,
# a leaf blade (widest a third down) with a centre ridge.
hs = lm["handslot.r"]
def at(y, u=0.0, v=0.0):
    return Vector((hs.x + u, y, hs.z + v))
P.loft([[at(0.078)], P.ring(at(0.064), 0.02, n=6, axis="y"), P.ring(at(0.05), 0.02, n=6, axis="y"),
        [at(0.038)]], "accent")
def sec(y, w, t):
    return [at(y, u, v) for u, v in ((w, 0), (0.5 * w, 0.6 * t), (0, t), (-0.5 * w, 0.6 * t), (-w, 0),
                                     (-0.5 * w, -0.6 * t), (0, -t), (0.5 * w, -0.6 * t))]
P.cylinder(at(0.052), at(-0.092), 0.016, n=6, role="leather")
P.cylinder(at(-0.084), at(-0.104), 0.02, n=6, role="accent")
bar = [(-0.062, 0.017, 0.016), (-0.04, 0.013, 0.013), (0.04, 0.013, 0.013), (0.062, 0.017, 0.016)]
P.loft([P.rect(at(-0.115, u), d, h, chamfer=0.005, axis="x") for u, d, h in bar], "accent")
P.loft([sec(-0.124, 0.022, 0.008), sec(-0.19, 0.036, 0.011), sec(-0.26, 0.03, 0.009), [at(-0.33)]], "metal")
