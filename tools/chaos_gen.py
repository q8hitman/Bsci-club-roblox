"""Chaos Campus prototype map (separate project): lobby + three minigame arenas.
Run: python tools/chaos_gen.py chaos-campus/src/map/Map.rbxmx
Names the server looks for:
  LobbySpawn (SpawnLocation)            Arena_<Name> folders with ArenaSpawn parts
  FallTile (Petri Floor)                OrbSpot (ATP Rush)        SweepHub (Enzyme Sweeper)
  KillFloor|<arena>                     ScoreBoard (lobby sign updated by the server)
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genmap as G  # noqa: E402

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign
rng = random.Random(42)
PASTEL = [(250, 222, 170), (205, 232, 60), (220, 165, 238), (160, 218, 236), (232, 150, 166)]
Y = 100.0


def lobby():
    with G.Group("Lobby"):
        disc("LobbyFloor", 0, Y - 1, 0, 90, 2, (110, 92, 150), "SmoothPlastic")   # deep lilac: no glare
        disc("LobbyRim", 0, Y - 0.6, 0, 91, 0.8, (120, 255, 200), "Neon", collide=False, shadow=False)  # a ring under the floor edge
        for i in range(10):
            a = i * 2 * math.pi / 10
            vcyl("LobbyPillar", 40 * math.cos(a), Y, Y + 14, 40 * math.sin(a), 3, PASTEL[i % 5], "SmoothPlastic")
            ball("LobbyLamp", 40 * math.cos(a), Y + 15.5, 40 * math.sin(a), 3, PASTEL[i % 5], "Neon", collide=False, shadow=False,
                 light=(1, 22, PASTEL[i % 5]))
        G.part("LobbySpawn", (12, 1, 12), (0, Y + 0.5, 12), (64, 140, 108), "SmoothPlastic", cls="SpawnLocation",
               extra='<bool name="Neutral">true</bool><int name="Duration">0</int>',
               text=dict(face="Top", text="CHAOS", color=(255, 255, 255), bg=(36, 96, 74), bg_t=0.0))
        sign("Title", "⚡ CHAOS CAMPUS ⚡\nفوضى الكلية", (0, Y + 16, -30), (34, 9, 0.6), "Back", bg=(80, 30, 110))
        G.part("ScoreBoard", (26, 16, 0.6), (-24, Y + 9, -22), (20, 24, 34), "SmoothPlastic", rot=(0, 35, 0),
               text=dict(face="Back", text="🏆", color=(255, 236, 160), bg=(20, 28, 44), bg_t=0.0))
        # v56: the "how to play" board became the ؟ help button (Help.client)
        # spectator balcony view of the sweeper arena is not needed: players watch from the lobby screens


def arena_spawns(name, cx, cz, r, y):
    for i in range(12):
        a = i * 2 * math.pi / 12
        G.part("ArenaSpawn", (2, 1, 2), (cx + r * math.cos(a), y + 0.5, cz + r * math.sin(a)), (0, 0, 0), "SmoothPlastic",
               transp=1, collide=False, shadow=False)


def petri_floor(cx=300.0, cz=0.0):
    """two layers of hexagonal agar tiles in a glass petri dish; each tile drops shortly after someone steps on it.
    v61 (owner: minigames look plain): agar colours (was pastel confetti), a glass dish wall and a lid overhead."""
    with G.Group("Arena_PetriFloor"):
        for layer, ly in enumerate((Y, Y - 26)):
            R, d = 7, 6.2
            for q in range(-R, R + 1):
                for r in range(-R, R + 1):
                    if abs(q + r) > R:
                        continue
                    x = cx + d * (q + r / 2)
                    z = cz + d * r * math.sqrt(3) / 2
                    k = ((q * 3 + r * 5) % 4) * 4
                    col = (238 - k, 226 - k, 196 - k) if layer == 0 else (212 - k, 190 - k, 150 - k)
                    G.part("FallTile", (1, d * 1.1, d * 1.1), (x, ly - 0.5, z), col, "SmoothPlastic", shape="Cylinder",
                           rot=(0, 0, 90))
        n, rw = 48, 52.0
        for i in range(n):   # the dish wall (decor, no collision: falling off the edge stays possible)
            a = i * 2 * math.pi / n
            G.part("DishWall", (1, 40, 2 * math.pi * rw / n + 0.3), (cx + rw * math.cos(a), Y - 24, cz + rw * math.sin(a)),
                   (215, 235, 245), "Glass", transp=0.7, rot=(0, -math.degrees(a), 0), collide=False, shadow=False)
            G.part("DishRim", (1.4, 0.8, 2 * math.pi * rw / n + 0.3), (cx + rw * math.cos(a), Y - 3.6, cz + rw * math.sin(a)),
                   (240, 248, 252), "SmoothPlastic", rot=(0, -math.degrees(a), 0), collide=False, shadow=False)
        disc("PetriLid", cx, Y + 48, cz, 112, 1, (220, 240, 250), "Glass", transp=0.88, collide=False, shadow=False)
        for i, (a, rr, dd, col) in enumerate(((0.4, 47.5, 5, (250, 240, 210)), (1.9, 48.5, 3.6, (240, 190, 90)),
                                             (3.1, 47.8, 4.4, (230, 140, 170)), (4.4, 48.2, 3, (250, 240, 210)),
                                             (5.5, 47.6, 4.8, (240, 190, 90)))):
            disc("Colony", cx + rr * math.cos(a), Y - 5, cz + rr * math.sin(a), dd, 0.6, col, "SmoothPlastic", collide=False,
                 shadow=False)
        disc("PetriGlass", cx, Y - 70, cz, 120, 2, (200, 230, 240), "Glass", transp=0.5, collide=False)
        G.part("KillFloor|PetriFloor", (200, 2, 200), (cx, Y - 60, cz), (255, 80, 80), "Neon", transp=0.6, collide=False)
        arena_spawns("PetriFloor", cx, cz, 24, Y)


def atp_rush(cx=-300.0, cz=0.0):
    """open arena with cover; glowing ATP orbs spawn on the OrbSpots. v61: inside a mitochondrion - a dark matrix
    floor (the orbs pop against it), cristae folds as the ramps and pillars, the pink double membrane as the wall."""
    with G.Group("Arena_ATPRush"):
        disc("RushFloor", cx, Y - 1, cz, 120, 2, (96, 44, 58), "SmoothPlastic")
        for i in range(24):
            a = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(8, 52)
            G.part("OrbSpot", (1, 1, 1), (cx + rr * math.cos(a), Y + 2.5, cz + rr * math.sin(a)), (0, 0, 0), "SmoothPlastic",
                   transp=1, collide=False, shadow=False)
        CRISTA = ((232, 130, 120), (214, 104, 104))
        for i in range(8):
            a = i * math.pi / 4 + 0.2
            box("RushRamp", (10, 1, 16), (cx + 34 * math.cos(a), Y + 2, cz + 34 * math.sin(a)), CRISTA[i % 2], "SmoothPlastic",
                rot=(-14, -math.degrees(a) + 90, 0))
            vcyl("RushPillar", cx + 18 * math.cos(a + 0.4), Y, Y + 8, cz + 18 * math.sin(a + 0.4), 4, CRISTA[(i + 1) % 2],
                 "SmoothPlastic")
            ball("RushPillarCap", cx + 18 * math.cos(a + 0.4), Y + 8, cz + 18 * math.sin(a + 0.4), 4, CRISTA[(i + 1) % 2],
                 "SmoothPlastic", collide=False, shadow=False)
        n = 40
        for i in range(n):
            a = i * 2 * math.pi / n
            G.part("RushWall", (1.5, 10, 2 * math.pi * 60 / n + 0.5), (cx + 60 * math.cos(a), Y + 5, cz + 60 * math.sin(a)),
                   (240, 150, 140), "SmoothPlastic", transp=0.35, rot=(0, -math.degrees(a), 0))
            G.part("RushOuterMembrane", (1.2, 12, 2 * math.pi * 63 / n + 0.5), (cx + 63 * math.cos(a), Y + 6,
                   cz + 63 * math.sin(a)), (250, 190, 170), "SmoothPlastic", transp=0.5, rot=(0, -math.degrees(a), 0),
                   collide=False, shadow=False)
        G.part("KillFloor|ATPRush", (200, 2, 200), (cx, Y - 40, cz), (255, 80, 80), "Neon", transp=0.6, collide=False)
        arena_spawns("ATPRush", cx, cz, 20, Y)


def enzyme_sweeper(cx=0.0, cz=300.0):
    """round platform; the server spins kill bars around the hub, faster and faster. v61: the hub is the enzyme (a
    purple globule with its active-site pocket), the floor tiles are substrate, a lipid rim marks the edge."""
    with G.Group("Arena_EnzymeSweeper"):
        disc("SweepFloor", cx, Y - 1, cz, 70, 2, (92, 80, 140), "SmoothPlastic")
        disc("SweepRing", cx, Y + 0.03, cz, 30, 0.06, (120, 106, 172), "SmoothPlastic", collide=False, shadow=False)
        for i in range(12):
            a = i * 2 * math.pi / 12
            disc("SweepTile", cx + 22 * math.cos(a), Y + 0.04, cz + 22 * math.sin(a), 6, 0.08, (255, 214, 140), "SmoothPlastic",
                 collide=False, shadow=False)
        vcyl("SweepHubBase", cx, Y, Y + 5, cz, 6, (150, 100, 210), "SmoothPlastic")
        ball("EnzymeGlobule", cx, Y + 7, cz, 8, (170, 120, 230), "SmoothPlastic", collide=False)
        ball("ActiveSite", cx + 3.2, Y + 7.6, cz, 3, (60, 30, 90), "SmoothPlastic", collide=False, shadow=False)
        ball("Substrate", cx + 4.6, Y + 7.6, cz, 1.8, (255, 214, 140), "Neon", collide=False, shadow=False)
        for i in range(44):
            a = i * 2 * math.pi / 44
            ball("SweepRim", cx + 35.4 * math.cos(a), Y - 0.6, cz + 35.4 * math.sin(a), 1.8,
                 (255, 196, 120) if i % 2 else (255, 150, 170), "SmoothPlastic", collide=False, shadow=False)
        G.part("SweepHub", (2, 2, 2), (cx, Y + 2.2, cz), (0, 0, 0), "SmoothPlastic", transp=1, collide=False, shadow=False)
        G.part("KillFloor|EnzymeSweeper", (200, 2, 200), (cx, Y - 40, cz), (255, 80, 80), "Neon", transp=0.6, collide=False)
        arena_spawns("EnzymeSweeper", cx, cz, 26, Y)


LAST_RINGS = (14.0, 22.0, 30.0, 38.0)   # outer radius of each membrane ring (the nucleus is r < 6)


def last_cell(cx=0.0, cz=-300.0):
    """v37 "Last Cell Standing": a round cell floating in the cytoplasm. Four membrane rings (segments named
    MembraneSeg|<ring>) drop from the outside in during the round; the nucleus in the middle never drops. Hazards
    (spores, cilia waves, lysosome shields) are spawned by the server module at run time."""
    cols = [(120, 200, 150), (150, 210, 120), (230, 200, 120), (240, 160, 150)]
    with G.Group("Arena_LastCell"):
        disc("Nucleus", cx, Y - 1, cz, 12, 2, (150, 110, 220), "SmoothPlastic")
        disc("Nucleolus", cx, Y + 0.05, cz, 5, 0.1, (110, 70, 190), "Neon", collide=False, shadow=False)
        inner = 6.0
        for k, outer in enumerate(LAST_RINGS):
            n = 8 + k * 4
            rm = (inner + outer) / 2
            chord = 2 * rm * math.sin(math.pi / n) + 1.4
            for i in range(n):
                a = (i + 0.5) * 2 * math.pi / n
                G.part("MembraneSeg|%d" % (k + 1), (outer - inner + 0.2, 2, chord), (cx + rm * math.cos(a), Y - 1, cz + rm * math.sin(a)),
                       cols[k] if i % 2 else tuple(min(255, v + 14) for v in cols[k]), "SmoothPlastic",
                       rot=(0, -math.degrees(a), 0))
            inner = outer
        # glowing lipid rim under the outer edge (decor only)
        for i in range(36):
            a = i * 2 * math.pi / 36
            ball("LastRim", cx + (LAST_RINGS[-1] + 0.6) * math.cos(a), Y - 2.2, cz + (LAST_RINGS[-1] + 0.6) * math.sin(a), 1.6,
                 (255, 196, 120) if i % 2 else (255, 150, 170), "SmoothPlastic", collide=False, shadow=False)
        G.part("KillFloor|LastCell", (200, 2, 200), (cx, Y - 40, cz), (255, 80, 80), "Neon", transp=0.6, collide=False)
        arena_spawns("LastCell", cx, cz, 30, Y)


def lab_rush(cx=-300.0, cz=300.0):
    """v38 "Lab Rush" (co-op), v61 real-science stations: a bright teaching lab. The server (Minigames/LabRush.luau)
    adds ProximityPrompts to the named stations at run time: DNABin|A/T/G/C + DNAConsole (complementary strand),
    MutIngredient|1..3 (enzyme shelves) + MutMachine (reaction tube) + MutOutput, SorterBelt + SortBin|1..2 (Gram
    stain / shape), ReactorLever|1..2 (centrifuge tubes) + ReactorCore (rotor), and writes the orders on OrderBoard."""
    W, D = 84.0, 64.0
    with G.Group("Arena_LabRush"):
        box("LabFloor", (W, 2, D), (cx, Y - 1, cz), (226, 232, 236), "SmoothPlastic")
        for i in range(-3, 4):   # floor stripes
            box("LabStripe", (0.6, 0.06, D - 4), (cx + i * 12, Y + 0.03, cz), (180, 220, 230), "SmoothPlastic", collide=False,
                shadow=False)
        for sx, sz, sw, sd in ((0, -D / 2, W, 1), (0, D / 2, W, 1), (-W / 2, 0, 1, D), (W / 2, 0, 1, D)):
            box("LabWall", (sw, 12, sd), (cx + sx, Y + 6, cz + sz), (232, 238, 242), "SmoothPlastic")
            box("LabWallStripe", (sw + 0.2 if sd < 2 else sw, 1, sd + 0.2 if sw < 2 else sd), (cx + sx, Y + 3, cz + sz),
                (60, 170, 190), "SmoothPlastic", collide=False, shadow=False)
        G.part("OrderBoard", (40, 10, 0.6), (cx, Y + 6.5, cz - D / 2 + 1), (20, 30, 44), "SmoothPlastic",
               text=dict(face="Back", text="🧪 مختبر السباق\nLab Rush", color=(255, 255, 255), bg=(20, 30, 44), bg_t=0.0))
        # DNA strand (west): four base bins and the console
        dx, dz = cx - 28, cz - 12
        for i, (L, col) in enumerate((("A", (220, 70, 70)), ("T", (235, 190, 50)), ("G", (70, 180, 90)), ("C", (70, 130, 230)))):
            G.part("DNABin|" + L, (4, 3, 4), (dx - 6 + i * 4.6, Y + 1.5, dz), col, "SmoothPlastic",
                   text=dict(face="Back", text=L, color=(255, 255, 255), bg=col, bg_t=0.0))
        G.part("DNAConsole", (12, 4, 3), (dx + 1, Y + 2, dz - 6), (60, 64, 80), "SmoothPlastic",
               text=dict(face="Back", text="🧬 الشريط المكمّل\nA ⇄ T   G ⇄ C", color=(255, 255, 255), bg=(60, 64, 80),
                         bg_t=0.0))
        # enzyme bench (east): three enzyme bottles, the reaction tube and its output tray
        mx, mz = cx + 26, cz - 12
        box("EnzymeShelf", (22, 1, 5), (mx, Y + 0.5, mz + 4), (150, 120, 90), "WoodPlanks")
        for i, (name, col) in enumerate((("أميليز", (120, 180, 255)), ("بروتياز", (255, 140, 140)), ("ليبيز", (255, 210, 90)))):
            G.part("MutIngredient|%d" % (i + 1), (3.4, 3.4, 3.4), (mx - 7 + i * 7, Y + 2.7, mz + 4), col, "SmoothPlastic",
                   text=dict(face="Back", text=name, color=(30, 30, 40), bg=col, bg_t=1.0))
            vcyl("BottleNeck", mx - 7 + i * 7, Y + 4.4, Y + 5.6, mz + 4, 1.4, (235, 240, 245), "SmoothPlastic", collide=False)
        G.part("MutMachine", (8, 7, 6), (mx, Y + 3.5, mz - 5), (70, 150, 180), "SmoothPlastic",
               text=dict(face="Back", text="🧪 أنبوب التفاعل\nEnzyme tube", color=(255, 255, 255), bg=(70, 150, 180), bg_t=0.0))
        vcyl("ReactionTube", mx - 5.5, Y, Y + 9, mz - 5, 2.4, (210, 240, 250), "Glass", transp=0.4, collide=False)
        disc("MutOutput", mx + 9, Y + 0.1, mz - 5, 5, 0.2, (255, 230, 120), "Neon", collide=False, shadow=False)
        # Gram sorter (south-west): belt start + two bins (labels are set by the server per rule)
        sx_, sz_ = cx - 22, cz + 16
        box("SorterBeltBase", (16, 1.2, 4), (sx_, Y + 0.6, sz_), (70, 74, 84), "SmoothPlastic")
        G.part("SorterBelt", (2, 0.4, 2), (sx_ - 6, Y + 1.4, sz_), (0, 0, 0), "SmoothPlastic", transp=1, collide=False, shadow=False)
        for i, (sym, col) in enumerate((("🟣", (130, 60, 170)), ("🩷", (235, 120, 170)))):
            G.part("SortBin|%d" % (i + 1), (5, 3.4, 4.4), (sx_ - 4 + i * 8, Y + 1.7, sz_ + 7), col, "SmoothPlastic",
                   text=dict(face="Front", text=sym, color=(255, 255, 255), bg=col, bg_t=0.0))
        # centrifuge (south-east): two tube holders on opposite sides of the rotor
        rx, rz = cx + 24, cz + 18
        vcyl("CentrifugeBody", rx, Y, Y + 3.6, rz + 4, 9, (232, 236, 242), "SmoothPlastic")
        vcyl("CentrifugeBowl", rx, Y + 3.6, Y + 3.8, rz + 4, 7, (60, 64, 74), "Metal", collide=False)
        G.part("ReactorCore", (8, 0.6, 1.6), (rx, Y + 4.2, rz + 4), (120, 255, 200), "Neon", collide=False, shadow=False)
        for i, ox in enumerate((-14, 14)):
            G.part("ReactorLever|%d" % (i + 1), (4, 1.6, 1.6), (rx + ox, Y + 3, rz), (120, 200, 255), "Glass", shape="Cylinder",
                   rot=(0, 0, 90), transp=0.2)
            box("LeverBase", (4, 1, 4), (rx + ox, Y + 0.5, rz), (60, 64, 74), "Metal")
        G.part("KillFloor|LabRush", (200, 2, 200), (cx, Y - 40, cz), (255, 80, 80), "Neon", transp=0.6, collide=False)
        for i in range(8):
            G.part("ArenaSpawn", (2, 1, 2), (cx - 14 + i * 4, Y + 0.5, cz + 4), (0, 0, 0), "SmoothPlastic", transp=1,
                   collide=False, shadow=False)


def cell_control_room(cx=0.0, cz=-650.0):
    """v61 puzzle room "Restart the Cell" (co-op or solo, no timer), map folder PuzzleRoom_CellControl.
    The room is the inside of a cell: membrane walls, cytoplasm floor, the nucleus at the north is the goal.
    Anchors used by server/PuzzleTypes/*: CircuitTile|r|c (4 x 5) + CircuitSource (mitochondrion) + CircuitSink,
    Pedestal|1..4 + SpecimenClues, CorePanel|1..4 + CoreLever + Core, SymbolScreen|1..2, StepLamp|1..3 (3 = floor ring),
    HintTerminal, ResetTerminal, RoomBounds, PuzzleSpawn."""
    W, D, H = 76.0, 60.0, 18.0
    deco = random.Random(61)   # own RNG: the shared rng feeds the arenas built after this room
    MEMB, HEAD = (196, 112, 150), (232, 170, 196)
    with G.Group("PuzzleRoom_CellControl"):
        box("PuzzleFloor", (W, 2, D), (cx, Y - 1, cz), (96, 150, 160), "SmoothPlastic")
        box("PuzzleCeiling", (W + 1.2, 0.6, D + 1.2), (cx, Y + H + 0.9, cz), (120, 70, 104), "SmoothPlastic")
        for lx in (-24, 0, 24):
            for lz in (-16, 10):
                disc("PuzzleLamp", cx + lx, Y + H + 0.5, cz + lz, 7, 0.3, (240, 228, 236), "SmoothPlastic", collide=False,
                     shadow=False, light=(0.9, 30, (255, 240, 236)))
        # membrane walls with a row of phospholipid heads along the floor and the ceiling
        for sx, sz, sw, sd in ((0, -D / 2, W, 1.2), (-W / 2, 0, 1.2, D), (W / 2, 0, 1.2, D)):
            box("PuzzleWall", (sw, H, sd), (cx + sx, Y + H / 2, cz + sz), MEMB, "SmoothPlastic")
        for sx in (-1, 1):
            box("PuzzleWall", (W / 2 - 8, H, 1.2), (cx + sx * (W / 4 + 4), Y + H / 2, cz + D / 2), MEMB, "SmoothPlastic")
        for hy in (0.9, H - 0.9):
            for i in range(int(W / 3) + 1):
                x = cx - W / 2 + i * 3
                if hy < 2:   # the goal wall keeps its top clear for the board and the lamps
                    ball("LipidHead", x, Y + hy, cz - D / 2 + 1, 1.8, HEAD, "SmoothPlastic", collide=False, shadow=False)
                if abs(x - cx) > 8:
                    ball("LipidHead", x, Y + hy, cz + D / 2 - 1, 1.8, HEAD, "SmoothPlastic", collide=False, shadow=False)
            for i in range(1, int(D / 3)):
                for side in (-1, 1):
                    ball("LipidHead", cx + side * (W / 2 - 1), Y + hy, cz - D / 2 + i * 3, 1.8, HEAD, "SmoothPlastic",
                         collide=False, shadow=False)
        # cytoplasm life: ribosome dots and rough ER folds along the side walls
        for _ in range(40):
            x, z = cx + deco.uniform(-W / 2 + 3, W / 2 - 3), cz + deco.uniform(-D / 2 + 3, D / 2 - 3)
            if abs(x - cx) < 12 or abs(z - cz) < 13:
                continue
            ball("Ribosome", x, Y + 0.3, z, deco.uniform(0.8, 1.4), (120, 90, 170), "SmoothPlastic", collide=False,
                 shadow=False)
        for side in (-1, 1):
            for k in range(5):
                box("RoughER", (1.2, 6, 4.6), (cx + side * (W / 2 - 2.2), Y + 6 + (k % 2) * 3, cz + 14 + k * 2.6),
                    (120, 170, 230), "SmoothPlastic", rot=(0, 0, side * 8), collide=False)
                for q in range(3):
                    ball("ERRibosome", cx + side * (W / 2 - 3), Y + 4.5 + (k % 2) * 3 + q * 1.8, cz + 14 + k * 2.6, 0.7,
                         (120, 90, 170), "SmoothPlastic", collide=False, shadow=False)
        G.part("RoomBounds", (W, 30, D), (cx, Y + 14, cz), (0, 0, 0), "SmoothPlastic", transp=1, collide=False, shadow=False)
        G.part("PuzzleSpawn", (8, 1, 8), (cx, Y + 0.5, cz + D / 2 - 6), (0, 0, 0), "SmoothPlastic", transp=1, collide=False)
        # goal wall: objective, three step lamps, the two code screens
        sign("PuzzleTitle", "🎯 شغّلوا نواة الخلية", (cx, Y + H - 1.6, cz - D / 2 + 0.7), (30, 2.8, 0.4), "Back",
             bg=(70, 40, 110))
        for i, ox in enumerate((-22, 22)):
            G.part("SymbolScreen|%d" % (i + 1), (10, 5, 0.4), (cx + ox, Y + 9, cz - D / 2 + 0.7), (16, 20, 30),
                   "SmoothPlastic", text=dict(face="Back", text="؟ ؟", color=(255, 255, 255), bg=(16, 20, 30), bg_t=0.0))
            # each station's progress lamp sits under its screen; the third lamp is the ring round the nucleus
            G.part("StepLamp|%d" % (i + 1), (10, 1.2, 0.4), (cx + ox, Y + 5.6, cz - D / 2 + 0.75), (70, 74, 90),
                   "SmoothPlastic")
        # 1) energy: a 4 x 5 pipe floor from the mitochondrion (west) to the receiver (east)
        G.disc("StationPadCircuit", cx - 18, Y + 0.05, cz, 34, 0.1, (150, 200, 205), "SmoothPlastic", collide=False,
               shadow=False)
        for r in range(4):
            for c in range(5):
                G.part("CircuitTile|%d|%d" % (r + 1, c + 1), (5.4, 0.4, 5.4), (cx - 30 + c * 6, Y + 0.2, cz - 9 + r * 6),
                       (90, 104, 124), "SmoothPlastic")
        G.part("CircuitSource", (6, 3.4, 3.4), (cx - 35.5, Y + 1.7, cz), (255, 150, 60), "Neon", shape="Cylinder")
        G.part("CircuitSink", (3, 4, 3), (cx - 0.5, Y + 2, cz), (80, 90, 110), "SmoothPlastic")
        # 2) microscope: four specimen stages and the field guide on the east wall
        G.disc("StationPadSpecimens", cx + 22, Y + 0.05, cz - 2, 30, 0.1, (150, 200, 205), "SmoothPlastic", collide=False,
               shadow=False)
        for i in range(4):
            px = cx + 12.5 + i * 6.5
            vcyl("Pedestal|%d" % (i + 1), px, Y, Y + 3, cz - 2, 3.6, (226, 230, 236), "SmoothPlastic")
            G.disc("StageLight", px, Y + 3.05, cz - 2, 2.6, 0.1, (255, 250, 220), "Neon", collide=False, shadow=False)
        G.part("SpecimenClues", (0.4, 11, 24), (cx + W / 2 - 0.8, Y + 7, cz - 2), (16, 20, 30), "SmoothPlastic",
               text=dict(face="Left", text="🔍", color=(255, 255, 255), bg=(16, 20, 30), bg_t=0.0))
        G.disc("StepLamp|3", cx, Y + 0.06, cz - 22, 18, 0.1, (70, 74, 90), "SmoothPlastic", collide=False, shadow=False)
        ball("NucleusEnvelope", cx, Y + 7.5, cz - 22, 14, (170, 130, 230), "Glass", transp=0.55, collide=False, shadow=False)
        ball("Core", cx, Y + 7.5, cz - 22, 7, (90, 100, 130), "Glass", transp=0.2, shadow=False)
        vcyl("CoreStand", cx, Y, Y + 1, cz - 22, 8, (120, 90, 170), "SmoothPlastic")
        for q in range(8):
            ang = math.radians(q * 45)
            ball("NuclearPore", cx + math.sin(ang) * 6.9, Y + 7.5 + math.cos(ang) * 6.9 * 0.3, cz - 22 + math.cos(ang) * 6.9,
                 1.2, (90, 60, 140), "SmoothPlastic", collide=False, shadow=False)
        for i, ox in enumerate((-9, -3, 3, 9)):
            G.part("CorePanel|%d" % (i + 1), (4.6, 4.6, 1.2), (cx + ox, Y + 2.6, cz - 11), (40, 50, 70), "SmoothPlastic")
        G.part("CoreLever", (1.6, 4, 1.6), (cx + 15, Y + 2, cz - 11), (250, 140, 60), "SmoothPlastic")
        # help desks by the door
        G.part("HintTerminal", (2.6, 4.4, 1.6), (cx - 8, Y + 2.2, cz + D / 2 - 10), (60, 140, 220), "SmoothPlastic",
               text=dict(face="Back", text="💡\nتلميح", color=(255, 255, 255), bg=(60, 140, 220), bg_t=0.0))
        G.part("ResetTerminal", (2.6, 4.4, 1.6), (cx + 8, Y + 2.2, cz + D / 2 - 10), (200, 90, 90), "SmoothPlastic",
               text=dict(face="Back", text="🔄\nإعادة", color=(255, 255, 255), bg=(200, 90, 90), bg_t=0.0))
        G.part("Portal|Arcade", (8, 10, 0.6), (cx, Y + 5.2, cz + D / 2 + 3), (120, 255, 200), "Neon", transp=0.45,
               collide=False, shadow=False)
        sign("PuzzleExit", "↩ الأركيد", (cx, Y + 11, cz + D / 2 + 3.3), (8, 1.8, 0.4), "Back", bg=(24, 80, 56))
        G.part("KillFloor|Puzzle", (200, 2, 200), (cx, Y - 40, cz), (255, 80, 80), "Neon", transp=0.6, collide=False)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "chaos-campus/src/map/Map.rbxmx"
    lobby()
    petri_floor()
    atp_rush()
    enzyme_sweeper()
    last_cell()
    lab_rush()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write('<roblox version="4"><Item class="Folder" referent="%s"><Properties><string name="Name">Map</string>'
                '</Properties>' % G.rid())
        for chunk in G.buf:
            f.write(chunk)
        f.write("</Item></roblox>")
    print("parts:", G.nparts[0])
