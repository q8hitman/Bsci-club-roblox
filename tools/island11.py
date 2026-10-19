"""v11 BSC Island gameplay layer (absolute coordinates; offsets must be 0 when called):
  island_layer()  spawn, plaza monument, gateways + portals in front of every building, signs, NPC markers
  exam_hall()     the Exam Hall interior: desks, screen, 4 answer zones over a drop pit (ExamZone|A..D, ExamTrap|A..D)
  arcade()        the minigames hall: lobby + the three Chaos Campus arenas (ArcadeLobby, Arena_*)
Meshes/scenery of the island itself come from tools/world/island.luau (Synty packs).
"""
import math

import genmap as G
import genmap5 as C5
import bsc_art as A

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign
rect = C5.rect

OX, OZ = 0.0, 9000.0                  # island origin
EX, EY, EZ = 6000.0, 300.0, -6000.0   # exam hall interior
AX, AY, AZ = -6000.0, 300.0, -6000.0  # arcade
PASTEL = [c for (_, c, _) in A.HEXES]
GREEN = (24, 80, 56)


def gateway_at(name, X, Y, Z, face, title, sub, col, width=10.0, h=12.5):
    """a free-standing glowing gateway (portal sheet inside a framed arch) at absolute (X, Y, Z) facing `face` = (nx, nz)"""
    nx, nz = face
    along_x = abs(nz) > 0.5
    METAL = (44, 50, 56)
    for s_ in (-1, 1):
        px, pz = (X + s_ * (width / 2 + 0.6), Z) if along_x else (X, Z + s_ * (width / 2 + 0.6))
        vcyl("GatePost", px, Y, Y + h + 0.8, pz, 1.0, METAL, "Metal")
        ball("GateCap", px, Y + h + 1.2, pz, 1.3, col, "Neon", collide=False, shadow=False)
    box("GateBeam", (width + 1.2, 0.7, 0.7) if along_x else (0.7, 0.7, width + 1.2), (X, Y + h + 0.45, Z), METAL, "Metal")
    G.part(name, (width, h, 0.4) if along_x else (0.4, h, width), (X, Y + h / 2 + 0.1, Z), col, "Neon", transp=0.5, collide=False,
           shadow=False)
    faceName = {(0, 1): "Back", (0, -1): "Front", (1, 0): "Right", (-1, 0): "Left"}[(int(round(nx)), int(round(nz)))]
    size = (min(width + 1, 11.5), 2.2, 0.3) if along_x else (0.3, 2.2, min(width + 1, 11.5))
    sign("GateTitle", title, (X + nx * 0.5, Y + h + 2.1, Z + nz * 0.5), size, faceName, color=(255, 246, 225), bg=(30, 36, 42))


def gateway(name, x, z, face, title, sub, col, width=12.0, h=14.0):
    """Compatibility wrapper placing gateway on Campus / HQ instead of retired Island"""
    gateway_at(name, x, 0.0, z, face, title, sub, col, width=width, h=h)


def island_layer():
    """v52: The separate Island (OZ=9000) is decommissioned per owner decision.
    All essential content (9 Biology Snack Kiosks, 8 NPCs, Activity Gateways, and Club Monument)
    is consolidated into the BSC Club HQ (0, 600, -9000) and KU College of Science Campus Plaza (0, 0, 44..110)."""
    import hq
    HX, HY, HZ = hq.HQ_OFFSET
    with G.Group("CampusHubMigration"):
        # Safe invisible fallback part named IslandSpawn at Campus Plaza so legacy references never error
        G.part("IslandSpawn", (6, 1, 6), (0, 0.5, 70), (64, 140, 108), "SmoothPlastic", transp=1.0, collide=False, shadow=False)

        # ---- 1. BSC Club HQ Activity Portal Gallery (West & East Walls of HQ so HQ is a complete 100% Hub)
        hq_portals = [
            ("Portal|Exam",   -73.8, -14.0, (1, 0),  "📝 قاعة الاختبارات", (255, 210, 80)),
            ("Portal|Lab",    -73.8,   6.0, (1, 0),  "🔬 معهد الأبحاث والمختبر", (140, 220, 255)),
            ("Portal|Arcade", -73.8,  26.0, (1, 0),  "🎮 صالة الألعاب (Chaos)", (240, 110, 200)),
            ("Portal|Quiz",    73.8, -14.0, (-1, 0), "🎓 مركز التحديات العلمية", (255, 200, 120)),
            ("Portal|Museum",  73.8,   6.0, (-1, 0), "🏛️ متحف العلوم التفاعلي", (120, 230, 190)),
            ("Portal|Show",    73.8,  26.0, (-1, 0), "🎪 مسرح المسابقات", (255, 150, 90)),
            ("Portal|Racers",  73.8,  45.0, (-1, 0), "🏎️ سباق الميكروبات", (110, 210, 255)),
            ("Portal|Laser",  -52.0, -54.0, (0, 1),  "⚡ الهروب من الليزر", (255, 95, 120)),
        ]
        for pname, dx, dz, face, title, col in hq_portals:
            gateway_at(pname, HX + dx, HY, HZ + dz, face, title, "", col, width=8.5, h=11.0)

        # ---- 2. Campus Courtyard Biology Snack Promenade (ShopOrder|1..9 migrated from Island to Campus!)
        # Placed along the shaded East & West Courtyard Promenades south of Building 114 (z = 48..96)
        names = [
            ("كافيه الخلية ☕", -1, 50.0),
            ("مخبز الخميرة 🥐", -1, 61.5),
            ("دونات DNA 🍩", -1, 73.0),
            ("سلطة الكلوروبلاست 🥗", -1, 84.5),
            ("ميلك شيك الكلوروفيل 🥤", -1, 96.0),
            ("آيس كريم الميتوكوندريا 🍦", 1, 54.0),
            ("برجر البروتين 🍔", 1, 67.5),
            ("بيتزا البكتيريا 🍕", 1, 81.0),
            ("عصير الفيتامينات 🍊", 1, 94.5),
        ]
        sign("CampusFoodHeaderW", "🍩 ركن الكافيهات العلمية • Biology Café Row", (-38, 10.8, 43.0), (14, 2.2, 0.4), "Back", bg=GREEN)
        sign("CampusFoodHeaderE", "🥤 استراحة نادي العلوم • Free Bio Snacks", (38, 10.8, 43.0), (14, 2.2, 0.4), "Back", bg=GREEN)
        for i, (text, side, z) in enumerate(names):
            kx = side * 38.0
            # Shaded kiosk booth + counter + menu sign + ShopOrder|1..9 marker
            box("KioskBack", (1.2, 8.6, 8.8), (kx + side * 2.2, 4.3, z), (236, 230, 218), "Marble")
            box("ShopCounter", (1.8, 3.4, 7.6), (kx, 1.7, z), (242, 236, 224), "Marble")
            box("ShopCounterTop", (2.4, 0.35, 8.0), (kx - side * 0.2, 3.55, z), (150, 104, 66), "WoodPlanks")
            box("ShopAwning", (4.2, 0.45, 9.0), (kx, 8.4, z), (200, 70, 60) if i % 2 else (36, 118, 88),
                "Fabric", rot=(0, 0, side * 10), collide=False)
            G.part("ShopName", (0.4, 2.2, 8.6), (kx + side * 1.4, 6.4, z), (30, 34, 42), "SmoothPlastic", collide=False,
                   text=dict(face="Right" if side < 0 else "Left", text=text, color=(255, 240, 200), bg=(24, 80, 56), bg_t=0.0))
            G.part("ShopOrder|%d" % (i + 1), (1.2, 1.2, 1.2), (kx - side * 1.3, 3.6, z), (0, 0, 0), "SmoothPlastic", transp=1,
                   collide=False, shadow=False)

        # ---- 3. Campus Outdoor Activity Gateways (West & East of the South Plaza so Campus also links to all worlds)
        campus_portals = [
            ("Portal|HQ",     -56.0, 48.0, (1, 0),  "🏠 مقر نادي العلوم (HQ)", (120, 255, 200)),
            ("Portal|Lab",    -56.0, 64.0, (1, 0),  "🔬 معهد الأبحاث والمختبر", (140, 220, 255)),
            ("Portal|Exam",   -56.0, 80.0, (1, 0),  "📝 قاعة الاختبارات", (255, 210, 80)),
            ("Portal|Quiz",   -56.0, 96.0, (1, 0),  "🎓 مركز التحديات", (255, 200, 120)),
            ("Portal|Cart",    56.0, 48.0, (-1, 0), "🚆 قطار التخصصات الـ8", (250, 160, 90)),
            ("Portal|Arcade",  56.0, 64.0, (-1, 0), "🎮 محطة الألعاب والألغاز", (240, 110, 200)),
            ("Portal|Course",  56.0, 80.0, (-1, 0), "🏃 باركور الـ100 مرحلة", (110, 200, 255)),
            ("Portal|Virus",   56.0, 96.0, (-1, 0), "🦠 مختبر العدوى (Virus Tag)", (140, 255, 90)),
        ]
        for pname, cx, cz, face, title, col in campus_portals:
            gateway_at(pname, cx, 0.0, cz, face, title, "", col, width=9.5, h=11.5)

        # ---- 4. All 8 Interactive NPCs migrated to meaningful Campus & Club HQ spots
        npcs_abs = [
            ("NPC|abu_ali",   HX + 20.0, HY + 0.5, HZ + 36.0, -35),   # Welcoming students inside BSC Club HQ
            ("NPC|gamer",     HX - 58.0, HY + 0.5, HZ + 24.0,  90),   # By the Arcade & Virus portals inside HQ
            ("NPC|dr_sara",       -16.0,      0.5,      24.0, 180),   # South Campus Atrium entrance (Specialties & Lab guide)
            ("NPC|noura",          16.0,      0.5,      24.0, 180),   # South Campus Atrium entrance (Campus tour guide)
            ("NPC|yousef",        -46.0,      0.5,      78.0,  90),   # Near Exam Hall & Quiz portals on Campus
            ("NPC|chef",           32.0,      0.5,      67.5, -90),   # By the Biology Snack Promenade on Campus
            ("NPC|lifeguard",      12.0,      0.5,      98.0,   0),   # By the Campus Plaza Fountain
            ("NPC|cat_lady",       74.0,      0.5,      58.0, -90),   # Along the Campus Garden Walk near the cats
        ]
        for name, nx, ny, nz, yaw in npcs_abs:
            G.part(name, (2, 1, 2), (nx, ny, nz), (0, 0, 0), "SmoothPlastic", transp=1, collide=False, shadow=False,
                   rot=(0, yaw, 0))


def exam_hall():
    """indoor exam hall: rows of desks at the back, the invigilator's desk and a big screen in front,
    and four answer zones (A-D) whose floors open under the wrong answers"""
    with G.Group("ExamHall"):
        rect("ExamFloor", EX - 70, EX + 70, EY - 1, EY, EZ - 10, EZ + 90, (226, 220, 206), "WoodPlanks")
        rect("ExamCeiling", EX - 70, EX + 70, EY + 40, EY + 41, EZ - 90, EZ + 90, (246, 244, 240), "SmoothPlastic")
        for (a, b, c_, d) in ((EX - 71, EX - 70, EZ - 90, EZ + 90), (EX + 70, EX + 71, EZ - 90, EZ + 90)):
            rect("ExamWall", a, b, EY - 40, EY + 40, c_, d, (236, 232, 222), "SmoothPlastic")
        rect("ExamWallBack", EX - 70, EX + 70, EY - 40, EY + 40, EZ + 90, EZ + 91, (236, 232, 222), "SmoothPlastic")
        rect("ExamWallFront", EX - 70, EX + 70, EY - 40, EY + 40, EZ - 91, EZ - 90, (60, 66, 80), "SmoothPlastic")
        for x in range(-56, 57, 28):
            for z in (10, 40, 70):
                C5.light_panel(EX + x, EY + 39.4, EZ + z, 14, 5, 1.6, 44)
        # student desks at the back (waiting area)
        for r in range(4):
            for c in range(7):
                x, z = EX - 48 + c * 16, EZ + 30 + r * 14
                box("Desk", (8, 0.6, 4), (x, EY + 3.4, z), (196, 150, 104), "WoodPlanks")
                box("DeskLegs", (7, 3.2, 0.6), (x, EY + 1.6, z), (70, 70, 76), "Metal", collide=False)
                box("Chair", (3, 0.5, 3), (x, EY + 2.2, z + 3.6), (60, 110, 86), "SmoothPlastic", collide=False)
                box("ChairBack", (3, 3, 0.4), (x, EY + 3.9, z + 5.0), (60, 110, 86), "SmoothPlastic", collide=False)
                box("Paper", (2.4, 0.06, 3), (x - 1.5, EY + 3.72, z), (250, 250, 248), "SmoothPlastic", collide=False)
        # the board / screen and the clock
        G.part("ExamScreen", (90, 26, 1), (EX, EY + 22, EZ - 89), (20, 26, 38), "SmoothPlastic",
               text=dict(face="Back", text="📝 قاعة الاختبارات\nقف على الجواب الصح قبل لا يخلص الوقت", color=(255, 255, 255),
                         bg=(20, 34, 54), bg_t=0.0))
        G.part("ExamClock", (1, 8, 8), (EX + 56, EY + 30, EZ - 89), (250, 250, 248), "SmoothPlastic", shape="Cylinder",
               rot=(0, 90, 0), text=dict(face="Right", text="⏰", color=(30, 30, 30), bg=(250, 250, 248), bg_t=0.0))
        box("InvigilatorDesk", (16, 4, 5), (EX - 50, EY + 2, EZ - 70), (150, 104, 66), "WoodPlanks")
        G.part("NPC|invigilator", (2, 1, 2), (EX - 50, EY + 0.5, EZ - 76), (0, 0, 0), "SmoothPlastic", transp=1, collide=False,
               shadow=False, rot=(0, 0, 0))
        cols = {"A": (230, 90, 80), "B": (80, 150, 240), "C": (90, 200, 110), "D": (240, 200, 70)}
        rect("ExamApron", EX - 70, EX + 70, EY - 1, EY, EZ - 27, EZ - 10, (226, 220, 206), "WoodPlanks")
        for (a, b) in ((EX - 70, EX - 58), (EX + 58, EX + 70)):
            rect("ExamSideFloor", a, b, EY - 1, EY, EZ - 55, EZ - 27, (226, 220, 206), "WoodPlanks")
        for i, L in enumerate("ABCD"):
            x = EX - 43.5 + i * 29
            z = EZ - 41
            G.part("ExamTrap|" + L, (28, 1, 28), (x, EY - 0.5, z), cols[L], "SmoothPlastic",
                   text=dict(face="Top", text=L, color=(255, 255, 255), bg=cols[L], bg_t=1.0))
            G.part("ExamZone|" + L, (28, 10, 28), (x, EY + 5, z), cols[L], "SmoothPlastic", transp=1, collide=False, shadow=False)
            box("ZoneRim", (28.2, 0.12, 28.2), (x, EY + 0.06, z), (255, 255, 255), "Neon", collide=False, shadow=False, transp=0.5)
            G.part("ExamLetter|" + L, (26, 7, 0.4), (x, EY + 10, z - 14.6), cols[L], "SmoothPlastic", collide=False,
                   text=dict(face="Back", text=L, color=(255, 255, 255), bg=cols[L], bg_t=0.0))
        for k in range(5):   # solid divider strips between / beside the zones (standing on one = no answer)
            x = EX - 58.5 + k * 29
            rect("ZoneDivider", x - 0.5, x + 0.5, EY - 1, EY + 0.15, EZ - 55, EZ - 27, (255, 255, 255), "Neon")
        rect("ExamFrontRail", EX - 70, EX + 70, EY, EY + 4, EZ - 56, EZ - 55, (200, 230, 245), "Glass", transp=0.5)
        rect("ExamFrontRailTop", EX - 70, EX + 70, EY + 4, EY + 4.4, EZ - 56.2, EZ - 54.8, (60, 66, 80), "Metal")
        rect("ExamPitFloor", EX - 60, EX + 60, EY - 60, EY - 58, EZ - 56, EZ - 24, (80, 200, 120), "Neon")   # "retake" slime
        G.part("ExamPitCatch", (130, 4, 40), (EX, EY - 50, EZ - 40), (0, 0, 0), "SmoothPlastic", transp=1, collide=False)
        rect("ExamDivider", EX - 60, EX + 60, EY, EY + 0.12, EZ - 27, EZ - 26, (60, 66, 80), "Neon", collide=False)  # start line
        # v52 Anti-Exploit Spectator Barrier: closes once Q1 locks so eliminated/late players cannot enter active answer zones mid-exam
        G.part("ExamActiveBarrier", (138, 12, 0.8), (EX, EY + 6, EZ - 26.5), (120, 210, 255), "Glass", transp=1.0, collide=False,
               shadow=False)
        G.part("ExamSpawn", (10, 1, 10), (EX, EY + 0.5, EZ + 10), (0, 0, 0), "SmoothPlastic", transp=1, collide=False)
        G.part("Portal|HQ", (12, 12, 0.6), (EX - 9, EY + 6.2, EZ + 88), (120, 255, 200), "Neon", transp=0.45, collide=False,
               shadow=False)
        sign("ExamExitHQ", "↩ مقر النادي", (EX - 9, EY + 14, EZ + 87.6), (11, 2.4, 0.4), "Front", bg=GREEN)
        G.part("Portal|Campus", (12, 12, 0.6), (EX + 9, EY + 6.2, EZ + 88), (255, 190, 120), "Neon", transp=0.45, collide=False,
               shadow=False)
        sign("ExamExitCampus", "↩ كلية العلوم", (EX + 9, EY + 14, EZ + 87.6), (11, 2.4, 0.4), "Front", bg=(150, 95, 35))
        sign("ExamRules", "طريقة الاختبار:\n1) ادخل منطقة الإجابات قبل قفل الجولة\n2) قف على الجواب (A B C D)\n3) المغادرة أثناء الجولة تستبعدك للجولة القادمة!",
             (EX + 69.4, EY + 12, EZ + 20), (0.4, 14, 28), "Left", bg=(30, 50, 70))


def arcade():
    """minigames hall: a lobby with the Chaos Campus arenas around it"""
    import chaos_gen as CG
    with G.Group("Arcade"):
        disc("ArcadeFloor", AX, AY - 1, AZ, 90, 2, (110, 92, 150), "SmoothPlastic")
        disc("ArcadeRim", AX, AY - 0.6, AZ, 91, 0.8, (120, 255, 200), "Neon", collide=False, shadow=False)
        for i in range(10):
            a = i * 2 * math.pi / 10
            vcyl("ArcadePillar", AX + 40 * math.cos(a), AY, AY + 14, AZ + 40 * math.sin(a), 3, PASTEL[i % 5], "SmoothPlastic")
            ball("ArcadeLamp", AX + 40 * math.cos(a), AY + 15.5, AZ + 40 * math.sin(a), 3, PASTEL[i % 5], "Neon", collide=False,
                 shadow=False, light=(1, 22, PASTEL[i % 5]))
        G.part("ArcadeLobby", (90, 30, 90), (AX, AY + 14, AZ), (0, 0, 0), "SmoothPlastic", transp=1, collide=False, shadow=False)
        G.part("ArcadeSpawn", (10, 1, 10), (AX, AY + 0.5, AZ + 12), (0, 0, 0), "SmoothPlastic", transp=1, collide=False)
        sign("ArcadeTitle", "🎮 محطة الألعاب | Chaos Campus\nكل جولة لعبة + طفرة عشوائية 🧬", (AX, AY + 16, AZ - 30), (34, 9, 0.6), "Back",
             bg=(80, 30, 110))
        G.part("ArcadeBoard", (26, 16, 0.6), (AX - 24, AY + 9, AZ - 22), (20, 24, 34), "SmoothPlastic", rot=(0, 35, 0),
               text=dict(face="Back", text="🏆", color=(255, 236, 160), bg=(20, 28, 44), bg_t=0.0))
        G.part("Portal|HQ", (10, 12, 0.6), (AX, AY + 6.2, AZ + 40), (120, 255, 200), "Neon", transp=0.45, collide=False,
               shadow=False)
        sign("ArcadeExit", "↩ مقر النادي", (AX, AY + 14, AZ + 40.4), (10, 2.2, 0.4), "Front", bg=GREEN)
        G.part("Portal|Campus", (10, 12, 0.6), (AX + 16, AY + 6.2, AZ + 40), (255, 190, 120), "Neon", transp=0.45, collide=False,
               shadow=False)
        sign("ArcadeExitCampus", "↩ كلية العلوم", (AX + 16, AY + 14, AZ + 40.4), (10, 2.2, 0.4), "Front", bg=(150, 95, 35))
        # v39: door to the puzzle rooms, next to the exit
        G.part("Portal|Puzzle", (8, 12, 0.6), (AX - 18, AY + 6.2, AZ + 40), (255, 200, 90), "Neon", transp=0.45, collide=False,
               shadow=False)
        sign("ArcadePuzzleSign", "🧩 غرف الألغاز", (AX - 18, AY + 14, AZ + 40.4), (10, 2.2, 0.4), "Front", bg=(110, 70, 150))
    CG.Y = AY
    CG.petri_floor(AX + 300, AZ)
    CG.atp_rush(AX - 300, AZ)
    CG.enzyme_sweeper(AX, AZ + 300)
    CG.last_cell(AX, AZ - 300)   # v37: Last Cell Standing
    CG.lab_rush(AX - 300, AZ + 300)   # v38: Lab Rush (co-op)
    CG.cell_control_room(AX, AZ - 650)   # v39: first puzzle room


def exam_hall_dressing():
    """v22: make the exam hall read as a College of Science lecture hall (no new Light objects; glow comes from Neon)"""
    WOOD, TRIM, FRAME = (150, 104, 66), (96, 64, 40), (70, 52, 38)
    with G.Group("ExamHallDressing"):
        # wood wainscot + trim along both side walls and the back wall
        for side in (-1, 1):
            x = EX + side * 69.6
            box("Wainscot", (0.5, 8, 178), (x, EY + 4, EZ), WOOD, "WoodPlanks", collide=False)
            box("WainscotTrim", (0.8, 0.8, 178), (x, EY + 8.3, EZ), TRIM, "Wood", collide=False)
        box("WainscotBack", (138, 8, 0.5), (EX, EY + 4, EZ + 89.6), WOOD, "WoodPlanks", collide=False)
        box("WainscotBackTrim", (138, 0.8, 0.8), (EX, EY + 8.3, EZ + 89.4), TRIM, "Wood", collide=False)
        # tall daylight windows on both side walls (Neon panes = bright without extra lights)
        for side in (-1, 1):
            x = EX + side * 69.5
            for z in ((-62, -30, 2, 34, 66) if side < 0 else (-62, -30, 66)):   # +x side keeps the rules board clear
                box("WindowPane", (0.3, 18, 11), (x, EY + 22, EZ + z), (205, 228, 245), "Neon", transp=0.15, collide=False,
                    shadow=False)
                box("WindowFrameV", (0.6, 19, 0.8), (x, EY + 22, EZ + z), FRAME, "Wood", collide=False)
                box("WindowFrameH", (0.6, 0.8, 12), (x, EY + 22, EZ + z), FRAME, "Wood", collide=False)
                box("WindowSill", (1.6, 0.8, 13), (x - side * 0.6, EY + 12.6, EZ + z), (240, 236, 226), "Marble", collide=False)
        # wooden ceiling beams
        for z in range(-75, 90, 20):   # between the light panels (z 10/40/70)
            box("CeilingBeam", (140, 1.6, 2.2), (EX, EY + 39.2, EZ + z), TRIM, "Wood", collide=False)
        # hall title over the screen
        sign("HallTitle", "كلية العلوم • قاعة الاختبارات\nCollege of Science • Exam Hall", (EX, EY + 37.6, EZ - 89.3),
             (64, 4.2, 0.4), "Back", color=(255, 236, 190), bg=(54, 38, 26))
        # science posters (short, accurate facts) on the side walls
        posters = [
            (-1, -46, "🧬 DNA\nحلزون مزدوج من سلسلتين", (36, 70, 120)),
            (-1, 50, "🌿 البناء الضوئي\nCO₂ + ماء + ضوء ← جلوكوز + O₂", (40, 110, 70)),
            (1, -46, "🔬 الخلية\nأصغر وحدة حيّة", (110, 50, 120)),
            (1, 52, "🦠 البكتيريا\nبعضها يتضاعف كل 20 دقيقة\nبالظروف المثالية", (150, 80, 40)),
        ]
        for side, z, text, col in posters:
            x = EX + side * 69.2
            box("PosterFrame", (0.4, 11, 15), (x, EY + 22, EZ + z), FRAME, "Wood", collide=False)
            sign("Poster", text, (x - side * 0.25, EY + 22, EZ + z), (0.3, 10, 14), "Right" if side < 0 else "Left",
                 bg=col)
        # green carpet runner down the aisle to the answer zones
        box("AisleRunner", (6, 0.08, 98), (EX + 8, EY + 0.05, EZ + 40), (30, 90, 62), "Fabric", collide=False)


def arcade_dressing():
    """v22: the arcade is a giant cell. Lipid-bilayer rim, floating organelles, a cytoplasm haze below,
    and glowing signposts pointing at the three arenas that float in the distance."""
    with G.Group("ArcadeDressing"):
        # cytoplasm haze under the lobby so it no longer floats in an empty sky
        disc("Cytoplasm", AX, AY - 40, AZ, 900, 1, (232, 170, 230), "Neon", transp=0.82, collide=False, shadow=False)
        # phospholipid bilayer around the lobby rim: two rings of heads with short tails
        n = 44
        for i in range(n):
            a = i * 2 * math.pi / n
            for k, (r, y) in enumerate(((44.6, AY + 0.6), (44.6, AY - 2.4))):
                x, z = AX + r * math.cos(a), AZ + r * math.sin(a)
                ball("LipidHead", x, y, z, 1.8, (255, 196, 120) if (i + k) % 2 else (255, 150, 170), "SmoothPlastic",
                     collide=False, shadow=False)
            vcyl("LipidTail", AX + 44.6 * math.cos(a), AY - 1.9, AY + 0.1, AZ + 44.6 * math.sin(a), 0.5, (250, 230, 190),
                 "SmoothPlastic", collide=False, shadow=False)
        # floating organelles around the lobby
        # nucleus with nucleolus
        ball("Nucleus", AX - 70, AY + 34, AZ - 80, 34, (150, 110, 220), "Glass", transp=0.35, collide=False, shadow=False)
        ball("Nucleolus", AX - 70, AY + 34, AZ - 80, 12, (90, 50, 170), "Neon", collide=False, shadow=False)
        # mitochondria: capsule + inner crista stripes
        for (x, y, z, yaw) in ((AX + 75, AY + 20, AZ - 60, 30), (AX + 85, AY + 42, AZ + 40, -20), (AX - 90, AY + 18, AZ + 55, 70)):
            G.part("Mitochondrion", (22, 9, 9), (x, y, z), (255, 140, 70), "SmoothPlastic", shape="Cylinder",
                   rot=(0, yaw, 0), collide=False, shadow=False)
            rad = math.radians(yaw)
            for e in (-1, 1):
                ball("MitoEnd", x + e * 11 * math.cos(rad), y, z - e * 11 * math.sin(rad), 9, (255, 140, 70), "SmoothPlastic",
                     collide=False, shadow=False)
            for q in (-6, -2, 2, 6):
                G.part("Crista", (0.8, 7, 7.6), (x + q * math.cos(rad), y, z - q * math.sin(rad)), (255, 210, 120), "Neon",
                       rot=(0, yaw, 0), collide=False, shadow=False)
        # golgi stack
        for q in range(5):
            disc("Golgi", AX + 30, AY + 52 + q * 2.2, AZ - 95, 18 - q * 1.6, 1.2, (120, 200, 255), "Neon", transp=0.1,
                 collide=False, shadow=False)
        # ribosomes sprinkled in the air
        for q in range(16):
            a = q * 2.399
            r = 60 + (q * 13) % 50
            ball("Ribosome", AX + r * math.cos(a), AY + 10 + (q * 7) % 40, AZ + r * math.sin(a), 2.4, (110, 230, 160), "Neon",
                 collide=False, shadow=False)
        # signposts pointing at the arenas that float in the distance
        arenas = (((1, 0), "🧫 أرضية بتري\nPetri Floor"), ((-1, 0), "⚡ سباق ATP\nATP Rush"), ((0, 1), "🧹 كانسة الإنزيم\nEnzyme Sweeper"),
                  ((0, -1), "🦠 آخر خلية صامدة\nLast Cell Standing"),
                  ((-0.7, 0.7), "🧪 مختبر الفوضى\nLab Rush"))
        for (dx, dz), text in arenas:
            x, z = AX + dx * 36 + (16 if dz else 0), AZ + dz * 36   # keep clear of the exit portal at z+40
            vcyl("ArenaSignPost", x, AY, AY + 9, z, 0.8, (60, 50, 80), "Metal", collide=False)
            if dx:
                sign("ArenaSign", text, (x, AY + 10.5, z), (0.4, 4, 13), "Right" if dx < 0 else "Left", bg=(80, 30, 110))
            else:
                sign("ArenaSign", text, (x, AY + 10.5, z), (13, 4, 0.4), "Front" if dz > 0 else "Back", bg=(80, 30, 110))
            # dotted glowing trail from the rim out towards the arena
            for q in range(1, 9):
                d = 46 + q * 9
                ball("ArenaTrail", AX + dx * d + (16 if dz else 0), AY - 0.5, AZ + dz * d, 1.6, (120, 255, 200), "Neon", collide=False, shadow=False)


def course_backdrop():
    """v23: a soft sea of clouds under the whole parkour course (z -26..8915 at x 12000) so the zones float above
    something instead of an empty void. 5 large glowing slabs (parts max 2048 studs per axis) + cloud puffs."""
    CX = 12000.0
    with G.Group("CourseBackdrop"):
        for k in range(5):
            z0 = -400 + k * 1960
            box("CloudSea", (1600, 1, 1960), (CX, -120, z0 + 980), (214, 230, 248), "Neon", transp=0.82, collide=False,
                shadow=False)
        for k in range(36):
            z = -200 + k * 255
            for side in (-1, 1):
                d = 46 + (k * 37) % 40
                x = CX + side * (120 + (k * 53) % 160)
                ball("CloudPuff", x, -112 + (k % 4) * 6, z + side * 60, d, (250, 252, 255), "SmoothPlastic", collide=False,
                     shadow=False)
                ball("CloudPuff", x + side * d * 0.55, -114 + (k % 3) * 5, z + side * 60 + 9, d * 0.7, (244, 248, 255),
                     "SmoothPlastic", collide=False, shadow=False)


def course_finish_exit():
    """v52: finish arch at Checkpoint_100 with portals returning to Club HQ and KU College of Science Campus."""
    X, Y, Z = 11998.5, 234.4, 8922.0   # Checkpoint_100: centre (11998.5, 233.9, 8914.9), 20x1x20
    with G.Group("CourseFinish"):
        for s_ in (-1, 1):
            box("FinishPillar", (2, 16, 2), (X + s_ * 7, Y + 8, Z), (250, 248, 240), "SmoothPlastic")
            ball("FinishLamp", X + s_ * 7, Y + 17, Z, 2.6, (255, 220, 90), "Neon", collide=False, shadow=False)
        box("FinishBeam", (16, 2, 2.4), (X, Y + 16.6, Z), (24, 80, 56), "SmoothPlastic")
        G.part("Portal|HQ", (12, 14, 0.6), (X, Y + 7.2, Z), (120, 255, 200), "Neon", transp=0.4, collide=False,
               shadow=False)
        sign("FinishSign", "🏁 خلصت الـ100 مرحلة!\n↩ ادخل البوابة لمقر النادي", (X, Y + 21, Z), (18, 5, 0.5), "Front",
             bg=(24, 80, 56))


LX, LY, LZ = 6000.0, 300.0, 6000.0   # research lab world


def research_lab():
    """v52: Rebuilt BSC Research Institute interior with realistic wet-lab equipment, safety infrastructure, and
    multi-step interactive benches (Microscope, PCR, Gel Electrophoresis, Light Microscopy, Gram Staining)."""
    WALL, WHITE, EPOXY = (236, 238, 240), (250, 250, 248), (226, 232, 230)
    GRN, DARK, WOOD = (24, 80, 56), (40, 46, 52), (150, 110, 74)

    def at(x, y, z):
        return (LX + x, LY + y, LZ + z)

    def r(name, x0, x1, y0, y1, z0, z1, col, mat="SmoothPlastic", **kw):
        rect(name, LX + x0, LX + x1, LY + y0, LY + y1, LZ + z0, LZ + z1, col, mat, **kw)

    with G.Group("ResearchLab"):
        # ---- shell
        r("LabFloor", -72, 72, -1, 0, -52, 52, EPOXY, "SmoothPlastic")
        r("LabCeiling", -72, 72, 26, 27, -52, 52, WHITE)
        for (a, b, c_, d) in ((-73, -72, -52, 52), (72, 73, -52, 52)):
            r("LabWall", a, b, -1, 26, c_, d, WALL)
        r("LabWallN", -72, 72, -1, 26, -53, -52, WALL)
        r("LabWallS", -72, 72, -1, 26, 52, 53, WALL)
        for x0 in (-72, 71.6):
            r("AccentStripe", x0, x0 + 0.4, 9, 10, -52, 52, GRN, collide=False)
        r("AccentStripeN", -72, 72, 9, 10, -51.6, -51.2, GRN, collide=False)
        # overhead cleanroom ventilation & gas piping along the ceiling
        for x in (-42, 42):
            r("CleanroomDuct", x - 2.2, x + 2.2, 23.5, 25.4, -48, 48, (206, 212, 218), "Metal", collide=False)
        # floor guide lines from the entrance to each wing
        r("GuideLine", -1, 1, 0, 0.06, -10, 50, (60, 180, 120), "Neon", collide=False)
        r("GuideLineW", -45, 0, 0, 0.06, 9, 11, (60, 180, 120), "Neon", collide=False)
        r("GuideLineE", 0, 45, 0, 0.06, 9, 11, (80, 160, 230), "Neon", collide=False)
        for x in (-40, 0, 40):
            for z in (-28, 12):
                C5.light_panel(LX + x, LY + 25.6, LZ + z, 18, 4, 1.0 if x == 0 else 0.0001, 40 if x == 0 else 1)
        # ---- entrance + portals back to HQ and Campus
        G.part("LabSpawn", (10, 1, 10), at(0, 0.5, 38), (0, 0, 0), "SmoothPlastic", transp=1, collide=False)
        G.part("Portal|HQ", (11, 13, 0.6), at(-8, 6.6, 51.2), (120, 255, 200), "Neon", transp=0.45, collide=False, shadow=False)
        sign("LabExitHQ", "↩ مقر النادي", at(-8, 14.5, 51.4), (10, 2.2, 0.4), "Front", bg=GRN)
        G.part("Portal|Campus", (11, 13, 0.6), at(8, 6.6, 51.2), (255, 190, 120), "Neon", transp=0.45, collide=False, shadow=False)
        sign("LabExitCampus", "↩ كلية العلوم", at(8, 14.5, 51.4), (10, 2.2, 0.4), "Front", bg=(150, 95, 35))
        sign("LabTitle", "🔬 معهد الأبحاث | BSC Research Institute", at(0, 19.5, 51.4), (40, 4, 0.4), "Front", bg=GRN)
        # ---- wet lab (west): three benches + realistic instruments
        sign("WetLab", "🧪 المختبر الرطب | Wet Lab", at(-71.6, 16, -5), (0.4, 3.4, 30), "Right", bg=(30, 70, 60))
        for z in (-30, -5, 20):
            r("Bench", -58, -26, 0, 3.6, z - 3, z + 3, (240, 240, 236), "Marble")
            r("BenchCabinet", -57.6, -26.4, 0, 3.2, z - 3.2, z - 2.8, WOOD, "WoodPlanks", collide=False)
            r("ReagentShelf", -58, -26, 7, 7.4, z + 2.2, z + 3, (220, 222, 224), "Metal", collide=False)
            # Micropipette stand & sterile tip box on every wet lab bench
            r("PipetteStand", -55.5, -53.5, 3.6, 5.8, z - 1.2, z - 0.4, (230, 234, 240), "SmoothPlastic", collide=False)
            r("TipBoxBlue", -52.5, -50.2, 3.6, 4.4, z - 1.6, z - 0.2, (70, 150, 235), "SmoothPlastic", collide=False)
            r("TipBoxYellow", -49.8, -47.8, 3.6, 4.3, z - 1.6, z - 0.2, (240, 200, 60), "SmoothPlastic", collide=False)
            for q in range(8):
                vcyl("Reagent", LX - 56 + q * 3.8, LY + 7.4, LY + 9.2, LZ + z + 2.6, 1.0,
                     [(80, 160, 230), (230, 120, 90), (120, 200, 120), (230, 200, 80)][q % 4], "Glass", transp=0.2, collide=False)
        # microscope (bench 1)
        r("LabStation|microscope", -44, -40, 3.6, 4.2, -32, -28, DARK, "Metal")
        r("ScopeArm", -42.6, -41.4, 4.2, 9.5, -28.8, -27.6, DARK, "Metal", collide=False)
        r("ScopeStage", -43.4, -40.6, 6, 6.4, -31, -28.6, (60, 64, 70), "Metal", collide=False)
        vcyl("ScopeObjective", LX - 42, LY + 6.6, LY + 8.4, LZ - 29.8, 0.7, (180, 184, 190), "Metal", collide=False)
        G.part("ScopeEyepiece", (2.6, 0.8, 0.8), at(-42, 9.8, -29.0), (50, 54, 60), "Metal", shape="Cylinder", rot=(0, 90, 60),
               collide=False)
        r("SlideBox", -37.5, -34.5, 3.6, 4.1, -31.2, -29.2, (245, 245, 240), "SmoothPlastic", collide=False)
        sign("ScopeLabel", "🔬 فحص وتصنيف الخلايا\nCell Classification", at(-34, 6.2, -32.9), (9.5, 2.4, 0.3), "Front", bg=(30, 70, 60))
        # PCR thermocycler (bench 2)
        r("LabStation|pcr", -46, -38, 3.6, 7.2, -8, -3, (210, 214, 220), "SmoothPlastic")
        r("PCRLid", -46.2, -37.8, 7.2, 7.8, -8.2, -2.8, (180, 186, 194), "SmoothPlastic", collide=False)
        r("PCRScreen", -44, -40, 4.6, 6.4, -8.25, -8.15, (60, 220, 140), "Neon", collide=False)
        # Ice bucket with Taq Polymerase & Master Mix tubes next to PCR
        r("IceBucket", -36.5, -33.0, 3.6, 5.2, -7.2, -3.8, (110, 195, 240), "SmoothPlastic", collide=False)
        r("IceTop", -36.2, -33.3, 5.2, 5.4, -6.9, -4.1, (225, 245, 255), "Neon", transp=0.25, collide=False)
        sign("PCRLabel", "🧬 تفاعل البوليميراز المتسلسل\nPCR Thermal Cycler", at(-34, 6.2, -7.9), (10, 2.4, 0.3), "Front", bg=(30, 70, 60))
        # gel electrophoresis (bench 3)
        r("LabStation|gel", -48, -38, 3.6, 5.2, 17, 22, (200, 230, 240), "Glass", transp=0.3)
        r("GelSlab", -47, -39, 4.2, 4.6, 17.6, 21.4, (90, 140, 255), "Neon", transp=0.35, collide=False)
        r("PowerSupply", -36, -32, 3.6, 6.2, 18, 21, (50, 54, 60), "SmoothPlastic", collide=False)
        r("LeadRed", -38, -36, 5.4, 5.6, 18.6, 18.9, (220, 50, 50), "SmoothPlastic", collide=False)
        r("LeadBlack", -38, -36, 5.4, 5.6, 20.1, 20.4, (20, 20, 22), "SmoothPlastic", collide=False)
        r("UVTransilluminator", -31.5, -27.0, 3.6, 5.0, 17.5, 21.5, (42, 38, 56), "Metal", collide=False)
        r("UVWindow", -31.0, -27.5, 5.0, 5.15, 18.0, 21.0, (175, 110, 255), "Neon", transp=0.25, collide=False)
        sign("GelLabel", "🧪 الفصل الكهربائي للـ DNA\nGel Electrophoresis", at(-30, 6.2, 17.1), (10.5, 2.4, 0.3), "Front", bg=(30, 70, 60))
        # v41: Light Microscopy lab bench (opens the full simulation: LightMicroscope.client)
        r("LabStation|lightmicro", -26, -12, 0, 3.6, 22, 28, (238, 238, 232), "Marble")
        r("ScopeBase2", -21, -17, 3.6, 4.4, 23.5, 26.5, (40, 44, 52), "Metal", collide=False)
        r("ScopeArm2", -19.6, -18.4, 4.4, 10, 25.4, 26.4, (40, 44, 52), "Metal", collide=False)
        r("ScopeStage2", -21, -17, 6.2, 6.6, 23.2, 25.6, (30, 32, 38), "Metal", collide=False)
        vcyl("ScopeObjective2", LX - 19, LY + 6.8, LY + 8.6, LZ + 24.4, 0.8, (190, 194, 200), "Metal", collide=False)
        G.part("ScopeTube2", (1.2, 3.6, 1.2), at(-19, 10.4, 24.8), (40, 44, 52), "Metal", rot=(-25, 0, 0), collide=False)
        ball("ScopeLamp2", LX - 19, LY + 5.0, LZ + 24.4, 1.2, (255, 240, 200), "Neon", collide=False, shadow=False)
        sign("LightMicroLabel", "🔬 مختبر المجهر الضوئي\nLight Microscopy", at(-19, 13.5, 28.2), (12, 3.4, 0.3), "Back",
             bg=(24, 80, 56))
        # v50: Gram Staining interactive lab bench (symmetrical on the north side of the wet lab)
        r("LabStation|gram", -26, -12, 0, 3.6, -33, -27, (238, 238, 232), "Marble")
        r("GramSink", -25, -21, 3.6, 4.3, -32, -28, (180, 192, 200), "Metal", collide=False)
        r("GramSlideRack", -20, -13, 3.6, 4.1, -31.5, -28.5, (60, 66, 74), "Metal", collide=False)
        for q, bcol in enumerate(((130, 60, 200), (190, 130, 40), (180, 220, 250), (230, 70, 120))):
            vcyl("GramReagent", LX - 19.2 + q * 1.8, LY + 4.1, LY + 6.1, LZ - 30.0, 0.75, bcol, "Glass", transp=0.15, collide=False)
        sign("GramLabLabel", "🧪 مختبر صبغة جرام\nGram Staining Lab", at(-19, 13.5, -33.2), (12, 3.4, 0.3), "Front",
             bg=(90, 40, 130))
        # ---- v52 Realistic Wet-Lab Perimeter Infrastructure (West Wall: Biosafety Cabinet, Incubator, Centrifuge, Autoclave, Safety Shower)
        # 1. Class II Biosafety Cabinet (Laminar Flow Hood)
        r("BiosafetyCabinet", -71, -61, 0, 16, -46, -34, (226, 232, 238), "Metal")
        r("BSCHepaHeader", -71, -60.5, 13.5, 16, -46, -34, (45, 115, 165), "Metal", collide=False)
        r("BSCSashGlass", -60.9, -60.6, 4.4, 12.6, -45, -35, (190, 225, 245), "Glass", transp=0.45, collide=False)
        r("BSCUVLight", -68, -63, 12.8, 13.2, -44, -36, (170, 135, 255), "Neon", transp=0.2, collide=False)
        sign("BSCSign", "🛡️ كابينة السلامة الحيوية (BSC Class II)", at(-60.4, 14.8, -40), (0.3, 1.8, 11), "Right", bg=(25, 75, 115))
        # 2. High-Speed Refrigerated Centrifuge & Vortex Prep Counter
        r("CentrifugeCounter", -71, -62, 0, 3.6, -24, -10, (238, 238, 234), "Marble")
        r("CentrifugeBody", -69.5, -63.5, 3.6, 6.8, -22, -16, (215, 222, 230), "Metal")
        disc("CentrifugeRotor", LX - 66.5, LY + 7.0, LZ - 19.0, 4.2, 0.4, (50, 60, 75), "Metal", collide=False)
        sign("CentrifugeSign", "🌀 جهاز الطرد المركزي\n14,000 RPM Centrifuge", at(-61.8, 8.2, -17), (0.3, 2.2, 11), "Right", bg=(40, 65, 95))
        # 3. CO2 Cell Culture Incubator & Autoclave Sterilizer
        r("CO2Incubator", -71, -63, 0, 12.5, -4, 6, (230, 234, 240), "Metal")
        r("IncubatorGlass", -62.9, -62.6, 1.5, 10.5, -2.8, 4.8, (180, 220, 230), "Glass", transp=0.4, collide=False)
        sign("IncubatorReadout", "🌡️ حاضنة الخلايا CO₂\n37.0°C • 5.0% CO₂", at(-62.5, 11.4, 1), (0.3, 1.6, 8.5), "Right", bg=(20, 85, 65))
        r("Autoclave", -71, -63, 0, 11.5, 10, 19, (195, 202, 210), "Metal")
        disc("AutoclaveWheel", LX - 62.6, LY + 6.0, LZ + 14.5, 3.2, 0.6, (40, 44, 50), "Metal", collide=False)
        sign("AutoclaveSign", "♨️ الأوتوكلاف (تعقيم بالبخار)\n121°C • 15 psi", at(-62.5, 10.5, 14.5), (0.3, 1.6, 8.5), "Right", bg=(140, 65, 30))
        # 4. Emergency Safety Shower & Eyewash Station
        vcyl("SafetyShowerPipe", LX - 68, LY, LY + 13.5, LZ + 34, 0.5, (240, 195, 40), "Metal", collide=False)
        disc("ShowerHead", LX - 68, LY + 12.8, LZ + 34, 3.0, 0.5, (40, 175, 95), "SmoothPlastic", collide=False)
        vcyl("EyewashBowl", LX - 68, LY + 3.2, LY + 4.0, LZ + 34, 2.4, (40, 175, 95), "Metal", collide=False)
        sign("Safety", "🚿 دُش الطوارئ وغسيل العيون\n🥽 التزم بالمعطف والقفازات والنظارة الواقية", at(-71.5, 14, 36), (0.3, 3.2, 16), "Right", bg=(30, 125, 70))
        # ---- computer lab (east)
        sign("CompLab", "💻 مختبر المعلوماتية الحيوية وتحليل الجينوم", at(71.6, 16, -5), (0.4, 3.4, 34), "Left", bg=(30, 50, 80))
        for row, z in enumerate((-20, -2, 16)):
            r("DeskRow", 22, 58, 0, 3, z - 2.5, z + 2.5, (238, 238, 232), "Marble")
            for k in range(4):
                x = 26 + k * 9
                r("Monitor", x - 2, x + 2, 3.8, 6.6, z - 1.4, z - 1.1, (20, 22, 26), "SmoothPlastic", collide=False)
                r("MonitorGlow", x - 1.8, x + 1.8, 4.0, 6.4, z - 1.05, z - 0.95,
                  [(70, 200, 240), (90, 230, 150), (200, 120, 240)][(k + row) % 3], "Neon", collide=False)
                box("Chair", (2.6, 0.6, 2.6), at(x, 2.0, z + 4.2), (40, 60, 90), "Fabric", collide=False)
        # the projects terminal (big screen)
        r("LabComputer", 30, 50, 0, 4, -44, -38, (50, 56, 64), "SmoothPlastic")
        r("TerminalScreen", 31, 49, 5, 15, -46.6, -46.2, (60, 200, 255), "Neon", transp=0.1, collide=False)
        sign("TerminalLabel", "💻 مشاريع المختبر: طوّر قدراتك بنقاط البحث", at(40, 17, -46.0), (22, 2.4, 0.3), "Back",
             bg=(30, 50, 80))
        for z in (-30, -15, 0, 15, 30):  # server racks
            r("Rack", 66, 71, 0, 12, z - 2.5, z + 2.5, (24, 26, 30), "SmoothPlastic")
            for q in range(5):
                r("RackLED", 65.8, 65.95, 2 + q * 2, 2.3 + q * 2, z - 1.5, z + 1.5,
                  (90, 255, 150) if q % 2 else (90, 170, 255), "Neon", collide=False)
        # ---- centre: DNA sculpture + bioreactors
        for q in range(46):
            a = q * 0.42
            y = 1 + q * 0.42
            for s_ in (0, math.pi):
                ball("Helix", LX + 4 * math.cos(a + s_), LY + y, LZ - 10 + 4 * math.sin(a + s_), 1.2,
                     (255, 90, 170) if s_ == 0 else (60, 200, 255), "Neon", collide=False, shadow=False)
            if q % 3 == 0:
                G.part("BasePair", (8, 0.35, 0.35), at(0, y, -10), (240, 240, 240), "SmoothPlastic",
                       rot=(0, -math.degrees(a), 0), collide=False, shadow=False)
        disc("HelixPlinth", LX, LY + 0.3, LZ - 10, 12, 0.6, (60, 66, 72), "Marble")
        for x in (14, 22):
            vcyl("Bioreactor", LX + x, LY, LY + 12, LZ + 30, 5, (225, 242, 250), "Glass", transp=0.78, collide=True)
            vcyl("Culture", LX + x, LY + 0.5, LY + 9, LZ + 30, 4.2, (110, 220, 120), "Neon", transp=0.3, collide=False)
        # ---- Batch Hall (north wall) + picker kiosk
        G.part("BatchBoard", (56, 20, 0.5), at(0, 13, -51.6), (30, 34, 40), "SmoothPlastic")
        r("BatchPicker", -3, 3, 0, 4.4, -42, -38, GRN, "SmoothPlastic")
        sign("BatchPickerLabel", "🎓 اختار دفعتك", at(0, 5.6, -37.9), (8, 1.8, 0.3), "Back", bg=GRN)


QX, QY, QZ = 0.0, 300.0, -6000.0   # science challenge center world
SPEC_COLORS = [(90, 170, 90), (210, 120, 70), (120, 190, 200), (230, 180, 60), (150, 110, 210), (110, 160, 60),
               (90, 100, 120), (60, 150, 220)]
SPEC_NAMES = ["بيولوجيا نبات", "بيولوجيا حيوان", "مايكروبيولوجي", "بايوكيمستري", "مولكلر",
              "الزراعة", "الأدلة الجنائية", "البايوتكنولوجي"]  # same order as Questions.luau / Shared/Zones


def quiz_center():
    """v52: مركز التحديات العلمية. Eight specialty booths (QuizKiosk|1..8, west + east galleries), the virtual practical
    bench (QuizKiosk|9, north), the group-challenge portal to the Exam Hall (east) and return portals to HQ & Campus (south)."""
    WALL, CREAM, WOOD, DARK = (232, 226, 214), (250, 246, 236), (122, 84, 52), (36, 40, 48)
    NAVY = (28, 44, 78)

    def at(x, y, z):
        return (QX + x, QY + y, QZ + z)

    def r(name, x0, x1, y0, y1, z0, z1, col, mat="SmoothPlastic", **kw):
        rect(name, QX + x0, QX + x1, QY + y0, QY + y1, QZ + z0, QZ + z1, col, mat, **kw)

    with G.Group("ChallengeCenter"):
        # ---- shell: warm library hall, wooden wainscot, coffered ceiling glow
        r("QuizFloor", -80, 80, -1, 0, -60, 60, (196, 180, 156), "Wood")
        r("QuizCarpet", -10, 10, 0, 0.08, -50, 56, (120, 40, 50), "Fabric", collide=False)
        r("QuizCeiling", -80, 80, 32, 33, -60, 60, CREAM)
        r("QuizWallW", -81, -80, -1, 32, -60, 60, WALL)
        r("QuizWallE", 80, 81, -1, 32, -60, 60, WALL)
        r("QuizWallN", -80, 80, -1, 32, -61, -60, WALL)
        r("QuizWallS", -80, 80, -1, 32, 60, 61, WALL)
        for (a, b) in ((-79.6, -79.2), (79.2, 79.6)):
            r("Wainscot", a, b, 0, 5, -60, 60, WOOD, "Wood", collide=False)
        r("WainscotN", -80, 80, 0, 5, -59.6, -59.2, WOOD, "Wood", collide=False)
        for x in (-48, 0, 48):
            for z in (-36, 0, 36):
                C5.light_panel(QX + x, QY + 31.6, QZ + z, 20, 6, 1.0 if x == 0 else 0.0001, 44 if x == 0 else 1)
        for x in (-30, 30):  # columns along the central aisle
            for z in (-40, -12, 16, 44):
                vcyl("QuizColumn", QX + x, QY, QY + 32, QZ + z, 3.2, CREAM, "Marble")
                r("ColumnBase", x - 2.2, x + 2.2, 0, 1, z - 2.2, z + 2.2, (210, 204, 190), "Marble")
        # ---- entrance (south): spawn + portals back to HQ and Campus
        G.part("QuizSpawn", (10, 1, 10), at(0, 0.5, 46), (0, 0, 0), "SmoothPlastic", transp=1, collide=False)
        G.part("Portal|HQ", (11, 13, 0.6), at(-8, 6.6, 59.2), (120, 255, 200), "Neon", transp=0.45, collide=False, shadow=False)
        sign("QuizExitHQ", "↩ مقر النادي", at(-8, 14.5, 59.4), (10, 2.2, 0.4), "Front", bg=NAVY)
        G.part("Portal|Campus", (11, 13, 0.6), at(8, 6.6, 59.2), (255, 190, 120), "Neon", transp=0.45, collide=False, shadow=False)
        sign("QuizExitCampus", "↩ كلية العلوم", at(8, 14.5, 59.4), (10, 2.2, 0.4), "Front", bg=(150, 95, 35))
        sign("QuizTitle", "🎓 مركز التحديات العلمية | Science Challenge Center", at(0, 25, -59.4), (60, 4.4, 0.4), "Back", bg=NAVY)
        sign("QuizHowTo", "اختار تخصصك ← حل 5 أسئلة ← 3 صح تفتح المستوى اللي بعده ⭐", at(0, 20, -59.4), (52, 2.6, 0.4),
             "Back", bg=(60, 70, 90))
        # ---- specialty booths: 4 west (facing east), 4 east (facing west)
        for i in range(8):
            west = i < 4
            z = (-40, -18, 4, 26)[i % 4]
            col = SPEC_COLORS[i]
            s_ = -1 if west else 1
            wx = 79.4 * s_                       # wall surface
            face = "Right" if west else "Left"
            r("BoothPanel", min(wx, wx - s_ * 0.6), max(wx, wx - s_ * 0.6), 0, 18, z - 8, z + 8, col, "SmoothPlastic", collide=False)
            sign("BoothTitle", SPEC_NAMES[i], (QX + wx - s_ * 0.8, QY + 15, QZ + z), (0.3, 2.6, 15), face, bg=(30, 34, 44))
            # shelf of books behind the console
            r("BoothShelf", min(wx - s_ * 0.6, wx - s_ * 3), max(wx - s_ * 0.6, wx - s_ * 3), 5.5, 6, z - 7, z + 7, WOOD, "Wood",
              collide=False)
            for k in range(9):
                bz = z - 6.2 + k * 1.5
                r("Book", min(wx - s_ * 0.8, wx - s_ * 2.6), max(wx - s_ * 0.8, wx - s_ * 2.6), 6, 6 + 1.6 + (k % 3) * 0.3,
                  bz - 0.6, bz + 0.6, [col, (240, 236, 220), (60, 70, 90)][k % 3], "SmoothPlastic", collide=False)
            # console: the kiosk part itself + a glowing screen toward the aisle
            kx = (79.4 - 9) * s_
            r("QuizKiosk|%d" % (i + 1), kx - 1.6, kx + 1.6, 0, 4.2, z - 2.6, z + 2.6, DARK, "Metal")
            r("KioskScreen", min(kx - s_ * 1.7, kx - s_ * 1.8), max(kx - s_ * 1.7, kx - s_ * 1.8), 4.4, 8.4, z - 2.4, z + 2.4,
              col, "Neon", collide=False)
            r("KioskRing", kx - 4, kx + 4, 0, 0.1, z - 4, z + 4, col, "Neon", transp=0.4, collide=False)
        # ---- virtual practical bench (north)
        r("PracticalBench", -16, 16, 0, 3.8, -52, -44, (238, 238, 232), "Marble")
        r("QuizKiosk|9", -2.5, 2.5, 3.8, 5, -48, -45, DARK, "Metal")
        r("PracticalScreen", -10, 10, 7, 16, -55.6, -55.2, (90, 220, 160), "Neon", transp=0.1, collide=False)
        sign("PracticalLabel", "🧪 التحديات العملية: تكبير المجهر • مربع بانيت • التخفيف • نمو البكتيريا • DNA", at(0, 17.6, -55.0),
             (40, 2.2, 0.3), "Back", bg=(30, 70, 60))
        for q in range(6):
            vcyl("Flask", QX - 13 + q * 2.2 if q < 3 else QX + 6.4 + (q - 3) * 2.2, QY + 3.8, QY + 6, QZ - 50, 0.8,
                 [(80, 160, 230), (230, 120, 90), (120, 200, 120)][q % 3], "Glass", transp=0.25, collide=False)
        # ---- group challenge: portal to the Exam Hall (east wall, near the entrance)
        G.part("Portal|Exam", (0.6, 13, 12), at(79.2, 6.6, 46), (255, 210, 80), "Neon", transp=0.45, collide=False, shadow=False)
        sign("GroupLabel", "👥 التحدي الجماعي ← قاعة الاختبارات", at(79.0, 15, 46), (0.3, 2.4, 16), "Left", bg=(150, 110, 20))
        # ---- centre: reading tables + a globe of knowledge
        disc("GlobePlinth", QX, QY + 0.4, QZ - 8, 13, 0.8, (210, 204, 190), "Marble")
        ball("KnowledgeGlobe", QX, QY + 7, QZ - 8, 8, (150, 205, 255), "Neon", transp=0.6, collide=False, shadow=False)
        ball("GlobeCore", QX, QY + 7, QZ - 8, 3, (255, 220, 120), "Neon", collide=False, shadow=False)
        for x in (-18, 18):
            for z in (-28, 20):
                r("ReadingTable", x - 5, x + 5, 0, 3, z - 2.5, z + 2.5, WOOD, "Wood")
                for dz in (-4, 4):
                    box("ReadingChair", (2.4, 0.6, 2.4), at(x, 2.0, z + dz), (120, 40, 50), "Fabric", collide=False)


def build():
    island_layer()
    research_lab()
    quiz_center()
    import gameshow
    gameshow.build()   # v40: BSC Game Show studio at (0, 300, -7000)
    course_backdrop()
    course_finish_exit()
    exam_hall()
    exam_hall_dressing()
    arcade()
    arcade_dressing()
