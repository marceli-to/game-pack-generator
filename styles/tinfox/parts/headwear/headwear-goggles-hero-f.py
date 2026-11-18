# Goggles pushed up on the forehead (tinfox, hero-f; player 4), from specs/player-4/reference: two round lens cups on
# the front of the hair above the brows, tilted up, a silver rim (`metal`) round a grey lens (`special`), a short
# bridge; a dark strap (`dark`) round the head over the curls, running down to the back (high in front, low behind).
# Built in hero-m coordinates and moved onto the hero-f head at the end (as head-hero-f).
# strap: a band on a tilted ellipse round the curls
def strap_pt(t, dz, out=0.0):
    x = (0.2 - 0.02 * max(0.0, -math.cos(t)) + out) * math.sin(t)
    y = -(0.19 + out) * math.cos(t) if math.cos(t) > 0 else -(0.19 + out) * math.cos(t)
    z = 1.77 + 0.09 * (math.cos(t) - 1) + dz
    return Vector((x, y + 0.012, z))
ts = [2 * math.pi * k / 14 for k in range(14)]
P.shell([[strap_pt(t, 0.016) for t in ts], [strap_pt(t, -0.016) for t in ts]], 0.012, "dark", cyclic=True)
# lens cups, facing forward and up 35 deg
for sgn in (1, -1):
    c = Vector((sgn * 0.058, -0.2, 1.775))
    ax = Vector((0, -math.cos(math.radians(35)), math.sin(math.radians(35))))
    q = Vector((0, 0, 1)).rotation_difference(ax)
    def rg(d, r, n=8):
        return [c + q @ Vector((r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), d)) for i in range(n)]
    P.loft([rg(-0.03, 0.036), rg(0.0, 0.042)], "dark", cap_roles=("dark", "dark"))
    P.loft([rg(-0.002, 0.049), rg(0.02, 0.047)], "metal", cap_roles=("metal", "metal"))
    P.loft([rg(0.012, 0.034), rg(0.024, 0.034)], "special")
# bridge between the cups
P.rbox((-0.03, -0.215, 1.765), (0.03, -0.19, 1.785), "dark", r=0.005, bevel=0, seg=1)
hb = lm["head_base"].z
P.transform(list(P.bm.faces), Matrix.Translation((0, 0, hb)) @ Matrix.Diagonal((0.95, 0.95, 1.0, 1.0))
            @ Matrix.Translation((0, 0, -1.47)))
