"""v33: College of Science - corrections from the satellite (Google Maps, 2026-10-17) on top of v32 (ku_science.py).

  * Central building: NOT a round pavilion. From above it is a triangular ring with rounded corners wrapped around a
    green courtyard; the apex points south and meets the south building (the "Physics" label sits there), the long top
    edge faces the north blocks ("Department of Biological Sciences", "Guidance"). Its outer faces are the stepped,
    curved white bands of photo 11. Here the ring wraps the existing garden walk (the courtyard) on columns, and its
    first floor is a walkable glazed loop joined to the Red Corridor (user memory) where they cross.
  * Pick sits inside the triangle near its north-east corner; Toby's Estate (KU) is east of the south building.
  * The v32 side wings become real wings: hall, doors, stairs and a first-floor corridor joined to the main building.
Everything is ~1:2.5 horizontally and ~true vertically (1 stud ~ 0.3 m, 16-stud floors, 10-stud doors).
"""
import math

import genmap as G
import genmap5 as C5
import genmap3 as C3
import ku_science as K

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign

# ---------------------------------------------------------------- central ring (triangle with rounded corners)
# vertices in campus coordinates (garden between south back z -30 and north front z 130)
TRI = [(0.0, -24.0), (86.0, 100.0), (-86.0, 100.0)]   # south apex, north-east, north-west (20-stud galleria to the north)
FILLET = 16.0   # small enough that the corners still read as a triangle from the air
RING_W = 20.0           # depth of the ring building (centreline +- 10)
L1 = 24.0               # first floor = the Red Corridor floor level (its top is 24.4)
RED_X = (-50.0, -30.0)  # Red Corridor (genmap5.outdoors) x range
PICK_AT = (30.0, 72.0)   # Pick kiosk centre (v34 overrides: the smaller triangle)
GARDEN_R = 25.0          # ring columns keep this far from the garden walk (v34: 12)


def _ring_path(step=6.0):
    """centreline of the triangle with filleted corners: list of (x, z, yaw_deg) every ~step studs"""
    n = len(TRI)
    corners = []
    for i in range(n):
        p0, p1, p2 = TRI[i - 1], TRI[i], TRI[(i + 1) % n]
        a = (p0[0] - p1[0], p0[1] - p1[1])
        b = (p2[0] - p1[0], p2[1] - p1[1])
        la, lb = math.hypot(*a), math.hypot(*b)
        ua, ub = (a[0] / la, a[1] / la), (b[0] / lb, b[1] / lb)
        cosang = ua[0] * ub[0] + ua[1] * ub[1]
        ang = math.acos(max(-1, min(1, cosang)))
        t = FILLET / math.tan(ang / 2)
        sa = (p1[0] + ua[0] * t, p1[1] + ua[1] * t)
        sb = (p1[0] + ub[0] * t, p1[1] + ub[1] * t)
        bis = (ua[0] + ub[0], ua[1] + ub[1])
        lbis = math.hypot(*bis)
        d = FILLET / math.sin(ang / 2)
        c = (p1[0] + bis[0] / lbis * d, p1[1] + bis[1] / lbis * d)
        corners.append((sa, sb, c))
    pts = []
    for i in range(n):
        sa, sb, c = corners[i]
        a0 = math.atan2(sa[1] - c[1], sa[0] - c[0])
        a1 = math.atan2(sb[1] - c[1], sb[0] - c[0])
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        m = max(2, int(abs(da) * FILLET / step))
        for k in range(m):
            a = a0 + da * k / m
            pts.append((c[0] + FILLET * math.cos(a), c[1] + FILLET * math.sin(a)))
        nxt = corners[(i + 1) % n][0]
        L = math.hypot(nxt[0] - sb[0], nxt[1] - sb[1])
        m = max(1, int(L / step))
        for k in range(m):
            pts.append((sb[0] + (nxt[0] - sb[0]) * k / m, sb[1] + (nxt[1] - sb[1]) * k / m))
    out = []
    for i, p in enumerate(pts):
        q = pts[(i + 1) % len(pts)]
        out.append((p, q))
    return out


def ring_distance(x, z):
    """distance from (x, z) to the ring centreline (for keeping trees and lamps out of it)"""
    best = 1e9
    for (p, q) in _ring_path(8.0):
        dx, dz = q[0] - p[0], q[1] - p[1]
        L2 = dx * dx + dz * dz or 1
        t = max(0, min(1, ((x - p[0]) * dx + (z - p[1]) * dz) / L2))
        best = min(best, math.hypot(x - (p[0] + dx * t), z - (p[1] + dz * t)))
    return best


def _centroid():
    return (sum(p[0] for p in TRI) / 3, sum(p[1] for p in TRI) / 3)


def red_crossings():
    """z values where the ring centreline crosses the Red Corridor (x ~ -40): the west side and the top edge"""
    (x0, z0), (x1, z1) = TRI[0], TRI[2]
    return [z0 + (z1 - z0) * ((-40 - x0) / (x1 - x0)), TRI[2][1]]


def red_crossing_z():
    return red_crossings()[0]


def crossings_at(x):
    """z values where the ring (west side + top edge) passes over the corridor line at this x"""
    (x0, z0), (x1, z1) = TRI[0], TRI[2]
    return [z0 + (z1 - z0) * ((x - x0) / (x1 - x0)), TRI[2][1]]


_garden_pts = []


def near_garden_path(x, z, r=25.0):
    """the winding garden walk (genmap5.winding_garden) has benches, lamps and statues within ~24 studs of it"""
    if not _garden_pts:
        ctrl = [(-40, -30), (-62, 4), (-34, 30), (14, 40), (58, 58), (74, 84), (44, 108), (10, 118), (8, 130)]
        _garden_pts.extend(C5._catmull(ctrl, 12))
    return any(math.hypot(x - px, z - pz) < r for px, pz in _garden_pts)


def central_ring():
    cx, cz = _centroid()
    zcs = red_crossings()
    with G.Group("CentralRing"):
        for i, ((px, pz), (qx, qz)) in enumerate(_ring_path(6.0)):
            mx, mz = (px + qx) / 2, (pz + qz) / 2
            L = math.hypot(qx - px, qz - pz) + 0.6
            yaw = math.degrees(math.atan2(qx - px, qz - pz))
            # outward normal (away from the courtyard centroid)
            nx, nz = math.cos(math.radians(yaw)), -math.sin(math.radians(yaw))
            if (mx - cx) * nx + (mz - cz) * nz < 0:
                nx, nz = -nx, -nz
            on_red = RED_X[0] - 6 <= mx <= RED_X[1] + 6 and any(abs(mz - zc) < 16 for zc in zcs)

            def at(off, y):
                return (mx + nx * off, y, mz + nz * off)

            # first floor: walkable glazed loop (the floor is skipped where the Red Corridor already is)
            box("RingFloor", (RING_W, 1.4, L), at(0, L1 - 0.5), (232, 228, 220), "Marble", rot=(0, yaw, 0))
            if not on_red:   # no glass across the Red Corridor's path
                box("RingGlassIn", (0.4, 11.6, L), at(-RING_W / 2 + 0.3, L1 + 6.2), (160, 205, 215), "Glass",
                    rot=(0, yaw, 0), transp=0.5)
                box("RingRail", (0.4, 3.4, L), at(RING_W / 2 - 0.3, L1 + 2.1), (180, 210, 220), "Glass", rot=(0, yaw, 0),
                    transp=0.5)
            # stepped curved bands: each level steps back toward the courtyard (the terraces of photo 11)
            for lvl, (y, back) in enumerate(((L1 + 12, 2.0), (L1 + 22, 5.0), (L1 + 32, 8.0))):
                w = RING_W - back
                box("RingSlab", (w, 1.2, L), at(-back / 2, y), (238, 236, 230), "Concrete", rot=(0, yaw, 0))
                box("RingBand", (0.8, 2.4, L), at(w / 2 - back / 2, y + 0.6), (248, 246, 240), "SmoothPlastic",
                    rot=(0, yaw, 0), collide=False)
                box("RingWall", (0.4, 9, L), at(w / 2 - back / 2 - 3, y - 4.8), (150, 196, 210), "Glass", rot=(0, yaw, 0),
                    transp=0.45, collide=False)
            box("RingRoofTurf", (RING_W - 10, 0.3, L), at(-5, L1 + 32.75), (80, 136, 78), "Grass", rot=(0, yaw, 0),
                collide=False)
            # columns on both edges every third segment; none on the Red Corridor
            if i % 3 == 0 and not on_red:
                for off in (-RING_W / 2 + 1.5, RING_W / 2 - 1.5):
                    px_, pz_ = mx + nx * off, mz + nz * off
                    if near_garden_path(px_, pz_, GARDEN_R) or (-106 < px_ < -77 and 56 < pz_ < 84):   # + the glass pavilion
                        continue   # benches / lamps / statues of the garden walk stand there (the slab cantilevers)
                    vcyl("RingColumn", px_, 0, L1 - 1.2, pz_, 2.4, K.COLUMN_WHITE, "Concrete")
        sign("RingSign", "الدور الأول متصل بالممر الأحمر", (0.0, L1 + 12.6, TRI[1][1] + RING_W / 2 - 1.6), (30, 2.6, 0.4), "Back",
             bg=(60, 70, 80))


# ---------------------------------------------------------------- enterable wings
WING_ZF, WING_ZB = K.FRONT_Z, K.FRONT_Z + 34      # -178 .. -144
WING_GLASS = K.FRONT_Z + 10                         # ground glass line (-168)


def wings():
    with G.Group("SouthWingsV33"):
        # west wing stops at x -110: the first desert-garden bed (campus9) starts at -112
        for (a, b, name) in ((K.X1 + 0.8, 150.0, "الجناح الشرقي | East Wing"), (K.X0 - 0.8, -110.0, "الجناح الغربي | West Wing")):
            s_ = 1 if b > 0 else -1
            lo, hi = min(a, b), max(a, b)
            cx0 = cx1 = b + s_ * 100   # v33: no stair core in the wings (first floor is reached from the main building)
            # floors
            C5.rect("WingFloor", lo, hi, 0, 0.05, WING_GLASS, WING_ZB, C5.TERRAZZO, "Marble", collide=False)
            C5.floor_slab(C5.Y_1, lo, hi, WING_ZF, WING_ZB, [], C5.TERRAZZO, "Marble", name="WingL1")
            C5.floor_slab(C5.Y_2, lo, hi, WING_ZF, WING_ZB, [], (228, 224, 214), "Concrete", name="WingL2")
            # ground: glass front with a door in the middle, solid back with a ribbon window, solid outer end
            mid = (lo + hi) / 2
            C5.glass_x(lo, hi, WING_GLASS, 0, C5.Y_1, 8.0, gaps=[(mid - 6, mid + 6)])
            C5.rect("WingBack", lo, hi, 0, C5.Y_2, WING_ZB, WING_ZB + 1, C5.WHITE, "Concrete")
            C5.rect("WingBackWin", lo + 2, hi - 2, 8, 14, WING_ZB + 1, WING_ZB + 1.2, C5.GLASS_DK, "Glass", transp=0.3,
                    collide=False)
            C5.rect("WingEnd", b - (1 if s_ > 0 else 0), b + (0 if s_ > 0 else 1), 0, C5.Y_4, WING_ZF + 2, WING_ZB + 1,
                    K.TERRACOTTA, "Concrete")
            # first floor: corridor behind the screen, glass to the front
            C5.rect("WingL1Glass", lo, hi, C5.Y_1, C5.Y_2, WING_ZF + 1.6, WING_ZF + 2.0, K.GLASS_BLUE, "Glass", transp=0.4)
            # mass above
            C5.rect("WingMass", lo, hi, C5.Y_2, C5.Y_4, WING_ZF + 2, WING_ZB + 1, K.TERRACOTTA, "Concrete")
            C5.rect("WingSoffit", lo, hi, C5.Y_1 - 1.2, C5.Y_1, WING_ZF, WING_GLASS, (226, 218, 200), "Concrete",
                    collide=False)
            sign("WingStairSign", "الدور الأول: من داخل المبنى الرئيسي ←" if s_ > 0 else "→ الدور الأول: من داخل المبنى الرئيسي",
                 (mid, 18, WING_GLASS + 0.8), (18, 2.2, 0.3), "Back", bg=(40, 60, 70))
            # colonnade, screen, crown
            x = a + s_ * 9
            while (x - b) * s_ < -4:
                if abs(x - mid) > 8:   # never a column right in front of the wing door
                    C5.column(x, K.FRONT_Z + 2, 0, C5.Y_1, 5.0, K.COLUMN_WHITE)
                x += s_ * 18
            C5.rect("WingScreen", lo, hi, C5.Y_1, C5.Y_4, K.SCREEN_Z - 0.3, K.SCREEN_Z + 0.3, K.BRONZE, "Metal", collide=False)
            K._cutouts_x(lo, hi, C5.Y_1 + 1, C5.Y_4 - 1, K.SCREEN_Z - 0.4)
            ex0, ex1 = (b - 0.6, b) if s_ > 0 else (b, b + 0.6)
            C5.rect("WingScreenEnd", ex0, ex1, C5.Y_1, C5.Y_4, K.SCREEN_Z, WING_ZF + 2, K.BRONZE, "Metal", collide=False)
            K.mansard(lo, hi, K.SCREEN_Z, C5.Y_4)
            # inside: benches, notice board, lights, classroom fronts upstairs (no room numbers: none are sourced)
            for k in range(3):
                bx = lo + 8 + k * 10 if s_ < 0 else lo + 16 + k * 14
                if (cx0 - 3 < bx < cx1 + 3) or bx - 4.5 < lo or bx + 4.5 > hi:
                    continue
                C3.bench(bx, 0, WING_ZB - 4, along="x")
            C5.rect("NoticeBoard", mid - 6, mid + 6, 5, 11, WING_ZB - 0.2, WING_ZB, (196, 160, 110), "Wood", collide=False,
                    text=dict(face="Front", text="لوحة الإعلانات\nNotice Board", color=(60, 40, 20), bg=(236, 224, 196),
                              bg_t=0.0))
            for x2 in range(int(lo) + 8, int(hi) - 6, 14):
                C5.light_panel(x2, C5.Y_1 - 0.4, (WING_GLASS + WING_ZB) / 2, 8, 4, 1.2, 30)
                C5.light_panel(x2, C5.Y_2 - 0.4, (WING_ZF + WING_ZB) / 2, 8, 4, 1.2, 30)
            for x2 in range(int(lo) + 4, int(hi) - 8, 12):
                if cx0 - 2 < x2 < cx1 + 2:
                    continue
                C5.rect("ClassDoor", x2, x2 + 5, C5.Y_1, C5.Y_1 + 10, WING_ZB - 0.3, WING_ZB, (150, 108, 72), "WoodPlanks",
                        collide=False)
                C5.rect("ClassSign", x2, x2 + 5, C5.Y_1 + 10.6, C5.Y_1 + 12.4, WING_ZB - 0.35, WING_ZB - 0.3, (40, 60, 70),
                        "SmoothPlastic", collide=False, text=dict(face="Front", text="قاعة دراسية", color=(255, 255, 255),
                                                                     bg=(40, 60, 70), bg_t=0.0))
            sign("WingName", name, (mid, 20, WING_GLASS - 0.4), (min(24, hi - lo - 4), 2.6, 0.3), "Front", bg=(46, 60, 70))


# ---------------------------------------------------------------- screen irregularity (v32 looked too regular)
def screen_detail():
    """fold ridges between the facets, denser cut-out clusters toward the entrance bay, a few quasicrystal stars"""
    z = K.SCREEN_Z - 0.45
    with G.Group("ScreenDetail"):
        for (a, b) in ((K.X0 + 6, -K.CENTER), (K.CENTER, K.X1 - 6)):
            n = 3
            for k in range(1, n):
                x = a + (b - a) * k / n
                C5.rect("ScreenRidge", x - 0.35, x + 0.35, C5.Y_1, K.Y_TOP, z - 0.4, z + 0.2, K.BRONZE_DK, "Metal",
                        collide=False)
            for k in range(6):
                fx = a + (b - a) * (0.15 + 0.14 * k)
                fy = C5.Y_1 + 10 + ((k * 37) % 5) * 10
                for q in range(5):
                    ang = q * 2 * math.pi / 5
                    box("ScreenStar", (1.4, 1.4, 0.2), (fx + 2.2 * math.cos(ang), fy + 2.2 * math.sin(ang), z - 0.05),
                        K.CUT, "SmoothPlastic", rot=(0, 0, 36 + q * 72), collide=False, shadow=False)
                box("ScreenStarCore", (1.8, 1.8, 0.2), (fx, fy, z - 0.05), K.CUT, "SmoothPlastic", rot=(0, 0, 45),
                    collide=False, shadow=False)


# ---------------------------------------------------------------- stairs: back-lit laser-cut stainless screens (NBBJ)
def stair_screens():
    with G.Group("StairScreens"):
        spots = [(-69.5, -48.0, 1, C5.Y_ROOF), (69.5, -48.0, -1, C5.Y_ROOF)]          # south cores (inner faces, from L1 up)
        oz = C5.NB_SHIFT
        spots += [(-59.5, 134.0 + oz, 1, 64.0), (79.5, 134.0 + oz, -1, 64.0)]          # north cores
        for (x, z, face, top) in spots:
            y0 = C5.Y_1 + 0.5 if z < 0 else 0.5   # south: the cafeteria counters stand in front of the cores on G
            C5.rect("StairScreen", x - 0.2, x + 0.2, y0, top - 2, z - 9, z + 9, (255, 236, 200), "Neon", transp=0.25,
                    collide=False)
            for j in range(int((top - 4 - y0) / 4)):
                for i in range(4):
                    box("StairLattice", (0.2, 1.4, 1.4), (x + face * 0.25, y0 + 2 + j * 4, z - 6 + i * 4 + (2 if j % 2 else 0)),
                        (120, 124, 130), "Metal", rot=(45, 0, 0), collide=False, shadow=False)


# ---------------------------------------------------------------- real names from the campus map
def place_names():
    with G.Group("PlaceNames"):
        oz = C5.NB_SHIFT
        sign("DeptBio", "قسم العلوم البيولوجية | Department of Biological Sciences", (-20, 18, 20 + oz - 0.6), (40, 3, 0.4),
             "Front", bg=(24, 80, 56))
        sign("Guidance", "التوجيه والإرشاد | Student Guidance", (-60, 9, 20 + oz - 0.6), (18, 2.4, 0.4), "Front", bg=(60, 70, 90))
        sign("DeptPhysics", "قسم الفيزياء | Department of Physics", (40, 16, -29.4), (30, 3, 0.4), "Back", bg=(40, 50, 90))


# ---------------------------------------------------------------- trees: natural variety instead of one repeated tree
TREE_KINDS = ("round", "palm", "sidr", "cypress", "round")


def varied_tree(x, z, s=1.0):
    h = math.sin(x * 12.9898 + z * 78.233) * 43758.5453
    h -= math.floor(h)
    kind = TREE_KINDS[int(h * len(TREE_KINDS)) % len(TREE_KINDS)]
    s *= 0.85 + 0.3 * ((h * 7) % 1)
    green = (int(70 + 30 * h), int(128 + 30 * ((h * 3) % 1)), int(70 + 20 * ((h * 5) % 1)))
    if kind == "palm":   # date palm, drawn without the shared RNG (genmap5.palm would shift every later placement)
        hgt = 13 + 6 * s
        vcyl("PalmTrunk", x, 0, hgt, z, 1.5, (150, 118, 82), "Wood", collide=False)
        for k in range(8):
            yaw = k * 45.0 + 20 * h
            pitch = 22 + 8 * ((h * (k + 3)) % 1)
            Lf = 8.0
            dx = math.sin(math.radians(yaw)) * (Lf / 2) * math.cos(math.radians(pitch))
            dz = math.cos(math.radians(yaw)) * (Lf / 2) * math.cos(math.radians(pitch))
            dy = -(Lf / 2) * math.sin(math.radians(pitch))
            box("Frond", (2.4, 0.25, Lf), (x + dx, hgt + dy, z + dz), (82, 150, 78), "Grass", collide=False,
                rot=(pitch, yaw, 0))
    elif kind == "sidr":       # Ziziphus / acacia: low wide flat crown on a short crooked trunk
        vcyl("Trunk", x, 0, 6 * s, z, 1.3 * s, (104, 78, 52), "Wood", collide=False)
        disc("SidrCrown", x, 7.5 * s, z, 15 * s, 3 * s, (green[0] + 10, green[1] - 6, green[2]), "Grass", collide=False)
        disc("SidrCrownTop", x + 1.5, 9 * s, z - 1, 9 * s, 2 * s, green, "Grass", collide=False)
    elif kind == "cypress":
        vcyl("Trunk", x, 0, 3 * s, z, 0.9 * s, (96, 72, 50), "Wood", collide=False)
        for k in range(4):
            ball("CypressCrown", x, 4 * s + k * 3 * s, z, (6 - k * 1.1) * s, (40, 96, 60), "Grass", collide=False)
    else:
        C3.tree(x, 0.0, z, s, green)


def install():
    """hooks on top of ku_science.install(): ring keeps clear of trees, Red Corridor glass opens at the ring,
    the sail plaza shifts east of the ring, Pick moves into the courtyard, Toby's moves east of the south building,
    main building sides open into the wings."""
    orig_rect, orig_tree, orig_box, orig_vcyl, orig_sign = C5.rect, C5.tree, C5.box, C5.vcyl, C5.sign
    orig_table, orig_glass_z, orig_pwz = C5.table_set, C5.glass_z, C5.panel_wall_z
    zcs = red_crossings()
    SAIL_DX, SAIL_DZ = 0.0, -50.0   # the sails move south inside the same open area (east of the ring, clear of the red block)
    SAIL_NAMES = ("SailA", "SailB", "SailC", "Mast", "SailSign")
    # kiosk moves: (bbox x0, x1, z0, z1) -> (dx, dz)
    MOVES = [((94.0, 120.0, -116.0, -92.0), (PICK_AT[0] - 106.0, PICK_AT[1] - (-100.0))),     # Pick -> courtyard NE (inside the ring)
             ((98.0, 122.0, -176.0, -152.0), (0.0, 48.0))]                         # Toby's -> east, clear of the wing

    def moved(x, z):
        for (x0, x1, z0, z1), (dx, dz) in MOVES:
            if x0 <= x <= x1 and z0 <= z <= z1:
                return dx, dz
        return 0.0, 0.0

    def rect(name, x0, x1, y0, y1, z0, z1, colour, mat="SmoothPlastic", **kw):
        if C5._off[2] == 0.0 and name in ("Base", "Roof", "Window") and y0 < 14:
            dx, dz = moved((x0 + x1) / 2, (z0 + z1) / 2)
            x0, x1, z0, z1 = x0 + dx, x1 + dx, z0 + dz, z1 + dz
        if name == "BridgeGlass":
            # the ring's first floor crosses the Red Corridor twice: open its side glass at both crossings
            cuts = sorted(crossings_at((x0 + x1) / 2))
            a = z0
            for zc in cuts:
                orig_rect(name, x0, x1, y0, y1, a, zc - 20, colour, mat, **kw)
                a = zc + 20
            return orig_rect(name, x0, x1, y0, y1, a, z1, colour, mat, **kw)
        return orig_rect(name, x0, x1, y0, y1, z0, z1, colour, mat, **kw)

    def tree(x, z, s=1.0):
        if C5._off[2] == 0.0 and -30 < z < 130 and ring_distance(x, z) < 18:
            return None
        if C5._off[2] == 0.0:
            return varied_tree(x, z, s)
        return orig_tree(x, z, s)

    def boxh(name, size, pos, *a, **kw):
        if name in SAIL_NAMES and C5._off[2] == 0.0:
            pos = (pos[0] + SAIL_DX, pos[1], pos[2] + SAIL_DZ)
        if name == "Mull" and C5._off[2] == 0.0 and RED_X[0] - 1 <= pos[0] <= RED_X[1] + 1 and any(abs(pos[2] - zc) < 20
                                                                                                   for zc in crossings_at(pos[0])):
            return None
        return orig_box(name, size, pos, *a, **kw)

    def vcylh(name, cx, y0, y1, cz, *a, **kw):
        if name in SAIL_NAMES and C5._off[2] == 0.0:
            cx += SAIL_DX
            cz += SAIL_DZ
        if name == "BridgeCol" and C5._off[2] == 0.0 and any(abs(cz - zc) < 17 for zc in crossings_at(cx)):
            return None   # the ring's columns carry the corridor there
        return orig_vcyl(name, cx, y0, y1, cz, *a, **kw)

    def signh(name, text, pos, *a, **kw):
        if name in SAIL_NAMES and C5._off[2] == 0.0:
            pos = (pos[0] + SAIL_DX, pos[1], pos[2] + SAIL_DZ)
        if name == "CafeSign" and C5._off[2] == 0.0 and pos[1] < 14:
            dx, dz = moved(pos[0], pos[2] + 0.3 + 6)
            pos = (pos[0] + dx, pos[1], pos[2] + dz)
        return orig_sign(name, text, pos, *a, **kw)

    def table(x, z, y, *a, **kw):
        if C5._off[2] == 0.0 and y == 0:
            dx, dz = moved(x, z + 6)
            x, z = x + dx, z + dz
        return orig_table(x, z, y, *a, **kw)

    def glass_z(z0, z1, x, y0, y1, step=8.0, gaps=(), tr=0.55, col=C5.GLASS):
        if C5._off[2] == 0.0 and abs(abs(x) - 90) < 0.01 and abs(z0 - (-160)) < 0.01:
            gaps = list(gaps) + [(-158.0, -148.0)]   # ground doorway main building <-> wing hall
        return orig_glass_z(z0, z1, x, y0, y1, step, gaps, tr, col)

    def pwz(z0, z1, x, y0, y1, face, ribbons=()):
        if K._in_south[0] and abs(z0 - K.FRONT_Z) < 0.01:
            # side wall with a first-floor doorway into the wing corridor (z -172..-162, y 24..36)
            orig_rect("Cladding", x - 0.8, x + 0.8, y0, y1, z0, -172, C5.PANEL, "Concrete")
            orig_rect("Cladding", x - 0.8, x + 0.8, y0, y1, -162, z1, C5.PANEL, "Concrete")
            orig_rect("Cladding", x - 0.8, x + 0.8, y0 + 12, y1, -172, -162, C5.PANEL, "Concrete")
            return None
        return orig_pwz(z0, z1, x, y0, y1, face, ribbons)

    C5.rect, C5.tree, C5.box, C5.vcyl, C5.sign = rect, tree, boxh, vcylh, signh
    C5.table_set, C5.glass_z, C5.panel_wall_z = table, glass_z, pwz


def build():
    central_ring()
    wings()
    screen_detail()
    stair_screens()
    place_names()
