"""BSC Club HQ: the game's lobby, a world of its own (players spawn here and reach everything by portal).

Layout (local coords, floor y=0, players spawn facing north = -Z):
  north wall   giant BSC logo + the 8 parkour zone gates and the Continue gate
  west side    quiz corner (8 specialty stations)
  east side    Cart Ride portal + Cell Train portal
  south wall   portal to the College of Science campus, Discord + codes boards
  around       club-office furniture (wood desk, shelves, trophies, DNA art), sofas, plants, mascot
"""
import math

import genmap as G
import genmap5 as C5
import genmap3 as C3
import bsc_art as A

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign
rect = C5.rect

HQ_OFFSET = (0.0, 600.0, -12000.0)
X, Z, H = 80.0, 72.0, 52.0
WALL = (246, 244, 240)
WOOD = (176, 128, 84)
CLUB_GREEN = (24, 80, 56)
PASTELS = [c for (_, c, _) in A.HEXES]


def portal(name, x, z, w, h, col, title, face_nx, face_nz, sub=""):
    """standing portal frame; the neon sheet teleports on touch"""
    along_x = abs(face_nz) > 0.5           # sheet spans x when it faces north/south
    size = (w, h, 0.6) if along_x else (0.6, h, w)
    for s_ in (-1, 1):
        px, pz = (x + s_ * (w / 2 + 1.2), z) if along_x else (x, z + s_ * (w / 2 + 1.2))
        box("PortalPost", (2.4, h + 3, 2.4), (px, (h + 3) / 2, pz), (60, 64, 74), "SmoothPlastic")
        box("PortalGlow", (2.6, h + 3, 0.4) if along_x else (0.4, h + 3, 2.6), (px + face_nx * 1.3, (h + 3) / 2, pz + face_nz * 1.3),
            col, "Neon", collide=False, shadow=False)
    box("PortalTop", (w + 5, 2.4, 2.4) if along_x else (2.4, 2.4, w + 5), (x, h + 3.6, z), (60, 64, 74), "SmoothPlastic")
    G.part(name, size, (x, h / 2 + 0.2, z), col, "Neon", transp=0.45, collide=False, shadow=False)
    face = {(0, 1): "Back", (0, -1): "Front", (1, 0): "Right", (-1, 0): "Left"}[(int(round(face_nx)), int(round(face_nz)))]
    ssize = (w + 4, 4.4, 0.5) if along_x else (0.5, 4.4, w + 4)
    sign("PortalSign", title + (("\n" + sub) if sub else ""), (x + face_nx * 0.6, h + 7.6, z + face_nz * 0.6), ssize, face,
         bg=tuple(max(0, v - 110) for v in col))


def shell():
    rect("HQFloor", -X, X, -1, 0, -Z, Z, (236, 226, 208), "WoodPlanks")
    # pastel hexagon inlay ring around the spawn (pattern only — the logo itself is never on the floor)
    for i in range(16):
        a = i * 2 * math.pi / 16
        A.floor_hex(22 * math.sin(a), 0.04, 30 + 22 * math.cos(a), 3.0, PASTELS[i % 5])
    rect("Carpet", -10, 10, 0, 0.06, 20, 42, (214, 232, 220), "SmoothPlastic", collide=False)
    rect("Aisle", -6, 6, 0, 0.05, -60, 20, (226, 236, 230), "SmoothPlastic", collide=False)
    rect("Ceiling", -X, X, H, H + 1, -Z, Z, (250, 250, 248), "SmoothPlastic")
    # walls; east/west get tall window bands so the sky shows
    rect("WallN", -X, X, 0, H, -Z - 1, -Z, WALL, "SmoothPlastic")
    # v52: the south wall opens into the World Gateway Hall (doorway x -12..12, 24 tall)
    rect("WallS", -X, -12, 0, H, Z, Z + 1, WALL, "SmoothPlastic")
    rect("WallS", 12, X, 0, H, Z, Z + 1, WALL, "SmoothPlastic")
    rect("WallS", -12, 12, 24, H, Z, Z + 1, WALL, "SmoothPlastic")
    for sx in (-1, 1):
        x0 = sx * X
        rect("WallLow", min(x0, x0 + sx), max(x0, x0 + sx), 0, 20, -Z, Z, WALL, "SmoothPlastic")
        rect("WallHigh", min(x0, x0 + sx), max(x0, x0 + sx), 40, H, -Z, Z, WALL, "SmoothPlastic")
        rect("Window", min(x0, x0 + sx) + 0.3, max(x0, x0 + sx) - 0.3, 20, 40, -Z, Z, (190, 225, 240), "Glass", transp=0.55)
        for z in range(-64, 65, 16):
            box("Mullion", (1.4, 20, 1.2), (x0, 30, z), (210, 212, 216), "SmoothPlastic", collide=False)
    # club colour ribbon around the hall + soft lighting
    for (a, b, c_, d) in ((-X, X, -Z + 0.1, -Z + 0.4), (-X, X, Z - 0.4, Z - 0.1)):
        rect("Ribbon", a, b, 18.6, 19.4, c_, d, CLUB_GREEN, "SmoothPlastic", collide=False)
    for x in range(-60, 61, 30):
        for z in range(-48, 61, 24):
            C5.light_panel(x, H - 0.4, z, 12, 5, 1.5, 44)
    for q in range(5):
        x = -48 + q * 24
        vcyl("PendantCord", x, 30, H, 30, 0.2, (40, 40, 44), "SmoothPlastic", collide=False)
        G.part("Pendant", (3.4, 3.4, 3.4), (x, 29, 30), PASTELS[q], "Neon", shape="Ball", collide=False, shadow=False,
               light=(0.9, 24, PASTELS[q]))


def north_wall():
    A.logo(-5, 38, -Z + 1.2, R=5.0, nx=0.0, nz=1.0, name=False)
    sign("ClubTitle", "نادي العلوم البيولوجية\nBiological Sciences Club\nKuwait University", (46, 38, -Z + 0.8), (30, 10, 0.5),
         "Back", bg=CLUB_GREEN)
    sign("HQTitle", "مقر النادي 🏠\nBSC Headquarters", (-52, 38, -Z + 0.8), (24, 8, 0.5), "Back", bg=(110, 70, 150))
    # parkour gates (names kept: the server/clients look for Portal|Zone|i and GateLamp|i)
    import genmap8 as G8
    zg = -Z + 8
    xs = [-66, -50, -34, -18, 18, 34, 50, 66]
    starts = G8.zone_starts()
    sign("GatesTitle", "بوابات الباركور — كل منطقة تنفتح لما تخلّص اللي قبلها", (0, 22, zg - 1.5), (70, 2.8, 0.5), "Back",
         bg=(24, 70, 48))
    for i, x in enumerate(xs):
        zone = i + 1
        ar, en, th = G8.ZONES[i][0], G8.ZONES[i][1], G8.ZONES[i][2]
        col = th["edge"]
        for s_ in (-1, 1):
            box("GatePost", (1.2, 14, 1.2), (x + s_ * 5.4, 7, zg), (60, 64, 74), "SmoothPlastic")
        box("GateTop", (12, 1.2, 1.4), (x, 14.4, zg), (60, 64, 74), "SmoothPlastic")
        G.part("Portal|Zone|%d" % zone, (9.6, 12.6, 0.5), (x, 6.5, zg), col, "Neon", transp=0.45, collide=False, shadow=False)
        sign("GateSign", "%s\n%s\n%d - %d" % (ar, en, starts[i] + 1, starts[i + 1]), (x, 17.4, zg + 0.2), (12, 4.6, 0.5), "Back",
             bg=tuple(max(0, v - 120) for v in col))
        G.part("GateLamp|%d" % zone, (1.4, 1.4, 1.4), (x, 20.2, zg), (90, 230, 140), "Neon", shape="Ball", collide=False,
               shadow=False)
    for s_ in (-1, 1):
        box("BigPost", (1.8, 18, 1.8), (s_ * 7.4, 9, zg + 4), (60, 64, 74), "SmoothPlastic")
    G.part("Portal|Course", (13, 16.5, 0.6), (0, 8.4, zg + 4), (120, 255, 200), "Neon", transp=0.45, collide=False, shadow=False)
    sign("ContinueSign", "كمّل من آخر نقطة\nContinue", (0, 20.4, zg + 4.4), (15, 4, 0.5), "Back", bg=(24, 90, 60))


def quiz_corner():
    import genmap8 as G8
    cx, cz, R = -50.0, 18.0, 14.0
    disc("QuizFloor", cx, 0.05, cz, 2 * R + 12, 0.1, (40, 52, 80), "SmoothPlastic", collide=False)
    disc("QuizRing", cx, 0.02, cz, 2 * R + 12.8, 0.06, (120, 200, 255), "Neon", collide=False, shadow=False)
    for face, dz in (("Back", 0.0), ("Front", -0.6)):
        sign("QuizTitle", "ركن الأسئلة | Quiz Corner\nقِف على محطة تخصصك وجاوب (+1 عملة)", (cx, 14, cz + dz), (18, 5, 0.5), face,
             bg=(40, 60, 110))
    vcyl("QuizPole", cx, 0, 11.4, cz - 0.3, 1.2, (60, 64, 74), "SmoothPlastic", collide=False)
    for i, (ar, en, th, _, _) in enumerate(G8.ZONES):
        a = i * 2 * math.pi / len(G8.ZONES)
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


def rides():
    portal("Portal|Cart", X - 6, -22, 16, 16, (240, 110, 200), "🚆 قطار التخصصات", -1, 0, "رحلة بين التخصصات الثمانية")
    # a cart on display next to the portal
    import cartride
    cartride.cart_model(X - 18, 0.0, -40, name="CartDisplay", yaw=90)
    portal("Portal|Train", X - 6, 26, 14, 14, (150, 90, 230), "🚋 قطار الخلية التعليمي", -1, 0, "Cell Train")
    A.logo_board(X - 1.4, 30, 2, R=1.6, nx=-1.0, nz=0.0)


# v52 World Gateway Hall: every world in one calm, spacious room behind the HQ's south doorway. One portal style
# (portal()), one destination per portal, nothing else on the walls. Kinds match Main.server destinations.
HALL_X, HALL_Z1, HALL_H = 48.0, 152.0, 30.0
HALL_PORTALS = [
    # (kind, wall, position along the wall, colour, Arabic title, English subtitle)
    ("Arcade", "W", 84, (240, 110, 200), "🎮 صالة الألعاب", "Arcade"),
    ("Puzzle", "W", 102, (255, 200, 90), "🧩 غرف الألغاز", "Puzzle Rooms"),
    ("Racers", "W", 120, (110, 210, 255), "🏎️ سباق الميكروبات", "Micro Racers"),
    ("Laser", "W", 138, (255, 95, 120), "⚡ الهروب من الليزر", "Laser Escape"),
    ("Exam", "E", 84, (255, 210, 80), "📝 قاعة الاختبارات", "Exam Hall"),
    ("Quiz", "E", 102, (255, 170, 110), "🎓 مركز التحديات العلمية", "Challenge Center"),
    ("Show", "E", 120, (255, 150, 90), "🎪 استوديو المسابقات", "Game Show"),
    ("Virus", "E", 138, (140, 255, 90), "🦠 مختبر العدوى", "Virus Tag"),
    ("Lab", "S", -26, (140, 220, 255), "🔬 معهد الأبحاث", "Research Lab"),
    ("Campus", "S", 0, (255, 190, 120), "🏛️ كلية العلوم", "College of Science"),
    ("Museum", "S", 26, (120, 230, 190), "🏺 متحف العلوم", "Science Museum"),
]


def gateway_hall():
    z0, z1, x = Z + 1, HALL_Z1, HALL_X
    rect("HallFloor", -x, x, -1, 0, z0, z1, (236, 226, 208), "WoodPlanks")
    rect("HallRunner", -8, 8, 0, 0.05, z0, z1 - 4, (214, 232, 220), "SmoothPlastic", collide=False)
    rect("HallCeiling", -x, x, HALL_H, HALL_H + 1, z0, z1, (250, 250, 248), "SmoothPlastic")
    rect("HallWallW", -x - 1, -x, 0, HALL_H, z0, z1, WALL, "SmoothPlastic")
    rect("HallWallE", x, x + 1, 0, HALL_H, z0, z1, WALL, "SmoothPlastic")
    rect("HallWallS", -x, x, 0, HALL_H, z1, z1 + 1, WALL, "SmoothPlastic")
    for (a, b, c_, d) in ((-x + 0.1, -x + 0.4, z0, z1), (x - 0.4, x - 0.1, z0, z1)):
        rect("Ribbon", a, b, 25.6, 26.4, c_, d, CLUB_GREEN, "SmoothPlastic", collide=False)
    rect("Ribbon", -x, x, 25.6, 26.4, z1 - 0.4, z1 - 0.1, CLUB_GREEN, "SmoothPlastic", collide=False)
    for lx in (-24, 0, 24):
        for lz in (92, 118, 144):
            C5.light_panel(lx, HALL_H - 0.4, lz, 12, 5, 1.2 if lx == 0 else 0.0001, 40 if lx == 0 else 1)
    sign("HallTitle", "🌍 بوابات العوالم | World Gateway Hall", (0, 26.5, Z - 0.6), (24, 3, 0.5), "Front", bg=CLUB_GREEN)
    sign("HallTitleIn", "🌍 بوابات العوالم\nاختر عالمك • القائمة 🌍 العوالم توديك لنفس الأماكن", (0, 27.2, z1 - 0.6), (40, 4.6, 0.5),
         "Front", bg=CLUB_GREEN)
    for kind, wall, at, col, title, sub in HALL_PORTALS:
        if wall == "W":
            px, pz, nx, nz = -x + 3, at, 1, 0
        elif wall == "E":
            px, pz, nx, nz = x - 3, at, -1, 0
        else:
            px, pz, nx, nz = at, z1 - 3, 0, -1
        portal("Portal|" + kind, px, pz, 11, 13, col, title, nx, nz, sub)   # 18-stud pitch: a clear gap between frames
        # a coloured floor pad in front of each portal guides the eye without cluttering the aisle
        cx, cz = px + nx * 5, pz + nz * 5
        rect("GatePad", cx - (2 if nx else 7), cx + (2 if nx else 7), 0, 0.06, cz - (7 if nx else 2), cz + (7 if nx else 2), col,
             "Neon", transp=0.55, collide=False)


def south_wall():
    gateway_hall()
    sign("Discord", "💬 انضموا لمجتمعنا على Discord\ndiscord.gg/8hw9hBn27\nأكواد الجوائز تنزل هناك أول بأول!", (-40, 10, Z - 0.6),
         (24, 9, 0.5), "Front", bg=(88, 101, 242))
    # v56: the "how to play" board became the ؟ help button (Help.client)


def club_office_corner():
    """the real office 088 vibe: wood desk, black shelving with trophies, DNA art, orange display, plants"""
    x0, z0 = -66.0, -40.0
    rect("Desk", x0, x0 + 14, 3, 3.9, z0, z0 + 6, WOOD, "Wood")
    rect("DeskBody", x0, x0 + 14, 0, 3, z0 + 1, z0 + 6, (130, 92, 60), "Wood")
    for q in range(3):
        box("Mon", (3.6, 2.4, 0.3), (x0 + 3 + q * 4.2, 5.4, z0 + 1.2), (20, 22, 28), "SmoothPlastic", collide=False,
            text=dict(face="Back", text=["🧬", "BSC", "🦠"][q], color=(140, 230, 190), bg=(12, 30, 26), bg_t=0.0))
    for q in range(4):
        rect("ShelfBoard", -X + 0.5, -X + 4, 3 + q * 4.2, 3.5 + q * 4.2, -60, -44, (30, 30, 34), "SmoothPlastic", collide=False)
        for k in range(3):
            vcyl("Trophy", -X + 2.2, 3.5 + q * 4.2, 6 + q * 4.2, -57 + k * 6, 1.4, (232, 184, 56), "Metal", collide=False)
    sign("Awards", "🏆 إنجازات النادي", (-X + 0.7, 21, -52), (0.4, 2.6, 16), "Right", bg=(70, 50, 20), color=(250, 210, 100))
    box("DNABoard", (12, 9, 0.4), (-56, 9, Z - 1.4), (248, 248, 246), "SmoothPlastic", collide=False)
    for q in range(24):
        a = q * 0.5
        ball("A", -56 + math.sin(a) * 4, 5.2 + q * 0.33, Z - 1.8, 0.8, (255, 90, 170), "Neon", collide=False, shadow=False)
        ball("B", -56 - math.sin(a) * 4, 5.2 + q * 0.33, Z - 1.8, 0.8, (60, 220, 255), "Neon", collide=False, shadow=False)
    for (x, z) in ((-74, -66), (74, -66), (-74, 66), (74, 66), (-30, 60), (30, 60), (-74, 40), (74, 6)):
        vcyl("Pot", x, 0, 3, z, 4, (230, 226, 218), "SmoothPlastic")
        for k in range(3):
            ball("Plant", x + (k - 1) * 1.2, 4.5 + k * 1.3, z, 3.6 - k * 0.6, (70 + k * 15, 150, 80), "Grass", collide=False)


def lounge():
    """two bright seating corners by the south wall; the mascot greets players beside the main aisle"""
    for sx in (-1, 1):
        x = sx * 40
        col = (150, 205, 172) if sx < 0 else (200, 170, 232)
        dark = tuple(v - 30 for v in col)
        A.floor_hex(x, 0.05, 54, 9, (246, 240, 228), name="Rug")
        rect("Sofa", x - 8, x + 8, 0, 2.2, 60, 64, col, "SmoothPlastic")
        rect("SofaBack", x - 8, x + 8, 2.2, 5.4, 63.4, 64.6, dark, "SmoothPlastic", collide=False)
        for k in (-1, 1):
            rect("SofaArm", x + k * 8 - 0.7, x + k * 8 + 0.7, 2.2, 3.6, 60, 64.6, dark, "SmoothPlastic", collide=False)
            rect("Pouf", x + k * 9 - 1.8, x + k * 9 + 1.8, 0, 2.2, 47, 50.6, PASTELS[(k + 2) % 5], "SmoothPlastic")
        disc("CoffeeTable", x, 2.0, 53, 7, 0.5, (250, 250, 248), "Marble")
        vcyl("TableLeg", x, 0, 2, 53, 1.2, (180, 180, 186), "Metal", collide=False)
        ball("Vase", x, 3.0, 53, 1.6, PASTELS[2 if sx < 0 else 4], "SmoothPlastic", collide=False)
    G.mascot(26, 0, -22)
    sign("Welcome", "أهلاً فيكم في مقر النادي! 👋", (26, 23.4, -22), (18, 2.6, 0.4), "Back", bg=CLUB_GREEN)


SPECIALTY_POSTERS = [("🌿", "بيولوجيا نبات", "Plant Biology"), ("🐢", "بيولوجيا حيوان", "Animal Biology"),
                     ("🦠", "مايكروبيولوجي", "Microbiology"), ("⚗️", "بايوكيمستري", "Biochemistry"),
                     ("🧬", "مولكلر", "Molecular Biology"), ("🌴", "الزراعة", "Agriculture"),
                     ("🔎", "الأدلة الجنائية", "Forensic Science"), ("🧪", "البايوتكنولوجي", "Biotechnology")]


def posters():
    """a poster for every specialty on the side walls"""
    spots = [(-1, -30), (-1, 2), (-1, 34), (-1, 60), (1, -58), (1, -40), (1, 46), (1, 64)]
    for i, ((side, z), (icon, ar, en)) in enumerate(zip(spots, SPECIALTY_POSTERS)):
        x = side * (X - 0.6)
        box("PosterFrame", (0.3, 9.8, 10.8), (x + side * 0.1, 11, z), (250, 250, 248), "SmoothPlastic", collide=False)
        sign("Poster", "%s\n%s\n%s" % (icon, ar, en), (x, 11, z), (0.4, 9, 10), "Right" if side < 0 else "Left",
             color=(30, 30, 36), bg=PASTELS[i % 5])


def dna_sculpture(cx=40.0, cz=14.0, h=34.0):
    """the HQ centrepiece: a tall glowing DNA helix on a round plinth. v63: moved to (40, 14), out of the view from the
    spawn to the north wall (at (-26, -22) it covered the HQ title and two parkour gates)"""
    disc("Plinth", cx, 0.8, cz, 16, 1.6, (240, 238, 232), "Marble")
    disc("PlinthGlow", cx, 1.62, cz, 15, 0.1, (120, 255, 200), "Neon", collide=False, shadow=False)
    for q in range(int(h / 1.7)):
        a = q * 0.42
        y = 3 + q * 1.7
        ax, az = cx + math.cos(a) * 4.6, cz + math.sin(a) * 4.6
        bx, bz = cx - math.cos(a) * 4.6, cz - math.sin(a) * 4.6
        ball("HelixA", ax, y, az, 1.7, (255, 90, 170), "Neon", collide=False, shadow=False)
        ball("HelixB", bx, y, bz, 1.7, (60, 220, 255), "Neon", collide=False, shadow=False)
        if q % 2 == 0:
            G.part("BasePair", (9.2, 0.35, 0.35), (cx, y, cz), PASTELS[(q // 2) % 5], "SmoothPlastic", rot=(0, -math.degrees(a), 0),
                   collide=False)
    sign("HelixPlate", "DNA — كل شي يبدأ من هنا 🧬", (cx, 2.6, cz + 8.05), (10, 1.6, 0.3), "Back", bg=CLUB_GREEN)


def build():
    with G.Group("ClubHQ"):
        dna_sculpture()
        posters()
        shell()
        north_wall()
        quiz_corner()
        rides()
        south_wall()
        club_office_corner()
        lounge()
        G.part("HQSpawn", (12, 1, 12), (0, 0.5, 30), (64, 140, 108), "SmoothPlastic",   # players spawn on the island now
               text=dict(face="Top", text="BSC", color=(255, 255, 255), bg=(36, 96, 74), bg_t=0.0))
