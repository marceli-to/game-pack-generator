# Short full beard (tinfox, hero-m, for head-hero-grin; player 3, specs/player-3/reference): one thick shell over the
# lower face from the sideburns along the jaw round the chin, its top edge framing the grin (just under the lower
# lip in the middle, up the mouth corners, rising diagonally over the cheeks to the sideburns), tucked under the
# jaw; a moustache over the upper lip running down into the beard at the corners. Role `accent` (beard brown).
# head surface: the profile and superellipse rings of head-hero-grin (z, half width, front, back, centre bump)
prof = [(1.445, 0.06, 0.1, 0.05, 0.0), (1.457, 0.074, 0.114, 0.07, 0.03), (1.474, 0.088, 0.124, 0.088, 0.036),
        (1.492, 0.102, 0.13, 0.1, 0.03), (1.512, 0.116, 0.134, 0.115, 0.014), (1.535, 0.13, 0.136, 0.13, 0.002),
        (1.575, 0.132, 0.139, 0.145, 0.01), (1.615, 0.127, 0.139, 0.152, 0.0), (1.66, 0.124, 0.137, 0.156, 0.02)]
def dims(z):
    z = max(prof[0][0], min(prof[-1][0], z))
    for a, b in zip(prof, prof[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return [u + (v - u) * t for u, v in zip(a[1:], b[1:])]
def head_pt(t, z, off, n=3.2):
    """Point on the head at angle t (radians, 0 = front, + towards +X) and height z, `off` outside it."""
    sx, fy, by, bump = dims(z)
    s, c = math.sin(t), -math.cos(t)
    x = (sx + off) * math.copysign(abs(s) ** (2 / n), s)
    y = (fy + off if c < 0 else by + off) * math.copysign(abs(c) ** (2 / n), c)
    y -= bump * max(0.0, -c) ** 6
    return Vector((x, y, z))
def lerp_tab(tab, x):
    x = abs(x)
    for (a, za), (b, zb) in zip(tab, tab[1:]):
        if a <= x <= b:
            return za + (zb - za) * (x - a) / (b - a)
    return tab[-1][1] if x > tab[-1][0] else tab[0][1]
TOP = [(0.0, 1.487), (0.048, 1.489), (0.066, 1.545), (0.085, 1.552), (0.112, 1.582), (0.135, 1.62)]   # by |x|
BOT = [(0.0, 1.442), (0.06, 1.448), (0.1, 1.475), (0.135, 1.53)]                                     # jaw line
OFF = 0.012
angs = [math.radians(a) for a in range(-104, 105, 13)]
grid = []
for v in (0.0, 0.5, 1.0):
    row = []
    for t in angs:
        x = head_pt(t, 1.52, 0.0).x
        z = lerp_tab(TOP, x) + (lerp_tab(BOT, x) - lerp_tab(TOP, x)) * v
        row.append(head_pt(t, z, OFF + 0.006 * v))
    grid.append(row)
# tucked under the jaw towards the neck
grid.append([Vector((p.x * 0.8, p.y * 0.75, p.z - 0.018)) for p in grid[-1]])
P.shell(grid, -0.022, "accent")
# moustache: a thick strap over the upper lip (the grin's top edge is at z 1.538 + 0.012 (x / 0.062)^4), running
# down beside the mouth corners into the beard
MW = 0.062
xs = [-0.072, -0.066, -0.05, -0.025, 0.0, 0.025, 0.05, 0.066, 0.072]
def mz(x):
    if abs(x) <= MW - 0.004:
        return 1.538 + 0.012 * (x / MW) ** 4 + 0.011
    return 1.53
def front_pt(x, z, off):
    """Point on the face at (x, z), `off` in front of it (sampled along the ring)."""
    pts = [head_pt(math.radians(a / 2), z, off) for a in range(-180, 181)]
    for a, b in zip(pts, pts[1:]):
        if a.x <= x <= b.x:
            return a.lerp(b, (x - a.x) / (b.x - a.x) if b.x > a.x else 0.0)
    return pts[0] if x < 0 else pts[-1]
path = [front_pt(x, mz(x), 0.004) for x in xs]
P.sweep(path, P.strap_profile(0.02, 0.012, 0.004, inset=0.012), "accent", [Vector((0, -1, 0))] * len(path))
