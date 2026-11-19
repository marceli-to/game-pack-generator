# Uniform trousers with knee pads (tinfox, hero-m), for specs/rifle-guard/reference: the guard's trousers
# (legs-trousers-hero) + an octagonal knee pad on each knee, a black rim round a dark-grey face, standing proud of
# the knee; the pad shares thigh and shin like a kneecap (half each), so it rides over the bent knee.
hip, kn = lm["hip.l"], lm["knee.l"]
x = hip.x
# facet pass (2026-11-19): the guard trousers' sections (legs-trousers-hero): chamfered rectangles, knee break at z 0.46
rows = [(0.95, 0.075, 0.08, 0.0), (hip.z, 0.105, 0.105, 0.0), (0.78, 0.13, 0.12, 0.0), (0.62, 0.13, 0.122, -0.005),
        (0.5, 0.126, 0.12, 0.0), (0.46, 0.134, 0.128, 0.008), (0.41, 0.112, 0.108, 0.018),
        (0.35, 0.1, 0.094, 0.04), (0.3, 0.082, 0.08, 0.05)]
dx = lambda z: 0.0 if z >= kn.z else 0.02 * min(1.0, (kn.z - z) / (kn.z - 0.3))
def sec(z, rx, ry, dy):
    return P.rrect((x + dx(z), dy, z), rx, ry, 0.38 * min(rx, ry), seg=1)
legs = P.loft([sec(*r) for r in rows], "primary")
# knee pad: the front of the knee is at y ~ -0.128 (ring ry 0.11 about y -0.018)
pz = kn.z + 0.05
oct_ = lambda y, rx, rz: P.ring((x, y, pz), rx, rz, n=8, axis="y", phase=22.5)
pad = P.loft([oct_(-0.085, 0.085, 0.08), oct_(-0.14, 0.098, 0.092), oct_(-0.158, 0.092, 0.086),
              oct_(-0.166, 0.072, 0.066)], "secondary", cap_roles=("secondary", "dark"))
pad += P.loft([oct_(-0.16, 0.074, 0.068), oct_(-0.17, 0.07, 0.064)], "dark")
P.set_weights(pad, {"upperleg.l": 0.5, "lowerleg.l": 0.5})
P.mirror_x(legs + pad)
