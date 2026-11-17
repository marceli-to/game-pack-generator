# Handlebar moustache (tinfox, hero-m, for head-hero-square): two thick tapering strands from under the nose out
# along the upper lip, their tips curling up beside the mouth; sunk 40 % into the face. Hair colour.
prof = [(1.443, 0.07, 0.1), (1.455, 0.088, 0.116), (1.472, 0.103, 0.126), (1.49, 0.118, 0.132), (1.51, 0.126, 0.135),
        (1.535, 0.13, 0.136), (1.575, 0.132, 0.139), (1.615, 0.127, 0.139)]
def face_y(x, z):
    for a, b in zip(prof, prof[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            sx, fy = a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t
            u = min(0.999, abs(x) / sx)
            return -fy * (1 - u ** 3.2) ** (1 / 3.2)
    return -0.13
# (x, z, half height, proud)
pts = [(-0.008, 1.553, 0.011, 0.02), (0.014, 1.551, 0.012, 0.02), (0.034, 1.546, 0.011, 0.018),
       (0.054, 1.542, 0.009, 0.015), (0.071, 1.546, 0.007, 0.012), (0.083, 1.557, 0.0055, 0.009),
       (0.088, 1.57, 0.0045, 0.007), (0.084, 1.58, 0.003, 0.004)]
path = [Vector((x, face_y(x, z) + 0.004 if x > 0.02 else -0.156, z)) for x, z, _, _ in pts]
nrm = [Vector((x * 2.5, -1, 0)).normalized() for x, _, _, _ in pts]
def profile(i):
    h, o = pts[i][2], pts[i][3]
    return [(o * 0.4 + o * 0.6 * math.cos(a) if math.cos(a) > 0 else o * 0.4 + 0.6 * o * math.cos(a),
             h * math.sin(a)) for a in [2 * math.pi * k / 8 for k in range(8)]]
m = P.sweep(path, profile, "hair", nrm)
P.mirror_x(m)
