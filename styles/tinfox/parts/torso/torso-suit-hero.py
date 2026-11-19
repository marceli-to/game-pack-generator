# Squad suit top (tinfox, hero-m; players 1 and 3), from specs/player-1/reference: the guard jacket's body (tall
# stand-up collar, broad V chest, narrow waist, wide hips, crotch V) with the suit's white accents (role
# `secondary`): a stripe across each shoulder pad, a white line from under each pad down the chest to the belt
# (front and back), a white name patch. Suit colour = `primary` (the player's slot colour).
# Shoulder pads: big rounded caps over the shoulder joints, on the torso (rigid on the chest: the rig has no
# clavicle), so the arm hangs under them as on the sheet; an orange stripe across each pad from the collar out.
def ring(z, sx, f, b, r):
    return P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=1)   # facet pass: 8 sides (v4 had 16)
# v3 (Marcel: more V-shaped, bulky): broad deep chest and shoulders tapering to a narrow waist under the belt;
# the chest's front-outer corners well rounded, so arms aiming forward pass in front of them, not through
body = [(1.455, 0.115, -0.1, 0.11, 0.05), (1.43, 0.2, -0.16, 0.14, 0.07),
        (1.38, 0.272, -0.2, 0.17, 0.15), (1.3, 0.28, -0.22, 0.178, 0.16), (1.22, 0.258, -0.21, 0.168, 0.13),
        (1.19, 0.226, -0.18, 0.158, 0.085), (1.1, 0.2, -0.155, 0.145, 0.075), (1.0, 0.18, -0.138, 0.136, 0.068),
        (0.9, 0.228, -0.152, 0.152, 0.075), (0.8, 0.238, -0.148, 0.152, 0.075), (0.75, 0.2, -0.13, 0.135, 0.065)]
rings = [ring(*b) for b in body]
# player: the body's top round the neck slopes down to the front (1.415) so the chin and the front of the neck show
_ys = [q.y for q in rings[0]]
rings[0] = [Vector((q.x, q.y, 1.415 + 0.04 * ((q.y - min(_ys)) / (max(_ys) - min(_ys))) ** 0.7)) for q in rings[0]]
# crotch: the last rings close to a V (the centre front and back points drop lowest)
for z, sx in ((0.72, 0.13), (0.7, 0.05)):
    pts = ring(z, sx, -0.115, 0.12, 0.05)
    rings.append([Vector((p.x, p.y, z - 0.03 * max(0.0, 1 - abs(p.x) / sx))) for p in pts])
P.loft(rings, "primary", cap_roles=("primary", "primary"))
# collar (player sheet): a wide stand-up funnel round the neck, open at the top (the body's top closes lower,
# round the neck), its rim rolled out a little
# its rim slopes down to the front (sheet side view: back 1.51, front ~1.45) so the chin stays clear of it
def sloped(rg, z_back, z_front):
    ys = [q.y for q in rg]
    y0, y1 = min(ys), max(ys)
    return [Vector((q.x, q.y, z_front + (z_back - z_front) * ((q.y - y0) / (y1 - y0)) ** 0.7)) for q in rg]
# v3 (Marcel: the collar must still show in front): a band all round, its front rim lower (1.465) but above the
# chest's top edge, and set forward (y -0.18) so the chin sits just behind it, as on the sheet
col = [sloped(ring(1.4, 0.15, -0.17, 0.13, 0.08), 1.415, 1.4),
       sloped(ring(1.45, 0.149, -0.176, 0.13, 0.08), 1.47, 1.44),
       sloped(ring(1.48, 0.153, -0.181, 0.134, 0.08), 1.505, 1.465)]
P.shell(col, 0.016, "primary", cyclic=True)
# placket down the front
P.loft([P.rect((0, -0.17, 1.425), 0.014, 0.008), P.rect((0, -0.208, 1.36), 0.014, 0.008),
        P.rect((0, -0.224, 1.28), 0.014, 0.008), P.rect((0, -0.214, 1.21), 0.014, 0.008),
        P.rect((0, -0.188, 1.17), 0.014, 0.008), P.rect((0, -0.146, 1.0), 0.014, 0.008)], "primary")
# name patch on the wearer's left chest
P.rbox((0.06, -0.228, 1.27), (0.16, -0.21, 1.31), "secondary", r=0.004, bevel=0, seg=1, axis="y")
# shoulder pads: rings round an axis that leans out and down from the collar over the shoulder joint
sh = lm["shoulder.l"]
def pad_frame(t):
    a0, a1 = Vector((0.17, 0.0, 1.35)), Vector((sh.x + 0.16, 0.0, sh.z - 0.08))
    c = a0.lerp(a1, t)
    d = (a1 - a0).normalized()
    u = Vector((0, 1, 0))
    w = d.cross(u)            # outward-up normal of the pad
    return c, u, w
def pad_ring(t, ry, rw, n=8):   # facet pass (was 16)
    c, u, w = pad_frame(t)
    return [c + u * (ry * math.cos(2 * math.pi * k / n)) + w * (rw * math.sin(2 * math.pi * k / n))
            for k in range(n)]
pad = [(0.0, 0.13, 0.08), (0.12, 0.168, 0.12), (0.55, 0.18, 0.135), (0.9, 0.164, 0.12), (1.05, 0.115, 0.08)]
pad_faces = P.loft([pad_ring(t, ry, rw) for t, ry, rw in pad], "primary")
faces = list(pad_faces)
# stripe: across the pad from front to back, near the collar end
t, ry, rw = 0.3, 0.175, 0.131
c, u, w = pad_frame(t)
angs = [math.radians(a) for a in (-13, 0, 45, 90, 135, 180, 193)]   # facet pass: on the 8-sided pad's facets
def _poly(a, n=8):
    step = 2 * math.pi / n
    da = (a % step) - step / 2
    return math.cos(step / 2) / math.cos(da)
path = [c + (u * (ry * math.cos(a)) + w * (rw * math.sin(a))) * _poly(a) + (u * (math.cos(a) / ry) + w * (math.sin(a) / rw)).normalized() * 0.003 for a in angs]
nrm = [(u * (math.cos(a) / ry) + w * (math.sin(a) / rw)).normalized() for a in angs]
keep = [k for k, a in enumerate(angs) if rw * math.sin(a) > -0.03]
faces += P.sweep([path[k] for k in keep], P.strap_profile(0.06, 0.004, 0.0015), "secondary", [nrm[k] for k in keep])
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
# white lines down the chest and the back: from under the pad (x 0.19, z 1.2) curving in to the belt (x 0.12)
def surf_y(x, z, side):
    """Body surface y at (x, z) on the front (side -1) or back (+1), from the ring table."""
    for a, b in zip(body, body[1:]):
        if b[0] <= z <= a[0]:
            t = (z - a[0]) / (b[0] - a[0])
            z_, sx, f, bk, r = [u + (v - u) * t for u, v in zip(a, b)]
            y = f if side < 0 else bk
            dx = abs(x) - (sx - r)
            if dx > 0:
                y -= side * min(dx, r)   # facet pass: a 45 deg chamfer, not a round corner
            return y
    return 0.0
for side in (-1, 1):
    pts = [(0.192, 1.21), (0.178, 1.15), (0.155, 1.08), (0.135, 1.02), (0.13, 0.985)]
    path = [Vector((x, surf_y(x, z, side), z)) for x, z in pts]
    line = P.sweep(path, P.strap_profile(0.028, 0.004, 0.0012), "secondary", [Vector((0, side, 0))] * len(path))
    P.mirror_x(line)
