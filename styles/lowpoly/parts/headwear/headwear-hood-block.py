# Big pointed hood (lowpoly chibi), fitted to specs/rogue/reference: ONE closed loft from the cowl at the neck up to
# a tip that bends back and to the wearer's left. Every ring has the same 12 points (angle 0 = front, 90 = +X):
# an arc round the sides and back, and three front points. On the rings around the face the front points are
# pulled back into the head (a lip at the opening edge, a recess at y -0.06 hidden inside the head), so the face
# shows framed by the hood and the strip between face and rim reads as the dark hood interior. Above the face the
# front points sit on the arc again (a closed crown), and the cone rings continue with the same angles.
def ring_pts(c, rx, ry, a0, o, rec=-0.06, frame=None):
    arc = [a0 + (360 - 2 * a0) * k / 8 for k in range(9)]
    def at(th, r1=rx, r2=ry):
        t = math.radians(th)
        if frame:
            u, w = frame
            return c + r1 * math.cos(t) * u + r1 * math.sin(t) * w
        return c + Vector((r1 * math.sin(t), -r2 * math.cos(t), 0))
    pts = [at(a) for a in arc]
    lip_r = c + Vector((rx * math.sin(math.radians(a0)) - 0.035, -ry * math.cos(math.radians(a0)) + 0.04, 0))
    lip_l = Vector((-lip_r.x + 2 * c.x, lip_r.y, lip_r.z))
    mid_o = Vector((c.x, rec, c.z))
    full_r, full_l, full_m = at(a0 / 2), at(360 - a0 / 2), at(0)
    mix = lambda a, b: a.lerp(b, o)
    return [mix(full_r, lip_r)] + pts + [mix(full_l, lip_l), mix(full_m, mid_o)]
# (z, rx, ry, y offset, a0, opening 0..1)
rows = [(0.745, 0.23, 0.2, 0.0, 30, 0.0), (0.77, 0.29, 0.25, 0.0, 62, 1.0), (0.85, 0.335, 0.27, 0.0, 58, 1.0),
        (0.95, 0.35, 0.28, 0.0, 52, 1.0), (1.05, 0.335, 0.29, -0.01, 46, 1.0), (1.13, 0.31, 0.29, -0.02, 40, 1.0),
        (1.19, 0.29, 0.285, -0.02, 34, 0.6), (1.235, 0.255, 0.255, -0.015, 30, 0.0)]
rings = [ring_pts(Vector((0, dy, z)), rx, ry, a0, o) for z, rx, ry, dy, a0, o in rows]
opens = [o for *_, o in rows]
# cone above the crown: rings with the same angles, oriented along the bisector of the spine segments
spine = [(Vector((0, -0.015, 1.235)), None), (Vector((0.012, 0.0, 1.3)), 0.175), (Vector((0.04, 0.05, 1.365)), 0.105),
         (Vector((0.11, 0.115, 1.405)), 0.06), (Vector((0.2, 0.195, 1.39)), 0.036), (Vector((0.275, 0.255, 1.32)), 0.021)]
for k in range(1, len(spine)):
    c, r = spine[k]
    prv = spine[k - 1][0]
    nxt = spine[k + 1][0] if k + 1 < len(spine) else c + (c - prv)
    t = ((c - prv).normalized() + (nxt - c).normalized()).normalized()
    u = (Vector((0, -1, 0)) - t * Vector((0, -1, 0)).dot(t)).normalized()
    rings.append(ring_pts(c, r, r, 30, 0.0, frame=(u, t.cross(u))))
    opens.append(0.0)
rings.append([Vector((0.305, 0.28, 1.25))])
opens.append(0.0)
def role(b, i):
    if i >= 10 and (opens[b] > 0 or opens[b + 1] > 0):
        return "dark"
    return "secondary"
P.loft(rings, role, cap_roles=("dark", None))
