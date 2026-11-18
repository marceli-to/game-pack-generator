# Belt with a round buckle (tinfox, hero-f; players 2 and 4), from specs/player-2/reference: the hero-m belt sized to
# the suit's waist: a broad dark belt, a small pouch either side of the front, a big round silver buckle.
def ring(z, sx, f, b, r):
    return P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=2)
P.loft([ring(z, sx, f, b, r) for z, sx, f, b, r in
        ((0.92, 0.132, -0.117, 0.104, 0.06), (0.925, 0.14, -0.125, 0.112, 0.064), (0.985, 0.14, -0.125, 0.112, 0.064),
         (0.99, 0.132, -0.117, 0.104, 0.06))], "dark")
pouch = P.rbox((0.085, -0.135, 0.915), (0.14, -0.1, 0.995), "dark", r=0.01, bevel=0, seg=1)
P.mirror_x(pouch)
P.cylinder(Vector((0, -0.12, 0.955)), Vector((0, -0.145, 0.955)), 0.042, n=12, role="metal")
P.cylinder(Vector((0, -0.143, 0.955)), Vector((0, -0.151, 0.955)), 0.03, n=12, role="metal")
