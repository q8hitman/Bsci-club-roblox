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
        sign("HowTo", "كيف تلعب؟\n• كل جولة لعبة مختلفة + طفرة عشوائية 🧬\n• آخر واحد يبقى أو أكثر نقاط يفوز\n• الفوز = نقاط ولقب",
             (24, Y + 9, -22), (26, 14, 0.6), "Back", bg=(30, 50, 70))
        # spectator balcony view of the sweeper arena is not needed: players watch from the lobby screens


def arena_spawns(name, cx, cz, r, y):
    for i in range(12):
        a = i * 2 * math.pi / 12
        G.part("ArenaSpawn", (2, 1, 2), (cx + r * math.cos(a), y + 0.5, cz + r * math.sin(a)), (0, 0, 0), "SmoothPlastic",
               transp=1, collide=False, shadow=False)


def petri_floor(cx=300.0, cz=0.0):
    """two layers of hexagonal tiles; each tile drops shortly after someone steps on it"""
    with G.Group("Arena_PetriFloor"):
        for layer, ly in enumerate((Y, Y - 26)):
            R, d = 7, 6.2
            for q in range(-R, R + 1):
                for r in range(-R, R + 1):
                    if abs(q + r) > R:
                        continue
                    x = cx + d * (q + r / 2)
                    z = cz + d * r * math.sqrt(3) / 2
                    col = PASTEL[(q * 2 + r + layer) % 5]
                    G.part("FallTile", (1, d * 1.1, d * 1.1), (x, ly - 0.5, z), col, "SmoothPlastic", shape="Cylinder",
                           rot=(0, 0, 90))
        disc("PetriGlass", cx, Y - 70, cz, 120, 2, (200, 230, 240), "Glass", transp=0.5, collide=False)
        G.part("KillFloor|PetriFloor", (200, 2, 200), (cx, Y - 60, cz), (255, 80, 80), "Neon", transp=0.6, collide=False)
        arena_spawns("PetriFloor", cx, cz, 24, Y)


def atp_rush(cx=-300.0, cz=0.0):
    """open arena with cover; glowing ATP orbs spawn on the OrbSpots"""
    with G.Group("Arena_ATPRush"):
        disc("RushFloor", cx, Y - 1, cz, 120, 2, (60, 90, 140), "SmoothPlastic")
        for i in range(24):
            a = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(8, 52)
            G.part("OrbSpot", (1, 1, 1), (cx + rr * math.cos(a), Y + 2.5, cz + rr * math.sin(a)), (0, 0, 0), "SmoothPlastic",
                   transp=1, collide=False, shadow=False)
        for i in range(8):
            a = i * math.pi / 4 + 0.2
            box("RushRamp", (10, 1, 16), (cx + 34 * math.cos(a), Y + 2, cz + 34 * math.sin(a)), PASTEL[i % 5], "SmoothPlastic",
                rot=(-14, -math.degrees(a) + 90, 0))
            vcyl("RushPillar", cx + 18 * math.cos(a + 0.4), Y, Y + 8, cz + 18 * math.sin(a + 0.4), 4, PASTEL[(i + 2) % 5],
                 "SmoothPlastic")
        n = 40
        for i in range(n):
            a = i * 2 * math.pi / n
            G.part("RushWall", (1.5, 10, 2 * math.pi * 60 / n + 0.5), (cx + 60 * math.cos(a), Y + 5, cz + 60 * math.sin(a)),
                   (120, 200, 255), "SmoothPlastic", transp=0.5, rot=(0, -math.degrees(a), 0))
        G.part("KillFloor|ATPRush", (200, 2, 200), (cx, Y - 40, cz), (255, 80, 80), "Neon", transp=0.6, collide=False)
        arena_spawns("ATPRush", cx, cz, 20, Y)


def enzyme_sweeper(cx=0.0, cz=300.0):
    """round platform; the server spins kill bars around the hub, faster and faster"""
    with G.Group("Arena_EnzymeSweeper"):
        disc("SweepFloor", cx, Y - 1, cz, 70, 2, (70, 80, 110), "SmoothPlastic")
        for i in range(12):
            a = i * 2 * math.pi / 12
            disc("SweepTile", cx + 22 * math.cos(a), Y + 0.04, cz + 22 * math.sin(a), 6, 0.08, PASTEL[i % 5], "SmoothPlastic",
                 collide=False, shadow=False)
        vcyl("SweepHubBase", cx, Y, Y + 5, cz, 6, (60, 64, 74), "Metal")
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
    """v38 "Lab Rush" (co-op): a bright fantasy lab. The server (Minigames/LabRush.luau) adds ProximityPrompts to the
    named stations at run time: DNABin|A/T/G/C + DNAConsole, MutIngredient|1..3 + MutMachine + MutOutput,
    SorterBelt + SortBin|1..3, ReactorLever|1..2 + ReactorCore, and writes the orders on OrderBoard."""
    W, D = 84.0, 64.0
    with G.Group("Arena_LabRush"):
        box("LabFloor", (W, 2, D), (cx, Y - 1, cz), (232, 238, 240), "SmoothPlastic")
        for i in range(-3, 4):   # floor stripes
            box("LabStripe", (0.6, 0.06, D - 4), (cx + i * 12, Y + 0.03, cz), (180, 220, 230), "SmoothPlastic", collide=False,
                shadow=False)
        for sx, sz, sw, sd in ((0, -D / 2, W, 1), (0, D / 2, W, 1), (-W / 2, 0, 1, D), (W / 2, 0, 1, D)):
            box("LabWall", (sw, 4, sd), (cx + sx, Y + 2, cz + sz), (90, 170, 200), "SmoothPlastic")
        G.part("OrderBoard", (40, 10, 0.6), (cx, Y + 9, cz - D / 2 + 0.6), (20, 30, 44), "SmoothPlastic",
               text=dict(face="Back", text="🧪 Lab Rush", color=(255, 255, 255), bg=(20, 30, 44), bg_t=0.0))
        vcyl("BoardLeg", cx - 16, Y, Y + 4.4, cz - D / 2 + 0.6, 0.8, (60, 64, 74), "Metal", collide=False)
        vcyl("BoardLeg", cx + 16, Y, Y + 4.4, cz - D / 2 + 0.6, 0.8, (60, 64, 74), "Metal", collide=False)
        # DNA mixer (west): four base bins and the console
        dx, dz = cx - 28, cz - 12
        for i, (L, col) in enumerate((("A", (230, 80, 80)), ("T", (80, 140, 230)), ("G", (80, 200, 110)), ("C", (240, 200, 60)))):
            G.part("DNABin|" + L, (4, 3, 4), (dx - 6 + i * 4.6, Y + 1.5, dz), col, "SmoothPlastic",
                   text=dict(face="Back", text=L, color=(255, 255, 255), bg=col, bg_t=0.0))
        G.part("DNAConsole", (12, 4, 3), (dx + 1, Y + 2, dz - 6), (60, 64, 80), "SmoothPlastic",
               text=dict(face="Back", text="🧬 DNA Mixer\nخلّاط الـDNA", color=(255, 255, 255), bg=(60, 64, 80), bg_t=0.0))
        # mutation machine (east): three ingredient shelves, the machine and an output pad
        mx, mz = cx + 26, cz - 12
        for i, col in enumerate(((255, 170, 60), (170, 120, 255), (90, 220, 200))):
            G.part("MutIngredient|%d" % (i + 1), (3.4, 3.4, 3.4), (mx - 7 + i * 7, Y + 1.7, mz + 4), col, "SmoothPlastic")
        G.part("MutMachine", (8, 7, 6), (mx, Y + 3.5, mz - 5), (200, 90, 160), "SmoothPlastic",
               text=dict(face="Back", text="🧪 Mutation Machine\nآلة الطفرات", color=(255, 255, 255), bg=(200, 90, 160), bg_t=0.0))
        disc("MutOutput", mx + 9, Y + 0.1, mz - 5, 5, 0.2, (255, 230, 120), "Neon", collide=False, shadow=False)
        # sample sorter (south-west): belt start + three bins
        sx_, sz_ = cx - 22, cz + 16
        box("SorterBeltBase", (16, 1.2, 4), (sx_, Y + 0.6, sz_), (70, 74, 84), "SmoothPlastic")
        G.part("SorterBelt", (2, 0.4, 2), (sx_ - 6, Y + 1.4, sz_), (0, 0, 0), "SmoothPlastic", transp=1, collide=False, shadow=False)
        for i, (sym, col) in enumerate((("●", (230, 80, 80)), ("■", (80, 140, 230)), ("▮", (240, 200, 60)))):
            G.part("SortBin|%d" % (i + 1), (4.4, 3.4, 4.4), (sx_ - 6 + i * 6, Y + 1.7, sz_ + 7), col, "SmoothPlastic",
                   text=dict(face="Front", text=sym, color=(255, 255, 255), bg=col, bg_t=0.0))
        # lab reactor (south-east): two levers far apart + the core between them
        rx, rz = cx + 24, cz + 18
        for i, ox in enumerate((-14, 14)):
            G.part("ReactorLever|%d" % (i + 1), (2, 4, 2), (rx + ox, Y + 2, rz), (250, 140, 60), "SmoothPlastic")
            box("LeverBase", (4, 1, 4), (rx + ox, Y + 0.5, rz), (60, 64, 74), "Metal")
        ball("ReactorCore", rx, Y + 4, rz + 4, 6, (120, 255, 200), "Neon", transp=0.2, shadow=False)
        G.part("KillFloor|LabRush", (200, 2, 200), (cx, Y - 40, cz), (255, 80, 80), "Neon", transp=0.6, collide=False)
        for i in range(8):
            G.part("ArenaSpawn", (2, 1, 2), (cx - 14 + i * 4, Y + 0.5, cz + 4), (0, 0, 0), "SmoothPlastic", transp=1,
                   collide=False, shadow=False)


def cell_control_room(cx=0.0, cz=-650.0):
    """v39 puzzle room "Cell Control Room" (co-op or solo, no timer). Anchors used by server/PuzzleTypes/*:
    CircuitTile|r|c (3x4 floor grid) + CircuitSource + CircuitSink, Pedestal|1..4 + SpecimenClues, CorePanel|1..2 +
    CoreLever + Core, SymbolScreen|1..2, HintTerminal, ResetTerminal, RoomBounds, PuzzleSpawn."""
    W, D = 76.0, 60.0
    with G.Group("PuzzleRoom_CellControl"):
        box("PuzzleFloor", (W, 2, D), (cx, Y - 1, cz), (96, 108, 132), "SmoothPlastic")
        for lx in (-24, 0, 24):   # ceiling lamps: the arcade's dusk lighting made the room too dark to read
            for lz in (-14, 10):
                box("PuzzleLamp", (10, 0.4, 4), (cx + lx, Y + 13, cz + lz), (255, 246, 226), "Neon", collide=False, shadow=False,
                    light=(1.2, 30, (255, 246, 226)))
        for sx, sz, sw, sd in ((0, -D / 2, W, 1.2), (-W / 2, 0, 1.2, D), (W / 2, 0, 1.2, D)):
            box("PuzzleWall", (sw, 12, sd), (cx + sx, Y + 6, cz + sz), (110, 140, 170), "SmoothPlastic")
            box("PuzzleTrim", (sw + 0.2, 0.4, sd + 0.2), (cx + sx, Y + 12.1, cz + sz), (120, 255, 200), "Neon", collide=False,
                shadow=False)
        for sx in (-1, 1):   # south wall with a wide doorway
            box("PuzzleWall", (W / 2 - 8, 12, 1.2), (cx + sx * (W / 4 + 4), Y + 6, cz + D / 2), (110, 140, 170), "SmoothPlastic")
        G.part("RoomBounds", (W, 30, D), (cx, Y + 14, cz), (0, 0, 0), "SmoothPlastic", transp=1, collide=False, shadow=False)
        G.part("PuzzleSpawn", (8, 1, 8), (cx, Y + 0.5, cz + D / 2 - 6), (0, 0, 0), "SmoothPlastic", transp=1, collide=False)
        sign("PuzzleTitle", "🧩 غرفة التحكم بالخلية\nCell Control Room", (cx, Y + 10, cz - D / 2 + 0.7), (26, 4.4, 0.4), "Back",
             bg=(24, 80, 56))
        # 1) energy circuit: 3 x 4 floor tiles, source on the west, device on the east (west half of the room)
        for r in range(3):
            for c in range(4):
                G.part("CircuitTile|%d|%d" % (r + 1, c + 1), (5.4, 0.4, 5.4), (cx - 30 + c * 6, Y + 0.2, cz - 6 + r * 6),
                       (70, 78, 96), "SmoothPlastic")
        box("CircuitSource", (3, 3, 3), (cx - 35, Y + 1.5, cz), (255, 200, 60), "Neon")
        G.part("CircuitSink", (3, 4, 3), (cx - 7.5, Y + 2, cz), (80, 90, 110), "SmoothPlastic")
        G.part("SymbolScreen|1", (8, 5, 0.4), (cx - 21, Y + 8, cz - D / 2 + 0.7), (16, 20, 30), "SmoothPlastic",
               text=dict(face="Back", text="⚡ ؟", color=(255, 255, 255), bg=(16, 20, 30), bg_t=0.0))
        # 2) specimen detective: four pedestals + the clue board (east half)
        for i in range(4):
            vcyl("Pedestal|%d" % (i + 1), cx + 12 + i * 6.5, Y, Y + 3, cz - 4, 3.6, (200, 206, 214), "Marble")
        G.part("SpecimenClues", (0.4, 9, 22), (cx + W / 2 - 0.8, Y + 6, cz - 4), (16, 20, 30), "SmoothPlastic",
               text=dict(face="Left", text="🔍", color=(255, 255, 255), bg=(16, 20, 30), bg_t=0.0))
        G.part("SymbolScreen|2", (8, 5, 0.4), (cx + 21, Y + 8, cz - D / 2 + 0.7), (16, 20, 30), "SmoothPlastic",
               text=dict(face="Back", text="🔬 ؟", color=(255, 255, 255), bg=(16, 20, 30), bg_t=0.0))
        # 3) core activation (north centre)
        ball("Core", cx, Y + 6, cz - 21, 7, (90, 100, 130), "Glass", transp=0.2, shadow=False)
        vcyl("CoreStand", cx, Y, Y + 2.6, cz - 21, 5, (60, 64, 80), "Metal")
        for i, ox in enumerate((-7, 7)):
            G.part("CorePanel|%d" % (i + 1), (4, 4, 1.2), (cx + ox, Y + 2, cz - 13), (40, 50, 70), "SmoothPlastic")
        G.part("CoreLever", (1.6, 4, 1.6), (cx, Y + 2, cz - 12), (250, 140, 60), "SmoothPlastic")
        # help desks by the door
        G.part("HintTerminal", (3, 4, 2), (cx - 8, Y + 2, cz + D / 2 - 10), (60, 140, 220), "SmoothPlastic",
               text=dict(face="Back", text="💡\nتلميح", color=(255, 255, 255), bg=(60, 140, 220), bg_t=0.0))
        G.part("ResetTerminal", (3, 4, 2), (cx + 8, Y + 2, cz + D / 2 - 10), (200, 90, 90), "SmoothPlastic",
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
