# Wizard hat (lowpoly): 10-sided conical brim, gold band with a big star, cone whose tip bends back and to the
# wearer's left and droops; tilted back 12 degrees. One loft (brim/band rings, then rings along a curved spine).
N = 10
def hring(z, r):
    return P.ring((0, 0, z), r, n=N)
REF = Vector((1, -1, 0)).normalized()
def oring(c, t, r):
    t = t.normalized()
    u = (REF - t * REF.dot(t)).normalized()
    w = t.cross(u)
    return [c + r * (math.cos(a) * u + math.sin(a) * w) for a in (math.radians(18 + 36 * k) for k in range(N))]
rings = [hring(1.13, 0.2), hring(0.985, 0.39), hring(1.01, 0.405), hring(1.035, 0.375), hring(1.15, 0.222),
         hring(1.155, 0.234), hring(1.235, 0.226), hring(1.24, 0.21)]
spine = [(Vector((0, 0, 1.24)), None), (Vector((0.01, 0.0, 1.33)), 0.165), (Vector((0.05, -0.005, 1.43)), 0.11),
         (Vector((0.13, 0.01, 1.51)), 0.07), (Vector((0.24, 0.09, 1.5)), 0.045), (Vector((0.32, 0.19, 1.4)), 0.028)]
for k in range(1, len(spine)):
    c, r = spine[k]
    nxt = spine[k + 1][0] if k + 1 < len(spine) else c + (c - spine[k - 1][0])
    rings.append(oring(c, nxt - spine[k - 1][0], r))
rings.append([Vector((0.345, 0.225, 1.32))])
faces = P.loft(rings, ["primary"] * 4 + ["accent"] * 3 + ["primary"] * (len(rings) - 8))
c = Vector((0.085, -0.224, 1.2))
n = Vector((0.085, -0.224, 0)).normalized()
u = Vector((-n.y, n.x, 0))
w = Vector((0, 0, 1))
pts = [(0.07 if k % 2 == 0 else 0.032, math.radians(90 + 36 * k)) for k in range(10)]
star = lambda d: [c + n * d + u * (r * math.cos(a)) + w * (r * math.sin(a)) for r, a in pts]
faces += P.loft([[c + n * 0.032], star(0.024), star(-0.012), [c - n * 0.012]], "accent")
piv = Vector((0, 0, 1.1))
P.transform(faces, Matrix.Translation(piv) @ Matrix.Rotation(math.radians(-12), 4, "X") @ Matrix.Translation(-piv))
