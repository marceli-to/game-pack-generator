# Uniform jacket (tinfox, hero-m), v2 fitted to specs/guard/reference: a jumpsuit top from a tall stand-up collar
# over high square shoulders and a broad chest (a crease under the chest), a narrower waist under the belt, wide
# hips and an upside-down V at the crotch (the trousers are a separate part); a raised placket down the front, an
# orange name patch on the wearer's left chest.
# Shoulder pads: big rounded caps over the shoulder joints, on the torso (rigid on the chest: the rig has no
# clavicle), so the arm hangs under them as on the sheet; an orange stripe across each pad from the collar out.
def ring(z, sx, f, b, r):
    return P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=3)   # v4: 16 sides
# v3 (Marcel: more V-shaped, bulky): broad deep chest and shoulders tapering to a narrow waist under the belt;
# the chest's front-outer corners well rounded, so arms aiming forward pass in front of them, not through
body = [(1.51, 0.095, -0.1, 0.09, 0.05), (1.44, 0.105, -0.115, 0.1, 0.05), (1.43, 0.2, -0.16, 0.14, 0.07),
        (1.38, 0.272, -0.2, 0.17, 0.15), (1.3, 0.28, -0.22, 0.178, 0.16), (1.22, 0.258, -0.21, 0.168, 0.13),
        (1.19, 0.226, -0.18, 0.158, 0.085), (1.1, 0.2, -0.155, 0.145, 0.075), (1.0, 0.18, -0.138, 0.136, 0.068),
        (0.9, 0.228, -0.152, 0.152, 0.075), (0.8, 0.238, -0.148, 0.152, 0.075), (0.75, 0.2, -0.13, 0.135, 0.065)]
rings = [ring(*b) for b in body]
# crotch: the last rings close to a V (the centre front and back points drop lowest)
for z, sx in ((0.72, 0.13), (0.7, 0.05)):
    pts = ring(z, sx, -0.115, 0.12, 0.05)
    rings.append([Vector((p.x, p.y, z - 0.03 * max(0.0, 1 - abs(p.x) / sx))) for p in pts])
P.loft(rings, "primary", cap_roles=("dark", "primary"))
# collar band (a step out at the top of the collar)
P.loft([ring(1.44, 0.112, -0.122, 0.106, 0.05), ring(1.5, 0.108, -0.115, 0.1, 0.05)], "primary")
# placket down the front
P.loft([P.rect((0, -0.17, 1.425), 0.014, 0.008), P.rect((0, -0.208, 1.36), 0.014, 0.008),
        P.rect((0, -0.224, 1.28), 0.014, 0.008), P.rect((0, -0.214, 1.21), 0.014, 0.008),
        P.rect((0, -0.188, 1.17), 0.014, 0.008), P.rect((0, -0.146, 1.0), 0.014, 0.008)], "primary")
# name patch on the wearer's left chest
P.rbox((0.06, -0.228, 1.27), (0.16, -0.21, 1.31), "accent", r=0.004, bevel=0, seg=1, axis="y")
# shoulder pads: rings round an axis that leans out and down from the collar over the shoulder joint
sh = lm["shoulder.l"]
def pad_frame(t):
    a0, a1 = Vector((0.17, 0.0, 1.35)), Vector((sh.x + 0.16, 0.0, sh.z - 0.08))
    c = a0.lerp(a1, t)
    d = (a1 - a0).normalized()
    u = Vector((0, 1, 0))
    w = d.cross(u)            # outward-up normal of the pad
    return c, u, w
def pad_ring(t, ry, rw, n=16):
    c, u, w = pad_frame(t)
    return [c + u * (ry * math.cos(2 * math.pi * k / n)) + w * (rw * math.sin(2 * math.pi * k / n))
            for k in range(n)]
pad = [(0.0, 0.13, 0.08), (0.12, 0.168, 0.12), (0.55, 0.18, 0.135), (0.9, 0.164, 0.12), (1.05, 0.115, 0.08)]
pad_faces = P.loft([pad_ring(t, ry, rw) for t, ry, rw in pad], "primary")
faces = list(pad_faces)
# stripe: across the pad from front to back, near the collar end
t, ry, rw = 0.3, 0.175, 0.131
c, u, w = pad_frame(t)
angs = [math.radians(a) for a in range(-80, 261, 20)]
path = [c + u * ((ry + 0.003) * math.cos(a)) + w * ((rw + 0.003) * math.sin(a)) for a in angs]
nrm = [(u * (math.cos(a) / ry) + w * (math.sin(a) / rw)).normalized() for a in angs]
keep = [k for k, a in enumerate(angs) if rw * math.sin(a) > -0.03]
faces += P.sweep([path[k] for k in keep], P.strap_profile(0.075, 0.004, 0.0015), "accent", [nrm[k] for k in keep])
# weights (v4, Marcel: the shoulders should move): the pad turns partway with the arm, like a shoulder. Each vertex
# shares chest and upper arm by its position along the pad, from all chest at the collar end to `follow` at the
# outer end (no clavicle bone in the rig)
follow = 0.6
a0, a1 = pad_frame(0.0)[0], pad_frame(1.0)[0]
axis = a1 - a0
verts = {v for f in faces for v in f.verts}
# the arms hang ~72 deg below the T-pose in every clip, and a vertex with arm share w turns about w x 72 deg with
# them: so in the rest (T) pose each pad vertex is tilted up by that much about the shoulder joint, and with the
# arms down the pads land on top of the shoulders as modelled
joint = Vector((sh.x, 0.0, sh.z))
for v in verts:
    t = max(0.0, min(1.0, (v.co - a0).dot(axis) / axis.length_squared))
    f_arm = follow * (3 * t * t - 2 * t * t * t)
    P.set_weights([v], {"chest": 1.0 - f_arm, "upperarm.l": f_arm})
    v.co = joint + Matrix.Rotation(math.radians(-72.0 * f_arm), 3, "Y") @ (v.co - joint)
P.mirror_x(faces)
