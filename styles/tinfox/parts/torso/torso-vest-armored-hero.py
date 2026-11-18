# v2 (Marcel, 2026-11-18: grey vest, to tell him from the guard at a distance): vest, rolled collar, plates and
# shoulder pads carry role `armor`; the jacket under it stays `primary`.
# Armoured vest over the uniform jacket (tinfox, hero-m), for specs/rifle-guard/reference: the guard's jacket
# (torso-jacket-hero, collar/placket/name patch dropped: the vest covers them) under a padded vest from the collar
# to the belt, 3 cm proud of the jacket; a thick rolled collar round the neck; three rounded plates stacked on the
# front and on the back, an orange tab on the top plate front and back, vertical orange straps beside the plates;
# shoulder pads as on the guard, 10 % bigger.
def ring(z, sx, f, b, r):
    return P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=3)   # v4: 16 sides
# v3 (Marcel: more V-shaped, bulky): broad deep chest and shoulders tapering to a narrow waist under the belt;
# the chest's front-outer corners well rounded, so arms aiming forward pass in front of them, not through
body = [(1.51, 0.095, -0.1, 0.09, 0.05), (1.44, 0.105, -0.115, 0.1, 0.05), (1.43, 0.2, -0.16, 0.14, 0.07),
        (1.38, 0.272, -0.2, 0.17, 0.15), (1.3, 0.28, -0.22, 0.178, 0.16), (1.22, 0.258, -0.21, 0.168, 0.13),
        (1.19, 0.226, -0.18, 0.158, 0.085), (1.1, 0.2, -0.155, 0.145, 0.075), (1.0, 0.18, -0.138, 0.136, 0.068),
        (0.9, 0.228, -0.152, 0.152, 0.075), (0.8, 0.238, -0.148, 0.152, 0.075), (0.75, 0.2, -0.13, 0.135, 0.065)]
# the vest hides the jacket from under the collar to z 1.1: the jacket is two pieces, the collar and the part from
# just inside the vest's lower edge down to the crotch
P.loft([ring(*b) for b in body[:3]], "primary", cap_roles=("primary", "dark"))
rings = [ring(*b) for b in body if b[0] <= 1.1]
# crotch: the last rings close to a V (the centre front and back points drop lowest)
for z, sx in ((0.72, 0.13), (0.7, 0.05)):
    pts = ring(z, sx, -0.115, 0.12, 0.05)
    rings.append([Vector((p.x, p.y, z - 0.03 * max(0.0, 1 - abs(p.x) / sx))) for p in pts])
P.loft(rings, "primary", cap_roles=("dark", "primary"))
# collar band (a step out at the top of the collar)
P.loft([ring(1.44, 0.112, -0.122, 0.106, 0.05), ring(1.5, 0.108, -0.115, 0.1, 0.05)], "primary")
# --- vest: the jacket's chest rings pushed out, from just under the collar to the belt
vest_rows = [(1.43, 0.2, -0.16, 0.14, 0.07), (1.38, 0.272, -0.2, 0.17, 0.15), (1.3, 0.28, -0.22, 0.178, 0.16),
             (1.22, 0.258, -0.21, 0.168, 0.13), (1.19, 0.226, -0.18, 0.158, 0.085), (1.1, 0.2, -0.155, 0.145, 0.075),
             (1.0, 0.18, -0.138, 0.136, 0.068)]
OUT = 0.028
def vrow(z, sx, f, b, r):
    return (z, sx + OUT, f - OUT, b + OUT, r + OUT * 0.5)
vrows = [vrow(*v) for v in vest_rows]
vrows[0] = (1.445, 0.215, -0.17, 0.15, 0.08)
P.loft([ring(*v) for v in vrows], "armor", cap_roles=("armor", "armor"))
def vest_y(x, z, side):
    """Surface y of the vest at (x, z) on the front (side -1) or back (+1)."""
    for a, b in zip(vrows, vrows[1:]):
        if b[0] <= z <= a[0]:
            t = (z - a[0]) / (b[0] - a[0])
            v = [p + (q - p) * t for p, q in zip(a, b)]
            break
    else:
        v = vrows[-1] if z < vrows[-1][0] else vrows[0]
    pts = ring(z, *v[1:])
    best = None
    for p, q in zip(pts, pts[1:] + pts[:1]):
        if (p.y * side > 0 or q.y * side > 0) and min(p.x, q.x) <= x <= max(p.x, q.x) and abs(q.x - p.x) > 1e-6:
            y = p.y + (q.y - p.y) * (x - p.x) / (q.x - p.x)
            if best is None or y * side > best * side:
                best = y
    return best
# rolled collar round the neck
# rising at the back to meet the helmet's neck guard (no skin between them from behind)
cpath = [Vector((p.x, p.y, p.z + 0.06 * max(0.0, p.y) / 0.12)) for p in P.rrect((0, -0.005, 1.455), 0.13, 0.125, 0.07, seg=3)]
cn = [Vector((p.x, p.y + 0.005, 0)).normalized() for p in cpath]
P.sweep(cpath, P.strap_profile(0.055, 0.035, 0.014, inset=0.02), "armor", cn, cyclic=True)
# plates: rounded pillows following the vest surface (3 rows front and back)
def plate(z0, z1, hw, side, role="armor"):
    zs = [z0, z0 + 0.012, z1 - 0.012, z1]
    xs = [-hw, -hw + 0.015, hw - 0.015, hw]
    if side > 0:   # keep the outer side outward (the shell's normal is du x dv)
        xs = xs[::-1]
    rows = []
    for i, z in enumerate(zs):
        lift = 0.022 if 0 < i < 3 else 0.006
        row = []
        for j, x in enumerate(xs):
            l = lift if 0 < j < 3 else 0.006
            row.append(Vector((x, vest_y(x, z, side) + side * (l - 0.008), z)))
        rows.append(row)
    return P.shell(rows, 0.016, role)
for z0, z1, hw in ((1.27, 1.36, 0.145), (1.165, 1.255, 0.15), (1.06, 1.15, 0.15)):
    plate(z0, z1, hw, -1)
for z0, z1, hw in ((1.27, 1.37, 0.15), (1.165, 1.26, 0.155), (1.06, 1.155, 0.155)):
    plate(z0, z1, hw, 1)
# orange tabs on the top plates
for side, z in ((-1, 1.325), (1, 1.335)):
    y = vest_y(0.0, z, side) + side * 0.01   # sunk into the plate (its face is 1.4 cm proud)
    P.rbox((-0.05, min(y, y + side * 0.008), z - 0.013), (0.05, max(y, y + side * 0.008), z + 0.013), "accent",
           r=0.003, bevel=0, seg=1, axis="y")
# vertical orange straps beside the plates, front and back, up under the pads
spath = lambda side: [Vector((0.19, vest_y(0.19, z, side) + side * 0.002, z)) for z in (1.08, 1.16, 1.24, 1.32, 1.4)]
straps = []
for side in (-1, 1):
    straps += P.sweep(spath(side), P.strap_profile(0.04, 0.006, 0.002), "accent", [Vector((0, side, 0))] * 5)
P.mirror_x(straps)
# shoulder pads (v4 guard code, 10 % bigger)
# rings round an axis that leans out and down from the collar over the shoulder joint
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
pad = [(t, ry * 1.1, rw * 1.1) for t, ry, rw in [(0.0, 0.13, 0.08), (0.12, 0.168, 0.12), (0.55, 0.18, 0.135), (0.9, 0.164, 0.12), (1.05, 0.115, 0.08)]]
pad_faces = P.loft([pad_ring(t, ry, rw) for t, ry, rw in pad], "armor")
faces = list(pad_faces)
# stripe: across the pad from front to back, near the collar end
t, ry, rw = 0.3, 0.175 * 1.1, 0.131 * 1.1
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
