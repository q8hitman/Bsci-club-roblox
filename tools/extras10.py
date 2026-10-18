"""v10 extras (absolute coordinates; call with every offset at 0):
  virus_arena()   Virus Tag arena floating near the HQ (+ Portal|Virus in the HQ, Portal|HQ back)
  graduation()    graduation stage at the sail plaza (GradPad)
  secret_roof()   hidden truss up the red brick block -> rooftop with the golden cat (Collect|golden|g1)
  daily_board()   HQ screen for the daily challenge + global best times (DailyBoard)
"""
import math
import random

import genmap as G
import genmap3 as C3
import genmap5 as C5
import bsc_art as A
import hq

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign
rect = C5.rect
rng = random.Random(1010)
HX, HY, HZ = hq.HQ_OFFSET
VX, VY, VZ = 0.0, 600.0, -12600.0      # Virus Tag arena centre (floor level)
PASTELS = hq.PASTELS


def virus_arena():
    R = 70.0
    with G.Group("VirusArena"):
        disc("ArenaFloor", VX, VY - 1, VZ, 2 * R, 2, (168, 132, 214), "SmoothPlastic")   # cytoplasm purple, less glare
        for i in range(12):
            a = i * 2 * math.pi / 12
            A.floor_hex(VX + 40 * math.cos(a), VY + 0.05, VZ + 40 * math.sin(a), 4.0, PASTELS[i % 5])
        disc("ArenaRing", VX, VY + 0.04, VZ, 2 * R - 2, 0.06, (120, 255, 200), "Neon", collide=False, shadow=False, transp=0.6)
        # membrane wall: a ring of tall translucent pink panels (keeps everyone inside)
        n = 36
        for i in range(n):
            a = i * 2 * math.pi / n
            x, z = VX + R * math.cos(a), VZ + R * math.sin(a)
            G.part("Membrane", (1.5, 16, 2 * math.pi * R / n + 0.6), (x, VY + 8, z), (246, 150, 205), "SmoothPlastic", transp=0.35,
                   rot=(0, -math.degrees(a), 0))
        disc("ArenaUnder", VX, VY - 8, VZ, 2 * R * 0.9, 12, (200, 170, 230), "SmoothPlastic", collide=False)
        # cover to dodge around: organelle-shaped blocks, a ramp ring, two trampolines
        ball("CoverNucleus", VX, VY + 6, VZ, 16, (150, 90, 210), "SmoothPlastic")
        for i in range(6):
            a = i * math.pi / 3 + 0.3
            x, z = VX + 30 * math.cos(a), VZ + 30 * math.sin(a)
            G.part("CoverMito", (14, 6, 6), (x, VY + 3, z), (250, 150, 80), "SmoothPlastic", shape="Cylinder",
                   rot=(0, -math.degrees(a) + 90, 0))
        for i in range(8):
            a = i * math.pi / 4
            x, z = VX + 52 * math.cos(a), VZ + 52 * math.sin(a)
            vcyl("CoverPillar", x, VY, VY + 7, z, 5, PASTELS[i % 5], "SmoothPlastic")
        for (dx, dz) in ((-18, 44), (18, -44)):
            box("Bounce|85", (7, 1, 7), (VX + dx, VY - 0.4, VZ + dz), (255, 220, 60), "Neon")
        for i in range(4):
            a = i * math.pi / 2 + math.pi / 4
            G.part("VaccineSpot|%d" % (i + 1), (2, 2, 2), (VX + 44 * math.cos(a), VY + 2.5, VZ + 44 * math.sin(a)), (0, 0, 0),
                   "SmoothPlastic", transp=1, collide=False, shadow=False)
        G.part("VirusSpawn", (8, 1, 8), (VX, VY + 0.5, VZ + 60), (0, 0, 0), "SmoothPlastic", transp=1, collide=False)
        G.part("VirusCenter", (2, 2, 2), (VX, VY + 2, VZ), (0, 0, 0), "SmoothPlastic", transp=1, collide=False)
        G.part("Portal|HQ", (10, 12, 0.6), (VX, VY + 6.2, VZ + 66), (120, 255, 200), "Neon", transp=0.45, collide=False,
               shadow=False)
        sign("VirusBack", "↩ مقر النادي", (VX, VY + 13.5, VZ + 66.4), (10, 2.2, 0.4), "Front", bg=(24, 80, 56))
        sign("VirusTitle", "🦠 لعبة الفيروس | Virus Tag\nالمصاب يلمس الأصحاء… الأصحاء يهربون ويجمعون اللقاح 💉",
             (VX, VY + 20, VZ - 66), (40, 7, 0.6), "Back", bg=(110, 40, 90))
        for q in range(30):
            a = rng.uniform(0, 2 * math.pi)
            r = rng.uniform(110, 200)
            for k in range(3):
                ball("Cloud", VX + r * math.cos(a) + rng.uniform(-10, 10), VY - 20 + rng.uniform(-10, 20),
                     VZ + r * math.sin(a) + rng.uniform(-10, 10), rng.uniform(14, 24), (250, 250, 252), "SmoothPlastic", transp=0.15,
                     collide=False, shadow=False)
    # portal from the HQ: west wall, between the posters
    x, z = HX - 74.0, HZ + 47.0
    G.part("Portal|Virus", (0.6, 12, 11), (x, HY + 6.2, z), (240, 110, 170), "Neon", transp=0.45, collide=False, shadow=False)
    for s_ in (-1, 1):
        box("VirusPost", (2, 15, 2), (x, HY + 7.5, z + s_ * 6.5), (60, 64, 74), "SmoothPlastic")
    box("VirusTop", (2, 2, 15), (x, HY + 15.5, z), (60, 64, 74), "SmoothPlastic")
    sign("VirusPortalSign", "🦠 لعبة الفيروس (مع الربع)", (x + 0.6, HY + 18.4, z), (0.4, 3, 15), "Right", bg=(110, 40, 90))


def graduation():
    """sail plaza: a little stage with a KU backdrop; standing on the gold pad = graduation photo"""
    cx, cz = 92.0, 46.0
    with G.Group("GraduationStage"):
        rect("GradStage", cx - 14, cx + 14, 0, 2, cz - 6, cz + 6, (60, 64, 74), "WoodPlanks")
        for k in range(3):
            rect("GradStep", cx - 4, cx + 4, 0, 0.7 * (k + 1), cz + 6 + (2 - k) * 1.6, cz + 7.6 + (2 - k) * 1.6, (60, 64, 74), "WoodPlanks")
        rect("GradBackdrop", cx - 14, cx + 14, 2, 20, cz - 6.4, cz - 5.8, (24, 80, 56), "Fabric")
        A.logo_board(cx + 8, 15.5, cz - 5.6, R=0.8, nx=0.0, nz=1.0)
        sign("GradText", "🎓 جامعة الكويت • كلية العلوم\nحفل التخرج", (cx - 4, 14, cz - 5.6), (14, 5, 0.3), "Back", bg=(24, 80, 56))
        G.part("GradPad", (6, 0.4, 6), (cx, 2.2, cz), (230, 190, 70), "Neon", transp=0.15, shadow=False)
        sign("GradHint", "قف على الذهبي وخذ صورة تخرجك 📸", (cx - 10, 3.6, cz + 6.2), (8, 1.6, 0.3), "Back", bg=(150, 110, 20))  # beside, not in front of the camera
        for s_ in (-1, 1):
            for k in range(4):
                ball("Balloon", cx + s_ * (12 + (k % 2)), 6 + k * 3, cz - 4 + (k % 2) * 2, 2.4,
                     [(250, 222, 170), (205, 232, 60), (220, 165, 238), (160, 218, 236)][k], "SmoothPlastic", collide=False)
            vcyl("BalloonString", cx + s_ * 12, 2, 14, cz - 4, 0.1, (240, 240, 240), "SmoothPlastic", collide=False)


def secret_roof():
    """the red brick block in the garden (x 120..180, z 49..75, top y 30) gets a hidden truss on its quiet
    north face and a rooftop hideout with the golden cat"""
    with G.Group("SecretRoof"):
        G.part("SecretTruss", (2, 30, 2), (170, 15, 76), (150, 66, 44), "Brick", cls="TrussPart")
        rect("RoofDeck", 124, 176, 30, 30.4, 52, 72, (200, 180, 150), "WoodPlanks")
        for (x, z) in ((132, 56), (168, 68)):
            C3.planter(x, 30.4, z, 6, 3)
        rect("RoofRug", 140, 160, 30.4, 30.5, 56, 68, (110, 70, 150), "Fabric", collide=False)
        disc("BeanBag", 144, 31.4, 64, 4, 2, PASTELS[0], "Fabric")
        disc("BeanBag", 156, 31.4, 60, 4, 2, PASTELS[2], "Fabric")
        A.cat(150, 30.5, 62, 180, "sit", coat=((230, 180, 50), (255, 240, 160)), s=1.4)
        G.part("Collect|golden|g1", (6, 6, 6), (150, 33, 62), (0, 0, 0), "SmoothPlastic", transp=1, collide=False, shadow=False)
        ball("Sparkle|g1", 150, 37.5, 62, 1.4, (255, 215, 80), "Neon", collide=False, shadow=False, light=(1.4, 18, (255, 215, 80)))
        sign("SecretNote", "🤫 لقيت السر! لا تقول لأحد…\n(أو قول للربع عشان يدورونه)", (150, 34, 71.6), (14, 3.4, 0.3), "Back",
             bg=(60, 40, 90))


def daily_board():
    x, z = HX - 16.0, HZ - 44.0
    vcyl("DailyPost", x, HY, HY + 6, z, 0.8, (90, 90, 96), "Metal", collide=False)
    G.part("DailyBoard", (12, 8, 0.4), (x, HY + 10, z), (20, 28, 44), "SmoothPlastic",
           text=dict(face="Back", text="📅 تحدي اليوم", color=(255, 236, 160), bg=(20, 28, 44), bg_t=0.0))


def build():
    virus_arena()
    graduation()
    secret_roof()
    daily_board()
