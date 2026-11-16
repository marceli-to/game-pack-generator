# Long dress (lowpoly chibi), fitted to specs/villager/reference: fitted bodice with a round white collar, leather waist sash, a wide A-line skirt to just above
# the boots (legs slot empty: skirt weights), gold hem; a white apron sheet on the skirt front.
# (z, rx, ry, y offset): the lower skirt sits 2 cm back and wide enough that the boot shafts' back corners stay
# inside the 10-sided hem
rings = [(0.77, 0.075, 0.07, 0), (0.755, 0.15, 0.12, 0), (0.72, 0.195, 0.145, 0), (0.62, 0.195, 0.15, 0),
         (0.52, 0.175, 0.14, 0), (0.48, 0.19, 0.15, 0.003), (0.40, 0.245, 0.195, 0.008), (0.30, 0.29, 0.245, 0.014),
         (0.235, 0.31, 0.27, 0.016), (0.19, 0.318, 0.278, 0.016)]
P.loft([P.ring((0, dy, z), rx, ry, n=10) for z, rx, ry, dy in rings],
       ["secondary", "primary", "primary", "primary", "leather", "primary", "primary", "primary", "accent"],
       cap_roles=("secondary", "dark"))
def size(z):
    for (z1, a1, b1, d1), (z0, a0, b0, d0) in zip(rings, rings[1:]):
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0)
            return a0 + (a1 - a0) * t, b0 + (b1 - b0) * t, d0 + (d1 - d0) * t
    return rings[0][1:] if z > rings[0][0] else rings[-1][1:]
rows = []
for z in (0.47, 0.39, 0.31, 0.25):
    rx, ry, dy = size(z)
    rows.append([Vector(((rx + 0.012) * math.sin(math.radians(a)), -(ry + 0.012) * math.cos(math.radians(a)) + dy, z))
                 for a in (-50, -30, -10, 10, 30, 50)])
P.shell(rows, 0.008, "secondary")
# round white collar lying on the shoulders (Peter-Pan style): a cyclic sheet from the neck out over the bodice,
# its outer edge dropping into two rounded points either side of the front
def on(th, z, out):
    rx, ry, dy = size(z)
    return Vector(((rx + out) * math.sin(th), -(ry + out) * math.cos(th) + dy, z))
cols = [math.radians(360 * k / 16) for k in range(16)]
bump = lambda t: math.exp(-((abs(math.degrees(t) if math.degrees(t) <= 180 else 360 - math.degrees(t)) - 28) / 22) ** 2)
P.shell([[on(t, 0.772, 0.012) for t in cols], [on(t, 0.745, 0.016) for t in cols],
         [on(t, 0.7 - 0.04 * bump(t), 0.02) for t in cols]], 0.012, "secondary", cyclic=True)
