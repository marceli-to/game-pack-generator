# Big round hood (lowpoly chibi), fitted to specs/archer/reference: ONE closed loft like headwear-hood-block (12 points
# per ring, angle 0 = front, 90 = +X), but a roomy rounded dome instead of a pointed cone: widest (+-0.35) at the
# cheeks, the back bulging 13 cm behind the head, the crown peaking a little forward above the face. Round the face
# the opening's front points are pulled back into the head (a lip at the edge, a recess at y -0.06 hidden in the
# head), so the strip between face and rim reads as the hood's inside; closed under the chin, where it sits on the
# cape; at ear height the edge comes in over the outer half of the ears. All in team red (`secondary`), inside included, so the team-colour swap covers the whole hood.
def ring_pts(c, rx, ry, a0, o, rec=-0.06, lip=None):
    arc = [a0 + (360 - 2 * a0) * k / 8 for k in range(9)]
    at = lambda th: c + Vector((rx * math.sin(math.radians(th)), -ry * math.cos(math.radians(th)), 0))
    pts = [at(a) for a in arc]
    f = 0.87 if a0 < 70 else 0.76
    lip_r = c + Vector((rx * math.sin(math.radians(a0)), -ry * math.cos(math.radians(a0)), 0)) * f
    if lip is not None:   # ear rows: the edge pulled in over the ear
        lip_r = Vector((lip[0], lip[1], c.z))
    lip_l = Vector((-lip_r.x + 2 * c.x, lip_r.y, lip_r.z))
    mid_o = Vector((c.x, rec, c.z))
    mix = lambda a, b: a.lerp(b, o)
    return [mix(at(a0 / 2), lip_r)] + pts + [mix(at(360 - a0 / 2), lip_l), mix(at(0), mid_o)]
# (z, rx, ry, y offset, a0, opening 0..1)
rows = [(0.745, 0.2, 0.17, 0.06, 30, 0.0), (0.78, 0.29, 0.24, 0.055, 40, 0.0), (0.84, 0.335, 0.265, 0.05, 72, 1.0),
        (0.92, 0.35, 0.28, 0.04, 80, 1.0), (1.0, 0.345, 0.3, 0.035, 74, 1.0), (1.07, 0.33, 0.325, 0.03, 62, 1.0),
        (1.14, 0.305, 0.33, 0.015, 48, 1.0), (1.2, 0.27, 0.31, 0.0, 36, 0.6), (1.26, 0.22, 0.27, 0.01, 30, 0.0),
        (1.31, 0.16, 0.205, 0.02, 30, 0.0), (1.345, 0.09, 0.115, 0.03, 30, 0.0)]
# ear rows (head-chibi-small-ears: ear from the head side at x 0.19 out to 0.232, front edge y -0.03): the opening's
# edge comes in to x 0.248 (v1: 0.262, full ears; 0.232 hid them), so the hood's rim hides its outer half (Marcel: ears stood out
# too much, show about half)
EAR_LIP = {0.92: (0.248, -0.012), 1.0: (0.25, -0.012)}
rings = [ring_pts(Vector((0, dy, z)), rx, ry, a0, o, lip=EAR_LIP.get(z)) for z, rx, ry, dy, a0, o in rows]
rings.append([Vector((0, 0.035, 1.365))])
P.loft(rings, "secondary")
