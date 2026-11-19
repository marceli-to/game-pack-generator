# Squad suit top, striped variant (tinfox, hero-f; player 4, specs/player-4/reference): torso-suit-hero-f with a
# white stripe (role `secondary`) down the centre front from the collar's rim to the belt instead of the seam.
# torso-suit-hero-f: a fitted one-piece suit from a
# stand-up collar (an open funnel round the neck, lower at the front, set forward so the chin sits behind it) over
# square shoulders, a bust, a narrow waist under the belt, wide hips and an upside-down V at the crotch (the legs are
# a separate part); a thin seam down the front, a white name patch (role `secondary`) on the wearer's left chest;
# rounded shoulder pads on the torso (blended chest / upper arm, pre-tilted for the hanging arms, as the guard's)
# with a white stripe across each. Suit colour = `primary` (the player's slot colour).
def ring(z, sx, f, b, r):
    return P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=1)   # facet pass: 8 sides
body = [(1.325, 0.08, -0.075, 0.085, 0.04), (1.3, 0.15, -0.115, 0.11, 0.06), (1.25, 0.178, -0.148, 0.12, 0.09),
        (1.17, 0.168, -0.165, 0.115, 0.09), (1.1, 0.14, -0.142, 0.105, 0.075), (1.0, 0.12, -0.112, 0.09, 0.06),
        (0.93, 0.132, -0.11, 0.1, 0.06), (0.85, 0.165, -0.096, 0.124, 0.08), (0.78, 0.145, -0.088, 0.11, 0.07)]
rings = [ring(*b) for b in body]
_ys = [q.y for q in rings[0]]
rings[0] = [Vector((q.x, q.y, 1.3 + 0.03 * ((q.y - min(_ys)) / (max(_ys) - min(_ys))) ** 0.7)) for q in rings[0]]
for z, sx in ((0.76, 0.115), (0.745, 0.042)):
    pts = ring(z, sx, -0.09, 0.1, 0.04)
    rings.append([Vector((p.x, p.y, z - 0.025 * max(0.0, 1 - abs(p.x) / sx))) for p in pts])
P.loft(rings, "primary", cap_roles=("primary", "primary"))
# collar: an open stand-up funnel, its rim sloping from 1.385 at the back to 1.345 at the front
def sloped(rg, z_back, z_front):
    ys = [q.y for q in rg]
    y0, y1 = min(ys), max(ys)
    return [Vector((q.x, q.y, z_front + (z_back - z_front) * ((q.y - y0) / (y1 - y0)) ** 0.7)) for q in rg]
col = [sloped(ring(1.29, 0.106, -0.122, 0.112, 0.06), 1.3, 1.285),
       sloped(ring(1.33, 0.104, -0.128, 0.112, 0.06), 1.355, 1.32),
       sloped(ring(1.36, 0.107, -0.133, 0.116, 0.06), 1.385, 1.345)]
P.shell(col, 0.014, "primary", cyclic=True)
# white stripe down the centre front, from the collar rim over the chest to the belt
pts = [(1.345, -0.137), (1.31, -0.13), (1.29, -0.128), (1.25, -0.152), (1.2, -0.164), (1.16, -0.166), (1.1, -0.146),
       (1.0, -0.116), (0.94, -0.114)]
P.sweep([Vector((0, y, z)) for z, y in pts], P.strap_profile(0.034, 0.004, 0.0012, inset=0.006), "secondary",
        [Vector((0, -1, 0))] * len(pts))
# name patch on the wearer's left chest
P.rbox((0.04, -0.172, 1.195), (0.11, -0.155, 1.222), "secondary", r=0.003, bevel=0, seg=1, axis="y")
# shoulder pads (as torso-suit-hero, 0.82 x)
sh = lm["shoulder.l"]
def pad_frame(t):
    a0, a1 = Vector((0.12, 0.0, 1.262)), Vector((sh.x + 0.095, 0.0, sh.z - 0.06))
    c = a0.lerp(a1, t)
    d = (a1 - a0).normalized()
    u = Vector((0, 1, 0))
    return c, u, d.cross(u)
def pad_ring(t, ry, rw, n=8):   # facet pass (was 16)
    c, u, w = pad_frame(t)
    return [c + u * (ry * math.cos(2 * math.pi * k / n)) + w * (rw * math.sin(2 * math.pi * k / n)) for k in range(n)]
pad = [(0.0, 0.1, 0.06), (0.12, 0.128, 0.09), (0.55, 0.136, 0.1), (0.9, 0.124, 0.09), (1.05, 0.086, 0.06)]
faces = list(P.loft([pad_ring(t, ry, rw) for t, ry, rw in pad], "primary"))
t, ry, rw = 0.3, 0.133, 0.098
c, u, w = pad_frame(t)
angs = [math.radians(a) for a in (-13, 0, 45, 90, 135, 180, 193)]   # facet pass: on the 8-sided pad's facets
def _poly(a, n=8):
    step = 2 * math.pi / n
    da = (a % step) - step / 2
    return math.cos(step / 2) / math.cos(da)
path = [c + (u * (ry * math.cos(a)) + w * (rw * math.sin(a))) * _poly(a) + (u * (math.cos(a) / ry) + w * (math.sin(a) / rw)).normalized() * 0.003 for a in angs]
nrm = [(u * (math.cos(a) / ry) + w * (math.sin(a) / rw)).normalized() for a in angs]
keep = [k for k, a in enumerate(angs) if rw * math.sin(a) > -0.025]
faces += P.sweep([path[k] for k in keep], P.strap_profile(0.05, 0.004, 0.0015), "secondary", [nrm[k] for k in keep])
follow, ARMS_DOWN = 0.6, 74.0
a0, a1 = pad_frame(0.0)[0], pad_frame(1.0)[0]
axis = a1 - a0
joint = Vector((sh.x, 0.0, sh.z))
for v in {v for f in faces for v in f.verts}:
    t = max(0.0, min(1.0, (v.co - a0).dot(axis) / axis.length_squared))
    f_arm = follow * (3 * t * t - 2 * t * t * t)
    P.set_weights([v], {"chest": 1.0 - f_arm, "upperarm.l": f_arm})
    v.co = joint + Matrix.Rotation(math.radians(-ARMS_DOWN * f_arm), 3, "Y") @ (v.co - joint)
P.mirror_x(faces)
