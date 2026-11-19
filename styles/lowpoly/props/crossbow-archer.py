# Two-handed wooden crossbow (lowpoly), from specs/archer/reference (the held item on the sheet; 0.85 m long, the
# sheet's length at the archer's scale). WEAPON prop (root STYLE.md §9b): lying along +X (bow and bolt forward), top
# +Z (bolt groove up), the limbs across ±Y; grip at the origin, the stock reaching 0.25 m behind it. Exported as its
# own GLB in the hand slot's frame (glTF +X forward, +Y up), like KayKit's 2H_Crossbow on `handslot.r`.
# Stock and gold band, dark iron bow arm sweeping back to the tips, cream string, a loaded bolt with a pointed head
# and one fin, a small iron trigger lever.
# The hand holds the beam 15 cm in front of the gold band (Marcel: grab it further towards the bow, so it hangs higher
# in idle); the stock behind the band is shortened to match, so the butt stays 0.25 m behind the hand as before (in
# KayKit's 2H aim it then sits ~2-6 cm behind the right shoulder; the full-length stock at this grip came out 15 cm).
GRIP, REAR = 0.15, 0.4
def at(x, up=0.0, across=0.0):
    return Vector(((x if x >= 0 else x * REAR) - GRIP, across, up))
def sec(x, hy, hz, cy=0.0, k=0.35):
    """chamfered rectangular section across the stock at x: hy up/down, hz across (8 points)"""
    a, b = hy * k, hz * k
    pts = [(hy, hz - b), (hy - a, hz), (-hy + a, hz), (-hy, hz - b), (-hy, -hz + b), (-hy + a, -hz), (hy - a, -hz),
           (hy, -hz + b)]
    return [at(x, cy + y, z) for y, z in pts]
# stock: flared butt (tall, the sheet's foot), narrowing to the grip, a gold band, the beam forward to the bow
P.loft([sec(-0.25, 0.065, 0.032, -0.02), sec(-0.17, 0.048, 0.03, -0.012), sec(-0.06, 0.03, 0.026),
        sec(-0.02, 0.03, 0.026)], "leather")
P.loft([sec(-0.022, 0.036, 0.031), sec(0.03, 0.036, 0.031)], "accent")
P.loft([sec(0.028, 0.036, 0.032), sec(0.38, 0.036, 0.032), sec(0.52, 0.03, 0.028), sec(0.555, 0.022, 0.022)], "leather")
# wooden block where the bow arm sits
P.loft([sec(0.4, 0.046, 0.05), sec(0.5, 0.046, 0.05)], "leather")
# bow arm: one dark iron bar across at x 0.45, sweeping back towards the tips
arm = [(0.0, 0.455), (0.1, 0.452), (0.2, 0.43), (0.27, 0.4), (0.31, 0.362)]
full = [(-z, x) for z, x in arm[::-1]] + arm[1:]
P.loft([[at(x - 0.026, 0.024, z), at(x - 0.026, -0.024, z), at(x + 0.026, -0.024, z), at(x + 0.026, 0.024, z)]
        for z, x in full], "metal")
# string: from the tips back to the nut at x 0.22, on top of the beam
nut = at(0.22, 0.038)
for s in (1, -1):
    P.cylinder(at(0.365, 0.0, s * 0.3), nut, 0.005, n=4, role="special")
# loaded bolt along the groove: shaft, pointed head in front of the bow, one fin at the nut
P.cylinder(at(0.2, 0.05), at(0.57, 0.05), 0.012, n=4, role="special")
P.loft([P.ring(at(0.57, 0.05), 0.026, n=4, axis="x"), [at(0.64, 0.05)]], "special")
fin = [at(0.205, 0.055), at(0.21, 0.09), at(0.28, 0.062), at(0.28, 0.055)]
P.loft([[p + Vector((0, 0.003, 0)) for p in fin], [p - Vector((0, 0.003, 0)) for p in fin]], "special")
# trigger lever under the stock just in front of the grip
P.loft([sec(0.05, 0.012, 0.008, -0.04), sec(0.09, 0.012, 0.008, -0.07)], "metal")
P.anchor("grip", (0, 0, 0))
P.anchor("muzzle", at(0.64, 0.05))
