# Work overalls, top (tinfox, hero-f), for specs/worker/reference: a teal one-piece suit from a shirt collar (points
# lying on the chest, a V opening) over square shoulders and a chest, a waist under the belt, hips and an
# upside-down V at the crotch (the legs are legs-overalls-hero-f); a raised placket, a big breast pocket with a flap
# in the middle of the chest, a white name patch with a teal wrench on the wearer's left.
def ring(z, sx, f, b, r):
    return P.rrect((0, (f + b) / 2, z), sx, (b - f) / 2, r, seg=3)
body = [(1.4, 0.06, -0.065, 0.058, 0.03), (1.33, 0.068, -0.072, 0.066, 0.033), (1.31, 0.16, -0.125, 0.115, 0.06),
        (1.28, 0.23, -0.165, 0.132, 0.1), (1.2, 0.222, -0.18, 0.138, 0.11), (1.12, 0.188, -0.165, 0.126, 0.08),
        (1.02, 0.162, -0.146, 0.106, 0.068), (0.93, 0.172, -0.14, 0.112, 0.07), (0.83, 0.198, -0.136, 0.134, 0.075),
        (0.77, 0.18, -0.12, 0.12, 0.065)]
rings = [ring(*b) for b in body]
for z, sx in ((0.75, 0.12), (0.735, 0.045)):
    pts = ring(z, sx, -0.1, 0.105, 0.045)
    rings.append([Vector((p.x, p.y, z - 0.025 * max(0.0, 1 - abs(p.x) / sx))) for p in pts])
P.loft(rings, "primary", cap_roles=("dark", "primary"))
# shirt collar: a band round the neck, its points lying on the chest either side of the V
P.loft([ring(1.335, 0.078, -0.082, 0.075, 0.035), ring(1.375, 0.074, -0.077, 0.071, 0.034)], "primary")
for s in (1, -1):
    tri = [Vector((s * 0.008, -0.09, 1.345)), Vector((s * 0.078, -0.06, 1.355)), Vector((s * 0.1, -0.125, 1.3)),
           Vector((s * 0.03, -0.15, 1.27))]
    grid = [tri[:2], tri[3:1:-1]]
    P.shell(grid, 0.012, "primary")
# placket from the V down to the belt
P.loft([P.rect((0, -0.15, 1.28), 0.012, 0.006), P.rect((0, -0.185, 1.2), 0.012, 0.006),
        P.rect((0, -0.17, 1.12), 0.012, 0.006), P.rect((0, -0.15, 1.0), 0.012, 0.006)], "primary")
# breast pocket (middle of the chest) with a flap
P.rbox((-0.085, -0.192, 1.06), (0.085, -0.165, 1.175), "primary", r=0.006, bevel=0, seg=1, axis="y")
P.rbox((-0.092, -0.2, 1.15), (0.092, -0.17, 1.19), "primary", r=0.006, bevel=0, seg=1, axis="y")
# name patch with a wrench (wearer's left chest)
P.rbox((0.06, -0.19, 1.205), (0.155, -0.172, 1.25), "secondary", r=0.004, bevel=0, seg=1, axis="y")
w = P.rbox((0.085, -0.193, 1.222), (0.128, -0.189, 1.232), "primary", r=0.0, bevel=0, seg=1, axis="y")
P.transform(w, Matrix.Translation((0.107, -0.19, 1.227)) @ Matrix.Rotation(math.radians(35), 4, "Y")
            @ Matrix.Translation((-0.107, 0.19, -1.227)))
P.rbox((0.122, -0.194, 1.226), (0.136, -0.189, 1.242), "primary", r=0.0, bevel=0, seg=1, axis="y")
