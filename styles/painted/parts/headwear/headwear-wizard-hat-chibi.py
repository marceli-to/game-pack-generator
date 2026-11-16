# Chibi wizard hat (painted): conical brim sloping down to a wide rim, gold band with a big star, tall cone
# whose tip bends back and to the wearer's left and droops. Whole hat tilted back 12 degrees. One loft:
# horizontal brim/band rings, then rings along a curved spine. 12 sides.
N = 12
def hring(z, r):
    return P.ring((0, 0, z), r, n=N)
REF = Vector((1, -1, 0)).normalized()                     # perpendicular to the bend direction (+X+Y)
def oring(c, t, r):
    t = t.normalized()
    u = (REF - t * REF.dot(t)).normalized()
    w = t.cross(u)
    return [c + r * (math.cos(a) * u + math.sin(a) * w) for a in (math.radians(15 + 30 * k) for k in range(N))]
rings = [hring(1.13, 0.2), hring(0.985, 0.39), hring(1.01, 0.405), hring(1.035, 0.375), hring(1.15, 0.222),
         hring(1.155, 0.232), hring(1.235, 0.224), hring(1.24, 0.21)]
spine = [(Vector((0, 0, 1.24)), None), (Vector((0.01, 0.0, 1.32)), 0.17), (Vector((0.04, -0.005, 1.4)), 0.125),
         (Vector((0.09, -0.01, 1.47)), 0.088), (Vector((0.16, 0.02, 1.52)), 0.062), (Vector((0.25, 0.1, 1.49)), 0.043),
         (Vector((0.32, 0.19, 1.4)), 0.028)]
for k in range(1, len(spine)):
    c, r = spine[k]
    nxt = spine[k + 1][0] if k + 1 < len(spine) else c + (c - spine[k - 1][0])
    rings.append(oring(c, nxt - spine[k - 1][0], r))
rings.append([Vector((0.345, 0.225, 1.32))])
roles = ["primary"] * 4 + ["accent"] * 3 + ["primary"] * (len(rings) - 8)
faces = P.loft(rings, roles)
# star on the band, front, a little to the wearer's left
c = Vector((0.085, -0.222, 1.2))
n = Vector((0.085, -0.222, 0)).normalized()
u = Vector((-n.y, n.x, 0))
w = Vector((0, 0, 1))
pts = [(0.068 if k % 2 == 0 else 0.03, math.radians(90 + 36 * k)) for k in range(10)]
star = lambda d: [c + n * d + u * (r * math.cos(a)) + w * (r * math.sin(a)) for r, a in pts]
faces += P.loft([[c + n * 0.032], star(0.024), star(-0.012), [c - n * 0.012]], "accent")
piv = Vector((0, 0, 1.1))
P.transform(faces, Matrix.Translation(piv) @ Matrix.Rotation(math.radians(-12), 4, "X") @ Matrix.Translation(-piv))
