# Fur-trimmed boots (lowpoly chibi), from specs/berserker/reference: the low boots' chunky leather foot and a short
# shaft, under a thick cream fur cuff (`accent`, 12 sides) from z 0.09 to 0.19 with a jagged lower edge; the
# trousers end inside the cuff.
a, t = lm["ankle.l"], lm["toes.l"]
x = a.x + 0.01
cy = a.y + 0.012
shaft = P.loft([P.rrect((x, cy, z), sx, sy, r, seg=1) for z, sx, sy, r in
                ((0.06, 0.09, 0.105, 0.04), (0.11, 0.088, 0.102, 0.04))], "leather")
foot = P.loft([P.rrect((x, a.y + 0.142, 0.05), 0.094, 0.05, 0.03, seg=1, axis="y"),
               P.rrect((x, a.y + 0.13, 0.055), 0.098, 0.055, 0.035, seg=1, axis="y"),
               P.rrect((x, a.y - 0.07, 0.055), 0.098, 0.055, 0.035, seg=1, axis="y"),
               P.rrect((x, t.y + 0.05, 0.05), 0.095, 0.05, 0.035, seg=1, axis="y"),
               P.rrect((x, t.y + 0.025, 0.04), 0.08, 0.04, 0.03, seg=1, axis="y")], "leather")
def cring(z, rx, ry, jag=0.0, tw=0.0):
    pts = []
    for k in range(12):
        th = math.radians(360 * k / 12 + tw)
        pts.append(Vector((x + rx * math.sin(th), cy - ry * math.cos(th), z + (jag if k % 2 else 0.0))))
    return pts
cuff = P.loft([cring(0.086, 0.112, 0.124, 0.024), cring(0.135, 0.126, 0.139, 0.0, 15),
               cring(0.182, 0.098, 0.11)], "accent")
P.mirror_x(shaft + foot + cuff)
