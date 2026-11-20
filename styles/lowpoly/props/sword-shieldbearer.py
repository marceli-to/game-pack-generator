# One-handed sword (lowpoly), from specs/shieldbearer/reference (the held item on the sheet, scaled to 0.8 of the
# sheet's size: "a short one-handed sword", 0.64 m). MELEE prop (root STYLE.md §9b): standing upright in the hand
# slot's frame, blade up (+Z = glTF +Y, KayKit's 1H_Sword on handslot.r), flat of the blade facing -Y, edges across X.
# Wide chunky blade with a centre ridge and a point, a flat crossguard, a leather grip, a faceted ball pommel.
K = 0.00189                                   # m per sheet pixel at 0.8 x the sheet's scale
def z(y): return (780 - y) * K                # sheet row -> height; the grip's centre (row 780) is the origin
def blade(y, w, t=0.026):
    """6-point blade section: edges at +-w/2 across X, a ridge on each face"""
    a, b = w / 2, w * 0.28
    return [Vector(p) for p in ((a, 0, z(y)), (b, -t / 2, z(y)), (-b, -t / 2, z(y)), (-a, 0, z(y)),
                                (-b, t / 2, z(y)), (b, t / 2, z(y)))]
P.loft([blade(712, 47 * K), blade(640, 51 * K), blade(574, 54 * K), blade(556, 40 * K, 0.02),
        [Vector((0, 0, z(526)))]], "metal")
# crossguard: a flat bar with chamfered ends
P.rbox((-52 * K, -0.03, z(742)), (52 * K, 0.03, z(714)), "metal", r=0.012, bevel=0, seg=1, axis="z")
# grip: six sides, leather, running into guard and pommel
P.cylinder((0, 0, z(745)), (0, 0, z(816)), 0.028, n=6, role="leather")
# pommel: a faceted ball
P.loft([P.ring((0, 0, z(814)), 0.02, n=8), P.ring((0, 0, z(826)), 0.046, n=8), P.ring((0, 0, z(850)), 0.048, n=8),
        P.ring((0, 0, z(864)), 0.026, n=8)], "metal")
P.anchor("grip", (0, 0, 0))
P.anchor("tip", (0, 0, z(526)))
