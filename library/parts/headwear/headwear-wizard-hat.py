# Wizard hat, one shell: brim underside -> curved drooping rim -> cone with a dark band; the tip
# bends progressively backwards (+Y). 12 sides. Tilted back 10 degrees.
N = 12
def ring(z, r, y=0.0):
    return P.ring((0, y, z), r, n=N)
rings = [ring(1.68, 0.225), ring(1.645, 0.32), ring(1.585, 0.41), ring(1.605, 0.415), ring(1.75, 0.228),
         ring(1.84, 0.20, 0.01), ring(1.95, 0.16, 0.025), ring(2.05, 0.112, 0.045), ring(2.15, 0.066, 0.065),
         [Vector((0, 0.09, 2.26))]]
P.loft(rings, ["primary", "primary", "primary", "primary", "dark", "primary", "primary", "primary", "primary"])
c = Vector((0, 0, 1.65))
P.transform(P.bm.faces[:], Matrix.Translation(c) @ Matrix.Rotation(math.radians(-10), 4, "X") @ Matrix.Translation(-c))
