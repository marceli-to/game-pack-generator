# Braided hair (tinfox, hero-f; player 2), from specs/player-2/reference: a full hair mass over the head (3-4.5 cm
# out), down over the tops of the ears at the sides and to the nape at the back; a thick fringe swept from the part on
# the wearer's left down across the right brow; a lock in front of each ear; a long braid from the nape down the
# back to the waist (bulging plaits alternating side to side, a white band near the end, role `secondary`), blended
# from the head to the chest along its length (skeleton.part_blend_bones) so it stays on the back.
# Built in hero-m coordinates (the head-hero-f head is the guard's, moved and scaled at the end the same way).
prof = [(1.52, 0.118, -0.14, 0.13, 0.055), (1.56, 0.12, -0.145, 0.142, 0.055), (1.65, 0.124, -0.146, 0.157, 0.06),
        (1.73, 0.115, -0.135, 0.153, 0.06), (1.80, 0.085, -0.095, 0.115, 0.045)]
def dims(z):
    z = max(prof[0][0], min(prof[-1][0], z))
    for a, b in zip(prof, prof[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return [u + (v - u) * t for u, v in zip(a[1:], b[1:])]
def pt(j, z, o):
    sx, f, b, r = dims(z)
    p = P.rrect((0, (f + b) / 2, z), sx + o, (b - f) / 2 + o, r + o, seg=3)[j]
    return Vector((p.x, p.y, z))
ref = P.rrect((0, 0, 0), 1, 1, 0.5, seg=3)
def z_bottom(j):
    """Lower edge: a diagonal hairline in front (high at the part on the wearer's left, down to the right temple),
    over the tops of the ears at the sides, the nape at the back."""
    d = Vector((ref[j].x, ref[j].y, 0)).normalized()
    fr = max(0.0, -d.y)
    return 1.63 + 0.1 * fr ** 2 + 0.05 * d.x * fr - 0.08 * max(0.0, d.y) ** 1.5
N = 16
rings = [[pt(j, z, o) for j in range(N)] for z, o in ((1.836, -0.05), (1.826, -0.018), (1.808, 0.014), (1.78, 0.032), (1.74, 0.04))]
for v in (0.5, 1.0):
    rings.append([pt(j, 1.74 + (z_bottom(j) - 1.74) * v, 0.04 - 0.016 * v) for j in range(N)])
rings.append([pt(j, z_bottom(j) + 0.012, -0.012) for j in range(N)])
P.loft([[Vector((0, 0.01, 1.842))]] + rings, "hair")
# the swoop: a thick lock from the part (wearer's left) over the front of the hair down to the right temple
def hair_front(x, z, o):
    ring_ = [Vector((q.x, q.y, z)) for q in
             P.rrect((0, (dims(z)[1] + dims(z)[2]) / 2, z), dims(z)[0] + o, (dims(z)[2] - dims(z)[1]) / 2 + o,
                     dims(z)[3] + o, seg=8)]
    front = sorted([q for q in ring_ if q.y < (dims(z)[1] + dims(z)[2]) / 2], key=lambda q: q.x)
    for a, b in zip(front, front[1:]):
        if a.x <= x <= b.x:
            return a.lerp(b, (x - a.x) / (b.x - a.x) if b.x > a.x else 0.0)
    return front[0] if x < front[0].x else front[-1]
sw = [(0.065, 1.805), (0.025, 1.792), (-0.025, 1.768), (-0.07, 1.738), (-0.105, 1.7), (-0.128, 1.66), (-0.136, 1.63)]
path = [hair_front(x, z, 0.03) for x, z in sw]
nrm = [Vector((q.x * 0.8, q.y - 0.01, (q.z - 1.62) * 0.8)).normalized() for q in path]
P.sweep(path, lambda i: P.strap_profile(0.075 - 0.006 * i, 0.02, 0.007, inset=0.014), "hair", nrm)
# head front surface (head-hero-square's profile) for the fringe
hp = [(1.535, 0.13, 0.136), (1.575, 0.132, 0.139), (1.615, 0.127, 0.139), (1.66, 0.124, 0.137), (1.7, 0.119, 0.13),
      (1.75, 0.108, 0.118)]
def face_y(x, z):
    for a, b in zip(hp, hp[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            sx, fy = a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t
            u = min(0.999, abs(x) / sx)
            return -fy * (1 - u ** 3.2) ** (1 / 3.2)
    return -0.1
# locks in front of the ears, flicking out at the jaw
lock = P.loft([P.rrect((0.112 + dx, -0.035, z), sx, sy, min(sx, sy) * 0.5, seg=1) for z, dx, sx, sy in
               ((1.68, 0.0, 0.016, 0.024), (1.63, 0.002, 0.016, 0.024), (1.6, 0.004, 0.012, 0.018), (1.58, 0.006, 0.005, 0.008))], "hair")
P.mirror_x(lock)
# braid: plaits alternating side to side from the nape down the back (final z 1.45 -> 0.93 after the move below)
braid = []
segs = [(1.585, 0.17, 0.0), (1.52, 0.178, 0.009), (1.45, 0.176, -0.009), (1.38, 0.175, 0.009), (1.31, 0.175, -0.009),
        (1.24, 0.176, 0.008), (1.17, 0.177, -0.007)]
for z, y, x in segs:
    braid += P.loft([P.ring((x * 0.5, y, z + 0.036), 0.026, 0.022, n=8), P.ring((x, y, z + 0.012), 0.04, 0.034, n=8),
                     P.ring((x, y, z - 0.022), 0.036, 0.03, n=8), P.ring((x * 0.5, y, z - 0.044), 0.022, 0.019, n=8)], "hair")
braid += P.loft([P.ring((0, 0.177, 1.12), 0.026, 0.023, n=8), P.ring((0, 0.177, 1.09), 0.026, 0.023, n=8)], "secondary")
braid += P.loft([P.ring((0, 0.177, 1.1), 0.02, 0.018, n=8), P.ring((0, 0.178, 1.07), 0.036, 0.032, n=8),
                 P.ring((0, 0.18, 1.04), 0.028, 0.025, n=8)] + [[Vector((0, 0.182, 1.02))]], "hair")
# from the head into the braid's top: a bun-like root on the back of the head
braid += P.loft([P.ring((0, 0.12, 1.63), 0.045, 0.03, n=8, axis="y"), P.ring((0, 0.17, 1.6), 0.036, 0.03, n=8, axis="y")],
                "hair")
# weights: head at the top, blending to the chest by final z 1.40 -> 1.30 (hero-m 1.50 -> 1.40)
for v in {v for f in braid for v in f.verts}:
    w = max(0.0, min(1.0, (v.co.z - 1.4) / 0.1))
    P.set_weights([v], {"head": w, "chest": 1.0 - w})
hb = lm["head_base"].z
P.transform(list(P.bm.faces), Matrix.Translation((0, 0, hb)) @ Matrix.Diagonal((0.95, 0.95, 1.0, 1.0))
            @ Matrix.Translation((0, 0, -1.47)))
