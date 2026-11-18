# Cuffed beanie (tinfox, hero-m; player 3, specs/player-3/reference): a thick turned-up cuff round the head, a step
# in at its top, a rounded crown; the whole beanie tilted back 12 deg (cuff bottom ~1.71 at the brow, ~1.635 at the
# back), so the short hair shows at the back and the ears below the cuff. Suit colour (`primary`), 16 sides.
def ring(z, sx, f, b, r=0.06):
    return P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=3)
rows = [(1.678, 0.13, -0.145, 0.162), (1.672, 0.153, -0.168, 0.187), (1.69, 0.157, -0.172, 0.191),
        (1.75, 0.157, -0.172, 0.191), (1.758, 0.152, -0.167, 0.186), (1.765, 0.142, -0.157, 0.176),
        (1.8, 0.134, -0.148, 0.168), (1.828, 0.11, -0.122, 0.142), (1.848, 0.066, -0.075, 0.092)]
faces = P.loft([ring(*r) for r in rows] + [[Vector((0, 0.008, 1.856))]], "primary")
piv = Vector((0, 0.01, 1.7))
P.transform(faces, Matrix.Translation(piv) @ Matrix.Rotation(math.radians(-12), 4, "X") @ Matrix.Translation(-piv))
