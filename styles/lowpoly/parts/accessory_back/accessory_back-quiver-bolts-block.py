# Quiver of crossbow bolts (lowpoly chibi), fitted to specs/archer/reference: an 8-sided leather tube slung across
# the back over the cape, top over the wearer's left shoulder (+X), bottom at the right hip; two lighter leather
# bands; three bolts standing out of the open top with cream fletching (two crossed fins each).
top, bot = Vector((0.13, 0.275, 0.76)), Vector((-0.085, 0.215, 0.42))
d = (top - bot).normalized()
u = Vector((0, 1, 0))
u = (u - d * u.dot(d)).normalized()
w = d.cross(u)
def ring(t, r, n=8):
    c = bot.lerp(top, t)
    return [c + u * (r * math.cos(2 * math.pi * (k + 0.5) / n)) + w * (r * math.sin(2 * math.pi * (k + 0.5) / n))
            for k in range(n)]
P.loft([ring(0.0, 0.048), ring(0.04, 0.056), ring(0.96, 0.056), ring(1.0, 0.05)], "dark")
for t0, t1 in ((0.16, 0.24), (0.78, 0.86)):
    P.loft([ring(t0, 0.062), ring(t1, 0.062)], "leather")
# bolts: shafts out of the top, fanned a little, fletching as two crossed thin fins
for du, dw, ln in ((-0.022, -0.018, 0.11), (0.024, -0.012, 0.12), (0.0, 0.024, 0.1)):
    base = top - d * 0.06 + u * du + w * dw
    tip = base + (d * 1.0 + u * du * 2 + w * dw * 2).normalized() * (ln + 0.06)
    P.cylinder(base, tip, 0.008, n=4, role="leather")
    ax = (tip - base).normalized()
    side = ax.cross(u).normalized()
    up = ax.cross(side).normalized()
    a, b = tip - ax * 0.07, tip - ax * 0.005
    # fletching: two crossed thin plates through the shaft, each a closed box
    for v in (side, up):
        nrm = ax.cross(v).normalized() * 0.003
        q = [a + v * 0.03 + ax * 0.012, b + v * 0.024, b - v * 0.024, a - v * 0.03 + ax * 0.012]
        P.loft([[p - nrm for p in q], [p + nrm for p in q]], "special")
