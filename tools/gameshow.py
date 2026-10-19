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


def build():
    with G.Group("GameShowStudio"):
        W, D = 104.0, 84.0
        box("StudioFloor", (W, 2, D), (SX, SY - 1, SZ), (40, 30, 64), "SmoothPlastic")
        for i in range(-4, 5):   # glowing floor lines toward the stage
            box("StudioLine", (0.5, 0.06, D - 10), (SX + i * 11, SY + 0.03, SZ + 4), (120, 90, 200), "Neon", collide=False,
                shadow=False)
        for sx, sz, sw, sd in ((0, -D / 2, W, 1.4), (-W / 2, 0, 1.4, D), (W / 2, 0, 1.4, D), (0, D / 2, W, 1.4)):
            box("StudioWall", (sw, 26, sd), (SX + sx, SY + 13, SZ + sz), (30, 24, 50), "SmoothPlastic")
        box("StudioCeilingRim", (W, 0.6, D), (SX, SY + 26.3, SZ), (24, 18, 40), "SmoothPlastic", transp=0.0)
        for lx in (-36, -12, 12, 36):   # stage lights
            for lz in (-26, 0, 22):
                box("StudioLamp", (8, 0.4, 3), (SX + lx, SY + 25.8, SZ + lz), (255, 236, 200), "Neon", collide=False,
                    shadow=False, light=(1.1, 34, (255, 236, 200)))
        G.part("StudioBounds", (W, 30, D), (SX, SY + 14, SZ), (0, 0, 0), "SmoothPlastic", transp=1, collide=False, shadow=False)
        G.part("GameShowSpawn", (8, 1, 8), (SX, SY + 0.5, SZ + 18), (0, 0, 0), "SmoothPlastic", transp=1, collide=False)
        # stage + host
        box("Stage", (60, 3, 16), (SX, SY + 1.5, SZ - 32), (70, 40, 110), "SmoothPlastic")
        box("StageEdge", (60.4, 0.5, 0.5), (SX, SY + 3.1, SZ - 23.8), (255, 200, 90), "Neon", collide=False, shadow=False)
        G.mascot(SX + 25, SY + 3, SZ - 29)   # right end of the stage: clear of the main screen (x -20..20) from the spawn view
        G.part("HostDesk", (10, 4, 3), (SX + 6, SY + 5, SZ - 26), (24, 80, 56), "SmoothPlastic",
               text=dict(face="Back", text="🎙️ ابدأ الحلقة\nStart the show", color=(255, 255, 255), bg=(24, 80, 56), bg_t=0.0))
        G.part("MainScreen", (40, 15, 0.6), (SX, SY + 15, SZ - 40.5), (14, 16, 26), "SmoothPlastic",
               text=dict(face="Back", text="🎮 BSC Game Show\nاستوديو المسابقات", color=(255, 255, 255), bg=(14, 16, 26), bg_t=0.0))
        G.part("ScoreBoard", (40, 4, 0.6), (SX, SY + 24, SZ - 40.5), (40, 20, 60), "SmoothPlastic",
               text=dict(face="Back", text="🏆", color=(255, 236, 160), bg=(40, 20, 60), bg_t=0.0))
        for name, x, col, ry in (("Red", -44, (200, 60, 70), 30), ("Blue", 44, (60, 110, 210), -30)):
            G.part("TeamScreen|" + name, (18, 12, 0.6), (SX + x, SY + 12, SZ - 30), col, "SmoothPlastic", rot=(0, ry, 0),
                   text=dict(face="Back", text="", color=(255, 255, 255), bg=col, bg_t=0.0))
            box("TeamFloor", (W / 2 - 2, 0.08, 40), (SX + (x / abs(x)) * (W / 4), SY + 0.05, SZ + 14), col, "SmoothPlastic",
                collide=False, shadow=False, transp=0.75)
        # picture board (left of the stage) with a 5x5 cover
        px, py, pz = SX - 30, SY + 13, SZ - 24
        G.part("PictureBoard", (14, 14, 0.6), (px, py, pz), (250, 250, 246), "SmoothPlastic",
               text=dict(face="Back", text="❔", color=(30, 30, 40), bg=(250, 250, 246), bg_t=0.0))
        k = 0
        for r in range(5):
            for c in range(5):
                k += 1
                G.part("PictureCover|%d" % k, (2.8, 2.8, 0.3), (px - 5.6 + c * 2.8, py + 5.6 - r * 2.8, pz + 0.5),
                       (90 + (r + c) % 2 * 20, 60, 140), "SmoothPlastic", collide=False, shadow=False)
        # four answer podiums in front of the stage
        for i, col in enumerate(POD_COLORS):
            x = SX - 21 + i * 14
            G.part("AnswerPod|%d" % (i + 1), (8, 3.6, 5), (x, SY + 1.8, SZ - 12), col, "SmoothPlastic",
                   text=dict(face="Back", text="ABCD"[i], color=(255, 255, 255), bg=col, bg_t=0.0))
            disc("PodGlow", x, SY + 0.08, SZ - 6, 9, 0.1, col, "Neon", collide=False, shadow=False)
        # audience-side exit
        G.part("Portal|Campus", (10, 12, 0.6), (SX, SY + 6.2, SZ + D / 2 - 1.4), (120, 255, 200), "Neon", transp=0.45,
               collide=False, shadow=False)
        sign("StudioExit", "↩ الكلية", (SX, SY + 14, SZ + D / 2 - 1.8), (10, 2.2, 0.4), "Front", bg=(24, 80, 56))
        A.logo_board(SX + 30, SY + 16, SZ - 40.4, R=1.2, nx=0.0, nz=1.0)
        G.part("KillFloor|GameShow", (220, 2, 220), (SX, SY - 40, SZ), (255, 80, 80), "Neon", transp=0.6, collide=False)
