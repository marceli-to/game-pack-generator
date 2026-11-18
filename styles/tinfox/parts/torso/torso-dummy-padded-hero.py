# Practice dummy torso (tinfox, hero-m), for specs/practice-dummy/reference: the guard's jacket body in padded canvas
# (role armor) with a high padded roll collar, the guard's shoulder pads (same chest / upper-arm blend and pre-tilt),
# a quilted pad on the chest and on the back, each carrying a big round target (red outer ring, cream ring, red
# bullseye, 16-sided discs stepped 5 mm apart so they never z-fight), and a cushion over the belt buckle.
# Pads and targets are rigid on the chest bone, so they stay flat on the chest whatever the arms do.
def ring(z, sx, f, b, r):
    return P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=3)
body = [(1.47, 0.09, -0.095, 0.085, 0.045), (1.44, 0.105, -0.115, 0.1, 0.05), (1.43, 0.2, -0.16, 0.14, 0.07),
        (1.38, 0.272, -0.2, 0.17, 0.15), (1.3, 0.28, -0.22, 0.178, 0.16), (1.22, 0.258, -0.21, 0.168, 0.13),
        (1.19, 0.226, -0.18, 0.158, 0.085), (1.1, 0.2, -0.155, 0.145, 0.075), (1.0, 0.18, -0.138, 0.136, 0.068),
        (0.9, 0.228, -0.152, 0.152, 0.075), (0.8, 0.238, -0.148, 0.152, 0.075), (0.75, 0.2, -0.13, 0.135, 0.065)]
rings = [ring(*b) for b in body]
for z, sx in ((0.72, 0.13), (0.7, 0.05)):
    pts = ring(z, sx, -0.115, 0.12, 0.05)
    rings.append([Vector((p.x, p.y, z - 0.03 * max(0.0, 1 - abs(p.x) / sx))) for p in pts])
P.loft(rings, "armor", cap_roles=("dark", "armor"))
# high padded roll collar: a thick tube round the neck, its rim rolled over and back down inside
coll = [(1.4, 0.142, -0.15, 0.128, 0.068), (1.43, 0.144, -0.152, 0.13, 0.07), (1.472, 0.134, -0.142, 0.12, 0.065),
        (1.495, 0.118, -0.125, 0.104, 0.056), (1.488, 0.1, -0.106, 0.088, 0.047), (1.45, 0.094, -0.1, 0.084, 0.045)]
P.loft([ring(*c) for c in coll], ["armor"] * 4 + ["dark"], cap_roles=("armor", "dark"))   # dark inside: the head reads apart
# chest and back pads: rounded slabs from inside the body out to a flat face, with a bevelled edge
def slab(y_in, y_out, zc, hx, hz, r, bev=0.012):
    s = 1 if y_out > y_in else -1
    return P.loft([P.rrect((0, y_in, zc), hx, hz, r, seg=2, axis="y"),
                   P.rrect((0, y_out - s * bev, zc), hx, hz, r, seg=2, axis="y"),
                   P.rrect((0, y_out, zc), hx - bev, hz - bev, r - bev * 0.6, seg=2, axis="y")], "armor")
ZT = 1.25                                # target centre
chest = slab(-0.13, -0.238, ZT, 0.215, 0.155, 0.075)
back = slab(0.1, 0.2, ZT - 0.02, 0.21, 0.15, 0.075)
def target(y, s, zc):
    out = []
    for r, role, d in ((0.15, "accent", 0.006), (0.104, "special", 0.011), (0.05, "accent", 0.016)):
        out += P.cylinder(Vector((0, y - s * 0.004, zc)), Vector((0, y + s * d, zc)), r, n=16, role=role)
    return out
tf = target(-0.238, -1, ZT) + target(0.2, 1, ZT - 0.02)
P.set_weights(chest + back + tf, {"chest": 1.0})
# belly cushion over the belt buckle
P.loft([P.rrect((0, -0.13, 0.965), 0.11, 0.065, 0.035, seg=2, axis="y"),
        P.rrect((0, -0.192, 0.965), 0.115, 0.07, 0.038, seg=2, axis="y"),
        P.rrect((0, -0.204, 0.965), 0.103, 0.058, 0.03, seg=2, axis="y")], "armor")
# shoulder pads (the guard's): rings round an axis leaning out and down from the collar over the shoulder joint
sh = lm["shoulder.l"]
def pad_frame(t):
    a0, a1 = Vector((0.17, 0.0, 1.35)), Vector((sh.x + 0.16, 0.0, sh.z - 0.08))
    c = a0.lerp(a1, t)
    d = (a1 - a0).normalized()
    u = Vector((0, 1, 0))
    return c, u, d.cross(u)
def pad_ring(t, ry, rw, n=16):
    c, u, w = pad_frame(t)
    return [c + u * (ry * math.cos(2 * math.pi * k / n)) + w * (rw * math.sin(2 * math.pi * k / n)) for k in range(n)]
pad = [(0.0, 0.13, 0.08), (0.12, 0.172, 0.124), (0.55, 0.186, 0.142), (0.9, 0.17, 0.126), (1.05, 0.12, 0.084)]
faces = list(P.loft([pad_ring(t, ry, rw) for t, ry, rw in pad], "armor"))
follow = 0.6
a0, a1 = pad_frame(0.0)[0], pad_frame(1.0)[0]
axis = a1 - a0
joint = Vector((sh.x, 0.0, sh.z))
for v in {v for f in faces for v in f.verts}:
    t = max(0.0, min(1.0, (v.co - a0).dot(axis) / axis.length_squared))
    f_arm = follow * (3 * t * t - 2 * t * t * t)
    P.set_weights([v], {"chest": 1.0 - f_arm, "upperarm.l": f_arm})
    v.co = joint + Matrix.Rotation(math.radians(-72.0 * f_arm), 3, "Y") @ (v.co - joint)
P.mirror_x(faces)
