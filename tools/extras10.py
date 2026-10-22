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
    """v63 (owner audit: "plain pink walls and cylinders, no identity"): the arena is a patch of tissue in the
    bloodstream fighting an infection. A giant virus in the middle, red blood cells standing on edge as cover, white
    blood cells round the outside, antibodies floating above, a membrane wall (low lipid wall + an invisible
    barrier). Names the server uses are unchanged: VirusCenter, VirusSpawn, VaccineSpot|1..4, Portal|HQ, Bounce|85."""
    R = 70.0
    TISSUE, TISSUE2 = (238, 166, 182), (224, 146, 166)
    with G.Group("VirusArena"):
        disc("ArenaFloor", VX, VY - 1, VZ, 2 * R, 2, (186, 100, 124), "SmoothPlastic")
        # the floor is tissue: rings of cell tiles, each with a darker nucleus dot
        for ring, (rr, n) in enumerate(((14, 8), (26, 14), (38, 20), (50, 26), (62, 32))):
            for i in range(n):
                a = (i + ring * 0.5) * 2 * math.pi / n
                x, z = VX + rr * math.cos(a), VZ + rr * math.sin(a)
                A.floor_hex(x, VY + 0.05, z, 4.6, TISSUE if (i + ring) % 2 else TISSUE2, name="TissueCell")
                disc("TissueNucleus", x, VY + 0.1, z, 1.6, 0.06, (160, 80, 120), "SmoothPlastic", collide=False, shadow=False)
        for i in range(72):   # glowing edge ring (the old full-floor neon disc washed the tissue out to yellow)
            a = i * 2 * math.pi / 72
            box("ArenaRing", (1, 0.1, 2 * math.pi * (R - 3) / 72 + 0.2), (VX + (R - 3) * math.cos(a), VY + 0.1,
                VZ + (R - 3) * math.sin(a)), (255, 200, 120), "Neon", rot=(0, -math.degrees(a), 0), collide=False, shadow=False)
        # membrane wall: a solid low wall, a double row of lipid heads on it, and an invisible barrier above
        n = 36
        for i in range(n):
            a = i * 2 * math.pi / n
            x, z = VX + R * math.cos(a), VZ + R * math.sin(a)
            G.part("MembraneWall", (2, 4, 2 * math.pi * R / n + 0.6), (x, VY + 2, z), (150, 70, 100), "SmoothPlastic",
                   rot=(0, -math.degrees(a), 0))
            G.part("Membrane", (1.5, 18, 2 * math.pi * R / n + 0.6), (x, VY + 9, z), (246, 150, 205), "SmoothPlastic",
                   transp=1, rot=(0, -math.degrees(a), 0), shadow=False)
        for i in range(72):
            a = i * 2 * math.pi / 72
            for rr, y in ((R - 0.6, VY + 4.6), (R + 0.6, VY + 4.6)):
                ball("LipidHead", VX + rr * math.cos(a), y, VZ + rr * math.sin(a), 2.2, (255, 190, 215), "SmoothPlastic",
                     collide=False, shadow=False)
        disc("ArenaUnder", VX, VY - 8, VZ, 2 * R * 0.9, 12, (160, 80, 110), "SmoothPlastic", collide=False)
        # the giant virus: capsid, spike proteins, a glowing genome core (the landmark from every corner)
        ball("VirusCapsid", VX, VY + 9, VZ, 16, (110, 190, 120), "SmoothPlastic")
        ball("VirusGenome", VX, VY + 9, VZ, 9, (230, 255, 120), "Neon", transp=0.3, collide=False, shadow=False,
             light=(1.4, 30, (190, 255, 140)))
        for i in range(14):
            t = i * 2.4   # golden-angle spread over the sphere
            yy = 1 - 2 * (i + 0.5) / 14
            r2 = math.sqrt(1 - yy * yy)
            nx, ny, nz = math.cos(t) * r2, yy, math.sin(t) * r2
            G.part("SpikeStalk", (3.6, 1, 1), (VX + nx * 9.6, VY + 9 + ny * 9.6, VZ + nz * 9.6), (90, 160, 100),
                   "SmoothPlastic", shape="Cylinder", rot=(0, math.degrees(math.asin(max(-1, min(1, -nz)))),
                                                          math.degrees(math.atan2(ny, nx))), collide=False)
            ball("SpikeTip", VX + nx * 11.6, VY + 9 + ny * 11.6, VZ + nz * 11.6, 2.4, (240, 120, 90), "SmoothPlastic",
                 collide=False, shadow=False)
        vcyl("VirusPedestal", VX, VY, VY + 2, VZ, 10, (150, 70, 100), "SmoothPlastic")
        # red blood cells standing on edge: cover to dodge round (a disc with a dimple on both faces)
        for i in range(6):
            a = i * math.pi / 3 + 0.3
            x, z = VX + 28 * math.cos(a), VZ + 28 * math.sin(a)
            yaw = -math.degrees(a)
            G.part("RedBloodCell", (3.2, 13, 13), (x, VY + 6.5, z), (205, 40, 55), "SmoothPlastic", shape="Cylinder",
                   rot=(0, yaw, 0))
            G.part("RBCDimple", (3.4, 6, 6), (x, VY + 6.5, z), (160, 25, 40), "SmoothPlastic", shape="Cylinder",
                   rot=(0, yaw, 0), collide=False)
        # white blood cells round the outside (lobed nucleus), clear of the vaccine spots (45 deg) and the spawn
        for i in range(8):
            a = i * math.pi / 4 + math.pi / 8
            x, z = VX + 58 * math.cos(a), VZ + 58 * math.sin(a)   # 58: clear of the bounce pads
            ball("WhiteBloodCell", x, VY + 4.5, z, 9, (240, 240, 246), "SmoothPlastic")
            for k in range(3):
                ball("WBCNucleus", x + math.cos(a + k * 2.1) * 1.6, VY + 5 + (k - 1) * 1.2, z + math.sin(a + k * 2.1) * 1.6,
                     3.6, (140, 100, 200), "SmoothPlastic", collide=False, shadow=False)
        # antibodies: glowing Y shapes floating over the arena (decor, out of reach)
        for i in range(10):
            a = i * 2 * math.pi / 10
            x, z, y = VX + 40 * math.cos(a), VZ + 40 * math.sin(a), VY + 22 + (i % 3) * 3
            box("AntibodyStem", (1, 5, 1), (x, y, z), (255, 220, 90), "Neon", collide=False, shadow=False)
            for s_ in (-1, 1):
                box("AntibodyArm", (1, 4.4, 1), (x + s_ * 1.6 * math.cos(a + math.pi / 2), y + 3.8, z + s_ * 1.6 *
                    math.sin(a + math.pi / 2)), (255, 220, 90), "Neon", rot=(s_ * 35, -math.degrees(a), 0), collide=False,
                    shadow=False)
        for (dx, dz) in ((-18, 44), (18, -44)):
            box("Bounce|85", (7, 1, 7), (VX + dx, VY - 0.4, VZ + dz), (255, 220, 60), "Neon")
        for i in range(4):
            a = i * math.pi / 2 + math.pi / 4
            G.part("VaccineSpot|%d" % (i + 1), (2, 2, 2), (VX + 44 * math.cos(a), VY + 2.5, VZ + 44 * math.sin(a)), (0, 0, 0),
                   "SmoothPlastic", transp=1, collide=False, shadow=False)
            disc("VaccinePad", VX + 44 * math.cos(a), VY + 0.12, VZ + 44 * math.sin(a), 7, 0.1, (90, 220, 255), "Neon",
                 transp=0.3, collide=False, shadow=False)
        # v63: z 48 (was 60): the follow camera sat behind the HQ portal at z 66 and looked through its glow
        G.part("VirusSpawn", (8, 1, 8), (VX, VY + 0.5, VZ + 48), (0, 0, 0), "SmoothPlastic", transp=1, collide=False)
        G.part("VirusCenter", (2, 2, 2), (VX, VY + 2, VZ), (0, 0, 0), "SmoothPlastic", transp=1, collide=False)
        G.part("Portal|HQ", (10, 12, 0.6), (VX, VY + 6.2, VZ + 66), (120, 255, 200), "Neon", transp=0.45, collide=False,
               shadow=False)
        sign("VirusBack", "↩ مقر النادي", (VX, VY + 13.5, VZ + 66.4), (10, 2.2, 0.4), "Front", bg=(24, 80, 56))
        sign("VirusTitle", "🦠 لعبة الفيروس | Virus Tag", (VX, VY + 22, VZ - 66), (30, 5, 0.6), "Back", bg=(120, 40, 70))
        for q in range(30):
            a = rng.uniform(0, 2 * math.pi)
            r = rng.uniform(110, 200)
            for k in range(3):
                ball("Cloud", VX + r * math.cos(a) + rng.uniform(-10, 10), VY - 20 + rng.uniform(-10, 20),
                     VZ + r * math.sin(a) + rng.uniform(-10, 10), rng.uniform(14, 24), (250, 250, 252), "SmoothPlastic", transp=0.15,
                     collide=False, shadow=False)
    # v52: the HQ's west-wall Virus gate (it clipped a plant pot) is replaced by the Virus Tag portal in the
    # World Gateway Hall (tools/hq.py HALL_PORTALS), so every world has one door in one place.


def graduation():
    """sail plaza: a little stage with a KU backdrop; standing on the gold pad = graduation photo.
    v59 (owner): it sat right against the garden walkway; now it stands across the lawn, just before the eastern
    palms, facing the walkway (front = west), with rows of guest chairs in front so it reads as a ceremony."""
    cx, cz = 136.0, 16.0
    GREEN_ = (24, 80, 56)
    with G.Group("GraduationStage"):
        rect("GradStage", cx - 6, cx + 6, 0, 2, cz - 14, cz + 14, (60, 64, 74), "WoodPlanks")
        for k in range(3):
            x1 = cx - 6 - (2 - k) * 1.6
            rect("GradStep", x1 - 1.6, x1, 0, 0.7 * (k + 1), cz - 4, cz + 4, (60, 64, 74), "WoodPlanks")
        rect("GradBackdrop", cx + 5.8, cx + 6.4, 2, 20, cz - 14, cz + 14, GREEN_, "Fabric")
        A.logo_board(cx + 5.6, 15.5, cz - 8, R=0.8, nx=-1.0, nz=0.0)
        sign("GradText", "جامعة الكويت • كلية العلوم" + chr(10) + "حفل التخرج", (cx + 5.6, 14, cz + 4), (0.3, 5, 14), "Left",
             bg=GREEN_)
        G.part("GradPad", (6, 0.4, 6), (cx, 2.2, cz), (230, 190, 70), "Neon", transp=0.15, shadow=False)
        sign("GradHint", "قف على الذهبي وخذ صورة تخرجك", (cx - 6.2, 3.6, cz + 10), (0.3, 1.6, 8), "Left", bg=(150, 110, 20))
        for s_ in (-1, 1):
            for k in range(4):
                ball("Balloon", cx + 4 - (k % 2) * 2, 6 + k * 3, cz + s_ * (12 + (k % 2)), 2.4,
                     [(250, 222, 170), (205, 232, 60), (220, 165, 238), (160, 218, 236)][k], "SmoothPlastic", collide=False)
            vcyl("BalloonString", cx + 4, 2, 14, cz + s_ * 12, 0.1, (240, 240, 240), "SmoothPlastic", collide=False)
        # guests: two blocks of white chairs facing the stage, with a centre aisle to the steps
        for row in range(3):
            x = cx - 16 - row * 4
            for side in (-1, 1):
                for k in range(3):
                    z = cz + side * (5 + k * 3.2)
                    rect("GuestSeat", x - 1, x + 1, 1.4, 1.8, z - 1, z + 1, (245, 245, 242), "SmoothPlastic")
                    rect("GuestBack", x - 1.2, x - 1, 1.8, 4.2, z - 1, z + 1, (245, 245, 242), "SmoothPlastic", collide=False)
                    for dz in (-0.8, 0.8):
                        rect("GuestLeg", x - 0.15, x + 0.15, 0, 1.4, z + dz - 0.1, z + dz + 0.1, (180, 182, 186), "Metal",
                             collide=False)


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
