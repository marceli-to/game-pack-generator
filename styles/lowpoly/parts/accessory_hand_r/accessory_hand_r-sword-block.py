# Arming sword (lowpoly, v2 detail pass, sized to specs/knight-lowpoly/reference): WEAPON grip, along the handslot
# bone axis (-Y in the T-pose); the edges lie along the forearm (X). Faceted gold pommel, leather grip with a gold
# ferrule, a gold crossguard with flared ends, a broad blade with a centre ridge and bevelled edges and a long point.
hs = lm["handslot.r"]
def at(y, u=0.0, v=0.0):
    return Vector((hs.x + u, y, hs.z + v))
def sec(y, w, t, ridge=1.0):
    """Blade section: 8 points, edges along X (w), ridge along Z (t)."""
    return [at(y, u, v) for u, v in ((w, 0), (0.55 * w, 0.55 * t), (0, t * ridge), (-0.55 * w, 0.55 * t),
                                     (-w, 0), (-0.55 * w, -0.55 * t), (0, -t * ridge), (0.55 * w, -0.55 * t))]
# pommel
P.loft([[at(0.104)], P.ring(at(0.094), 0.02, n=6, axis="y"), P.ring(at(0.08), 0.03, n=6, axis="y"),
        P.ring(at(0.062), 0.026, n=6, axis="y"), [at(0.054)]], "accent")
# grip + ferrule under the guard
P.cylinder(at(0.064), at(-0.098), 0.017, n=6, role="leather")
P.cylinder(at(-0.09), at(-0.112), 0.022, n=6, role="accent")
# crossguard: a bar along X, flared and chamfered at the ends
g = [(-0.112, 0.0), (-0.136, 0.0)]
bar = [(-0.11, 0.018, 0.016), (-0.085, 0.014, 0.014), (-0.03, 0.012, 0.013), (0.03, 0.012, 0.013),
       (0.085, 0.014, 0.014), (0.11, 0.018, 0.016)]
P.loft([P.rect(at(-0.124, u), d, h, chamfer=0.005, axis="x") for u, d, h in bar], "accent")
# blade
P.loft([sec(-0.134, 0.042, 0.013), sec(-0.42, 0.04, 0.012), sec(-0.5, 0.03, 0.01), [at(-0.57)]], "metal")
