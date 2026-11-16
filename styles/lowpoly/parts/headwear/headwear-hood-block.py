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
# snug: 2.5-3 cm outside the head and ears (head +-0.19, ears to +-0.235)
rows = [(0.745, 0.22, 0.185, 0.0, 30, 0.0), (0.77, 0.27, 0.215, 0.0, 62, 1.0), (0.85, 0.268, 0.226, 0.0, 56, 1.0),
        (0.95, 0.265, 0.232, 0.0, 50, 1.0), (1.05, 0.268, 0.236, -0.005, 46, 1.0), (1.13, 0.258, 0.232, -0.008, 40, 1.0),
        (1.19, 0.235, 0.22, -0.008, 34, 0.6), (1.235, 0.195, 0.188, -0.008, 30, 0.0)]
rings = [ring_pts(Vector((0, dy, z)), rx, ry, a0, o) for z, rx, ry, dy, a0, o in rows]
opens = [o for *_, o in rows]
# cone above the crown: rings with the same angles, oriented along the bisector of the spine segments
spine = [(Vector((0, -0.008, 1.235)), None), (Vector((0.01, 0.0, 1.29)), 0.15), (Vector((0.035, 0.04, 1.345)), 0.088),
         (Vector((0.095, 0.1, 1.38)), 0.052), (Vector((0.175, 0.17, 1.37)), 0.032), (Vector((0.24, 0.225, 1.31)), 0.019)]
for k in range(1, len(spine)):
    c, r = spine[k]
    prv = spine[k - 1][0]
    nxt = spine[k + 1][0] if k + 1 < len(spine) else c + (c - prv)
    t = ((c - prv).normalized() + (nxt - c).normalized()).normalized()
    u = (Vector((0, -1, 0)) - t * Vector((0, -1, 0)).dot(t)).normalized()
    rings.append(ring_pts(c, r, r, 30, 0.0, frame=(u, t.cross(u))))
    opens.append(0.0)
rings.append([Vector((0.265, 0.248, 1.245))])
opens.append(0.0)
def role(b, i):
    if i >= 10 and (opens[b] > 0 or opens[b + 1] > 0):
        return "dark"
    return "secondary"
P.loft(rings, role, cap_roles=("dark", None))
