# One-handed bearded axe (lowpoly), from specs/berserker/reference (the held items on the sheet, 0.8 x the sheet's
# scale like the shieldbearer's sword: 0.67 m). MELEE prop (root STYLE.md §9b): upright in the hand slot's frame, head
# up (+Z = glTF +Y), as KayKit's 1H_Axe on the Barbarian. KayKit's right axe points its blade along handslot.r's +X,
# the offhand axe along handslot.l's -X: SIDE = 1 for the right hand, -1 for the left (the same axe turned about its
# haft). Iron head: a chamfered poll block with a cap, a bearded blade thinning to the edge; wooden haft with leather
# wraps (two bands and a crossed middle), an octagonal iron butt cap.
SIDE = 1
K = 0.001742                                  # m per sheet pixel at 0.8 x the sheet's 2.178 mm/px
def x(px): return SIDE * (px - 1172) * K      # sheet column -> across (blade side), haft centre at column 1172
def z(py): return (760 - py) * K              # sheet row -> height; the fist (row 760) is the origin
def sec(px, top, bot, t):
    """blade section at a column: 6 points, a ridge at top and bottom, flat faces t thick"""
    c = 0.004
    return [Vector(p) for p in ((x(px), 0, z(top)), (x(px), t / 2, z(top) - c), (x(px), t / 2, z(bot) + c),
                                (x(px), 0, z(bot)), (x(px), -t / 2, z(bot) + c), (x(px), -t / 2, z(top) - c))]
blade = [sec(1192, 538, 582, 0.028), sec(1212, 530, 597, 0.02), sec(1232, 511, 621, 0.014),
         sec(1249, 501, 614, 0.009), sec(1262, 528, 592, 0.004)]
if SIDE < 0: blade = [list(reversed(r)) for r in blade]       # keep the faces' winding outward when mirrored
P.loft(blade, "metal")
# poll: the block behind the blade, chamfered; a small cap on top
x0, x1 = sorted((x(1138), x(1196)))
P.rbox((x0, -0.026, z(578)), (x1, 0.026, z(521)), "metal", r=0.008, bevel=0, seg=1, axis="z")
x0, x1 = sorted((x(1154), x(1181)))
P.rbox((x0, -0.017, z(523)), (x1, 0.017, z(514)), "metal", r=0.004, bevel=0, seg=1, axis="z")
# haft: eight sides, a little thicker towards the butt, running into the head and the cap
P.loft([P.ring((0, 0, z(845)), 0.0265, n=8), P.ring((0, 0, z(700)), 0.025, n=8),
        P.ring((0, 0, z(560)), 0.023, n=8)], "accent")
# leather wraps: two bands and a thinner crossed middle
for top, bot, r in ((648, 673, 0.031), (720, 746, 0.031), (673, 720, 0.028)):
    P.cylinder((0, 0, z(bot)), (0, 0, z(top)), r, n=8, role="leather")
# butt cap: octagonal, chamfered top and bottom
P.loft([P.ring((0, 0, z(888)), 0.033, n=8), P.ring((0, 0, z(880)), 0.042, n=8), P.ring((0, 0, z(853)), 0.042, n=8),
        P.ring((0, 0, z(843)), 0.033, n=8)], "metal")
P.anchor("grip", (0, 0, 0))
P.anchor("tip", (x(1262), 0, z(560)))
