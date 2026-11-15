# Wooden staff with a curved fork holding a faceted crystal, UPRIGHT grip: the long axis is world +Z
# in the rest pose; the grip sits at the handslot, 0.76 m above the foot of the staff (in `idle` the
# hand hangs at ~0.76 m, so the staff stands on the floor). Phase 3 keeps the slot upright in clips.
hs = lm["handslot.r"]
def at(t, u=0.0):
    return hs + Vector((u, 0, t))
P.loft([P.ring(at(-0.76), 0.024, n=8), P.ring(at(0.2), 0.027, n=8), P.ring(at(0.96), 0.031, n=8)], "leather")
P.cylinder(at(0.94), at(1.02), 0.043, n=8, role="leather")
for u in (-1, 1):
    P.loft([P.ring(at(1.0, 0.02 * u), 0.017, n=6), P.ring(at(1.07, 0.058 * u), 0.015, n=6),
            P.ring(at(1.14, 0.06 * u), 0.012, n=6)], "leather")
P.loft([[at(1.02)], P.ring(at(1.10), 0.045, n=8), P.ring(at(1.17), 0.056, n=8), [at(1.34)]], "special")
