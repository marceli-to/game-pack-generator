# Tall riding boots (tinfox, hero-m), for the officer (specs/officer/reference): the guard's chunky foot and sole
# under a straight shaft up to just below the knee (0.39 m) with a thicker rim at the top, open into the trouser leg.
a, t = lm["ankle.l"], lm["toes.l"]
x = a.x + 0.018
cy = a.y - 0.005
shaft = P.loft([P.rrect((x, cy, z), sx, sy, r, seg=2) for z, sx, sy, r in
                ((0.07, 0.096, 0.09, 0.035), (0.2, 0.09, 0.086, 0.035), (0.33, 0.096, 0.094, 0.038),
                 (0.37, 0.1, 0.098, 0.04), (0.375, 0.106, 0.104, 0.042), (0.395, 0.106, 0.104, 0.042),
                 (0.398, 0.09, 0.088, 0.035))], "leather")
heel, toe = a.y + 0.145, t.y + 0.01
foot = P.loft([P.rrect((x, heel, 0.1), 0.104, 0.06, 0.035, seg=2, axis="y"),
               P.rrect((x, heel - 0.025, 0.104), 0.112, 0.064, 0.038, seg=2, axis="y"),
               P.rrect((x, a.y - 0.065, 0.104), 0.116, 0.064, 0.038, seg=2, axis="y"),
               P.rrect((x, toe + 0.06, 0.095), 0.114, 0.056, 0.038, seg=2, axis="y"),
               P.rrect((x, toe + 0.018, 0.082), 0.098, 0.044, 0.03, seg=2, axis="y")], "leather")
secs = [(heel + 0.005, 0.104), (heel - 0.025, 0.112), (a.y - 0.065, 0.116), (toe + 0.06, 0.114), (toe + 0.018, 0.098),
        (toe - 0.004, 0.08)]
def width(y):
    for (y0, w0), (y1, w1) in zip(secs, secs[1:]):
        if y1 <= y <= y0:
            return w0 + (w1 - w0) * (y0 - y) / (y0 - y1)
    return secs[-1][1]
prof = [(heel + 0.005, 0.0), (heel - 0.07, 0.0), (heel - 0.085, 0.02), (a.y - 0.02, 0.02), (a.y - 0.035, 0.0),
        (toe + 0.06, 0.0), (toe + 0.018, 0.0), (toe - 0.004, 0.006)]
top = 0.06
soles = P.loft([P.rrect((x, y, (zb + top) / 2), width(y) + 0.005, (top - zb) / 2, 0.01, seg=2, axis="y")
                for y, zb in prof], "dark")
P.mirror_x(shaft + foot + soles)
