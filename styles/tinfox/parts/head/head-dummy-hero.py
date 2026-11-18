# Practice dummy head (tinfox, hero-m), for specs/practice-dummy/reference: a round canvas mannequin head (an egg,
# 16 sides) on a short neck, with a painted friendly face as geometry: two dot eyes and a small smile, both in
# dark brown and a few millimetres proud. No hair, ears or nose. Same size and joint as the guard's head, so the
# game's head hit zone fits.
z1 = lm["head_top"].z
N = 16
P.loft([P.ring((0, 0.01, 1.38), 0.075, 0.07, n=10), P.ring((0, 0.01, 1.48), 0.078, 0.074, n=10)], "skin")
# (z, half width, half depth, centre y)
prof = [(1.47, 0.06, 0.06, 0.004), (1.49, 0.088, 0.086, 0.002), (1.52, 0.115, 0.112, 0.0), (1.56, 0.138, 0.134, 0.0),
        (1.61, 0.15, 0.145, 0.002), (1.66, 0.146, 0.142, 0.004), (1.7, 0.134, 0.132, 0.006), (1.745, 0.108, 0.11, 0.006),
        (1.78, 0.07, 0.075, 0.006), (1.797, 0.035, 0.04, 0.006)]
P.loft([[Vector((0, 0.005, 1.462))]] + [P.ring((0, cy, z), rx, ry, n=N) for z, rx, ry, cy in prof]
       + [[Vector((0, 0.006, z1))]], "skin")
def front(x, z):
    """Front surface y of the faceted head at (x, z): the ellipse, pulled in to the 16-gon's flats."""
    for a, b in zip(prof, prof[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            rx, ry, cy = (a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t, a[3] + (b[3] - a[3]) * t)
            u = min(0.98, abs(x) / rx)
            return cy - ry * math.sqrt(1 - u * u) * math.cos(math.pi / N)
    return -0.1
# dot eyes: 8-sided discs, rooted 1 cm inside the head, 3 mm proud
ex, ez = 0.054, 1.628
def disc(x, z, r, h):
    y = front(x, z)
    n = Vector((x * 0.6, -1, 0)).normalized()
    c = Vector((x, y, z))
    return P.loft([P.ring(c - n * 0.012, r, n=8, axis="y", phase=22.5), P.ring(c + n * (h - 0.002), r, n=8, axis="y", phase=22.5),
                   P.ring(c + n * h, r * 0.8, n=8, axis="y", phase=22.5)], "eyes", cap_roles=("eyes", "eyes"))
eye = disc(ex, ez, 0.022, 0.004)
P.mirror_x(eye)
# smile: a thin curved strap, corners up
xs = [-0.06, -0.042, -0.021, 0.0, 0.021, 0.042, 0.06]
zs = [1.552 + 9.0 * x * x for x in xs]
P.sweep([Vector((x, front(x, z) - 0.002, z)) for x, z in zip(xs, zs)], P.strap_profile(0.012, 0.006, 0.002),
        "eyes", [Vector((x * 4, -1, 0)).normalized() for x in xs])
