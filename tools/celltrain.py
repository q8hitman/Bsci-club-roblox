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
    ry = math.radians(yaw)
    ux, uz = math.cos(ry), -math.sin(ry)
    G.part("Mito", (L, d, d), (cx, cy, cz), (255, 150, 70), "SmoothPlastic", shape="Cylinder", rot=(0, yaw, 0), collide=False)
    G.part("MitoMatrix", (L * 0.9, d * 0.55, d * 0.55), (cx, cy, cz), (255, 210, 120), "Neon", shape="Cylinder", rot=(0, yaw, 0),
           transp=0.35, collide=False, shadow=False)
    for e in (-1, 1):
        ball("MitoEnd", cx + e * ux * L / 2, cy, cz + e * uz * L / 2, d, (250, 150, 80), "SmoothPlastic", collide=False)
    for q in range(6):
        t = (q - 2.5) * (L / 7)
        box("Crista", (2, d * 0.8, d * 0.9), (cx + ux * t, cy, cz + uz * t), (210, 100, 40), "SmoothPlastic", rot=(0, yaw, 0),
            collide=False)


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
        ball("Nucleus", 0, 95, 0, 120, (150, 80, 210), "SmoothPlastic", transp=0.15, collide=False)
        ball("Nucleolus", 14, 100, -10, 44, (80, 30, 130), "SmoothPlastic", collide=False)
        for q in range(26):
            a, b = rng.uniform(0, 6.28), rng.uniform(-1.3, 1.3)
            ball("NuclearPore", 60 * math.cos(a) * math.cos(b), 95 + 60 * math.sin(b), 60 * math.sin(a) * math.cos(b), 5,
                 (60, 20, 90), "SmoothPlastic", collide=False)
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
        # rough ER: wavy sheets studded with ribosomes
        for q in range(7):
            x, _, z = polar(120 + (q % 2) * 10, 10 + q * 7, 0)
            box("RoughER", (4, 40, 34), (x, 60 + (q % 3) * 6, z), (130, 140, 230), "SmoothPlastic", collide=False,
                rot=(0, -(10 + q * 7), 0))
            for d in range(10):
                ball("Ribosome", x + rng.uniform(-3, 3), 44 + rng.uniform(0, 40), z + rng.uniform(-15, 15), 2.6, (40, 30, 70),
                     "SmoothPlastic", collide=False)
        # free ribosome cluster
        cx, _, cz = polar(150, 62, 0)
        for q in range(40):
            ball("FreeRibosome", cx + rng.uniform(-18, 18), rng.uniform(40, 80), cz + rng.uniform(-18, 18), 3, (40, 30, 70),
                 "SmoothPlastic", collide=False)
        # golgi stack
        gx, _, gz = polar(145, 142, 0)
        for q in range(7):
            disc("Golgi", gx, 40 + q * 6, gz, 60 - q * 4, 3.4, (250, 200, 110), "SmoothPlastic", collide=False)
        for q in range(8):
            ball("Vesicle", gx + rng.uniform(-36, 36), rng.uniform(40, 90), gz + rng.uniform(-36, 36), 7, (150, 220, 255), "Glass",
                 transp=0.3, collide=False)
        # lysosomes
        lx, _, lz = polar(150, 178, 0)
        for q in range(7):
            ball("Lysosome", lx + rng.uniform(-24, 24), rng.uniform(40, 80), lz + rng.uniform(-24, 24), 18, (180, 90, 230),
                 "SmoothPlastic", collide=False)
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
        for deg in range(-100, 266, 4):
            y = 42 + 10 * math.sin(math.radians(deg * 2))
            pts.append(polar(TRACK_R, deg, y))
            for sdeg, text in stops:
                if abs(deg - sdeg) < 2:
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
        for sdeg, text in stops[:-1]:
            label_board(sdeg, 70, text.split(":")[0])
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
