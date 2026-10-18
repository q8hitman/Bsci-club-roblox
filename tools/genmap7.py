"""v7: everything from genmap6 + new parkour mechanics, Challenge Hall (zone gates inside the
college), Quiz Hall (practice stations), fuller floors and building details.
Run: python tools/genmap7.py kuwait-parkour/src/map/Map.rbxmx
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genmap6 as G6  # noqa: E402  (themes, specialty envs, mechanics v6)
import genmap5 as C5  # noqa: E402
import genmap3 as C3  # noqa: E402
import genmap2 as M2  # noqa: E402
import genmap as G  # noqa: E402

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign
rect = C5.rect
rng = random.Random(7007)


# ====================================================================== new stage kinds
def k_log(c, th, t, k):
    """rolling log: walk along it while it spins"""
    L, d = 30.0, 6.5
    z0 = M2.cursor_gap(c, L, 1.6)
    spd = (0.45 + 0.45 * t) * (1 if k % 2 else -1)
    M2.walk.append(("brk",))
    G.part("Log|%.2f" % spd, (L, d, d), (c["x"], c["y"] - d / 2, z0), (150, 108, 70), "Wood", shape="Cylinder",
           rot=(0, 90, 0))
    for s_ in (-1, 1):
        disc("Ring", c["x"], c["y"] - d / 2, z0 + s_ * (L / 2 - 1), d + 0.4, 0.6, th["edge"], "Neon", collide=False) if False else None
    M2.set_c(c, c["x"], c["y"], z0, L)
    M2._land(c, th, 10, 1.6)


def k_windmill(c, th, t, k):
    """vertical blades sweeping across the path: time your run"""
    L = 30
    z0 = M2.cursor_gap(c, L, 2)
    M2.slab(th, c["x"], c["y"], z0, 14, L)
    gid = "w%d" % k
    spd = 1.1 + 0.9 * t
    hub_y = c["y"] + 12.5
    for bz in ([z0] if t < 0.5 else [z0 - 7, z0 + 7]):
        g2 = gid + str(int(bz))
        G.part("Wheel|%.2f|%s" % (spd, g2), (22, 1.4, 1.2), (c["x"], hub_y, bz), (255, 80, 80), "Neon")
        G.part("Wheel|%.2f|%s" % (spd, g2), (1.4, 22, 1.2), (c["x"], hub_y, bz), (255, 80, 80), "Neon")
        disc("Hub", c["x"], hub_y, bz, 3, 1.6, (60, 64, 72), "SmoothPlastic", collide=False, rot=(90, 0, 0)) if False else None
        for s_ in (-1, 1):
            box("Tower", (1.4, 13, 1.4), (c["x"] + s_ * 8, c["y"] + 6.5, bz), th["pillar"][0], th["pillar"][1], collide=False)
        box("Beam", (17.4, 1.2, 1.2), (c["x"], hub_y, bz + 1.4), th["pillar"][0], th["pillar"][1], collide=False)
    M2.set_c(c, c["x"], c["y"], z0, L)


def k_seesaw(c, th, t, k):
    n = 2 if t < 0.5 else 3
    col, mat = th["alt"]
    M2.walk.append(("brk",))
    for i in range(n):
        L = 22.0
        z0 = M2.cursor_gap(c, L, 2.2)
        G.part("Tilt", (6, 1, L), (c["x"], c["y"] - 0.5, z0), col, mat)
        vcyl("Pivot", c["x"], M2.SEA, c["y"] - 1.0, z0, 1.6, th["pillar"][0], th["pillar"][1], collide=False)
        M2.set_c(c, c["x"], c["y"], z0, L)
        if i < n - 1:
            M2._land(c, th, 6, 2.2)
            M2.walk.append(("brk",))
    M2._land(c, th, 10, 2.2)


def k_ice(c, th, t, k):
    """slippery tilted ice slabs (Ice friction is very low)"""
    n = 4
    M2.walk.append(("brk",))
    for i in range(n):
        L, w = 14.0, 8.0 - 2 * t
        z0 = M2.cursor_gap(c, L, 2.4)
        tilt = (7 + 5 * t) * (1 if i % 2 else -1)
        G.part("IceSlab", (w, 1, L), (c["x"], c["y"] - 0.5, z0), (190, 230, 250), "Ice", rot=(0, 0, tilt))
        M2.set_c(c, c["x"], c["y"], z0, L)
    M2._land(c, th, 10, 2.4)


def k_truss(c, th, t, k):
    """climb truss ladders up two ledges"""
    M2.walk.append(("brk",))
    for i in range(2):
        z_base = M2.cursor_gap(c, 8, 2.0)
        M2.slab(th, c["x"], c["y"], z_base, 10, 8, record=False)
        H = 14.0
        G.part("Truss", (2, H, 2), (c["x"], c["y"] + H / 2, z_base + 5.0), (210, 214, 220), "Metal", cls="TrussPart")
        top = c["y"] + H
        z_top = z_base + 5.0 + 1.0 + 5.0
        M2.slab(th, c["x"], top, z_top, 10, 10, alt=True, record=False)
        vcyl("LedgePost", c["x"] - 4, M2.SEA, top - 1, z_top, 1.2, th["pillar"][0], th["pillar"][1], collide=False)
        M2.set_c(c, c["x"], top, z_top, 10)


def k_maze(c, th, t, k):
    """small hedge maze: find the way through"""
    N, cell, H = 5, 9.0, 9.0
    W = N * cell
    z_start = c["z"] + c["sz"] / 2 + 2.0
    x0, z0 = c["x"] - W / 2, z_start
    M2.walk.append(("brk",))
    rect("MazeFloor", x0, x0 + W, c["y"] - 1, c["y"], z0, z0 + W, th["main"][0], th["main"][1])
    # DFS maze; walls[(i,j,'N'/'E')]
    visited = set()
    walls_n = {(i, j): True for i in range(N) for j in range(N)}
    walls_e = {(i, j): True for i in range(N) for j in range(N)}
    stack = [(N // 2, 0)]
    visited.add((N // 2, 0))
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
        stack.append((ni, nj))
    hedge = (64, 128, 70)
    y0, y1 = c["y"], c["y"] + H
    for i in range(N):
        for j in range(N):
            cx0, cz0 = x0 + i * cell, z0 + j * cell
            if walls_n[(i, j)] and not (j == N - 1 and i == N // 2):
                rect("Hedge", cx0 - 0.6, cx0 + cell + 0.6, y0, y1, cz0 + cell - 0.6, cz0 + cell + 0.6, hedge, "Grass")
            if walls_e[(i, j)] and i < N - 1:
                rect("Hedge", cx0 + cell - 0.6, cx0 + cell + 0.6, y0, y1, cz0 - 0.6, cz0 + cell + 0.6, hedge, "Grass")
    for i in range(N):                                          # outer south wall (entrance gap in the middle)
        if i != N // 2:
            rect("Hedge", x0 + i * cell - 0.6, x0 + (i + 1) * cell + 0.6, y0, y1, z0 - 0.6, z0 + 0.6, hedge, "Grass")
    rect("Hedge", x0 - 0.6, x0 + 0.6, y0, y1, z0, z0 + W, hedge, "Grass")
    rect("Hedge", x0 + W - 0.6, x0 + W + 0.6, y0, y1, z0, z0 + W, hedge, "Grass")
    rect("Ceiling", x0, x0 + W, y1 + 6, y1 + 6.4, z0, z0 + W, (200, 230, 220), "Glass", transp=0.8)
    sign("MazeSign", "متاهة! لاقي المخرج", (c["x"], y1 + 2, z0 - 1), (14, 2.4, 0.4), "Front", bg=(40, 80, 50))
    z_exit = z0 + W
    M2.set_c(c, c["x"], c["y"], z_exit - 0.5, 1.0)
    M2._land(c, th, 10, 1.0)


def k_sequence(c, th, t, k):
    """DNA complement puzzle: press the complementary bases in order to open the bridge"""
    comp = {"A": "T", "T": "A", "G": "C", "C": "G"}
    n = 3 if t < 0.5 else 4
    template = "".join(rng.choice("ATGC") for _ in range(n))
    answer = "".join(comp[b] for b in template)
    sid = "q%d" % k
    L = 16
    z0 = M2.cursor_gap(c, L, 2)
    M2.slab(th, c["x"], c["y"], z0, 22, L)
    G.part("SeqKey|%s|%s" % (sid, answer), (1, 1, 1), (c["x"], c["y"] - 3, z0), (0, 0, 0), "SmoothPlastic", transp=1,
           collide=False)
    cols = {"A": (230, 80, 80), "T": (80, 150, 240), "G": (90, 200, 110), "C": (240, 200, 70)}
    for i, b in enumerate("ATGC"):
        x = c["x"] - 7.5 + i * 5
        G.part("SeqBtn|%s|%s" % (sid, b), (3.6, 0.6, 3.6), (x, c["y"] + 0.3, z0 + 3), cols[b], "Neon",
               text=dict(face="Top", text=b, color=(255, 255, 255), bg=cols[b], bg_t=0.0))
    sign("SeqSign", "القالب: %s\nاضغط القواعد المكمّلة بالترتيب" % " - ".join(template), (c["x"], c["y"] + 6, z0 + L / 2 - 0.5),
         (20, 5, 0.5), "Front", bg=(30, 40, 70))
    M2.walk.append(("brk",))
    z = z0 + L / 2 + 1.5
    for i in range(5):
        z += 3.5 + 3.5
        box("Ghost|%s" % sid, (7, 1, 7), (c["x"], c["y"] - 0.5, z), th["edge"], "Neon", transp=0.75, collide=False)
        z += 3.5
    M2.set_c(c, c["x"], c["y"], z - 0.5, 1.0)
    M2._land(c, th, 10, 1.5)


def k_moon(c, th, t, k):
    """low-gravity jumps across big gaps"""
    n = 5
    M2.walk.append(("brk",))
    z_first = c["z"]
    for i in range(n):
        w = 8.0
        z = M2.cursor_gap(c, w, 13.0 + 3 * t)
        x = M2.clampx(c["x"] * 0.4 + rng.uniform(-5, 5))
        top = c["y"] + rng.choice([2, 4, 3, -1, 5])
        disc("MoonRock", x, top - 0.5, z, w, 1, (200, 204, 214), "Slate")
        disc("MoonGlow", x, top + 0.02, z, w + 0.2, 0.12, th["edge"], "Neon", collide=False, shadow=False)
        # v26: craters on every rock (decor only)
        for q in range(2):
            disc("Crater", x + (q * 2 - 1) * 1.6, top + 0.03, z + (q - 0.5) * 2.2, 1.6 + q * 0.6, 0.1, (150, 154, 166), "Slate",
                 collide=False, shadow=False)
        M2.set_c(c, x, top, z, w)
    z_last = c["z"]
    cx = 0 + c["x"] * 0.5
    G.part("LowGrav|62", (60, 60, z_last - z_first + 30), (cx, c["y"] + 10, (z_first + z_last) / 2),
           (180, 200, 255), "ForceField", transp=0.92, collide=False, shadow=False)
    # v26 space dressing: the client turns the sky to night inside LowGrav (Zones.client); a ringed planet,
    # stars and a fact sign make the stage read as "space" rather than grey discs
    zm = (z_first + z_last) / 2
    ball("Planet", cx + 24, c["y"] + 30, zm + 6, 18, (120, 90, 200), "SmoothPlastic", collide=False, shadow=False)
    G.part("PlanetRing", (0.4, 30, 30), (cx + 24, c["y"] + 30, zm + 6), (255, 210, 140), "Neon", shape="Cylinder",
           rot=(0, 25, 70), transp=0.25, collide=False, shadow=False)
    srng = random.Random(4242 + k)  # own RNG: decoration must not shift the course layout
    for q in range(22):
        sx = cx + srng.uniform(-28, 28)
        sz = srng.uniform(z_first - 10, z_last + 10)
        ball("Star", sx, c["y"] + srng.uniform(14, 38), sz, srng.choice([0.5, 0.7, 1.0]), (255, 250, 220), "Neon",
             collide=False, shadow=False)
    sign("SpaceSign", "🚀 منطقة الفضاء — جاذبية خفيفة!\n🐻 دب الماء (Tardigrade) عاش بفراغ الفضاء",
         (cx, c["y"] + 14, z_first + 2), (24, 6, 0.5), "Front", bg=(20, 18, 50))
    M2._land(c, th, 10, 3.0)


def k_fan(c, th, t, k):
    """ride an updraft to a high ledge"""
    M2.walk.append(("brk",))
    z_fan = M2.cursor_gap(c, 9, 2.5)
    disc("Fan", c["x"], c["y"] - 0.3, z_fan, 9, 0.6, (60, 64, 72), "SmoothPlastic")
    for a in range(4):
        box("FanBlade", (8, 0.2, 1.6), (c["x"], c["y"] + 0.1, z_fan), (200, 204, 210), "SmoothPlastic", collide=False,
            rot=(0, a * 45, 0))
    H = 24.0
    G.part("Updraft|36", (9, H + 6, 9), (c["x"], c["y"] + (H + 6) / 2, z_fan), (220, 240, 255), "ForceField", transp=0.85,
           collide=False, shadow=False)
    top = c["y"] + H
    z_top = z_fan + 4.5 + 1.0 + 5
    M2.slab(th, c["x"], top, z_top, 10, 10)
    M2.set_c(c, c["x"], top, z_top, 10)


M2.KINDS.update(dict(log=k_log, windmill=k_windmill, seesaw=k_seesaw, ice=k_ice, truss=k_truss, maze=k_maze,
                     sequence=k_sequence, moon=k_moon, fan=k_fan))

M2.SEQ[:] = [
    ["hops", "leaves", "truss", "seesaw", "blink", "maze", "log", "windmill", "crumble", ("leaves", "truss", "windmill")],
    ["hops", "ferry", "log", "pillars", "glass", "sweeper", "seesaw", "elevator", "maze", ("ferry", "log", "sweeper")],
    ["zigzag", "blink", "spinner", "fan", "crumble", "carousel", "sequence", "laser", "moon", ("blink", "carousel", "fan")],
    ["hops", "glass", "elevator", "molecule", "sequence", "seesaw", "ice", "blink", "sweeper", ("glass", "molecule", "ice")],
    ["stairs", "helix", "zigzag", "spinner", "sequence", "switch", "truss", "windmill", "carousel", ("helix", "sequence", "spinner")],
    ["molecule", "gel", "hops", "conveyor", "switch", "laser", "fan", "glass", "log", ("molecule", "gel", "laser")],
    ["hops", "ferry", "log", "leaves", "maze", "truss", "ice", "crumble", "windmill", ("ferry", "leaves", "maze")],
    ["heartbeat", "laser", "seesaw", "elevator", "blink", "sequence", "carousel", "fan", "crumble", ("heartbeat", "laser", "carousel")],
    ["gel", "bounce", "laser", "glass", "helix", "moon", "switch", "carousel", "sweeper", ("gel", "helix", "moon")],
    ["blink", "molecule", "sequence", "laser", "moon", "heartbeat", "glass", "windmill", "ice", ("blink", "laser", "helix", "heartbeat")],
]



def course_start():
    """bright start plaza for the obby (replaces the old dark hub room)"""
    with G.Group("CourseStart"):
        rect("StartDeck", -32, 32, -1, 0, -66, -8, (234, 230, 220), "Marble")
        for zz in (-66, -8):
            rect("DeckEdge", -32, 32, 0, 0.08, zz - 0.4, zz + 0.4, (90, 230, 160), "Neon", collide=False)
        for x in (-28, 28):
            for z in (-62, -12):
                vcyl("DeckLeg", x, -24, -1, z, 3, (226, 220, 206), "Concrete", collide=False)
        G.part("Checkpoint_0", (12, 1, 12), (0, 0.5, -26), (64, 140, 108), "SmoothPlastic",
               text=dict(face="Top", text="START", color=(255, 255, 255), bg=(36, 96, 74), bg_t=0.0))
        sign("StartTitle", "100 Level Parkour\nابدأ من هنا ↑", (0, 13, -62), (30, 7, 0.6), "Back", bg=(24, 70, 48))
        names = "\n".join("%d) %s" % (i + 1, M2.ZONE_NAMES[i][0]) for i in range(len(M2.ZONE_NAMES)))
        sign("ZoneList", names, (-31.4, 9, -40), (0.5, 15, 18), "Right", bg=(30, 40, 56))
        sign("Tips", "نصايح:\n• السقوط يرجّعك لآخر نقطة\n• كل 5 مراحل سؤال\n• المنصات الشفافة تختفي وترجع",
             (31.4, 9, -40), (0.5, 12, 18), "Left", bg=(30, 40, 56))
        for s_ in (-1, 1):
            box("ExitPost", (1.2, 14, 1.2), (s_ * 7, 7, -57), (60, 64, 74), "SmoothPlastic", collide=False)
        G.part("Portal|Campus", (12.6, 12.5, 0.5), (0, 6.4, -57), (255, 190, 120), "Neon", transp=0.5, collide=False,
               shadow=False)
        sign("BackSign", "العودة لقاعة التحديات\nBack to the College", (0, 15.6, -57.3), (15, 3.2, 0.5), "Back", bg=(110, 70, 30))
        for x in (-22, 22):
            C5.C3.planter(x, 0, -14, 10, 4)
            C5.C3.lamp_post(x, 0, -50, 10)


# ====================================================================== campus additions
ZONE_COLORS = [th["edge"] for th in M2.THEMES]


def challenge_hall():
    """G floor, rear east of the south building: ten zone gates + a big Continue gate"""
    x0, x1, z0, z1, y = 12.0, 66.0, -100.0, -48.0, 0.0
    rect("HallFloor", x0, x1, y, y + 0.08, z0, z1, (36, 44, 62), "SmoothPlastic", collide=False)
    for zz in (z0, z1):
        rect("HallEdge", x0, x1, y + 0.08, y + 0.12, zz - 0.3, zz + 0.3, (90, 230, 160), "Neon", collide=False)
    sign("HallTitle", "قاعة التحديات | Challenge Hall", ((x0 + x1) / 2, 19, z0 + 2), (40, 4.4, 0.5), "Back", bg=(24, 70, 48))
    sign("HallRules", "كل منطقة تنفتح لما تخلّص اللي قبلها 🔓\nادخل البوابة الكبيرة عشان تكمّل من آخر نقطة",
         (x0 + 0.6, 8, (z0 + z1) / 2), (0.4, 3.6, 17), "Right", bg=(24, 70, 48))
    G.part("HallSpawn", (6, 1, 6), (36, 0.5, -74), (0, 0, 0), "SmoothPlastic", transp=1, collide=False)
    xs = [19, 29, 39, 49, 59]
    for row, (zz, face, sgn) in enumerate(((-95.0, "Back", 1), (-53.0, "Front", -1))):
        for q, x in enumerate(xs):
            zone = row * 5 + q + 1
            ar, en = M2.ZONE_NAMES[zone - 1]
            col = ZONE_COLORS[zone - 1]
            for s_ in (-1, 1):
                box("GatePost", (0.9, 12, 0.9), (x + s_ * 3.8, 6, zz), (60, 64, 74), "SmoothPlastic", collide=False)
            G.part("Portal|Zone|%d" % zone, (6.6, 10.5, 0.5), (x, 5.4, zz), col, "Neon", transp=0.45, collide=False, shadow=False)
            sign("GateSign", "%d. %s\n%s\n%d - %d" % (zone, ar, en, (zone - 1) * 10 + 1, zone * 10), (x, 13.6, zz),
                 (8.6, 3.4, 0.5), face, bg=tuple(max(0, v - 120) for v in col))
            G.part("GateLamp|%d" % zone, (1.2, 1.2, 1.2), (x, 15.9, zz), (90, 230, 140), "Neon", shape="Ball", collide=False,
                   shadow=False)
    # continue gate (east end)
    for s_ in (-1, 1):
        box("BigPost", (1.4, 16, 1.4), (64.5, 8, -74 + s_ * 6.5), (60, 64, 74), "SmoothPlastic", collide=False)
    G.part("Portal|Course", (0.6, 14, 11.6), (64.5, 7.2, -74), (120, 255, 200), "Neon", transp=0.45, collide=False, shadow=False)
    sign("ContinueSign", "كمّل من آخر نقطة | Continue", (64.0, 17.4, -74), (0.5, 3, 14), "Left", bg=(24, 90, 60))
    for x in (25, 45):
        C5.light_panel(x, 23.0, -74, 14, 6, 1.4, 40)


def quiz_hall():
    """3rd floor: ten practice stations in a ring (questions can be swapped later)"""
    y, cx, cz, R = C5.Y_3, 0.0, -150.0, 21.0
    disc("QuizFloor", cx, y + 0.05, cz, 2 * R + 14, 0.1, (40, 52, 80), "SmoothPlastic", collide=False)
    disc("QuizRing", cx, y + 0.03, cz, 2 * R + 15.5, 0.06, (120, 200, 255), "Neon", collide=False, shadow=False)
    sign("QuizTitle", "قاعة الأسئلة | Quiz Hall\nقِف على أي محطة وجاوب", (cx, y + 12, cz), (18, 5, 0.5), "Back",
         bg=(40, 60, 110))
    sign("QuizTitle2", "قاعة الأسئلة | Quiz Hall\nقِف على أي محطة وجاوب", (cx, y + 12, cz - 0.6), (18, 5, 0.5), "Front",
         bg=(40, 60, 110))
    for i in range(10):
        a = i * 2 * math.pi / 10
        x, z = cx + R * math.sin(a), cz + R * math.cos(a)
        yaw = math.degrees(a)
        col = ZONE_COLORS[i]
        ar, en = M2.ZONE_NAMES[i]
        box("Podium", (3.6, 4, 3.6), (x, y + 2, z), (236, 236, 232), "SmoothPlastic")
        box("PodiumBand", (3.7, 0.6, 3.7), (x, y + 3.2, z), col, "Neon", collide=False, shadow=False)
        G.part("Screen", (6, 3.6, 0.3), (x + math.sin(a) * 0.9, y + 6.6, z + math.cos(a) * 0.9), (20, 24, 34), "SmoothPlastic",
               rot=(0, yaw, 0), collide=False,
               text=dict(face="Front", text="%s\n%s" % (ar, en), color=(255, 255, 255), bg=tuple(max(0, v - 130) for v in col),
                         bg_t=0.0))
        px, pz = cx + (R - 5.5) * math.sin(a), cz + (R - 5.5) * math.cos(a)
        G.part("QuizStation|%d" % (i + 1), (5, 0.4, 5), (px, y + 0.2, pz), col, "Neon", transp=0.2, rot=(0, yaw, 0), shadow=False)
    for x in (-20, 0, 20):
        C5.light_panel(x, C5.Y_4 - 1.0, cz, 10, 6, 1.4, 40)


def department_offices():
    """3rd floor: real rooms behind the department doors"""
    y = C5.Y_3
    C5.wall_x(-88, 88, -88, y, y + 15, (236, 232, 222), "Concrete",
              gaps=[(-76 + i * 22 - 3, -76 + i * 22 + 3) for i in range(8)])
    for i in range(8):
        x = -76 + i * 22
        if i < 7:
            C5.wall_z(-88, -34, x + 11, y, y + 15, (236, 232, 222), "Concrete")
        box("OfficeDesk", (8, 0.8, 4), (x, y + 3.4, -60), (160, 112, 70), "Wood")
        box("OfficeChair", (2.6, 0.6, 2.6), (x, y + 2.2, -56), (60, 62, 68), "Fabric", collide=False)
        box("Shelf", (8, 10, 1.6), (x, y + 5, -36), (150, 104, 66), "Wood", collide=False)
        C5.light_panel(x, C5.Y_4 - 1.0, -62, 6, 4, 1.0, 26)


def lounges():
    """fill the open floors with student lounges, plants and notice boards"""
    # L1 front balconies (wings) - lounge chairs
    for sx in (-73, 73):
        for q in range(3):
            box("Lounge", (6, 2, 3), (sx, C5.Y_1 + 1, -150 + q * 14), (230, 190, 60) if q % 2 else (60, 100, 170), "Fabric",
                collide=False)
            C5.C3.planter(sx + (8 if sx < 0 else -8), C5.Y_1, -144 + q * 14, 4, 4, True)
    # L4 front: research poster wall + lounge
    for q in range(6):
        x = -60 + q * 24
        box("Poster", (16, 9, 0.4), (x, C5.Y_4 + 7, -176.6), (248, 248, 246), "SmoothPlastic", collide=False,
            text=dict(face="Back", text=["Gene Expression", "Microbial Growth", "Protein Folding", "Plant Stress",
                                         "Coral Reefs of Kuwait", "CRISPR in Agriculture"][q],
                      color=(40, 40, 50), bg=(248, 248, 246), bg_t=0.0))
    for q in range(4):
        box("Sofa", (9, 2.2, 3.4), (-45 + q * 30, C5.Y_4 + 1.1, -150), (90, 130, 160), "Fabric", collide=False)
        C5.table_set(-45 + q * 30, -140, C5.Y_4, 3)
    # vending machines + water coolers near the cores on G
    for x, label in ((-62, "مشروبات"), (-58, "سناك")):
        box("Vending", (3.6, 9, 3), (x, 4.5, -38), (40, 44, 52), "SmoothPlastic",
            text=dict(face="Front", text=label, color=(255, 255, 255), bg=(200, 40, 50), bg_t=0.0))


def building_details():
    """facade lettering, roof solar arrays and plant, entrance canopy lights"""
    sign("FacadeName", "كلية العلوم  •  COLLEGE OF SCIENCE", (0, 46, -179.9), (70, 6, 0.4), "Front", color=(255, 255, 255),
         bg=(46, 52, 60))
    for zz in range(-170, -40, 14):
        for xx in range(-80, 81, 16):
            if -32 < xx < 32 and -130 < zz < -64:
                continue
            box("Solar", (12, 0.5, 8), (xx, C5.Y_ROOF + 1.2, zz), (34, 52, 92), "Glass", rot=(-12, 0, 0), collide=False)
    for xx in (-70, 70):
        box("HVAC", (14, 6, 10), (xx, C5.Y_ROOF + 3, -40), (190, 192, 196), "SmoothPlastic", collide=False)
    for x in range(-81, 82, 18):
        box("Downlight", (2, 0.2, 2), (x, 23.0, -170), (255, 240, 205), "Neon", collide=False, shadow=False)


# ====================================================================== build
def build_campus():
    with G.Group("Campus"):
        C5.outdoors()
        C5.south_building()
        challenge_hall()
        quiz_hall()
        department_offices()
        lounges()
        building_details()
        C5._off[2] = C5.NB_SHIFT
        C5.north_building()
        C5._off[2] = 0.0


if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else "kuwait-parkour/src/map/Map.rbxmx"
    build_campus()
    C5._off[0], C5._off[1], C5._off[2] = C5.COURSE_OFFSET
    G.hub = course_start
    C3.build()
    gap, rise, bad, n = M2.validate()
    xml = ('<roblox version="4"><Item class="Folder" referent="%s"><Properties>'
           '<string name="Name">Map</string></Properties>%s</Item></roblox>') % (G.rid(), "".join(G.buf))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(xml)
    print("parts:", G.nparts[0], "| steps:", n, "| gap %.2f rise %.2f" % (gap, rise), "| violations:", len(bad),
          "| KB:", len(xml) // 1024)
    for v in bad[:6]:
        print("  BAD", v)
