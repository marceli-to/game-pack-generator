# Wooden staff with a slight zigzag, a gold ring, a two-prong holder and a faceted crystal ball (8 x 5).
# UPRIGHT grip: long axis world +Z through the handslot; the foot is 0.4 m below the grip (with the hand
# hanging in `idle` the staff stands on the floor).
hs = lm["handslot.r"]
def at(t, u=0.0, v=0.0):
    return hs + Vector((u, v, t))
P.loft([P.ring(at(-0.40), 0.022, n=6), P.ring(at(-0.12, 0.012), 0.023, n=6), P.ring(at(0.12, -0.012), 0.024, n=6),
        P.ring(at(0.36), 0.026, n=6)], "secondary")
P.cylinder(at(0.30), at(0.34), 0.034, n=6, role="accent")
for u in (-1, 1):
    P.loft([P.ring(at(0.35, 0.012 * u), 0.016, n=6), P.ring(at(0.42, 0.05 * u), 0.014, n=6),
            P.ring(at(0.48, 0.05 * u), 0.012, n=6)], "secondary")
c, r = at(0.47), 0.058
lat = [math.radians(a) for a in (-54, -18, 18, 54)]
P.loft([[c + Vector((0, 0, -r))]] + [P.ring(c + Vector((0, 0, r * math.sin(b))), r * math.cos(b), n=8) for b in lat]
       + [[c + Vector((0, 0, r))]], "special")
