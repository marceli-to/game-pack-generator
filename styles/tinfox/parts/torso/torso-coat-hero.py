# Officer's greatcoat (tinfox, hero-m), fitted to specs/officer/reference: the guard jacket's chest, shoulders and
# stand-up collar (brass trim along its top and down the front V), one row of brass buttons, an orange name patch;
# below the belt the coat flares to a hem at 0.55 m (skirt weights, so the front follows a lifted thigh), its inside
# dark. Epaulettes: the guard's shoulder caps in orange with a pleated fringe hanging round their outer end and a
# brass button by the collar (blended chest/upper-arm weights, pre-tilted, as the guard's pads).
def ring(z, sx, f, b, r):
    return P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=3)
body = [(1.51, 0.095, -0.1, 0.09, 0.05), (1.44, 0.105, -0.115, 0.1, 0.05), (1.43, 0.2, -0.16, 0.14, 0.07),
        (1.38, 0.272, -0.2, 0.17, 0.15), (1.3, 0.28, -0.22, 0.178, 0.16), (1.22, 0.258, -0.21, 0.168, 0.13),
        (1.19, 0.226, -0.18, 0.158, 0.085), (1.1, 0.2, -0.155, 0.145, 0.075), (1.0, 0.18, -0.138, 0.136, 0.068),
        (0.9, 0.198, -0.16, 0.16, 0.08), (0.8, 0.25, -0.185, 0.192, 0.09), (0.7, 0.275, -0.2, 0.214, 0.1),
        (0.62, 0.29, -0.21, 0.23, 0.105), (0.555, 0.3, -0.218, 0.242, 0.11)]
# v2 (game report: the skirt front lifted as a rigid plank and the thigh tore through it): the closed body ends
# under the belt; below it the skirt is an open sheet with a 1.2 cm slit up the front, so each front panel follows
# its own thigh (`centre_width_front`) and the two never share space; the follow ramps from 0 at the hips to 0.6
# at the hem (`full_at` 1.0), so the panel bends instead of swinging as one board. The back stays one piece.
upper = [b for b in body if b[0] >= 0.9]
P.loft([ring(*b) for b in upper], "primary", cap_roles=("dark", "primary"))
P.skirt = {"follow": 0.6, "full_at": 1.0, "centre_width_front": 0.01}
def dims(z):
    for z0z, z1z in zip(body, body[1:]):
        if z1z[0] <= z <= z0z[0]:
            k = (z0z[0] - z) / (z0z[0] - z1z[0])
            return [a + (c - a) * k for a, c in zip(z0z[1:], z1z[1:])]
    return list(body[-1][1:])
GAP = 0.006
def skirt_row(z, out=0.003):
    sx, f, b_, r = dims(z)
    pts = ring(z, sx + out, f - out, b_ + out, r)        # 16 points, corner order (+,+) (-,+) (-,-) (+,-)
    fy = pts[12].y
    return ([Vector((GAP, fy, z))] + pts[12:16] + pts[0:12] + [Vector((-GAP, fy, z))])
rows = [skirt_row(z) for z in (0.96, 0.9, 0.8, 0.7, 0.62, 0.555)]
P.shell(rows, -0.015, "primary")
# collar band (a step out at the top of the collar)
P.loft([ring(1.44, 0.112, -0.122, 0.106, 0.05), ring(1.5, 0.108, -0.115, 0.1, 0.05)], "primary")
# brass trim: along the collar's top edge, and a V down its front
top = ring(1.502, 0.108, -0.115, 0.1, 0.05)
P.sweep(top, P.strap_profile(0.018, 0.005, 0.0015), "metal", [Vector((0, 0, 1))] * len(top), cyclic=True)
for s in (1, -1):
    path = [Vector((s * 0.034, -0.121, 1.5)), Vector((s * 0.016, -0.124, 1.465)), Vector((s * 0.002, -0.125, 1.44))]
    P.sweep(path, P.strap_profile(0.014, 0.005, 0.0015), "metal", [Vector((0, -1, 0))] * 3)
# front of the coat at the centre line (the rrect's front edge is flat there)
def front_y(z):
    zs = [(b[0], b[2]) for b in body]
    for (z0, f0), (z1, f1) in zip(zs, zs[1:]):
        if z1 <= z <= z0:
            return f0 + (f1 - f0) * (z0 - z) / (z0 - z1)
    return zs[-1][1]
for z in (1.31, 1.2, 1.09, 0.85, 0.73, 0.61):
    y = front_y(z) - (0.003 if z < 0.96 else 0.0)
    x = 0.022 if z < 0.96 else 0.0      # below the belt: on the wearer's left panel, beside the slit
    r = 0.03                            # 15 % larger than v1 (game report: buttons read only near)
    P.cylinder(Vector((x, y + 0.006, z)), Vector((x, y - 0.008, z)), r, n=10, role="metal")
    P.cylinder(Vector((x, y - 0.007, z)), Vector((x, y - 0.013, z)), r * 0.7, n=10, role="metal")
# name patch on the wearer's left chest
P.rbox((0.07, -0.228, 1.255), (0.17, -0.21, 1.285), "accent", r=0.004, bevel=0, seg=1, axis="y")
# epaulettes: rings round an axis that leans out and down from the collar over the shoulder joint
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
pad = [(0.0, 0.11, 0.06), (0.12, 0.142, 0.088), (0.55, 0.152, 0.098), (0.9, 0.142, 0.088), (1.05, 0.1, 0.06)]
faces = list(P.loft([pad_ring(t, ry, rw) for t, ry, rw in pad], "primary"))
def pad_dims(t):
    for (t0, y0, w0), (t1, y1, w1) in zip(pad, pad[1:]):
        if t0 <= t <= t1:
            k = (t - t0) / (t1 - t0)
            return y0 + (y1 - y0) * k, w0 + (w1 - w0) * k
    return pad[-1][1], pad[-1][2]
def on_pad(t, al, off):
    """Point on the pad surface at t, angle al from the top (towards +u = back), `off` out."""
    c, u, w = pad_frame(t)
    ry, rw = pad_dims(min(t, 1.05))
    return c + u * ((ry + off) * math.sin(al)) + w * ((rw + off) * math.cos(al))
# orange board: a shell lying on the pad's top from the collar to past its outer end
ts = [0.04, 0.25, 0.5, 0.75, 0.95, 1.06]
als = [math.radians(a) for a in range(-48, 49, 16)]
board = [[on_pad(t, al, 0.016) for al in als] for t in ts]
faces += P.shell(board, 0.014, "accent")
# fringe: a pleated curtain hanging 7 cm from the board's rim (front side, outer end, back side)
rim = [on_pad(t, als[0], 0.014) for t in (0.4, 0.6, 0.8, 0.96)]
rim += [on_pad(1.06, al, 0.014) for al in als[1:-1]]
rim += [on_pad(t, als[-1], 0.014) for t in (0.96, 0.8, 0.6, 0.4)]
mid = pad_frame(0.55)[0]
def hang(k, p, dz, out):
    n = p - mid
    n.z = 0
    n.normalize()
    pleat = 0.008 if k % 2 else -0.006
    return p + n * (out + pleat) + Vector((0, 0, -dz))
faces += P.shell([[hang(k, p, 0.0, 0.0) for k, p in enumerate(rim)],
                  [hang(k, p, 0.05, 0.006) for k, p in enumerate(rim)],
                  [hang(k, p, 0.095, 0.016) for k, p in enumerate(rim)]], 0.01, "accent")
# brass button near the collar end
faces += P.dome(on_pad(0.14, 0.0, 0.016), pad_frame(0.14)[2], 0.022, 0.012, n=10, role="metal")
follow = 0.6
a0, a1 = pad_frame(0.0)[0], pad_frame(1.0)[0]
axis = a1 - a0
verts = {v for f in faces for v in f.verts}
joint = Vector((sh.x, 0.0, sh.z))
for v in verts:
    t = max(0.0, min(1.0, (v.co - a0).dot(axis) / axis.length_squared))
    f_arm = follow * (3 * t * t - 2 * t * t * t)
    P.set_weights([v], {"chest": 1.0 - f_arm, "upperarm.l": f_arm})
    v.co = joint + Matrix.Rotation(math.radians(-72.0 * f_arm), 3, "Y") @ (v.co - joint)
P.mirror_x(faces)
