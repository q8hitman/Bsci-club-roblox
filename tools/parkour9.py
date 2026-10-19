"""v9 parkour: harder, more varied stages and real puzzles (no more waiting on blinking tiles).

New stage kinds (all registered into genmap2.KINDS):
  doors:<zone>     answer door: walk through the right doorway, the wrong corridors collapse
  order:<name>     press the steps of a biology process in the right order to open the bridge
  codon            translate an mRNA strand with the codon table (distractor buttons reset you)
  simon            memory: lamps flash a colour pattern, repeat it on the floor buttons
  maze_hedge/dark  7x7 maze; a key button hidden in the farthest dead end opens the exit gate
  footprints       invisible path that only the faint footprints reveal (decoy trails too)
  pendulum         narrow beam under swinging blades
  orbit            small platforms circled by "electron" kill balls
  wind             narrow beam with sideways gusts
  wrap             Tower-of-Hell style ledges wrapping around a pillar
  timed            a button opens the bridge for a few seconds only: sprint!
Server/client support: Swing, Orbit, Gate, Button|id|seconds, SimonLamp (Obstacles), Wind (Zones.client).
"""
import math
import random

import genmap as G
import genmap2 as M2
import genmap5 as C5

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign
rect = C5.rect
rng = random.Random(9009)


def _ghost_bridge(c, th, sid, n=5, size=7.0, gap=3.5):
    z = c["z"] + c["sz"] / 2 + 1.5
    for i in range(n):
        z += gap + size / 2
        box("Ghost|%s" % sid, (size, 1, size), (c["x"], c["y"] - 0.5, z), th["edge"], "Neon", transp=0.75, collide=False)
        z += size / 2
    M2.set_c(c, c["x"], c["y"], z - 0.5, 1.0)
    M2._land(c, th, 10, gap)


# ====================================================================== answer doors
DOOR_Q = {
    "plant": [("وين يصير البناء الضوئي؟", "البلاستيدات الخضراء", "الميتوكوندريا", "الريبوسومات"),
              ("الغاز اللي يطلعه النبات بالبناء الضوئي", "الأكسجين", "ثاني أكسيد الكربون", "النيتروجين")],
    "animal": [("أي واحد من الثدييات؟", "الحوت", "القرش", "السلحفاة"),
               ("كم حجرة في قلب الإنسان؟", "4", "3", "2")],
    "micro": [("البكتيريا كائنات…", "بدائية النواة", "حقيقية النواة", "عديدة الخلايا"),
              ("الفيروس يقدر يتكاثر…", "داخل خلية حيّة فقط", "بروحه بالهواء", "على أي سطح")],
    "biochem": [("الإنزيمات غالباً عبارة عن…", "بروتينات", "دهون", "سكريات"),
                ("وحدة بناء البروتين", "الأحماض الأمينية", "النيوكليوتيدات", "الأحماض الدهنية")],
    "molecular": [("القاعدة اللي في RNA بدل الثايمين", "اليوراسيل U", "الأدينين A", "السايتوسين C"),
                  ("نسخ DNA إلى mRNA اسمه…", "النسخ Transcription", "الترجمة Translation", "التضاعف Replication")],
    "agri": [("الرمز N في الأسمدة يعني…", "النيتروجين", "الصوديوم", "النيون"),
             ("أي نبات يتحمّل ملوحة التربة أكثر؟", "النخيل", "الخس", "الفراولة")],
    "forensic": [("أكثر نمط بصمات منتشر بين الناس", "المنحني Loop", "الدوّامي Whorl", "المقوّس Arch"),
                 ("أي عيّنة تنفع لتحليل DNA؟", "جذر الشعرة", "طرف الظفر المقصوص", "الشعر بدون جذر")],
    "biotech": [("تقنية تضاعف قطعة DNA ملايين المرات", "PCR", "ELISA", "الطرد المركزي"),
                ("الإنسولين البشري ينتج اليوم باستخدام…", "بكتيريا معدّلة وراثياً", "دم الأبقار فقط", "النباتات البرية")],
}


def k_doors(c, th, t, k, zone):
    q, right, *wrong = DOOR_Q[zone][k % len(DOOR_Q[zone])]
    answers = [right] + wrong
    order = [0, 1, 2]
    rng.shuffle(order)
    # landing with the question
    z_land = M2.cursor_gap(c, 12, 2.0)
    M2.slab(th, c["x"], c["y"], z_land, 40, 12)
    M2.set_c(c, c["x"], c["y"], z_land, 12)
    zw = z_land + 6.5
    y = c["y"]
    wall_col = th["pillar"][0]
    sign("DoorQ", "❓ %s\nادخل من الباب الصح" % q, (c["x"], y + 19, zw - 0.6), (38, 6, 0.5), "Front", bg=(30, 40, 70))
    # front wall with three doorways at -12, 0, 12 (width 6)
    xs = [-12.0, 0.0, 12.0]
    edges = [-20.0, -15.0, -9.0, -3.0, 3.0, 9.0, 15.0, 20.0]
    for a, b in ((edges[0], edges[1]), (edges[2], edges[3]), (edges[4], edges[5]), (edges[6], edges[7])):
        rect("DoorWall", c["x"] + a, c["x"] + b, y, y + 16, zw - 0.6, zw + 0.6, wall_col, "SmoothPlastic")
    rect("DoorLintel", c["x"] - 20, c["x"] + 20, y + 10, y + 16, zw - 0.6, zw + 0.6, wall_col, "SmoothPlastic")
    L = 22.0
    for slot, x in enumerate(xs):
        ans = answers[order[slot]]
        is_right = order[slot] == 0
        sign("DoorLabel", ans, (c["x"] + x, y + 8.4, zw - 0.7), (6, 2.6, 0.3), "Front", bg=(20, 24, 34))
        # corridor (walls between corridors reach the exit)
        col, mat = th["main"]
        nm = "Floor" if is_right else "Crumble|0.12|3"
        box(nm, (6, 1, L), (c["x"] + x, y - 0.5, zw + L / 2), col, mat)
    # solid blocks between the corridors, so nobody can hop across from a wrong one
    for a, b in ((-16.0, -15.0), (-9.0, -3.0), (3.0, 9.0), (15.0, 16.0)):
        rect("CorridorWall", c["x"] + a, c["x"] + b, y, y + 16, zw, zw + L, wall_col, "SmoothPlastic")
    rect("CorridorRoof", c["x"] - 15.5, c["x"] + 15.5, y + 16, y + 16.6, zw, zw + L, (230, 230, 226), "Glass", transp=0.5)
    M2.walk.append(("brk",))
    M2.set_c(c, c["x"], y, zw + L - 0.5, 1.0)
    z_out = M2.cursor_gap(c, 12, 0.0)
    M2.slab(th, c["x"], y, z_out, 34, 12, record=False)
    M2.set_c(c, c["x"], y, z_out, 12)
    M2.walk.append(("r", c["x"], z_out, y, 34, 12))


# ====================================================================== ordering puzzles
ORDERS = {
    "growth": ("رتّب مراحل حياة النبات", ["بذرة", "إنبات", "بادرة", "نبات بالغ", "إزهار", "ثمرة"]),
    "foodchain": ("رتّب السلسلة الغذائية من المنتج", ["عشب", "جرادة", "ضفدع", "ثعبان", "صقر"]),
    "gram": ("رتّب خطوات صبغة جرام", ["كريستال البنفسج", "اليود", "الكحول", "السفرانين"]),
    "protein": ("رتّب مستويات بناء البروتين", ["أولي", "ثانوي", "ثالثي", "رباعي"]),
    "mitosis": ("رتّب أطوار الانقسام المتساوي", ["تمهيدي", "استوائي", "انفصالي", "نهائي", "انقسام السيتوبلازم"]),
    "agri": ("رتّب خطوات الزراعة", ["حرث التربة", "بذر البذور", "الري", "التسميد", "الحصاد"]),
    "crime": ("رتّب خطوات التعامل مع مسرح الجريمة",
              ["تأمين المسرح", "التصوير والتوثيق", "جمع الأدلة", "تحريز الأدلة", "التحليل بالمختبر"]),
    "cloning": ("رتّب خطوات الاستنساخ الجيني",
                ["قطع DNA بإنزيم القطع", "ربطه بالبلازميد", "إدخاله للبكتيريا", "انتقاء الخلايا الناجحة", "تكاثر البكتيريا"]),
}
LETTERS = "ABCDEFGHIJ"
BTN_COLS = [(230, 90, 80), (80, 150, 240), (90, 200, 110), (240, 200, 70), (180, 100, 230), (250, 140, 60),
            (60, 200, 200), (230, 110, 170), (150, 150, 160), (120, 200, 90)]


def _button_board(c, th, sid, labels, letters, title, key, extra_sign=None, depth=26.0):
    z0 = M2.cursor_gap(c, depth, 2)
    M2.slab(th, c["x"], c["y"], z0, 46, depth)
    G.part("SeqKey|%s|%s" % (sid, key), (1, 1, 1), (c["x"], c["y"] - 3, z0), (0, 0, 0), "SmoothPlastic", transp=1,
           collide=False)
    n = len(labels)
    per_row = 5 if n > 5 else n
    rows = (n + per_row - 1) // per_row
    for i, (lab, let) in enumerate(zip(labels, letters)):
        r, q = divmod(i, per_row)
        cnt = min(per_row, n - r * per_row)
        x = c["x"] + (q - (cnt - 1) / 2) * 8.4
        z = z0 - depth / 2 + 5.5 + r * 9.0
        col = BTN_COLS[i % len(BTN_COLS)]
        G.part("SeqBtn|%s|%s" % (sid, let), (4.6, 0.6, 4.6), (x, c["y"] + 0.3, z), col, "Neon")
        sign("BtnLabel", lab, (x, c["y"] + 1.8, z + 2.8), (5.6, 1.8, 0.25), "Front", bg=tuple(max(0, v - 90) for v in col), collide=False)
    sign("PuzzleSign", "🧩 %s\nاضغط الخطوات بالترتيب الصحيح لفتح الجسر" % title, (c["x"], c["y"] + 13.5, z0 + depth / 2 - 0.5), (32, 5.5, 0.5),
         "Front", bg=(30, 40, 70), collide=False)
    if extra_sign:
        text, size = extra_sign
        sign("PuzzleHelp", text, (c["x"] + 22.6, c["y"] + 8.5, z0), (0.5, size[1], size[0]), "Left", bg=(24, 30, 44), collide=False)
    M2.set_c(c, c["x"], c["y"], z0, depth)
    M2.walk.append(("brk",))


def k_order(c, th, t, k, name):
    title, steps = ORDERS[name]
    sid = "o%d" % k
    letters = LETTERS[:len(steps)]
    idx = list(range(len(steps)))
    rng.shuffle(idx)
    labels = [steps[i] for i in idx]
    lets = [letters[i] for i in idx]
    _button_board(c, th, sid, labels, lets, title, letters)
    _ghost_bridge(c, th, sid, 5, 6.0, 3.6)


CODONS = [("AUG", "ميثيونين Met"), ("UUU", "فينيل ألانين Phe"), ("GGC", "جلايسين Gly"), ("UGG", "تربتوفان Trp"),
          ("AAA", "لايسين Lys"), ("GAU", "أسبارتيك Asp"), ("CAU", "هستدين His"), ("UAC", "تايروسين Tyr")]


def k_codon(c, th, t, k):
    sid = "d%d" % k
    n = 3 if t < 0.5 else 4
    picks = [0] + rng.sample(range(1, len(CODONS)), n - 1)   # always starts with AUG
    strand = " ".join(CODONS[i][0] for i in picks)
    key = "".join(LETTERS[i] for i in picks)
    idx = list(range(len(CODONS)))
    rng.shuffle(idx)
    table = "جدول الشفرات\n" + "\n".join("%s = %s" % (CODONS[i][0], CODONS[i][1].split()[-1]) for i in range(len(CODONS)))
    _button_board(c, th, sid, [CODONS[i][1] for i in idx], [LETTERS[i] for i in idx],
                  "ترجم الـ mRNA:  %s\nاضغط الأحماض الأمينية بالترتيب" % strand, key, (table, (14, 16)), depth=26)
    _ghost_bridge(c, th, sid, 5, 6.0, 3.6)


SIMON = [("R", (235, 70, 70)), ("G", (70, 210, 100)), ("B", (70, 140, 245)), ("Y", (245, 210, 60))]


def k_simon(c, th, t, k):
    sid = "m%d" % k
    n = 4 + int(t * 3)
    key = "".join(rng.choice("RGBY") for _ in range(n))
    while any(key[i] == key[i + 1] for i in range(n - 1)):
        key = "".join(rng.choice("RGBY") for _ in range(n))
    depth = 20.0
    z0 = M2.cursor_gap(c, depth, 2)
    M2.slab(th, c["x"], c["y"], z0, 34, depth)
    G.part("SeqKey|%s|%s" % (sid, key), (1, 1, 1), (c["x"], c["y"] - 3, z0), (0, 0, 0), "SmoothPlastic", transp=1,
           collide=False)
    yb = c["y"] + 11.5
    box("SimonBoard", (31, 9, 1), (c["x"], yb, z0 + depth / 2), (24, 26, 34), "SmoothPlastic", collide=False)
    for i, (let, col) in enumerate(SIMON):
        x = c["x"] + (i - 1.5) * 7.4
        G.part("SimonLamp|%s|%s" % (sid, let), (4.6, 4.6, 0.6), (x, yb, z0 + depth / 2 - 0.7), tuple(v // 4 for v in col),
               "Neon", collide=False, shadow=False)
        G.part("SeqBtn|%s|%s" % (sid, let), (4.4, 0.6, 4.4), (x, c["y"] + 0.3, z0 - 2), col, "Neon")
    sign("SimonSign", "🧠 لعبة الذاكرة: شوف ترتيب الأضواء وكرّره على الأزرار (%d)" % n, (c["x"], yb + 6.2, z0 + depth / 2 - 0.6),
         (28, 3, 0.4), "Front", bg=(30, 40, 70), collide=False)
    M2.set_c(c, c["x"], c["y"], z0, depth)
    M2.walk.append(("brk",))
    _ghost_bridge(c, th, sid, 5, 6.0, 3.6)


# ====================================================================== maze with a key
def k_maze9(c, th, t, k, style="hedge"):
    N, cell, H = 7, 8.0, 11.0
    W = N * cell
    sid = "z%d" % k
    z0 = c["z"] + c["sz"] / 2 + 2.0
    x0 = c["x"] - W / 2
    M2.walk.append(("brk",))
    rect("MazeFloor", x0, x0 + W, c["y"] - 1, c["y"], z0, z0 + W, th["main"][0], th["main"][1])
    walls_n = {(i, j): True for i in range(N) for j in range(N)}
    walls_e = {(i, j): True for i in range(N) for j in range(N)}
    start = (N // 2, 0)
    visited, stack = {start}, [start]
    parent = {start: None}
    while stack:
        i, j = stack[-1]
        nbrs = [(i + di, j + dj) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))
                if 0 <= i + di < N and 0 <= j + dj < N and (i + di, j + dj) not in visited]
        if not nbrs:
            stack.pop()
            continue
        ni, nj = rng.choice(nbrs)
        if ni == i + 1:
            walls_e[(i, j)] = False
        elif ni == i - 1:
            walls_e[(ni, nj)] = False
        elif nj == j + 1:
            walls_n[(i, j)] = False
        else:
            walls_n[(ni, nj)] = False
        visited.add((ni, nj))
        parent[(ni, nj)] = (i, j)
        stack.append((ni, nj))
    # depth of each cell from the entrance; the key sits in the deepest dead end
    def depth(cl):
        d = 0
        while parent[cl]:
            cl = parent[cl]
            d += 1
        return d
    exit_cell = (N // 2, N - 1)
    dead = [cl for cl in visited if cl not in (start, exit_cell)
            and sum(1 for p in parent.values() if p == cl) == 0]
    key_cell = max(dead, key=depth)
    if style == "hedge":
        wall_col, wall_mat, roof_t = (64, 128, 70), "Grass", 0.8
    else:
        wall_col, wall_mat, roof_t = (54, 58, 70), "Concrete", 0.0
    y0, y1 = c["y"], c["y"] + H

    def wall(a0, a1, b0, b1):
        rect("MazeWall", a0, a1, y0, y1, b0, b1, wall_col, wall_mat)
    for i in range(N):
        for j in range(N):
            cx0, cz0 = x0 + i * cell, z0 + j * cell
            if walls_n[(i, j)] and j < N - 1:
                wall(cx0 - 0.6, cx0 + cell + 0.6, cz0 + cell - 0.6, cz0 + cell + 0.6)
            if walls_e[(i, j)] and i < N - 1:
                wall(cx0 + cell - 0.6, cx0 + cell + 0.6, cz0 - 0.6, cz0 + cell + 0.6)
    for i in range(N):
        if i != start[0]:
            wall(x0 + i * cell - 0.6, x0 + (i + 1) * cell + 0.6, z0 - 0.6, z0 + 0.6)
        if i != exit_cell[0]:
            wall(x0 + i * cell - 0.6, x0 + (i + 1) * cell + 0.6, z0 + W - 0.6, z0 + W + 0.6)
    wall(x0 - 0.6, x0 + 0.6, z0, z0 + W)
    wall(x0 + W - 0.6, x0 + W + 0.6, z0, z0 + W)
    ex = x0 + exit_cell[0] * cell + cell / 2
    G.part("Gate|%s" % sid, (cell - 1.2, H, 1.0), (ex, y0 + H / 2, z0 + W), (255, 70, 70), "Neon", transp=0.2)
    kx, kz = x0 + key_cell[0] * cell + cell / 2, z0 + key_cell[1] * cell + cell / 2
    G.part("Button|%s|35" % sid, (4, 0.6, 4), (kx, y0 + 0.3, kz), (255, 220, 60), "Neon")
    ball("KeyGlow", kx, y0 + 3.5, kz, 1.6, (255, 230, 120), "Neon", collide=False, shadow=False,
         light=(1.2, 14, (255, 220, 120)))
    rect("MazeRoof", x0, x0 + W, y1, y1 + 0.5, z0, z0 + W, (40, 44, 54) if style != "hedge" else (200, 230, 220),
         "SmoothPlastic" if style != "hedge" else "Glass", transp=roof_t)
    if style != "hedge":
        for i in range(0, N, 2):
            for j in range(0, N, 2):
                box("MazeLamp", (1, 0.3, 1), (x0 + i * cell + cell / 2, y1 - 0.4, z0 + j * cell + cell / 2), (180, 200, 255),
                    "Neon", collide=False, shadow=False, light=(0.5, 12, (170, 190, 255)))
    sign("MazeSign", "🗝️ متاهة بمفتاح: لاقي الزر الأصفر عشان ينفتح باب الخروج الأحمر", (c["x"], y1 + 3, z0 - 1),
         (30, 3, 0.4), "Front", bg=(40, 60, 50) if style == "hedge" else (40, 40, 60))
    M2.set_c(c, c["x"], c["y"], z0 + W + 0.5, 1.0)
    M2._land(c, th, 10, 1.0)


# ====================================================================== invisible footprint path
def k_footprints(c, th, t, k):
    n = 8
    M2.walk.append(("brk",))
    x = c["x"]
    zc = c["z"] + c["sz"] / 2
    rect("DarkZone", c["x"] - 22, c["x"] + 22, c["y"] + 16, c["y"] + 16.5, zc, zc + n * 9 + 8, (16, 16, 22), "SmoothPlastic")
    sign("FootSign", "👣 الأرض مخفية! امشِ على آثار الأقدام بس… وانتبه من الآثار المزيفة", (c["x"], c["y"] + 12.5, zc + 0.5),
         (26, 3, 0.4), "Back", bg=(60, 50, 20), collide=False)
    prev = (x, zc)
    for i in range(n):
        z = zc + 2.8 + 6.4 / 2 + i * 9.0
        x = M2.clampx(x + rng.choice([-5, 5, -4, 4, 0]), 12)
        G.part("Hidden", (6.4, 1, 6.4), (x, c["y"] - 0.5, z), (40, 40, 40), "SmoothPlastic", transp=1)
        for q in range(2):
            box("Footprint", (1.3, 0.06, 2.4), (x + (-1 if q == 0 else 1), c["y"] + 0.03, z + (-1.4 if q == 0 else 1.4)),
                (200, 230, 255), "Neon", transp=0.35, collide=False, shadow=False)
        M2.walk.append(("r", x, z, c["y"], 6.4, 6.4))
        # decoy prints off to the side lead nowhere
        if i % 2 == 1:
            dx = 13 if x <= 0 else -13
            for q in range(2):
                box("Footprint", (1.3, 0.06, 2.4), (x + dx + (-1 if q == 0 else 1), c["y"] + 0.03, z + (-1.4 if q == 0 else 1.4)),
                    (200, 230, 255), "Neon", transp=0.35, collide=False, shadow=False)
        prev = (x, z)
        M2.set_c(c, x, c["y"], z, 6.4)
    M2._land(c, th, 10, 2.6)


# ====================================================================== moving hazards
def k_pendulum(c, th, t, k):
    L = 44.0
    bw = 3.0 - 0.8 * t
    z0 = M2.cursor_gap(c, L, 2)
    col, mat = th["alt"]
    box("Beam", (bw, 1, L), (c["x"], c["y"] - 0.5, z0), col, mat)
    M2.walk.append(("r", c["x"], z0, c["y"], bw, L))
    n = 3 + int(t * 2)
    period = 2.6 - 0.6 * t
    pivot_h = 18.0
    for i in range(n):
        bz = z0 - L / 2 + (i + 1) * L / (n + 1)
        box("SwingFrame", (24, 1, 1), (c["x"], c["y"] + pivot_h, bz), th["pillar"][0], th["pillar"][1], collide=False)
        for s_ in (-1, 1):
            box("SwingPost", (1, pivot_h, 1), (c["x"] + s_ * 12, c["y"] + pivot_h / 2, bz), th["pillar"][0], th["pillar"][1],
                collide=False)
        # blade hangs from the pivot; the server swings it around the path (Z) axis
        G.part("Swing|0,%.1f,0|55|%.2f|%.2f" % (pivot_h - 3.0, period, i * period / n), (6, 3, 0.8),
               (c["x"], c["y"] + 3.0, bz), (230, 230, 240), "Metal")
        G.part("Swing|0,%.1f,0|55|%.2f|%.2f|safe" % ((pivot_h - 3.0) / 2, period, i * period / n), (0.5, pivot_h - 4.5, 0.5),
               (c["x"], c["y"] + 3.0 + (pivot_h - 3.0) / 2, bz), (90, 94, 100), "Metal", collide=False)
    M2.set_c(c, c["x"], c["y"], z0, L)
    M2._land(c, th, 10, 2)


def k_orbit(c, th, t, k):
    n, d = 5, 6.0
    spd = 1.6 + 1.2 * t
    M2.walk.append(("brk",))
    cols = [(255, 90, 170), (60, 220, 255)]
    for i in range(n):
        z = M2.cursor_gap(c, d, 3.2 + 1.4 * t)
        x = M2.clampx(c["x"] * 0.4 + rng.uniform(-4, 4))
        disc("Nucleus", x, c["y"] - 0.5, z, d, 1, (236, 120, 90) if i % 2 else (240, 240, 244), "SmoothPlastic")
        disc("Shell", x, c["y"] + 0.03, z, d + 7.4, 0.1, th["edge"], "Neon", transp=0.6, collide=False, shadow=False)
        r = 4.6
        for e in range(1 if t < 0.5 else 2):
            ang = e * math.pi
            ex, ez = x + r * math.cos(ang), z + r * math.sin(ang)
            G.part("Orbit|%.2f,0,%.2f|%.2f" % (x - ex, z - ez, spd * (1 if i % 2 else -1)), (1.8, 1.8, 1.8),
                   (ex, c["y"] + 1.6, ez), cols[e], "Neon", shape="Ball", shadow=False)
        M2.walk.append(("c", x, z, c["y"], d, d))
        M2.set_c(c, x, c["y"], z, d)
    M2.walk.append(("brk",))
    M2._land(c, th, 10, 3.0)


def k_wind(c, th, t, k):
    L = 40.0
    bw = 3.6 - 0.8 * t
    z0 = M2.cursor_gap(c, L, 2)
    col, mat = th["alt"]
    box("Beam", (bw, 1, L), (c["x"], c["y"] - 0.5, z0), col, mat)
    M2.walk.append(("r", c["x"], z0, c["y"], bw, L))
    side = 1 if k % 2 else -1
    on, off = 1.6, 2.2 - 0.5 * t
    G.part("Wind|%.1f,0|%.1f|%.1f" % (side * (22 + 10 * t), on, off), (30, 14, L), (c["x"], c["y"] + 6, z0), (210, 230, 255),
           "ForceField", transp=0.93, collide=False, shadow=False)
    for q in range(4):
        zz = z0 - L / 2 + 5 + q * 10
        G.part("FanRing", (1.2, 7, 7), (c["x"] - side * 15, c["y"] + 4, zz), (60, 64, 72), "SmoothPlastic", shape="Cylinder",
               collide=False)
        box("FanBox", (2, 7.4, 7.4), (c["x"] - side * 15.6, c["y"] + 4, zz), (90, 96, 106), "Metal", collide=False)
    sign("WindSign", "💨 رياح جانبية! امشِ لما تهدأ", (c["x"] - side * 15, c["y"] + 10, z0 - L / 2 + 2), (12, 2.4, 0.4), "Back",
         bg=(40, 70, 100))
    M2.set_c(c, c["x"], c["y"], z0, L)
    M2._land(c, th, 10, 2)


def k_wrap(c, th, t, k):
    """narrow ledges spiralling around a fat pillar"""
    R = 7.0
    cz = c["z"] + c["sz"] / 2 + R + 3.0
    cx = c["x"]
    col, mat = th["pillar"]
    vcyl("WrapPillar", cx, M2.SEA, c["y"] + 26, cz, 2 * R, col, mat)
    M2.walk.append(("brk",))
    n = 13                      # 1.5 turns: starts on the near side, ends on the far side
    w = 2.2 - 0.6 * t
    start = 180.0
    for i in range(n):
        a = math.radians(start - i * 45)
        rr = R + w / 2
        x, z = cx + rr * math.sin(a), cz + rr * math.cos(a)
        y = c["y"] + 1.2 * i
        acol, amat = th["alt"]
        box("WrapLedge", (w, 1, 4.2), (x, y - 0.5, z), acol, amat, rot=(0, math.degrees(a) + 90, 0))
        box("WrapEdge", (0.2, 0.14, 4.2), (x + 0.0, y + 0.02, z), th["edge"], "Neon", collide=False, shadow=False,
            rot=(0, math.degrees(a) + 90, 0))
    top = c["y"] + 1.2 * (n - 1)
    M2.set_c(c, cx, top, cz + R + w / 2, 0.0)
    M2._land(c, th, 10, 2.4)


def k_timed(c, th, t, k):
    sid = "t%d" % k
    secs = 7.5 - 2.0 * t
    box("Button|%s|%.1f" % (sid, secs), (4, 0.6, 4), (c["x"], c["y"] + 0.3, c["z"]), (255, 220, 60), "Neon")
    sign("TimedSign", "⏱️ دوس الزر… الجسر يطلع %d ثواني بس! اركض" % int(secs), (c["x"], c["y"] + 12.5, c["z"] + c["sz"] / 2),
         (20, 3, 0.4), "Front", bg=(90, 60, 10), collide=False)
    M2.walk.append(("brk",))
    z = c["z"] + c["sz"] / 2 + 1.5
    x = c["x"]
    for i in range(7):
        z += 3.6 + 3.0
        x = M2.clampx(x + (5 if i % 2 else -5), 10)
        box("Ghost|%s" % sid, (6, 1, 6), (x, c["y"] - 0.5 + (i % 3) * 0.8, z), th["edge"], "Neon", transp=0.75, collide=False)
        z += 3.0
    M2.set_c(c, c["x"], c["y"], z - 0.5, 1.0)
    M2._land(c, th, 10, 3.6)


def register():
    K = M2.KINDS
    for zone in DOOR_Q:
        K["doors:" + zone] = (lambda zn: lambda c, th, t, k: k_doors(c, th, t, k, zn))(zone)
    for name in ORDERS:
        K["order:" + name] = (lambda nm: lambda c, th, t, k: k_order(c, th, t, k, nm))(name)
    K["maze_hedge"] = lambda c, th, t, k: k_maze9(c, th, t, k, "hedge")
    K["maze_dark"] = lambda c, th, t, k: k_maze9(c, th, t, k, "dark")
    K.update(dict(codon=k_codon, simon=k_simon, footprints=k_footprints, pendulum=k_pendulum, orbit=k_orbit, wind=k_wind,
                  wrap=k_wrap, timed=k_timed))


SEQS = [
    ["hops", "order:growth", "leaves", "wrap", "doors:plant", "pendulum", "maze_hedge", "truss", "windmill", "lava", "simon",
     ("leaves", "wrap", "log")],
    ["hops", "doors:animal", "log", "pendulum", "order:foodchain", "ledge", "sweeper", "maze_dark", "seesaw", "timed", "lava",
     ("ferry", "pendulum", "wrap")],
    ["zigzag", "order:gram", "spinner", "fan", "doors:micro", "timed", "carousel", "simon", "laser", "moon", "wind",
     ("carousel", "pendulum", "laser")],
    ["molecule", "doors:biochem", "gel", "orbit", "order:protein", "laser", "wind", "simon", "glass", "log", "timed",
     ("orbit", "gel", "pendulum")],
    ["stairs", "codon", "helix", "orbit", "order:mitosis", "sequence", "spinner", "doors:molecular", "wrap", "windmill", "timed",
     "ice", ("helix", "orbit", "pendulum")],
    ["hops", "doors:agri", "conveyor", "maze_hedge", "truss", "order:agri", "seesaw", "wind", "windmill", "simon", "pendulum",
     ("leaves", "wind", "conveyor")],
    ["laser", "footprints", "doors:forensic", "ledge", "order:crime", "maze_dark", "pendulum", "simon", "sweeper", "timed",
     "glass", "wrap", ("laser", "footprints", "sweeper")],
    ["gel", "doors:biotech", "orbit", "order:cloning", "moon", "codon", "laser", "simon", "wind", "maze_dark", "pendulum",
     "timed", "helix", ("gel", "orbit", "pendulum", "laser")],
]
