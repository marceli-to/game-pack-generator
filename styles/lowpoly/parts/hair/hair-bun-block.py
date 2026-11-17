# Big hair with a top bun (lowpoly chibi), fitted to specs/villager/reference: ONE closed loft (like the rogue's
# hood) from the nape up to the crown, 12 points per ring with the same angles (0 = front, 90 = +X). Round the
# face the opening reaches behind the ears (they show in front of the hair mass, outside the locks) and its front points are pulled
# into the head; above the eyes the rings close into a fringe that dips to a point at the centre. A tapered lock
# hangs in front of each ear, and a faceted ball bun sits on top at the back. v2: the front sits back (overhangs
# the forehead ~4 cm, not 10) and the fringe is a row of flat pointed locks on the forehead.
def ring_pts(z, rx, ry, dy, a0, o, lip=(0.165, 0.05), mid=(-0.02, 0.0)):
    c = Vector((0, dy, z))
    arc = [a0 + (360 - 2 * a0) * k / 8 for k in range(9)]
    at = lambda th: c + Vector((rx * math.sin(math.radians(th)), -ry * math.cos(math.radians(th)), 0))
    lip_r, lip_l = Vector((lip[0], lip[1], z)), Vector((-lip[0], lip[1], z))
    mid_o = Vector((0, mid[0], z + mid[1]))
    mix = lambda a, b: a.lerp(b, o)
    return [mix(at(a0 / 2), lip_r)] + [at(a) for a in arc] + [mix(at(360 - a0 / 2), lip_l), mix(at(0), mid_o)]
rows = [  # (z, rx, ry, y offset, a0, opening)
    (0.86, 0.15, 0.12, 0.03, 30, 0.0), (0.875, 0.25, 0.23, 0.03, 105, 1.0), (0.96, 0.3, 0.27, 0.02, 100, 1.0),
    (1.02, 0.315, 0.28, 0.0, 72, 1.0), (1.065, 0.328, 0.24, 0.0, 40, 0.0), (1.13, 0.335, 0.27, 0.01, 30, 0.0),
    (1.22, 0.297, 0.27, 0.0, 30, 0.0), (1.29, 0.23, 0.215, 0.0, 30, 0.0), (1.34, 0.14, 0.13, 0.0, 30, 0.0)]
rings = []
for z, rx, ry, dy, a0, o in rows:
    # the fringe ring dips at the centre (a point over the forehead)
    rings.append(ring_pts(z, rx, ry, dy, a0, o, mid=(-0.02, -0.035 if 0 < o < 1 else 0.0)))
rings.append([Vector((0, 0, 1.36))])
P.loft(rings, "hair", cap_roles=("hair", None))
# locks beside the cheeks (the ears show outside them): tapered, flattened, ending above the jaw line
lock = P.loft([P.rrect((0.168, -0.09, z), sx, sy, 0.014, seg=1) for z, sx, sy in
               ((0.83, 0.018, 0.025), (0.93, 0.03, 0.04), (1.05, 0.036, 0.05))] + [[Vector((0.168, -0.09, 1.1))]], "hair")
P.mirror_x(lock)
# fringe (v2 detail pass): a row of seven flat pointed locks across the forehead, from under the hair's front edge
# down to just above the eyes (eye tops at z 1.0), swept to the wearer's left; they hide the edge's straight line
yf = lambda u: -0.198 + 0.5 * u * u / 0.19
for x, zt in ((-0.162, 1.045), (-0.108, 1.02), (-0.054, 1.032), (0.0, 1.012), (0.054, 1.028), (0.108, 1.016),
              (0.162, 1.042)):
    tip = Vector((x + 0.02, yf(x + 0.02) - 0.008, zt))
    P.loft([P.rrect((x, yf(x) - 0.018, 1.1), 0.036, 0.016, 0.009, seg=1),
            P.rrect((x + 0.008, yf(x + 0.008) - 0.01, 1.062), 0.032, 0.013, 0.008, seg=1), [tip]], "hair")
c, r = Vector((0, 0.17, 1.4)), 0.125
lat = [math.radians(a) for a in (-60, -30, 0, 30, 60)]
P.loft([[c + Vector((0, 0, -r))]] + [P.ring(c + Vector((0, 0, r * math.sin(b))), r * math.cos(b), n=10) for b in lat]
       + [[c + Vector((0, 0, r))]], "hair")
