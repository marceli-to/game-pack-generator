# Short hair under a hood (lowpoly chibi), fitted to specs/archer/reference: hair-short-chibi's cap over the crown
# (1.8 cm out, tucked into the head; the hood hides most of it) with a big fringe in front: one thick sheet of
# pointed locks swept forward over the brow (ending above the eyes), plus long side locks on the head's front
# corners down to the cheeks, in front of the ears.
prof = [(lm["head_base"].z, 0.11, -0.12, 0.08, 0.05), (0.85, 0.17, -0.17, 0.14, 0.07), (0.97, 0.19, -0.18, 0.165, 0.08),
        (1.08, 0.18, -0.172, 0.16, 0.08), (lm["head_top"].z, 0.12, -0.11, 0.11, 0.05)]
N = 12
def dims(z):
    z = max(prof[0][0], min(prof[-1][0], z))
    for a, b in zip(prof, prof[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return [u + (v - u) * t for u, v in zip(a[1:], b[1:])]
def pt(j, z, o):
    sx, f, b, r = dims(z)
    p = P.rrect((0, (f + b) / 2, z), sx + o, (b - f) / 2 + o, r + 0.4 * o, seg=2)[j]
    return Vector((p.x, p.y, z))
ref = P.rrect((0, 0, 0), 1, 1, 0.4, seg=2)
def z_bottom(j):
    d = Vector((ref[j].x, ref[j].y, 0)).normalized()
    return 1.03 + 0.06 * max(0.0, -d.y) ** 2 - 0.12 * max(0.0, d.y)
rings = [[pt(j, z, o) for j in range(N)] for z, o in ((1.215, 0.01), (1.165, 0.018), (1.1, 0.02))]
rings.append([pt(j, z_bottom(j), 0.022) for j in range(N)])
rings.append([pt(j, z_bottom(j) + 0.012, -0.015) for j in range(N)])
P.loft([[Vector((0, 0, 1.23))]] + rings, "hair")
# fringe: a thick sheet out of the front of the cap, swept forward, its lower edge a zigzag of pointed locks
def fpt(th, z, rx, ry, dy=0.0):
    t_ = math.radians(th)
    return Vector((rx * math.sin(t_), -ry * math.cos(t_) + dy, z))
cols = [-72 + 18 * k for k in range(9)]
tips = [1.04, 1.085, 1.005, 1.075, 1.0, 1.07, 1.005, 1.08, 1.04]
grid = [[fpt(th, 1.19, 0.17, 0.165) for th in cols], [fpt(th, 1.15, 0.21, 0.215) for th in cols],
        [fpt(th + 4, (1.13 + tz) / 2, 0.218, 0.232) for th, tz in zip(cols, tips)],
        [fpt(th + 9 if tz < 1.05 else th + 4, tz, 0.214, 0.238) for th, tz in zip(cols, tips)]]
P.shell(grid, 0.022, "hair")
# side locks on the front corners of the head, from the fringe down to the cheek
n = Vector((1, -1, 0)).normalized()
u = Vector((1, 1, 0)).normalized()
def sb(z, c, half):
    p = Vector((c[0], c[1], z)) + n * 0.012
    return [p + u * half + n * 0.012, p + u * half - n * 0.004, p - u * half - n * 0.004, p - u * half + n * 0.012]
side = P.loft([sb(1.1, (0.168, -0.11), 0.045), sb(1.0, (0.172, -0.118), 0.035), sb(0.92, (0.165, -0.122), 0.022),
               [Vector((0.158, -0.124, 0.87)) + n * 0.014]], "hair")
P.mirror_x(side)
