# Tower shield (lowpoly), from specs/shieldbearer/reference (the held item on the sheet at 0.8 of the sheet's size:
# 0.44 x 0.78 m, "taller than half the character"). SHIELD prop (root STYLE.md §9b): standing upright in the hand
# slot's frame (KayKit's Rectangle_Shield on handslot.l), top +Z (glTF +Y), face towards -Y (glTF +Z), the fist at
# the origin behind it. Team-coloured board (`primary` = team cell 17) with cut corners, a raised steel rim with
# twelve rivets, a round faceted steel boss in the middle; a leather handle bar on two blocks behind.
K = 0.00189                                   # m per sheet pixel at 0.8 x the sheet's scale
CX, CY = 1182, 667                            # sheet: the shield's centre column / row (the fist sits there)
def xz(px, py, y):
    return Vector(((px) * K, y, (CY - py) * K))
OUT = [(45, 462), (116, 505), (116, 835), (75, 873), (-75, 873), (-116, 835), (-116, 505), (-45, 462)]
INN = [(36, 488), (92, 518), (92, 824), (62, 849), (-62, 849), (-92, 824), (-92, 518), (-36, 488)]
FRONT, BACK = -0.085, -0.055                  # board faces (y); the fist (r ~6 cm) stays behind the board
P.loft([[xz(px, py, BACK) for px, py in OUT], [xz(px, py, FRONT) for px, py in OUT]], "primary")
# raised rim: a flat band on the front face, from the outline in to the inner line
P.shell([[xz(px, py, FRONT - 0.001) for px, py in OUT], [xz(px, py, FRONT - 0.001) for px, py in INN]], 0.014,
        "metal", cyclic=True)
# rivets on the rim: the corners and two along each long side, one on top and bottom
RIV = [(40, 478), (-40, 478), (104, 512), (-104, 512), (104, 615), (-104, 615), (104, 720), (-104, 720),
       (104, 828), (-104, 828), (68, 862), (-68, 862)]
for px, py in RIV:
    P.dome(xz(px, py, FRONT - 0.014), (0, -1, 0), 0.011, 0.008, n=6, role="metal")
# boss: a round faceted dome in the middle, on a flat ring
c = xz(0, 650, FRONT)
P.loft([[c + Vector((0.09 * math.cos(a), 0.003, 0.09 * math.sin(a))) for a in [k * math.pi / 5 for k in range(10)]],
        [c + Vector((0.09 * math.cos(a), -0.012, 0.09 * math.sin(a))) for a in [k * math.pi / 5 for k in range(10)]],
        [c + Vector((0.062 * math.cos(a), -0.045, 0.062 * math.sin(a))) for a in [k * math.pi / 5 for k in range(10)]],
        [c + Vector((0.022 * math.cos(a), -0.058, 0.022 * math.sin(a))) for a in [k * math.pi / 5 for k in range(10)]]],
       "metal")
# handle behind: a leather bar the fist closes round, on two blocks against the board's back
P.cylinder((0, -0.012, -0.075), (0, -0.012, 0.075), 0.018, n=6, role="leather")
for zz in (-0.085, 0.085):
    P.box((-0.025, BACK - 0.004, zz - 0.02), (0.025, -0.005, zz + 0.02), "leather")
P.anchor("grip", (0, 0, 0))
