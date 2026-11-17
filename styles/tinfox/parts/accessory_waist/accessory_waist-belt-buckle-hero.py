# Belt with a round buckle (tinfox, hero-m), fitted to specs/guard/reference: a broad belt round the jacket's waist,
# a pouch either side of the front, a big round brass buckle in front (enemies brass; players silver: recolour).
def ring(z, sx, f, b, r):
    return P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=2)
P.loft([ring(z, sx, f, b, r) for z, sx, f, b, r in
        ((0.925, 0.2, -0.152, 0.15, 0.075), (0.93, 0.207, -0.158, 0.157, 0.078), (0.995, 0.207, -0.158, 0.157, 0.078),
         (1.0, 0.2, -0.152, 0.15, 0.075))], "dark")
pouch = P.rbox((0.12, -0.172, 0.91), (0.19, -0.13, 1.015), "dark", r=0.012, bevel=0, seg=1)
P.mirror_x(pouch)
P.cylinder(Vector((0, -0.155, 0.962)), Vector((0, -0.18, 0.962)), 0.05, n=12, role="metal")
P.cylinder(Vector((0, -0.178, 0.962)), Vector((0, -0.186, 0.962)), 0.036, n=12, role="metal")
