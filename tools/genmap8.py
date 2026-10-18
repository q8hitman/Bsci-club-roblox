"""v8: 8 BSC specialty zones, one shared lobby (quiz corner + parkour gates + cell train),
classic obby mechanics (lava stones, narrow ledges) and the Cell Train world.
Run: python tools/genmap8.py kuwait-parkour/src/map/Map.rbxmx
Also writes kuwait-parkour/src/shared/Zones.luau (zone names + level ranges) for the scripts.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genmap7 as G7  # noqa: E402  (mechanics v7, campus helpers)
import genmap6 as G6  # noqa: E402
import genmap5 as C5  # noqa: E402
import genmap3 as C3  # noqa: E402
import genmap2 as M2  # noqa: E402
import genmap as G  # noqa: E402
import celltrain  # noqa: E402

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign
rect = C5.rect
rng = random.Random(8008)

OLD_THEMES = [dict(t) for t in M2.THEMES]
OLD_NAMES = list(M2.ZONE_NAMES)
FORENSIC = dict(main=((70, 74, 84), "Slate"), alt=((236, 200, 60), "SmoothPlastic"), edge=(255, 214, 60),
                pillar=((50, 54, 62), "Metal"))
AGRI = dict(main=((150, 112, 72), "Ground"), alt=((120, 170, 90), "Grass"), edge=(250, 236, 140),
            pillar=((120, 90, 60), "Wood"))

# name_ar, name_en, theme, env index in genmap6 (None = custom), stage list
ZONES = [
    ("بيولوجيا نبات", "Plant Biology", OLD_THEMES[0], 1,
     ["hops", "leaves", "truss", "seesaw", "blink", "maze", "log", "windmill", "ledge", "crumble", "lava",
      ("leaves", "truss", "windmill")]),
    ("بيولوجيا حيوان", "Animal Biology", OLD_THEMES[1], 2,
     ["hops", "ferry", "log", "lava", "pillars", "glass", "sweeper", "seesaw", "ledge", "elevator", "maze",
      ("ferry", "log", "sweeper")]),
    ("مايكروبيولوجي", "Microbiology", OLD_THEMES[2], 3,
     ["zigzag", "blink", "spinner", "fan", "lava", "crumble", "carousel", "sequence", "laser", "moon", "ledge",
      ("blink", "carousel", "fan")]),
    ("بايوكيمستري", "Biochemistry", OLD_THEMES[5], 6,
     ["molecule", "gel", "hops", "conveyor", "lava", "switch", "laser", "fan", "glass", "log", "ledge",
      ("molecule", "gel", "laser")]),
    ("مولكلر", "Molecular Biology", OLD_THEMES[4], 5,
     ["stairs", "helix", "zigzag", "sequence", "spinner", "switch", "truss", "windmill", "lava", "carousel", "ice", "ledge",
      ("helix", "sequence", "spinner")]),
    ("الزراعة", "Agriculture", AGRI, None,
     ["hops", "leaves", "ferry", "conveyor", "maze", "truss", "ice", "crumble", "windmill", "lava", "ledge",
      ("leaves", "maze", "conveyor")]),
    ("الأدلة الجنائية", "Forensic Science", FORENSIC, None,
     ["laser", "ledge", "blink", "sequence", "sweeper", "glass", "switch", "lava", "heartbeat", "maze", "fan", "crumble",
      ("laser", "sweeper", "glass")]),
    ("البايوتكنولوجي", "Biotechnology", OLD_THEMES[8], 9,
     ["gel", "bounce", "laser", "glass", "helix", "moon", "switch", "carousel", "lava", "sweeper", "heartbeat", "windmill",
      "ledge", ("gel", "helix", "moon", "laser")]),
]
assert sum(len(z[4]) for z in ZONES) == 100, sum(len(z[4]) for z in ZONES)

M2.THEMES[:] = [z[2] for z in ZONES]
M2.ZONE_NAMES[:] = [(z[0], z[1]) for z in ZONES]
M2.SEQ[:] = [z[4] for z in ZONES]


# ====================================================================== classic obby mechanics
def k_lava(c, th, t, k):
    """hop across stepping stones over a glowing lava floor"""
    L = 34 + 8 * t
    z0 = M2.cursor_gap(c, L, 2.0)
    box("Kill", (18, 1, L), (c["x"], c["y"] - 1.1, z0), (255, 84, 40), "Neon")
    for s_ in (-1, 1):
        box("LavaRim", (1, 2, L), (c["x"] + s_ * 9.5, c["y"] - 1, z0), (60, 40, 36), "Basalt", collide=False)
    s = 4.4 - 1.2 * t
    gap = 2.6 + 2.0 * t
    z = z0 - L / 2
    prev_x = c["x"]
    while True:
        zc = z + gap + s / 2
        if zc + s / 2 > z0 + L / 2 - 1:
            break
        x = M2.clampx(prev_x * 0.5 + rng.uniform(-4.5, 4.5) + c["x"] * 0.5, 7) if abs(c["x"]) < 20 else c["x"] + rng.uniform(-4, 4)
        box("Stone", (s, 2, s), (x, c["y"] - 0.6, zc), (90, 84, 80), "Basalt")
        M2.walk.append(("r", x, zc, c["y"] + 0.4, s, s))
        prev_x = x
        z = zc + s / 2
        M2.set_c(c, x, c["y"] + 0.4, zc, s)
    M2.set_c(c, c["x"], c["y"] - 0.4, c["z"], c["sz"])
    M2._land(c, th, 10, 2.4)


def k_ledge(c, th, t, k):
    """walk a narrow ledge hugging a wall (classic wrap)"""
    L = 36
    z0 = M2.cursor_gap(c, L, 2)
    side = 1 if k % 2 else -1
    col, mat = th["pillar"]
    box("LedgeWall", (2, 18, L + 4), (c["x"] + side * 3.0, c["y"] + 7, z0), col, mat)
    n = 3 + int(t * 2)
    gap = 2.4 + 1.2 * t
    seg = (L - gap * (n - 1)) / n
    z = z0 - L / 2
    w = 2.2 - 0.5 * t
    for i in range(n):
        zc = z + seg / 2
        xc = c["x"] + side * (2.0 - w / 2)
        acol, amat = th["alt"]
        box("Ledge", (w, 1, seg), (xc, c["y"] - 0.5, zc), acol, amat)
        box("LedgeEdge", (0.2, 0.14, seg), (xc - side * (w / 2 - 0.1), c["y"] + 0.02, zc), th["edge"], "Neon", collide=False,
            shadow=False)
        M2.walk.append(("r", xc, zc, c["y"], w, seg))
        z = zc + seg / 2 + gap
    M2.set_c(c, c["x"], c["y"], z0 + L / 2 - 0.5, 1.0)
    M2._land(c, th, 10, 1.0)


M2.KINDS.update(dict(lava=k_lava, ledge=k_ledge))


# ====================================================================== specialty environments
def palm_at(x, g, z, h=16.0):
    vcyl("PalmTrunk", x, g, g + h, z, 1.6, (150, 118, 82), "Wood", collide=False)
    for a in range(8):
        yaw = a * 45.0
        pitch = 26
        L = 8.0
        dx = math.sin(math.radians(yaw)) * (L / 2) * math.cos(math.radians(pitch))
        dz = math.cos(math.radians(yaw)) * (L / 2) * math.cos(math.radians(pitch))
        dy = -(L / 2) * math.sin(math.radians(pitch))
        box("Frond", (2.4, 0.25, L), (x + dx, g + h + dy, z + dz), (82, 150, 78), "Grass", collide=False, rot=(pitch, yaw, 0))
    for q in range(4):
        ball("Dates", x + math.cos(q * 1.6) * 1.2, g + h - 1.2, z + math.sin(q * 1.6) * 1.2, 1.2, (150, 80, 30), "SmoothPlastic",
             collide=False)


def env_agri(j, z0, z1, g):
    th = M2.THEMES[j - 1]
    L, zc = z1 - z0, (z0 + z1) / 2
    C3.hall(g, z0, z1, ((132, 98, 64), "Ground"), ((200, 228, 205), "Glass"), 0.6, trim=th["edge"])
    for s_ in (-1, 1):
        for r in range(5):
            x = s_ * (24 + r * 8)
            rect("CropRow", x - 1.6, x + 1.6, g, g + 2.4, z0 + 6, z1 - 6, [(110, 170, 80), (210, 190, 90)][r % 2], "Grass",
                 collide=False)
            rect("Drip", x - 0.2, x + 0.2, g + 0.2, g + 0.5, z0 + 6, z1 - 6, (70, 140, 200), "SmoothPlastic", collide=False)
    for z in range(int(z0) + 24, int(z1), 34):
        for s_ in (-1, 1):
            palm_at(s_ * 64, g, z)
        for s_ in (-1, 1):
            vcyl("Hoop", s_ * 58, g, g + 40, z + 17, 0.8, (240, 240, 236), "SmoothPlastic", collide=False)
        box("HoopTop", (116, 0.8, 0.8), (0, g + 40, z + 17), (240, 240, 236), "SmoothPlastic", collide=False)
    C3.zone_sign("الزراعة\nAgriculture", 0, g, z0 + 14, 40, 9, y=g + 50, bg=(70, 100, 40))


def env_forensic(j, z0, z1, g):
    th = M2.THEMES[j - 1]
    L, zc = z1 - z0, (z0 + z1) / 2
    C3.hall(g, z0, z1, ((44, 46, 54), "Slate"), ((62, 64, 74), "SmoothPlastic"), 0.0, trim=th["edge"])
    for z in range(int(z0) + 20, int(z1), 46):
        for s_ in (-1, 1):
            x = s_ * (C3.WALL_X - 1.0)
            sign("Tape", "CRIME SCENE  •  DO NOT CROSS  •  مسرح جريمة", (x, g + 14, z), (0.4, 2.6, 40),
                 "Right" if s_ < 0 else "Left", color=(20, 20, 20), bg=(250, 214, 50))
            for q, d in enumerate((22, 18, 14, 10, 6)):
                G.part("Print", (0.3 + q * 0.05, d, d), (x + (-s_) * (0.3 + q * 0.06), g + 34, z + 20), (60, 220, 255) if q % 2 == 0
                       else (30, 40, 70), "Neon" if q % 2 == 0 else "SmoothPlastic", shape="Cylinder", collide=False, shadow=False)
            rect("Board", x - 0.3, x + 0.3, g + 4, g + 12, z - 6, z + 6, (170, 120, 70), "Wood", collide=False)
            for q in range(4):
                box("Photo", (0.2, 2.4, 3), (x + (-s_) * 0.4, g + 6 + (q % 2) * 3.4, z - 3.5 + (q // 2) * 7), (245, 245, 240),
                    "SmoothPlastic", collide=False)
        for q in range(6):
            box("Footprint", (1.6, 0.06, 3.2), (-4 + (q % 2) * 4, g + 0.05, z + q * 5), (24, 24, 28), "SmoothPlastic",
                collide=False)
    for q in range(int(L / 24)):
        box("UV", (C3.WALL_X * 2, 0.5, 1.4), (0, g + 100, z0 + 10 + q * 24), (170, 80, 255), "Neon", collide=False, shadow=False)
    C3.zone_sign("الأدلة الجنائية\nForensic Science", 0, g, z0 + 14, 40, 9, y=g + 50, bg=(90, 70, 10))


def env8(j, z0, z1, g):
    name_ar, name_en, theme, env_idx, _ = ZONES[j - 1]
    if env_idx is None:
        (env_agri if name_en.startswith("Agri") else env_forensic)(j, z0, z1, g)
        return
    saved_themes, saved_names = M2.THEMES[:], M2.ZONE_NAMES[:]
    names = list(OLD_NAMES)
    names[env_idx - 1] = (name_ar, name_en)
    M2.THEMES[:] = OLD_THEMES
    M2.ZONE_NAMES[:] = names
    try:
        G6.env6(env_idx, z0, z1, g)
    finally:
        M2.THEMES[:] = saved_themes
        M2.ZONE_NAMES[:] = saved_names


C3.env = env8


# ====================================================================== shared lobby
def shared_lobby():
    """the big ground-floor lobby: quiz corner in the middle, zone gates along the back, cell train on the side"""
    zone_cols = [z[2]["edge"] for z in ZONES]
    # quiz corner
    cx, cz, R = 0.0, -123.0, 15.0
    disc("QuizFloor", cx, 0.06, cz, 2 * R + 12, 0.1, (40, 52, 80), "SmoothPlastic", collide=False)
    disc("QuizRing", cx, 0.02, cz, 2 * R + 12.6, 0.06, (120, 200, 255), "Neon", collide=False, shadow=False)
    for face, dz in (("Back", 0.0), ("Front", -0.6)):
        sign("QuizTitle", "ركن الأسئلة | Quiz Corner\nقِف على محطة تخصصك وجاوب", (cx, 13, cz + dz), (17, 4.6, 0.5), face,
             bg=(40, 60, 110))
    for i, (ar, en, th, _, _) in enumerate(ZONES):
        a = i * 2 * math.pi / len(ZONES)
        x, z = cx + R * math.sin(a), cz + R * math.cos(a)
        col = th["edge"]
        box("Podium", (3.4, 3.6, 3.4), (x, 1.8, z), (238, 238, 234), "SmoothPlastic")
        box("PodiumBand", (3.5, 0.5, 3.5), (x, 2.9, z), col, "Neon", collide=False, shadow=False)
        G.part("Screen", (5.4, 3.2, 0.3), (x + math.sin(a) * 0.9, 6.0, z + math.cos(a) * 0.9), (20, 24, 34), "SmoothPlastic",
               rot=(0, math.degrees(a), 0), collide=False,
               text=dict(face="Front", text="%s\n%s" % (ar, en), color=(255, 255, 255),
                         bg=tuple(max(0, v - 130) for v in col), bg_t=0.0))
        px, pz = cx + (R - 5.2) * math.sin(a), cz + (R - 5.2) * math.cos(a)
        G.part("QuizStation|%d" % (i + 1), (4.6, 0.4, 4.6), (px, 0.2, pz), col, "Neon", transp=0.2, rot=(0, math.degrees(a), 0),
               shadow=False)
    # parkour gates along the back of the lobby, Continue in the middle
    zg = -84.0
    xs = [-56, -42, -28, -14, 14, 28, 42, 56]
    starts = zone_starts()
    sign("GatesTitle", "بوابات الباركور | Parkour Gates — كل منطقة تنفتح لما تخلّص اللي قبلها", (0, 20.5, zg + 0.6),
         (64, 3.2, 0.5), "Front", bg=(24, 70, 48))
    for i, x in enumerate(xs):
        zone = i + 1
        ar, en = ZONES[i][0], ZONES[i][1]
        col = zone_cols[i]
        for s_ in (-1, 1):
            box("GatePost", (0.9, 12, 0.9), (x + s_ * 4.6, 6, zg), (60, 64, 74), "SmoothPlastic", collide=False)
        G.part("Portal|Zone|%d" % zone, (8.2, 10.5, 0.5), (x, 5.4, zg), col, "Neon", transp=0.45, collide=False, shadow=False)
        first, last = starts[i] + 1, starts[i + 1]
        sign("GateSign", "%s\n%s\n%d - %d" % (ar, en, first, last), (x, 13.8, zg - 0.2), (10, 3.6, 0.5), "Front",
             bg=tuple(max(0, v - 120) for v in col))
        G.part("GateLamp|%d" % zone, (1.2, 1.2, 1.2), (x, 16.2, zg), (90, 230, 140), "Neon", shape="Ball", collide=False,
               shadow=False)
    for s_ in (-1, 1):
        box("BigPost", (1.4, 16, 1.4), (s_ * 6.2, 8, zg + 4), (60, 64, 74), "SmoothPlastic", collide=False)
    G.part("Portal|Course", (11, 14, 0.6), (0, 7.2, zg + 4), (120, 255, 200), "Neon", transp=0.45, collide=False, shadow=False)
    sign("ContinueSign", "كمّل من آخر نقطة\nContinue", (0, 17.6, zg + 3.6), (13, 3.4, 0.5), "Front", bg=(24, 90, 60))
    G.part("HallSpawn", (6, 1, 6), (0, 0.5, -110), (0, 0, 0), "SmoothPlastic", transp=1, collide=False)
    # the Cell Train has its own station on the east lawn
    sign("TrainDirection", "🚋 محطة قطار الخلية ← اطلع من الباب الخلفي للحديقة الشرقية", (40, 9, -104.4), (26, 3, 0.4), "Front",
         bg=(110, 50, 150))
    # club banner over the lobby
    sign("Banner", "نادي العلوم البيولوجية  •  Biological Sciences Club", (0, 30, -104.6), (60, 5, 0.5), "Front",
         bg=(24, 80, 56))
    for x in (-28, 28):
        C5.light_panel(x, 23.0, -84, 14, 6, 1.4, 40)


def zone_starts():
    starts = [0]
    for z in ZONES:
        starts.append(starts[-1] + len(z[4]))
    return starts


# ====================================================================== cell train world
CELL_OFFSET = (-3000.0, 40.0, 0.0)


def cell_world():
    with G.Group("CellTrain"):
        # membrane as inward-facing panels (a Ball is invisible from inside, so the sky showed through)
        Rm = 165.0
        for li in range(-4, 5):
            lat = li * math.pi / 10
            ring_r = Rm * math.cos(lat)
            n = max(6, int(2 * math.pi * ring_r / 34))
            for q in range(n):
                lon = q * 2 * math.pi / n
                px, py, pz = ring_r * math.cos(lon), Rm * math.sin(lat), ring_r * math.sin(lon)
                yaw = -math.degrees(lon) + 90
                G.part("Membrane", (2 * math.pi * ring_r / n + 4, 2 * math.pi * Rm / 20 + 4, 2), (px, py, pz),
                       (250, 170, 200) if (q + li) % 2 else (240, 150, 190), "SmoothPlastic", transp=0.15, collide=False,
                       shadow=False, rot=(math.degrees(lat), yaw, 0))
        for cap in (-1, 1):
            disc("MembraneCap", 0, cap * Rm * 0.97, 0, 2 * Rm * math.cos(math.pi * 4.5 / 10) + 30, 2, (245, 160, 195),
                 "SmoothPlastic", transp=0.15, collide=False, shadow=False)
        # nucleus
        ball("Nucleus", 0, 0, 0, 70, (150, 90, 200), "SmoothPlastic", transp=0.3, collide=False)
        ball("Nucleolus", 6, 4, -4, 26, (90, 40, 130), "SmoothPlastic", collide=False)
        for q in range(14):
            a, b = rng.uniform(0, 6.28), rng.uniform(-1.2, 1.2)
            ball("Pore", 35 * math.cos(a) * math.cos(b), 35 * math.sin(b), 35 * math.sin(a) * math.cos(b), 3, (60, 30, 90),
                 "SmoothPlastic", collide=False)
        # rough ER sheets with ribosome dots
        for q in range(10):
            a = q * 0.42 + 0.3
            r = 52 + (q % 3) * 6
            box("ER", (2, 22, 30), (r * math.cos(a), -6 + (q % 2) * 10, r * math.sin(a)), (120, 130, 220), "SmoothPlastic",
                collide=False, rot=(0, -math.degrees(a), 0))
            for d in range(6):
                ball("Ribosome", r * math.cos(a) + 1.4, -14 + d * 4 + (q % 2) * 10, r * math.sin(a) + rng.uniform(-12, 12), 1.6,
                     (40, 40, 60), "SmoothPlastic", collide=False)
        # golgi stack
        for q in range(5):
            disc("Golgi", 85, 20 + q * 3.2, 55, 30 - q * 3, 1.8, (250, 200, 110), "SmoothPlastic", collide=False)
        # mitochondria
        for q, (mx, my, mz) in enumerate(((-90, -20, 40), (-60, 30, -90), (100, -30, -60), (40, 50, 110), (-110, 10, -30))):
            G.part("Mito", (24, 10, 10), (mx, my, mz), (250, 150, 80), "SmoothPlastic", shape="Cylinder", collide=False,
                   rot=(0, q * 35, 0))
            for e in (-1, 1):
                ball("MitoEnd", mx + e * 12 * math.cos(math.radians(q * 35)), my, mz - e * 12 * math.sin(math.radians(q * 35)), 10,
                     (250, 150, 80), "SmoothPlastic", collide=False)
            for c_ in range(4):
                box("Crista", (1, 8, 9), (mx + (c_ - 1.5) * 4 * math.cos(math.radians(q * 35)), my,
                                           mz - (c_ - 1.5) * 4 * math.sin(math.radians(q * 35))), (200, 100, 40), "SmoothPlastic",
                    collide=False, rot=(0, q * 35, 0))
        # lysosomes, vesicles, free ribosomes, centrioles
        for q in range(9):
            ball("Lysosome", rng.uniform(-120, 120), rng.uniform(-60, 60), rng.uniform(-120, 120), 7, (170, 90, 220), "SmoothPlastic",
                 collide=False)
        for q in range(12):
            ball("Vesicle", rng.uniform(-120, 120), rng.uniform(-60, 60), rng.uniform(-120, 120), 5, (150, 220, 255), "Glass",
                 transp=0.3, collide=False)
        for q in range(60):
            ball("FreeRibo", rng.uniform(-130, 130), rng.uniform(-70, 70), rng.uniform(-130, 130), 1.4, (50, 50, 70),
                 "SmoothPlastic", collide=False, shadow=False)
        G.part("Centriole", (14, 4, 4), (60, -40, 80), (120, 220, 140), "SmoothPlastic", shape="Cylinder", collide=False)
        G.part("Centriole", (14, 4, 4), (60, -40, 80), (120, 220, 140), "SmoothPlastic", shape="Cylinder", collide=False,
               rot=(0, 90, 0))
        # track (waypoints + rails) and labelled stops
        stops = [((0, -40, -150), "الغشاء الخلوي: يحمي الخلية ويتحكم في دخول المواد"),
                 ((-60, -30, -100), "السيتوبلازم: السائل اللي تسبح فيه العضيات"),
                 ((-85, -10, -35), "الميتوكوندريا: مصنع الطاقة في الخلية"),
                 ((-70, 0, 40), "الشبكة الإندوبلازمية الخشنة وعليها الريبوسومات"),
                 ((-30, 10, 75), "الريبوسومات: تصنع البروتين"),
                 ((30, 25, 70), "النواة: فيها المادة الوراثية DNA"),
                 ((70, 22, 40), "جهاز جولجي: يعبّئ البروتين ويوزعه"),
                 ((90, -10, -20), "الليسوسومات: تهضم الفضلات"),
                 ((55, -35, 75), "الجسيم المركزي: يساعد في انقسام الخلية"),
                 ((20, -40, -120), "نهاية الرحلة! شكراً لركوبك قطار الخلية")]
        ctrl = [s[0] for s in stops]
        path3 = catmull3(ctrl, 10)
        stop_idx = {}
        for si, (p, _) in enumerate(stops):
            best = min(range(len(path3)), key=lambda i: sum((path3[i][k] - p[k]) ** 2 for k in range(3)))
            stop_idx[best] = stops[si][1]
        for i, p in enumerate(path3):
            label = stop_idx.get(i, "")
            G.part("WP|%d|%s" % (i + 1, label), (1, 1, 1), p, (0, 0, 0), "SmoothPlastic", transp=1, collide=False, shadow=False)
        for a, b in zip(path3, path3[1:]):
            dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
            L = math.sqrt(dx * dx + dy * dy + dz * dz)
            yaw = math.degrees(math.atan2(dx, dz))
            pitch = -math.degrees(math.atan2(dy, math.hypot(dx, dz)))
            mx, my, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 1.6, (a[2] + b[2]) / 2
            box("Rail", (5, 0.4, L + 0.4), (mx, my, mz), (230, 230, 240), "SmoothPlastic", collide=False, shadow=False,
                rot=(pitch, yaw, 0))
        for si, (p, text) in enumerate(stops[:-1]):
            sign("CellLabel", text, (p[0], p[1] + 9, p[2]), (22, 4, 0.4), "Front", bg=(60, 30, 80))


def catmull3(pts, per):
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(per):
            t = k / per
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(3)))
    out.append(pts[-1])
    return out


def write_zones_module(path):
    starts = zone_starts()
    lines = ["-- Generated by tools/genmap8.py: parkour zones in order (levels start+1 .. finish).", "return {"]
    for i, z in enumerate(ZONES):
        lines.append('\t{ nameAr = "%s", nameEn = "%s", start = %d, finish = %d },' % (z[0], z[1], starts[i], starts[i + 1]))
    lines.append("}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def build_campus():
    with G.Group("Campus"):
        C5.outdoors()
        C5.south_building()
        shared_lobby()
        G7.department_offices()
        G7.lounges()
        G7.building_details()
        celltrain.train_station()
        C5._off[2] = C5.NB_SHIFT
        C5.north_building()
        C5._off[2] = 0.0


if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else "kuwait-parkour/src/map/Map.rbxmx"
    build_campus()
    C5._off[0], C5._off[1], C5._off[2] = C5.COURSE_OFFSET
    G.hub = G7.course_start
    C3.build()
    C5._off[0], C5._off[1], C5._off[2] = celltrain.CELL_OFFSET
    celltrain.cell_world()
    C5._off[0], C5._off[1], C5._off[2] = 0.0, 0.0, 0.0
    gap, rise, bad, n = M2.validate()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    size = 0
    with open(out_path, "w", encoding="utf-8") as f:   # stream: the joined string can exhaust memory
        f.write('<roblox version="4"><Item class="Folder" referent="%s"><Properties>'
                '<string name="Name">Map</string></Properties>' % G.rid())
        for chunk in G.buf:
            f.write(chunk)
            size += len(chunk)
        f.write("</Item></roblox>")
    write_zones_module(os.path.join(os.path.dirname(os.path.dirname(out_path)), "shared", "Zones.luau"))
    print("parts:", G.nparts[0], "| steps:", n, "| gap %.2f rise %.2f" % (gap, rise), "| violations:", len(bad),
          "| KB:", size // 1024, "| zone starts:", zone_starts())
    for v in bad[:6]:
        print("  BAD", v)
