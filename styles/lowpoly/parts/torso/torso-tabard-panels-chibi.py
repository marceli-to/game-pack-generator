# Shieldbearer body (lowpoly chibi), fitted to specs/shieldbearer/reference: a dark grey padded body (12 sides)
# that continues as a skirt to the hem under the tabard (it shows at the sides and in the front slit); a tabard as
# two panels, front and back, in the team colour (`primary`) with dark edges, the front panel split from the belt
# down; a thick brown belt with a square steel buckle and prong; a dark collar round the neck.
# Legs are a separate part.
N = 12
BODY = [(0.775, 0.085, 0.08), (0.76, 0.165, 0.13), (0.725, 0.21, 0.158), (0.665, 0.218, 0.164),
        (0.6, 0.21, 0.16), (0.53, 0.198, 0.154), (0.45, 0.204, 0.16), (0.38, 0.214, 0.168), (0.3, 0.228, 0.18),
        (0.245, 0.236, 0.186)]
def rad(z):
    for (z0, x0, y0), (z1, x1, y1) in zip(BODY, BODY[1:]):
        if z1 <= z <= z0:
            t = (z0 - z) / (z0 - z1)
            return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
    return BODY[-1][1:] if z < BODY[-1][0] else BODY[0][1:]
def on(z, a, out=0.0):
    """point on the body at height z, angle a (deg, 0 = front, + towards the wearer's left), pushed `out`"""
    rx, ry = rad(z)
    t = math.radians(a)
    return Vector(((rx + out) * math.sin(t), -(ry + out) * math.cos(t), z))
P.loft([[on(z, 360 * k / N) for k in range(N)] for z, _, _ in BODY], "dark", cap_roles=("dark", "dark"))
# tabard panels, 1.4 cm out from the body, each 1.2 cm thick with dark edges
T = 0.014
up = [0.745, 0.7, 0.62, 0.54, 0.44]
P.shell([[on(z, -62 + 124 * k / 6, T) for k in range(7)] for z in up], 0.012, "primary", edge_role="dark")
low = [(0.46, 2.0), (0.38, 4.0), (0.3, 7.0), (0.25, 9.0)]
for s in (1, -1):
    P.shell([[on(z, s * (g + (64 - g) * k / 3), T) for k in range(4)][::s] for z, g in low], 0.012, "primary",
            edge_role="dark")
P.shell([[on(z, 118 + 124 * k / 6, T) for k in range(7)] for z in up + [0.36, 0.25]], 0.012, "primary",
        edge_role="dark")
# belt: thick, bevelled top and bottom, over the tabard
def bring(z, out):
    return [on(z, 360 * k / N, out) for k in range(N)]
P.loft([bring(0.448, 0.028), bring(0.456, 0.036), bring(0.522, 0.036), bring(0.53, 0.028)], "leather",
       cap_roles=("leather", "leather"))
# buckle: a square steel frame on the belt front with a prong across it
yb = -rad(0.49)[1] - 0.04
zb, hw, hh, ch = 0.49, 0.046, 0.042, 0.01
frame = [(hw - ch, -hh), (hw, -hh + ch), (hw, hh - ch), (hw - ch, hh), (-hw + ch, hh), (-hw, hh - ch),
         (-hw, -hh + ch), (-hw + ch, -hh)]
P.sweep([Vector((x, yb, zb + z)) for x, z in frame], [(-0.004, -0.009), (0.012, -0.009), (0.012, 0.009),
        (-0.004, 0.009)][::-1], "metal", [Vector((0, -1, 0))] * 8, cyclic=True)
P.rbox((-0.012, yb - 0.012, zb - 0.008), (0.03, yb + 0.004, zb + 0.008), "metal", r=0.004, bevel=0, seg=1, axis="y")
# dark collar round the neck
P.loft([P.ring((0, -0.004, 0.74), 0.11, 0.1, n=10), P.ring((0, -0.004, 0.805), 0.105, 0.095, n=10)], "dark")
