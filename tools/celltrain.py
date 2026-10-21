"""Cell Train: a dedicated station on campus + a big purple cell world with a visible train.

train_station()  -> campus east lawn (station building, platform, parked train used as the ride template)
cell_world()     -> enclosed purple cell interior at CELL_OFFSET with large, well-spaced organelles
"""
import math
import random

import genmap as G
import genmap5 as C5

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign
rect = C5.rect
rng = random.Random(5150)

PURPLE = (120, 64, 176)
DEEP = (58, 28, 96)
PINK = (246, 150, 205)
WHITE = (244, 244, 248)


# ---------------------------------------------------------------- the train (built along +X)
def train(x0, y0, z0, name="TrainTemplate"):
    """locomotive + two open cars; parts named so the client can find the seats"""
    with G.Group(name, "Model"):
        # locomotive
        G.part("Base", (16, 1.2, 7), (x0, y0 + 0.6, z0), (40, 30, 60), "SmoothPlastic")
        box("LocoBody", (12, 6, 6.4), (x0 - 1, y0 + 4.2, z0), PURPLE, "SmoothPlastic")
        box("LocoStripe", (12.1, 0.8, 6.5), (x0 - 1, y0 + 3.0, z0), WHITE, "SmoothPlastic")
        box("Cab", (5, 3.4, 6), (x0 - 4.5, y0 + 8.9, z0), (90, 50, 140), "SmoothPlastic")
        box("CabGlass", (5.2, 2.2, 6.2), (x0 - 4.5, y0 + 9.0, z0), (180, 220, 255), "Glass", transp=0.4)
        ball("Nose", x0 + 6.5, y0 + 4.2, z0, 6.2, PURPLE, "SmoothPlastic")
        ball("Headlight", x0 + 9.2, y0 + 4.8, z0, 1.8, (255, 255, 230), "Neon", light=(2.0, 30, (255, 250, 220)))
        sign("LocoName", "قطار الخلية", (x0 - 1, y0 + 4.6, z0 + 3.25), (10, 1.6, 0.2), "Back", bg=PURPLE)
        sign("LocoName2", "Cell Train", (x0 - 1, y0 + 4.6, z0 - 3.25), (10, 1.6, 0.2), "Front", bg=PURPLE)
        for wx in (-5, 0, 5):
            for wz in (-3.6, 3.6):
                G.part("Wheel", (1.0, 3, 3), (x0 + wx, y0 + 0.9, z0 + wz), (40, 40, 46), "SmoothPlastic", shape="Cylinder",
                       rot=(0, 90, 0))
        # two open passenger cars
        for ci in range(4):  # v29: a longer train (4 cars)
            cx = x0 - 15 - ci * 14
            box("CarBase", (12, 1.2, 7), (cx, y0 + 0.6, z0), (40, 30, 60), "SmoothPlastic")
            box("CarFloor", (12, 0.6, 6.4), (cx, y0 + 1.5, z0), (250, 240, 250), "SmoothPlastic")
            for s_ in (-1, 1):
                box("CarSide", (12, 2.6, 0.5), (cx, y0 + 3.0, z0 + s_ * 3.2), PINK, "SmoothPlastic")
            box("CarEnd", (0.5, 2.6, 6.4), (cx - 6, y0 + 3.0, z0), PINK, "SmoothPlastic")
            for si in range(2):
                box("Seat%d" % (ci * 2 + si + 1), (2.6, 1.2, 5), (cx + 2.5 - si * 5, y0 + 2.4, z0), (90, 60, 150), "Fabric")
                box("SeatBack", (0.6, 2.4, 5), (cx + 1.2 - si * 5, y0 + 3.6, z0), (90, 60, 150), "Fabric")
            for wx in (-3.5, 3.5):
                for wz in (-3.6, 3.6):
                    G.part("Wheel", (1.0, 2.6, 2.6), (cx + wx, y0 + 0.8, z0 + wz), (40, 40, 46), "SmoothPlastic",
                           shape="Cylinder", rot=(0, 90, 0))
            box("Coupler", (2, 0.6, 0.6), (cx + 7, y0 + 1.0, z0), (60, 60, 66), "SmoothPlastic")


# ---------------------------------------------------------------- station on campus
def train_station():
    """east lawn, next to Pick: platform, canopy, parked train, departure board"""
    x0, x1 = 104.0, 166.0
    zp = -44.0          # platform centre line
    zt = -33.0          # track centre line
    with G.Group("CellTrainStation"):
        rect("StationGround", 98, 172, -0.2, 0.2, -62, -20, (210, 204, 196), "Concrete")
        rect("Platform", x0, x1, 0, 1.4, zp - 6, zp + 6, (238, 234, 226), "Marble")
        rect("PlatformEdge", x0, x1, 1.4, 1.5, zp + 5.4, zp + 6, (250, 220, 70), "SmoothPlastic", collide=False)
        # tracks
        rect("Ballast", 96, 174, 0, 0.5, zt - 4, zt + 4, (120, 112, 104), "Pebble")
        for s_ in (-1, 1):
            rect("Rail", 96, 174, 0.5, 1.0, zt + s_ * 2.6 - 0.3, zt + s_ * 2.6 + 0.3, (190, 194, 200), "Metal")
        for x in range(98, 174, 4):
            rect("Sleeper", x - 0.7, x + 0.7, 0.4, 0.7, zt - 3.6, zt + 3.6, (110, 80, 54), "Wood", collide=False)
        # canopy
        for x in (108, 124, 140, 156):
            vcyl("CanopyPost", x, 1.4, 14, zp - 4.5, 1.0, (70, 50, 100), "SmoothPlastic")
        box("Canopy", (64, 0.8, 18), (135, 14.4, zp + 1), PURPLE, "SmoothPlastic", transp=0.1)
        box("CanopyGlow", (64, 0.2, 0.6), (135, 13.9, zp + 9.6), PINK, "Neon", collide=False, shadow=False)
        sign("StationName", "محطة قطار الخلية  |  Cell Train Station", (135, 17.5, zp - 4.0), (40, 4.6, 0.4), "Back",
             bg=(80, 40, 130))
        sign("StationName2", "محطة قطار الخلية  |  Cell Train Station", (135, 17.5, zp - 4.6), (40, 4.6, 0.4), "Front",
             bg=(80, 40, 130))
        sign("Departures", "الرحلة القادمة: جولة داخل الخلية الحيوانية\nاركب من الباب الوردي ← المدة: دقيقتين",
             (118, 7, zp - 5.6), (18, 5, 0.4), "Back", color=(255, 220, 120), bg=(20, 16, 32))
        for x in (130, 146):
            box("Bench", (8, 0.6, 2.4), (x, 3.3, zp - 3.6), (150, 100, 62), "WoodPlanks", collide=False)
            box("BenchBase", (7, 1.8, 1.6), (x, 2.3, zp - 3.6), (50, 50, 56), "SmoothPlastic", collide=False)
        # boarding door
        G.part("TrainStart", (6, 0.4, 6), (150, 1.6, zp + 2.0), (255, 120, 190), "Neon", transp=0.1, shadow=False)
        for s_ in (-1, 1):
            box("DoorPost", (0.8, 9, 0.8), (150 + s_ * 3.6, 6, zp + 5.2), (90, 60, 140), "SmoothPlastic", collide=False)
        sign("BoardSign", "🚋 اركب هنا", (150, 11.4, zp + 5.2), (8, 2.2, 0.4), "Back", bg=(200, 60, 140))
        # parked train (also the template the ride clones)
        train(164, 0.5, zt)  # v29: 4 cars now, shifted so the whole train sits on the ballast (x 96..174)
        # entrance arch from the garden side
        for s_ in (-1, 1):
            box("ArchPost", (1.4, 12, 1.4), (101, 6, -41 + s_ * 7), (90, 60, 140), "SmoothPlastic", collide=False)
        sign("ArchSign", "قطار الخلية →", (101, 12.6, -41), (0.6, 2.6, 15), "Left", bg=(90, 40, 140))


# ---------------------------------------------------------------- the cell world
CELL_OFFSET = (-12000.0, 0.0, 0.0)
ROOM = 320.0
HEIGHT = 240.0
TRACK_R = 235.0


def polar(r, deg, y):
    a = math.radians(deg)
    return (r * math.cos(a), y, r * math.sin(a))


def facing_out(deg):
    """yaw so that a sign's Front face points outward (toward a track at larger radius)"""
    a = math.radians(deg)
    return math.degrees(math.atan2(-math.cos(a), -math.sin(a)))


def label_board(deg, y, text):
    # v31: radius 205 (was 170, inside the organelles at three stops): between the rails and the organelle, so the name
    # floats in front of what it names instead of cutting through it
    x, _, z = polar(205, deg, y)
    # v29: compact floating label (no post); the ride's on-screen caption carries the full explanation
    G.part("CellLabel", (20, 4.4, 0.4), (x, y, z), (60, 30, 90), "SmoothPlastic", rot=(0, facing_out(deg), 0), collide=False,
           shadow=False, text=dict(face="Front", text=text, color=(255, 255, 255), bg=(70, 30, 110), bg_t=0.15))


def mito(cx, cy, cz, yaw, L=60, d=24):
    """v53: double membrane. A see-through outer membrane, the inner membrane folded into cristae (shelves growing from
    alternate walls), and the glowing matrix between them. One Model each so CellLife.client can move it slowly."""
    ry = math.radians(yaw)
    ux, uz = math.cos(ry), -math.sin(ry)
    with G.Group("MitoModel", "Model"):
        G.part("Mito", (L, d, d), (cx, cy, cz), (255, 170, 100), "SmoothPlastic", shape="Cylinder", rot=(0, yaw, 0),
               transp=0.55, collide=False)
        for e in (-1, 1):
            ball("MitoEnd", cx + e * ux * L / 2, cy, cz + e * uz * L / 2, d, (255, 170, 100), "SmoothPlastic", transp=0.55,
                 collide=False)
        G.part("MitoInner", (L * 0.96, d * 0.84, d * 0.84), (cx, cy, cz), (240, 120, 50), "SmoothPlastic", shape="Cylinder",
               rot=(0, yaw, 0), transp=0.25, collide=False)
        G.part("MitoMatrix", (L * 0.9, d * 0.4, d * 0.4), (cx, cy, cz), (255, 214, 130), "Neon", shape="Cylinder",
               rot=(0, yaw, 0), transp=0.3, collide=False, shadow=False)
        n = 7
        for q in range(n):
            t = (q - (n - 1) / 2) * (L * 0.8 / n)
            side = 1 if q % 2 else -1
            box("Crista", (1.6, d * 0.5, d * 0.78), (cx + ux * t, cy + side * d * 0.17, cz + uz * t), (200, 90, 30),
                "SmoothPlastic", rot=(0, yaw, 0), collide=False)


def radial_rot(dx, dy, dz):
    """rot for a Cylinder part whose axis (local X) points along the unit vector (dx, dy, dz)"""
    b = math.degrees(math.asin(max(-1.0, min(1.0, -dz))))
    c = math.degrees(math.atan2(dy, dx))
    return (0, b, c)


def tube(name, a, b, d, col, mat="Neon", transp=0.0):
    dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    L = math.sqrt(dx * dx + dy * dy + dz * dz) or 1.0
    G.part(name, (L, d, d), ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2), col, mat, shape="Cylinder",
           rot=radial_rot(dx / L, dy / L, dz / L), transp=transp, collide=False, shadow=False)


def catmull(ctrl, before, after, step):
    """points every ~step studs along a Catmull-Rom curve through ctrl (before/after shape the two ends)"""
    P = [before] + ctrl + [after]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        seg = math.dist(p1, p2)
        n = max(1, int(seg / step))
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(3)))
    out.append(tuple(P[-2]))
    return out


def cell_world():
    with G.Group("CellTrain"):
        # enclosed purple room (we see the inside faces of boxes, unlike a Ball)
        rect("CellFloor", -ROOM, ROOM, -4, 0, -ROOM, ROOM, DEEP, "SmoothPlastic")
        rect("CellCeiling", -ROOM, ROOM, HEIGHT, HEIGHT + 4, -ROOM, ROOM, (90, 44, 140), "SmoothPlastic")
        for s_ in (-1, 1):
            rect("CellWall", -ROOM, ROOM, 0, HEIGHT, s_ * ROOM - 2, s_ * ROOM + 2, PURPLE, "SmoothPlastic")
            rect("CellWall", s_ * ROOM - 2, s_ * ROOM + 2, 0, HEIGHT, -ROOM, ROOM, PURPLE, "SmoothPlastic")
        # phospholipid bilayer bands along the walls (membrane look)
        for s_ in (-1, 1):
            for q in range(26):
                t = -ROOM + 12 + q * 24.5
                for yy in (60, 72):
                    ball("Lipid", t, yy, s_ * (ROOM - 3), 10, PINK, "SmoothPlastic", collide=False, shadow=False)
                    ball("Lipid", s_ * (ROOM - 3), yy, t, 10, PINK, "SmoothPlastic", collide=False, shadow=False)
        # soft lights
        for x in (-160, 0, 160):
            for z in (-160, 0, 160):
                box("CellLight", (2, 2, 2), (x, HEIGHT - 6, z), (255, 220, 255), "Neon", collide=False, shadow=False,
                    light=(1.6, 60, (255, 210, 255)))
        # cytoplasm particles
        for q in range(120):
            ball("Cytosol", rng.uniform(-ROOM + 20, ROOM - 20), rng.uniform(10, HEIGHT - 20), rng.uniform(-ROOM + 20, ROOM - 20),
                 rng.uniform(1.2, 3), (200, 160, 255), "Neon", collide=False, shadow=False)
        # organelles (big, well spaced, inside the track loop)
        # v53 nucleus: outer + inner membrane (the envelope), pore complexes through both, chromatin threads inside
        ball("Nucleus", 0, 95, 0, 124, (160, 90, 220), "SmoothPlastic", transp=0.6, collide=False)
        ball("NucleusInner", 0, 95, 0, 114, (130, 70, 200), "SmoothPlastic", transp=0.45, collide=False)
        ball("Nucleolus", 0, 92, 0, 34, (80, 30, 130), "SmoothPlastic", collide=False)   # v54: centred; the track circles it
        for q in range(30):
            a, b = rng.uniform(0, 6.28), rng.uniform(-1.2, 1.2)
            nx, ny, nz = math.cos(a) * math.cos(b), math.sin(b), math.sin(a) * math.cos(b)
            G.part("NuclearPore", (2.4, 8, 8), (62 * nx, 95 + 62 * ny, 62 * nz), (60, 20, 90), "SmoothPlastic",
                   shape="Cylinder", rot=radial_rot(nx, ny, nz), collide=False)
            G.part("PoreChannel", (2.8, 3, 3), (62 * nx, 95 + 62 * ny, 62 * nz), (255, 200, 120), "Neon", shape="Cylinder",
                   rot=radial_rot(nx, ny, nz), collide=False, shadow=False)
        for q in range(8):
            x, y, z = rng.uniform(-30, 30), 95 + rng.uniform(-30, 30), rng.uniform(-30, 30)
            for k in range(12):
                x2, y2, z2 = x + rng.uniform(-6, 6), y + rng.uniform(-6, 6), z + rng.uniform(-6, 6)
                if math.sqrt(x2 * x2 + (y2 - 95) ** 2 + z2 * z2) < 48:
                    tube("Chromatin", (x, y, z), (x2, y2, z2), 1.6, (240, 150, 255), "Neon")
                    x, y, z = x2, y2, z2
        mito(*polar(140, -20, 55)[::1], yaw=30)
        mito(*polar(140, 200, 60)[::1], yaw=-40, L=50, d=20)
        mito(*polar(110, -40, 120)[::1], yaw=70, L=44, d=18)
        mito(*polar(160, 120, 130)[::1], yaw=10, L=40, d=16)
        # v29: smooth ER (tubes, no ribosomes): lipid synthesis
        for q in range(9):
            x, _, z = polar(118, 38 + q * 2.2, 0)
            G.part("SmoothER", (30, 3.2, 3.2), (x, 52 + (q % 3) * 9, z), (150, 200, 240), "SmoothPlastic", shape="Cylinder",
                   rot=(0, rng.uniform(0, 180), rng.uniform(-30, 30)), collide=False)
        # v29: peroxisomes (crystalline core)
        px, _, pz = polar(150, 200, 0)
        for q in range(5):
            qx, qy, qz = px + rng.uniform(-20, 20), rng.uniform(40, 80), pz + rng.uniform(-20, 20)
            ball("Peroxisome", qx, qy, qz, 12, (120, 220, 200), "Glass", transp=0.35, collide=False)
            box("PeroxisomeCore", (4, 4, 4), (qx, qy, qz), (40, 120, 110), "Neon", collide=False, shadow=False)
        # rough ER: wavy sheets studded with ribosomes; v53: flattened sacs run from the nuclear envelope out to them
        for q in range(7):
            x, _, z = polar(120 + (q % 2) * 10, 10 + q * 7, 0)
            box("RoughER", (4, 40, 34), (x, 60 + (q % 3) * 6, z), (130, 140, 230), "SmoothPlastic", collide=False,
                rot=(0, -(10 + q * 7), 0))
            for d in range(10):
                ball("Ribosome", x + rng.uniform(-3, 3), 44 + rng.uniform(0, 40), z + rng.uniform(-15, 15), 2.6, (40, 30, 70),
                     "SmoothPlastic", collide=False)
        for q in range(4):
            deg = 14 + q * 11
            a, b = polar(58, deg, 82 - q * 5), polar(118, deg, 70 - q * 3)
            tube("RERLink", a, b, 7, (130, 140, 230), "SmoothPlastic")
            for k in range(8):
                f = (k + 0.5) / 8
                ball("Ribosome", a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f + 3.6, a[2] + (b[2] - a[2]) * f, 2.4,
                     (40, 30, 70), "SmoothPlastic", collide=False)
        # free ribosome cluster
        cx, _, cz = polar(150, 62, 0)
        for q in range(40):
            ball("FreeRibosome", cx + rng.uniform(-18, 18), rng.uniform(40, 80), cz + rng.uniform(-18, 18), 3, (40, 30, 70),
                 "SmoothPlastic", collide=False)
        # v53 Golgi: curved cisternae, cis face (bottom, blue, receives from the ER) to trans face (top, orange, ships out)
        gx, _, gz = polar(145, 142, 0)
        for q in range(7):
            f = q / 6
            col = (int(130 + 125 * f), int(170 + 0 * f), int(255 - 165 * f))
            y = 40 + q * 6
            r = 26 - q * 1.5
            disc("Golgi", gx, y, gz, r * 1.2, 3.0, col, "SmoothPlastic", collide=False)
            for k in range(10):   # the rim curls up: a shallow bowl
                a = k * math.pi / 5
                box("GolgiRim", (3.0, 2.6, r * 0.66), (gx + math.cos(a) * r * 0.78, y + 1.6, gz + math.sin(a) * r * 0.78), col,
                    "SmoothPlastic", rot=(0, -math.degrees(a), 24), collide=False)
        for q in range(8):
            a = rng.uniform(0, 6.28)
            ball("Vesicle", gx + math.cos(a) * 24, rng.uniform(74, 86), gz + math.sin(a) * 24, 6, (150, 220, 255), "Glass",
                 transp=0.3, collide=False)
        # lysosomes (v53: smaller than a mitochondrion's width)
        lx, _, lz = polar(150, 178, 0)
        for q in range(7):
            ball("Lysosome", lx + rng.uniform(-24, 24), rng.uniform(40, 80), lz + rng.uniform(-24, 24), 12, (180, 90, 230),
                 "SmoothPlastic", collide=False)
        # v53 microtubules (the cell's rails) and the secretion route the vesicles travel: rough ER -> Golgi -> membrane
        route = [polar(120, 30, 72), polar(112, 70, 104), polar(112, 110, 106), polar(132, 142, 38),   # v54: above the nucleus detour
                 polar(160, 142, 84), polar(240, 142, 96), polar(314, 142, 96)]
        for a, b in zip(route, route[1:]):
            tube("Microtubule", a, b, 1.0, (210, 255, 230), "Neon")
        for i, pnt in enumerate(route, 1):
            G.part("CellPath|%d" % i, (1, 1, 1), pnt, (0, 0, 0), "SmoothPlastic", transp=1, collide=False, shadow=False)
        # centrioles
        ox, _, oz = polar(150, 222, 0)
        G.part("Centriole", (40, 12, 12), (ox, 60, oz), (120, 220, 140), "SmoothPlastic", shape="Cylinder", collide=False)
        G.part("Centriole", (40, 12, 12), (ox, 60, oz), (110, 210, 130), "SmoothPlastic", shape="Cylinder", collide=False,
               rot=(0, 90, 0))
        # cytoskeleton strands high up
        for q in range(10):
            a = rng.uniform(0, 3.14)
            box("Cytoskeleton", (1.2, 1.2, 560), (rng.uniform(-100, 100), rng.uniform(150, 220), rng.uniform(-100, 100)),
                (230, 200, 255), "Neon", rot=(0, math.degrees(a), 0), collide=False, shadow=False)
        # track: a loop around everything at radius TRACK_R, labels at each stop
        stops = [(-90, "الغشاء الخلوي: يحمي الخلية ويتحكم في دخول المواد"),
                 (-55, "السيتوبلازم: السائل اللي تسبح فيه العضيات"),
                 (-20, "الميتوكوندريا: مصنع الطاقة في الخلية"),
                 (25, "الشبكة الإندوبلازمية الخشنة وعليها الريبوسومات"),
                 (44, "الشبكة الإندوبلازمية الملساء: تصنع الدهون"),
                 (62, "الريبوسومات: تصنع البروتين"),
                 (100, "النواة: فيها المادة الوراثية DNA"),
                 (142, "جهاز جولجي: يعبّئ البروتين ويوزعه"),
                 (178, "الليسوسومات: تهضم الفضلات"),
                 (200, "البيروكسيسومات: تفكك المواد الضارة مثل فوق أكسيد الهيدروجين"),
                 (222, "الجسيم المركزي: يساعد في انقسام الخلية"),
                 (262, "نهاية الرحلة! شكراً لركوبك قطار الخلية")]
        pts = []
        labels = {}

        def loop_y(deg):
            return 42 + 10 * math.sin(math.radians(deg * 2))

        for deg in range(-100, 266, 4):
            if 92 <= deg <= 128:
                if deg == 92:
                    # v54: detour INTO the nucleus through one pore, round the nucleolus, out through another pore
                    ctrl = [polar(TRACK_R, 84, loop_y(84)), polar(TRACK_R, 88, loop_y(88)), polar(175, 92, 56),
                            polar(110, 94, 72), polar(66, 96, 84), polar(36, 104, 88)]
                    for a in range(80, -230, -30):          # inner circle, clockwise, around the nucleolus
                        ctrl.append(polar(36, a, 88))
                    ctrl += [polar(36, 118, 88), polar(66, 126, 84), polar(110, 128, 72), polar(175, 130, 56),
                             polar(TRACK_R, 132, loop_y(132)), polar(TRACK_R, 136, loop_y(136))]
                    first = len(pts)
                    pts.extend(catmull(ctrl[1:-1], ctrl[0], ctrl[-1], 5.0))
                    labels[first + 6] = "ثقب نووي: البروتينات وmRNA تدخل وتطلع من هالثقوب"
                    labels[first + 30] = "داخل النواة: الـ DNA ملفوف ككروماتين، والنوية تصنع الريبوسومات"
                continue
            pts.append(polar(TRACK_R, deg, loop_y(deg)))
            for sdeg, text in stops:
                # v54: <= 2 on the 4-degree grid (with < 2, half the stops never got their caption), once per stop
                if abs(deg - sdeg) <= 2 and text not in labels.values():
                    labels[len(pts)] = text
        for i, p in enumerate(pts, 1):
            G.part("WP|%d|%s" % (i, labels.get(i, "")), (1, 1, 1), p, (0, 0, 0), "SmoothPlastic", transp=1, collide=False,
                   shadow=False)
        for a, b in zip(pts, pts[1:]):
            dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
            L = math.sqrt(dx * dx + dy * dy + dz * dz)
            yaw = math.degrees(math.atan2(dx, dz))
            pitch = -math.degrees(math.atan2(dy, math.hypot(dx, dz)))
            mx, my, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 0.9, (a[2] + b[2]) / 2
            box("TrackBed", (6, 0.6, L + 0.5), (mx, my, mz), (230, 220, 245), "SmoothPlastic", rot=(pitch, yaw, 0), collide=False,
                shadow=False)
            vcyl("TrackPier", mx, 0, my - 0.3, mz, 1.6, (170, 130, 210), "SmoothPlastic", collide=False) if int(mx + mz) % 3 == 0 else None
        # v54: no floating name boards (the ride caption names each stop); the scenery does the teaching
        # v51: Glowing phospholipid bilayer entry tunnel around the Membrane stop (-98..-74 deg)
        for deg in range(-98, -72, 4):
            tx, ty, tz = polar(TRACK_R, deg, 42 + 10 * math.sin(math.radians(deg * 2)))
            rad = math.radians(deg)
            rx, rz = math.cos(rad), math.sin(rad)
            for s_ in (-1, 1):
                for layer, col in ((11.0, PINK), (14.5, (140, 220, 255))):
                    ball("BilayerHead", tx + rx * s_ * layer, ty + 6, tz + rz * s_ * layer, 3.2, col, "Neon",
                         collide=False, shadow=False)
            ball("MembraneArch", tx, ty + 16, tz, 4.0, (255, 190, 235), "Neon", collide=False, shadow=False)
