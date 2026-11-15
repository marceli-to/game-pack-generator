# Grinning skull head (painted chibi), v3 of head-skull: heavy angry brow ridge over deep sockets with
# glowing eyes, wide cheekbones, heart-shaped nose hole, upper and lower jaw as arches with the teeth set
# along them, mouth corners curving up (grin). Cranium stays simple: it is hidden under the helmet.
z0, z1 = lm["head_base"].z, lm["head_top"].z
# cranium + face base: (z, half width, front y, back y, corner radius)
prof = [(z0, 0.09, -0.17, 0.05, 0.04), (0.83, 0.11, -0.185, 0.08, 0.05), (0.88, 0.125, -0.19, 0.12, 0.055),
        (0.935, 0.155, -0.188, 0.16, 0.065), (0.99, 0.165, -0.183, 0.17, 0.07), (1.07, 0.163, -0.173, 0.17, 0.07),
        (1.15, 0.14, -0.145, 0.15, 0.065), (z1, 0.085, -0.085, 0.09, 0.04)]
P.loft([P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=2) for z, sx, f, b, r in prof], "skin")

def tilted(lo, hi, role, deg, r=0.012):
    f = P.rbox(lo, hi, role, r=r, bevel=0, seg=1, axis="y")
    c = (Vector(lo) + Vector(hi)) / 2
    P.transform(f, Matrix.Translation(c) @ Matrix.Rotation(math.radians(deg), 4, "Y") @ Matrix.Translation(-c))
    return f

# deep sockets (dark) and glowing eyes, slanted down towards the nose
sock = tilted((0.018, -0.2, 0.962), (0.148, -0.15, 1.062), "dark", 16, r=0.03)
eye = tilted((0.052, -0.206, 0.992), (0.112, -0.188, 1.03), "special", 16, r=0.014)
P.mirror_x(sock + eye)

# cheekbones: wide, sticking out past the face sides
cb = P.rbox((0.1, -0.205, 0.922), (0.18, -0.11, 0.976), "skin", r=0.022, bevel=0.009, seg=1, axis="y")
P.mirror_x(cb)

# nose hole: inverted heart, fanned from its centre
heart = [(0.0, 0.997), (0.012, 0.983), (0.025, 0.962), (0.027, 0.944), (0.014, 0.934), (0.0, 0.942),
         (-0.014, 0.934), (-0.027, 0.944), (-0.025, 0.962), (-0.012, 0.983)]
hf = [Vector((x, -0.2, z)) for x, z in heart]
hb = [Vector((x, -0.165, z)) for x, z in heart]
P.loft([[Vector((0, -0.196, 0.962))], hf, hb, [Vector((0, -0.168, 0.962))]], "dark")

# mouth cavity behind the teeth
P.rbox((-0.112, -0.19, 0.83), (0.112, -0.14, 0.915), "dark", r=0.02, bevel=0, seg=1, axis="y")
# chin / mandible below the lower teeth
P.rbox((-0.125, -0.205, 0.772), (0.125, -0.02, 0.83), "skin", r=0.035, bevel=0.012, seg=1, axis="z")

def arc_y(x, y0, k):
    return y0 + k * x * x
def arch(y0, k, zc, zk, width, height, bevel):
    """bevelled bar along the jaw arc (plan: y = y0 + k x^2), corners raised by zk x^2 (grin)"""
    xs = [-0.15, -0.105, -0.055, 0.0, 0.055, 0.105, 0.15]
    path = [Vector((x, arc_y(x, y0, k), zc + zk * x * x)) for x in xs]
    norm = [Vector((2 * k * x, -1, 0)) for x in xs]
    return P.sweep(path, P.strap_profile(width, height, bevel, inset=0.022), "skin", norm)

UY0, UK, UZ, UZK = -0.212, 2.0, 0.918, 1.6      # upper gum arc
LY0, LK, LZ, LZK = -0.214, 1.9, 0.818, 1.3      # lower jaw arc
arch(UY0, UK, UZ, UZK, 0.024, 0.022, 0.008)
arch(LY0, LK, LZ, LZK, 0.032, 0.026, 0.01)

def tooth(x, y0, k, z_top, z_bot, w, d=0.03, tip=0.85):
    """6-sided tooth on the arc, front bulging, narrowing towards its biting edge"""
    yc = arc_y(x, y0, k) + 0.004
    ang = math.atan(2 * k * x)
    sec = [(w / 2, -d * 0.32), (0, -d * 0.5), (-w / 2, -d * 0.32), (-w / 2, d / 2), (0, d / 2), (w / 2, d / 2)]
    R = Matrix.Rotation(ang, 3, "Z")
    ring = lambda z, s: [Vector((x, yc, z)) + R @ Vector((u * s, v * s, 0)) for u, v in sec]
    return P.loft([ring(z_top, 1.0), ring(z_bot, tip)], "skin")

N = 8
txs = [-0.118 + 0.236 * (i + 0.5) / N for i in range(N)]
for x in txs:
    a = abs(x) / 0.118
    w = 0.236 / N * 0.97
    up_top = UZ + UZK * x * x - 0.006
    up_bot = up_top - (0.052 - 0.016 * a)
    tooth(x, UY0, UK, up_top, up_bot, w)
    lo_bot = LZ + LZK * x * x + 0.01
    lo_top = min(up_bot - 0.004, lo_bot + 0.034 - 0.008 * a)
    tooth(x, LY0, LK, lo_bot, lo_top, w * 0.92)
