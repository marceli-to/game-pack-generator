# Utility belt (tinfox, hero-f), for specs/worker/reference: a broad dark belt round the overalls' waist, a big
# square silver buckle, a tall pouch either side of the front with a flap and a grey snap.
def ring(z, sx, f, b, r):
    return P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=2)
P.loft([ring(z, sx, f, b, r) for z, sx, f, b, r in
        ((0.9, 0.17, -0.143, 0.112, 0.07), (0.905, 0.178, -0.15, 0.119, 0.073), (0.965, 0.178, -0.151, 0.12, 0.073),
         (0.97, 0.17, -0.144, 0.113, 0.07))], "dark")
P.rbox((-0.05, -0.17, 0.895), (0.05, -0.145, 0.975), "metal", r=0.008, bevel=0, seg=1, axis="y")
P.rbox((-0.03, -0.174, 0.913), (0.03, -0.165, 0.957), "dark", r=0.0, bevel=0, seg=1, axis="y")
# pouches at the front corners of the waist, turned to face out; high on the belt and well to the side, so a
# lifted thigh passes under/in front of them (first try hung to 0.845 m and cut 8 cm into the thigh in walk/run)
pf = []
pf += P.rbox((-0.05, -0.032, -0.05), (0.05, 0.032, 0.05), "dark", r=0.012, bevel=0, seg=1)
pf += P.rbox((-0.055, -0.037, 0.025), (0.055, 0.037, 0.068), "dark", r=0.01, bevel=0, seg=1)   # flap
pf += P.rbox((-0.015, -0.043, 0.005), (0.015, -0.033, 0.035), "metal", r=0.0, bevel=0, seg=1)   # snap
P.transform(pf, Matrix.Translation((0.168, -0.098, 0.93)) @ Matrix.Rotation(math.radians(52), 4, "Z"))
P.mirror_x(pf)
