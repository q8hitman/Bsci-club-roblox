"""v40 BSC Game Show studio (world at (0, 300, -7000)). Names used by server/GameShow.server.luau:
  StudioBounds, GameShowSpawn, HostDesk (start prompt), MainScreen, ScoreBoard, TeamScreen|Red, TeamScreen|Blue,
  AnswerPod|1..4, PictureBoard (big emoji) + PictureCover|1..25 (5x5 tiles in front of it), Portal|Campus (exit).
"""
import math

import genmap as G
import bsc_art as A

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign
SX, SY, SZ = 0.0, 300.0, -7000.0
POD_COLORS = [(230, 80, 80), (80, 140, 230), (90, 200, 110), (240, 190, 60)]


GOLD = (255, 200, 90)
FRAME = (34, 36, 46)


def light_tower(x, z, col):
    """truss column with stacked colour lamps beside the LED wall"""
    for dx in (-1.2, 1.2):
        for dz in (-1.2, 1.2):
            vcyl("TowerPost", SX + x + dx, SY, SY + 24, SZ + z + dz, 0.4, (150, 154, 162), "Metal", collide=False)
    for k in range(5):
        box("TowerRung", (3, 0.3, 3), (SX + x, SY + 2 + k * 5, SZ + z), (150, 154, 162), "Metal", collide=False)
        ball("TowerLamp", SX + x, SY + 4.5 + k * 5, SZ + z + 1.6, 1.6, col if k % 2 == 0 else GOLD, "Neon", collide=False,
             shadow=False)


def build():
    """v59 (owner: 'a collection of basic blocks'): a TV studio. Big framed LED wall between two light towers, a
    bulb-lined stage, real contestant podiums (lit top strip = PodLight|i, the server turns the right one green),
    a framed picture screen, tiered audience seating and a lighting truss. Every scripted part keeps its name."""
    NL = chr(10)
    with G.Group("GameShowStudio"):
        W, D = 104.0, 84.0
        box("StudioFloor", (W, 2, D), (SX, SY - 1, SZ), (22, 20, 34), "SmoothPlastic")
        disc("ArenaFloor", SX, SY + 0.02, SZ - 8, 62, 0.1, (40, 34, 86), "SmoothPlastic", collide=False, shadow=False)
        disc("ArenaRing", SX, SY + 0.01, SZ - 8, 63.6, 0.08, GOLD, "Neon", collide=False, shadow=False)
        for sx, sz, sw, sd in ((0, -D / 2, W, 1.4), (-W / 2, 0, 1.4, D), (W / 2, 0, 1.4, D), (0, D / 2, W, 1.4)):
            box("StudioWall", (sw, 26, sd), (SX + sx, SY + 13, SZ + sz), (26, 22, 44), "SmoothPlastic")
        for side in (-1, 1):   # LED strips on the side walls
            for k in range(5):
                box("WallStrip", (0.3, 18, 1.2), (SX + side * (W / 2 - 0.9), SY + 11, SZ - 30 + k * 14),
                    (120, 80, 220) if k % 2 else (70, 200, 230), "Neon", collide=False, shadow=False)
        box("StudioCeilingRim", (W, 0.6, D), (SX, SY + 26.3, SZ), (18, 14, 30), "SmoothPlastic", transp=0.0)
        for lz in (-26, -6, 14):   # lighting truss + spot lamps
            box("Truss", (W - 4, 1, 1), (SX, SY + 24.5, SZ + lz), (150, 154, 162), "Metal", collide=False)
            for lx in (-36, -12, 12, 36):
                G.part("SpotLamp", (2.6, 2, 2), (SX + lx, SY + 23, SZ + lz), FRAME, "Metal", shape="Cylinder", rot=(0, 0, 90),
                       collide=False, shadow=False)
                box("StudioLamp", (1.6, 0.2, 1.6), (SX + lx, SY + 21.9, SZ + lz), (255, 236, 200), "Neon", collide=False,
                    shadow=False, light=(1.1, 34, (255, 236, 200)))
        G.part("StudioBounds", (W, 30, D), (SX, SY + 14, SZ), (0, 0, 0), "SmoothPlastic", transp=1, collide=False, shadow=False)
        G.part("GameShowSpawn", (8, 1, 8), (SX, SY + 0.5, SZ + 18), (0, 0, 0), "SmoothPlastic", transp=1, collide=False)
        # stage: two tiers, gold edge and a row of marquee bulbs
        box("Stage", (60, 3, 16), (SX, SY + 1.5, SZ - 32), (60, 34, 100), "SmoothPlastic")
        box("StageRiser", (44, 1.4, 6), (SX, SY + 3.7, SZ - 37), (48, 28, 84), "SmoothPlastic")
        box("StageEdge", (60.4, 0.5, 0.5), (SX, SY + 3.1, SZ - 23.8), GOLD, "Neon", collide=False, shadow=False)
        for k in range(15):
            ball("StageBulb", SX - 28 + k * 4, SY + 1.6, SZ - 23.7, 0.9, (255, 236, 180), "Neon", collide=False, shadow=False)
        G.mascot(SX + 25, SY + 3, SZ - 29)   # right end of the stage: clear of the main screen (x -20..20) from the spawn view
        G.part("HostDesk", (10, 4, 3), (SX + 6, SY + 5, SZ - 26), (24, 80, 56), "SmoothPlastic",
               text=dict(face="Back", text="ابدأ الحلقة" + NL + "Start the show", color=(255, 255, 255), bg=(24, 80, 56),
                         bg_t=0.0))
        box("HostDeskTop", (10.6, 0.4, 3.6), (SX + 6, SY + 7.2, SZ - 26), (230, 230, 226), "SmoothPlastic")
        # LED wall: the main screen in a bezel, the score strip above, light towers either side
        box("ScreenBezel", (43, 18, 0.8), (SX, SY + 15, SZ - 41.1), FRAME, "Metal")
        G.part("MainScreen", (40, 15, 0.6), (SX, SY + 15, SZ - 40.5), (14, 16, 26), "SmoothPlastic",
               text=dict(face="Back", text="BSC Game Show" + NL + "استوديو المسابقات", color=(255, 255, 255), bg=(14, 16, 26),
                         bg_t=0.0))
        box("ScoreBezel", (42, 5, 0.8), (SX, SY + 24, SZ - 41.1), FRAME, "Metal")
        G.part("ScoreBoard", (40, 4, 0.6), (SX, SY + 24, SZ - 40.5), (40, 20, 60), "SmoothPlastic",
               text=dict(face="Back", text="BSC", color=(255, 236, 160), bg=(40, 20, 60), bg_t=0.0))
        light_tower(-25, -39, (70, 200, 230))
        light_tower(25, -39, (230, 80, 120))
        for name, x, col, ry in (("Red", -44, (200, 60, 70), 30), ("Blue", 44, (60, 110, 210), -30)):
            G.part("TeamScreen|" + name, (18, 12, 0.6), (SX + x, SY + 12, SZ - 30), col, "SmoothPlastic", rot=(0, ry, 0),
                   text=dict(face="Back", text="", color=(255, 255, 255), bg=col, bg_t=0.0))
            box("TeamFloor", (W / 2 - 2, 0.08, 40), (SX + (x / abs(x)) * (W / 4), SY + 0.05, SZ + 14), col, "SmoothPlastic",
                collide=False, shadow=False, transp=0.75)
        # picture screen (left of the stage): bigger, framed, 5x5 cover tiles
        px, py, pz = SX - 30, SY + 13, SZ - 24
        box("PictureBezel", (19.6, 19.6, 0.5), (px, py, pz - 0.5), FRAME, "Metal")
        G.part("PictureBoard", (18, 18, 0.6), (px, py, pz), (250, 250, 246), "SmoothPlastic",
               text=dict(face="Back", text="?", color=(30, 30, 40), bg=(250, 250, 246), bg_t=0.0))
        vcyl("PicturePost", px, SY, py - 9.8, pz - 0.6, 1.2, FRAME, "Metal", collide=False)
        k = 0
        for r in range(5):
            for c in range(5):
                k += 1
                G.part("PictureCover|%d" % k, (3.6, 3.6, 0.3), (px - 7.2 + c * 3.6, py + 7.2 - r * 3.6, pz + 0.5),
                       (110, 60, 160) if (r + c) % 2 else (240, 180, 70), "SmoothPlastic", collide=False, shadow=False)
        # contestant podiums: AnswerPod|i is the lettered front (prompt + touch), PodLight|i the lit top strip
        for i, col in enumerate(POD_COLORS):
            x = SX - 21 + i * 14
            G.part("AnswerPod|%d" % (i + 1), (8, 3.6, 5), (x, SY + 1.8, SZ - 12), col, "SmoothPlastic",
                   text=dict(face="Back", text="ABCD"[i], color=(255, 255, 255), bg=col, bg_t=0.0))
            box("PodTop", (8.6, 0.5, 5.6), (x, SY + 3.85, SZ - 12), (236, 236, 240), "SmoothPlastic")
            G.part("PodLight|%d" % (i + 1), (8.2, 0.35, 0.3), (x, SY + 3.4, SZ - 9.4), col, "Neon", collide=False, shadow=False)
            box("PodBase", (9, 0.4, 6), (x, SY + 0.2, SZ - 12), FRAME, "Metal")
            disc("PodGlow", x, SY + 0.08, SZ - 6, 9, 0.1, col, "Neon", transp=0.3, collide=False, shadow=False)
        # audience: three tiers each side of the centre aisle
        for side in (-1, 1):
            for t in range(3):
                h = 1.2 + t * 1.6
                box("Bleacher", (34, h, 5), (SX + side * 26, SY + h / 2, SZ + 26 + t * 5),
                    (70, 40, 110) if t % 2 == 0 else (90, 52, 140), "SmoothPlastic")
                box("BleacherEdge", (34, 0.2, 0.3), (SX + side * 26, SY + h + 0.05, SZ + 23.6 + t * 5), GOLD, "Neon",
                    collide=False, shadow=False)
        # audience-side exit
        G.part("Portal|Campus", (10, 12, 0.6), (SX, SY + 6.2, SZ + D / 2 - 1.4), (120, 255, 200), "Neon", transp=0.45,
               collide=False, shadow=False)
        sign("StudioExit", "الكلية", (SX, SY + 14, SZ + D / 2 - 1.8), (10, 2.2, 0.4), "Front", bg=(24, 80, 56))
        A.logo_board(SX + 30, SY + 16, SZ - 40.4, R=1.2, nx=0.0, nz=1.0)
        G.part("KillFloor|GameShow", (220, 2, 220), (SX, SY - 40, SZ), (255, 80, 80), "Neon", transp=0.6, collide=False)
