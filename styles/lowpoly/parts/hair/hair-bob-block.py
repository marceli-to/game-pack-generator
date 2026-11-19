# Short bob (lowpoly chibi), fitted to specs/healer/reference: ONE closed loft like hair-bun-block (12 points per
# ring, th 0 = front, 90 = +X). A rounded ball ~9 cm outside the head, widest at the cheeks, tucked under at the
# bottom. Round the face the opening reaches just behind the ears (head-chibi-small-ears), its front points pulled
# into the head; the back points keep fixed angles on every ring so the back reads as even facets.
# The hairline sits high (1.06) and is hidden by a fringe of five big overlapping flat locks (a part on the
# wearer's right, the big lock sweeping to the left brow); sideburn plates lie on the head's front corners from the
# hairline down to the jaw, in front of the ears.
BACK = [130, 155, 180, 205, 230]
def ring_pts(z, rx, ry, dy, a0, o, lip, mid=-0.02, back=None, near=1.0, a1=None):
    c = Vector((0, dy, z))
    arc = [a0, (a0 + BACK[0]) / 2] + BACK + [360 - (a0 + BACK[0]) / 2, 360 - a0]
    at = lambda th: c + Vector((rx * math.sin(math.radians(th)), -ry * math.cos(math.radians(th)), 0))
    def at_back(th):
        if back is None:
            return at(th)
        bx, by, bd = back
        return Vector((bx * math.sin(math.radians(th)), -by * math.cos(math.radians(th)) + bd, z))
    side = lambda th, s: c + Vector((rx * s * math.sin(math.radians(th)), -ry * math.cos(math.radians(th)), 0))
    a1 = (a0 + BACK[0]) / 2 if a1 is None else a1
    pts = [side(a0, near), side(a1, 1.0)] + [at_back(a) for a in BACK] \
        + [side(360 - a1, 1.0), side(360 - a0, near)]
    lip_r, lip_l = Vector((lip[0], lip[1], z)), Vector((-lip[0], lip[1], z))
    mid_o = Vector((0, mid, z))
    mix = lambda a, b: a.lerp(b, o)
    return [mix(at(a0 / 2), lip_r)] + pts + [mix(at(360 - a0 / 2), lip_l), mix(at(0), mid_o)]
rows = [  # (z, rx, ry, y offset, a0, opening, lip)
    (0.793, 0.16, 0.155, 0.045, 56, 1.0, (0.08, -0.01)),
    (0.806, 0.212, 0.2, 0.04, 56, 1.0, (0.10, -0.02)),
    (0.824, 0.246, 0.232, 0.036, 56, 1.0, (0.12, -0.03)),
    (0.846, 0.268, 0.25, 0.032, 58, 1.0, (0.13, -0.03)),
    (0.872, 0.282, 0.26, 0.03, 64, 1.0, (0.145, -0.02)),
    (0.905, 0.284, 0.263, 0.028, 78, 1.0, (0.17, -0.02)),
    (0.94, 0.276, 0.264, 0.025, 90, 1.0, (0.18, 0.02)),
    (0.985, 0.27, 0.264, 0.02, 72, 1.0, (0.175, -0.05)),
    (1.025, 0.27, 0.262, 0.02, 50, 1.0, (0.14, -0.11)),
    (1.065, 0.268, 0.25, 0.025, 36, 1.0, (0.12, -0.13)),
    (1.10, 0.262, 0.238, 0.022, 30, 0.0, (0.16, 0.0)),
    (1.15, 0.236, 0.228, 0.02, 30, 0.0, (0.16, 0.0)),
    (1.2, 0.196, 0.198, 0.015, 30, 0.0, (0.16, 0.0)),
    (1.243, 0.138, 0.142, 0.01, 30, 0.0, (0.16, 0.0)),
    (1.27, 0.074, 0.08, 0.01, 30, 0.0, (0.16, 0.0)),
]
# the middle rows share their back points (one vertical band of big flat facets, as on the sheet); round the
# ears the hair's front-most side point hugs closer, so the ears stand proud of it from the side
MID = (0.278, 0.264, 0.025)
rings = []
for z, rx, ry, dy, a0, o, lip in rows:
    back = MID if 0.9 < z < 1.07 else None
    # ear rows: the opening reaches just behind the ear; there the hair's edge hugs the head a little, so the
    # ear sits in front of the hair that wraps round behind it
    # thin at the edge: the front-most hair point of these rows sits ~1.5-2 cm off the head (the bob bulges only
    # further back), so the opening round the ear shows no deep wall
    near, a1 = {0.872: (0.86, None), 0.905: (0.73, 114), 0.94: (0.75, 114), 0.985: (0.8, 112),
                1.025: (0.85, None), 1.065: (0.9, None)}.get(z, (1.0, None))
    rings.append(ring_pts(z, rx, ry, dy, a0, o, lip, back=back, near=near, a1=a1))
rings.append([Vector((0, 0.01, 1.283))])
P.loft(rings, "hair", cap_roles=("hair", None))

# fringe: one thick sheet coming out of the front of the mass (top rows inside it), lying ~2.5 cm in front of
# the forehead, its lower edge a zigzag of pointed locks slanting towards the wearer's left; plus the big lock
# sweeping from the part over to the left brow
def fpt(th, z, rx, ry, dy=-0.005):
    t_ = math.radians(th)
    return Vector((rx * math.sin(t_), -ry * math.cos(t_) + dy, z))
cols = [-78 + 13 * k for k in range(13)]
tips = [1.06, 1.1, 1.035, 1.09, 1.03, 1.085, 1.025, 1.08, 1.03, 1.09, 1.035, 1.095, 1.05]
grid = [[fpt(th, 1.145, 0.205, 0.198) for th in cols], [fpt(th, 1.105, 0.214, 0.206) for th in cols],
        [fpt(th + 3, (1.105 + tz) / 2 + 0.01, 0.216, 0.205) for th, tz in zip(cols, tips)],
        [fpt(th + 6, tz, 0.214, 0.2) for th, tz in zip(cols, tips)]]
P.shell(grid, 0.02, "hair")
def lock(root, tip, w, t=0.022, bend=0.014):
    root, tip = Vector(root), Vector(tip)
    mid = root.lerp(tip, 0.5) + Vector((0, -bend, 0))
    P.loft([P.rrect(root, w, t, t * 0.6, seg=1, axis="z"), P.rrect(mid, w * 0.85, t * 0.85, t * 0.5, seg=1, axis="z"),
            [tip]], "hair")
lock((-0.04, -0.196, 1.185), (0.06, -0.214, 1.045), 0.07, bend=0.016)
# sideburns: narrow plates on the outer half of the head's front corner chamfer, hairline down to the jaw, in
# front of the ears (which stand out past them)
n = Vector((1, -1, 0)).normalized()
u = Vector((1, 1, 0)).normalized()  # along the chamfer, towards the back
def sb(z, c, half):
    p = Vector((c[0], c[1], z)) + n * 0.01
    return [p + u * half + n * 0.01, p + u * half - n * 0.004, p - u * half - n * 0.004, p - u * half + n * 0.01]
side = P.loft([sb(1.08, (0.172, -0.112), 0.04), sb(0.985, (0.17, -0.12), 0.03), sb(0.89, (0.158, -0.122), 0.02),
               [Vector((0.15, -0.122, 0.85)) + n * 0.012]], "hair")
P.mirror_x(side)
