# Plain belt (tinfox, hero-m): the guard's belt band without pouches or buckle, role leather (the dummy's brown).
def ring(z, sx, f, b, r):
    return P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=2)
P.loft([ring(z, sx, f, b, r) for z, sx, f, b, r in
        ((0.925, 0.2, -0.152, 0.15, 0.075), (0.93, 0.207, -0.158, 0.157, 0.078), (0.995, 0.207, -0.158, 0.157, 0.078),
         (1.0, 0.2, -0.152, 0.15, 0.075))], "leather")
