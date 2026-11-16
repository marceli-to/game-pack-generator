# Spellbook (lowpoly): WEAPON grip on the left hand, pinched in the fist and hanging past the fingertips; in the
# T-pose the covers face up/down (+-Z), so with the arms down the cover faces outward. Leather covers and spine,
# pages (`secondary`), gold corner clasp.
hs = lm["handslot.l"]
x0, x1 = hs.x - 0.02, hs.x + 0.19
P.rbox((x0 + 0.004, -0.07, hs.z - 0.016), (x1 - 0.006, 0.068, hs.z + 0.016), "secondary", r=0.004, bevel=0, seg=1)
for z0 in (hs.z - 0.028, hs.z + 0.016):
    P.rbox((x0, -0.077, z0), (x1, 0.075, z0 + 0.012), "leather", r=0.01, bevel=0, seg=1)
P.rbox((x0, 0.064, hs.z - 0.024), (x1, 0.082, hs.z + 0.024), "leather", r=0.006, bevel=0, seg=1)
P.box((x1 - 0.045, -0.084, hs.z - 0.03), (x1 - 0.015, -0.068, hs.z + 0.03), "accent")
