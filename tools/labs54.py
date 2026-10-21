"""v54 hands-on wet lab: four real workstations in the Research Institute (west wing) + a PPE rack at the entrance.

Everything the player handles is a real 3D object. Naming contract with Labs54.server.luau:
  Bench|<kind>   Model per workstation (gram, gel, pcr, micro)
  Item|<id>      Model the player can pick up and carry (its "Handle" part is the grip; every other part follows it)
  Slot|<id>      invisible part where a carried item can be put down (its CFrame is where the item goes)
  Use|<id>       part you interact with (reagent sources, burner, power supply, electrode posts, cycler, eyepiece)
  Liquid|<id>, Screen|<id>, Lead|<id>, Well|<n>  visual parts the server animates
Bench long axis runs along Z; the player stands on the east side (x ~ -33) facing the bench, shelf on the west edge.
"""
import math

import genmap as G
import genmap5 as C5

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign
LX, LY, LZ = 6000.0, 300.0, 6000.0

EPOXY = (36, 40, 44)
CAB = (232, 234, 236)
STEEL = (196, 200, 206)
GLASS = (210, 232, 245)
TOP = 3.8   # bench top surface (local y)


def at(x, y, z):
    return (LX + x, LY + y, LZ + z)


def r(name, x0, x1, y0, y1, z0, z1, col, mat="SmoothPlastic", **kw):
    C5.rect(name, LX + min(x0, x1), LX + max(x0, x1), LY + min(y0, y1), LY + max(y0, y1), LZ + min(z0, z1),
            LZ + max(z0, z1), col, mat, **kw)


def part(name, size, pos, col, mat="SmoothPlastic", **kw):
    kw.setdefault("collide", False)
    G.part(name, size, at(*pos), col, mat, **kw)


def vc(name, x, y0, y1, z, d, col, mat="SmoothPlastic", **kw):
    kw.setdefault("collide", False)
    vcyl(name, LX + x, LY + y0, LY + y1, LZ + z, d, col, mat, **kw)


def slot(name, x, y, z, sx=1.6, sz=1.6):
    part("Slot|" + name, (sx, 0.2, sz), (x, y, z), (0, 0, 0), transp=1, shadow=False)


# ---------------------------------------------------------------- reusable equipment
def bench(cz, title):
    """lab bench: white cabinets, black epoxy top, back shelf, a small hanging name plate"""
    r("BenchCabinet", -46, -36, 0, 3.4, cz - 11, cz + 11, CAB, "SmoothPlastic")
    for z in range(int(cz - 10), int(cz + 11), 4):
        r("DrawerLine", -36.05, -35.95, 0.6, 3.0, z - 0.05, z + 0.05, (170, 174, 180), collide=False)
        r("DrawerHandle", -35.95, -35.8, 2.6, 2.8, z + 1.2, z + 2.6, STEEL, "Metal", collide=False)
    r("BenchTop", -46.3, -35.7, 3.4, TOP, cz - 11.3, cz + 11.3, EPOXY, "Slate")
    r("ShelfBack", -46.2, -45.6, TOP, 10.5, cz - 11, cz + 11, CAB)
    r("Shelf", -46, -43.6, 7.2, 7.5, cz - 10.8, cz + 10.8, STEEL, "Metal", collide=False)
    r("ShelfLight", -45.5, -44.2, 10.2, 10.4, cz - 10, cz + 10, (255, 250, 236), "Neon", collide=False, shadow=False)
    # a slim plate hanging over the aisle edge: readable, never in front of the work area
    for face, dx in (("Right", 0.15), ("Left", -0.15)):
        part("BenchPlate", (0.3, 1.6, 9), (-35.4 + dx, 13.2, cz), (24, 80, 56), text=dict(face=face, text=title,
             color=(255, 255, 255), bg=(24, 80, 56), bg_t=0.0))
    vc("PlateCable", -35.4, 14, 26, cz - 3.5, 0.12, (60, 60, 66), "Metal")
    vc("PlateCable", -35.4, 14, 26, cz + 3.5, 0.12, (60, 60, 66), "Metal")


def bottle(item, x, z, col, cap=(240, 240, 240), h=1.7, d=0.95):
    with G.Group("Item|" + item, "Model"):
        part("Handle", (h, d, d), (x, TOP + h / 2, z), col, "Glass", shape="Cylinder", rot=(0, 0, 90), transp=0.15)
        part("Cap", (0.5, d * 0.7, d * 0.7), (x, TOP + h + 0.25, z), cap, "SmoothPlastic", shape="Cylinder", rot=(0, 0, 90))
        part("Label", (h * 0.45, d * 1.02, d * 1.02), (x, TOP + h * 0.45, z), (250, 250, 246), "SmoothPlastic",
             shape="Cylinder", rot=(0, 0, 90))


def tube_rack(name_prefix, x, z, tubes):
    """a rack of fixed source tubes: each is a Use|<id> the player draws from with the pipette"""
    r("TubeRack", x - 0.6, x + 0.6, TOP, TOP + 0.9, z - 0.2 - len(tubes) * 0.75, z + 0.2 + len(tubes) * 0.75,
      (230, 236, 240), "SmoothPlastic", collide=False)
    for i, (uid, col) in enumerate(tubes):
        zz = z + (i - (len(tubes) - 1) / 2) * 1.5
        vc("Use|" + uid, x, TOP + 0.4, TOP + 1.9, zz, 0.5, col, "Glass", transp=0.1)
        vc("TubeCap", x, TOP + 1.9, TOP + 2.15, zz, 0.55, (250, 250, 250))


def pipette(x, z):
    with G.Group("Item|pipette", "Model"):
        part("Handle", (2.2, 0.32, 0.32), (x, TOP + 1.3, z), (240, 240, 244), shape="Cylinder", rot=(0, 0, 90))
        part("Plunger", (0.5, 0.2, 0.2), (x, TOP + 2.6, z), (60, 120, 220), shape="Cylinder", rot=(0, 0, 90))
        part("Tip", (0.9, 0.16, 0.16), (x, TOP + 0.15, z), (240, 246, 250), "Glass", shape="Cylinder", rot=(0, 0, 90),
             transp=0.3)
    r("PipetteStand", x - 0.4, x + 0.4, TOP, TOP + 0.3, z - 0.4, z + 0.4, (90, 96, 104), "Metal", collide=False)


def microscope(x, z, prefix):
    """compound microscope facing the player (east): base, arm, stage (Slot), objectives, eyepiece (Use)"""
    r("ScopeBase", x - 1.2, x + 1.0, TOP, TOP + 0.5, z - 1.0, z + 1.0, (34, 38, 44), "Metal")
    r("ScopeArm", x - 1.2, x - 0.5, TOP + 0.5, TOP + 4.4, z - 0.35, z + 0.35, (34, 38, 44), "Metal")
    r("ScopeStage", x - 0.6, x + 1.0, TOP + 1.8, TOP + 2.0, z - 0.9, z + 0.9, (24, 26, 30), "Metal")
    ball("ScopeLamp", LX + x + 0.2, LY + TOP + 1.2, LZ + z, 0.5, (255, 244, 210), "Neon", collide=False, shadow=False)
    for q, c in enumerate(((220, 60, 60), (240, 200, 60), (60, 140, 220))):
        vc("ScopeObjective", x + 0.05 + (q - 1) * 0.35, TOP + 2.3, TOP + 3.2, z, 0.3, c, "Metal")
    r("ScopeHead", x - 0.8, x + 0.4, TOP + 3.3, TOP + 4.4, z - 0.5, z + 0.5, (34, 38, 44), "Metal")
    part("Use|" + prefix + "eyepiece", (1.4, 0.45, 0.45), (x + 0.6, TOP + 4.9, z), (24, 26, 30), "Metal", shape="Cylinder",
         rot=(0, 0, 50))
    for s_ in (-1, 1):
        part("FocusKnob", (0.3, 0.9, 0.9), (x - 0.85, TOP + 1.6, z + s_ * 0.55), (60, 64, 72), "Metal", shape="Cylinder",
             rot=(0, 90, 0))
    slot(prefix + "stage", x + 0.2, TOP + 2.1, z, 1.4, 1.4)


# ---------------------------------------------------------------- the four workstations
def gram_bench(cz):
    with G.Group("Bench|gram", "Model"):
        bench(cz, "🧪 صبغة جرام • Gram stain")
        # Bunsen burner (heat-fix the smear)
        vc("BurnerBase", -39, TOP, TOP + 0.3, cz - 8, 1.4, (60, 64, 72), "Metal")
        vc("Use|burner", -39, TOP + 0.3, TOP + 2.2, cz - 8, 0.45, STEEL, "Metal")
        part("Flame", (0.7, 1.2, 0.7), (-39, TOP + 2.8, cz - 8), (90, 160, 255), "Neon", shape="Ball", transp=0.35,
             shadow=False, light=(1.2, 8, (120, 170, 255)))
        r("GasHose", -42, -39.3, TOP + 0.1, TOP + 0.3, cz - 8.1, cz - 7.9, (240, 170, 60), collide=False)
        # staining rack over a small sink
        r("Sink", -41.2, -36.8, TOP - 0.6, TOP + 0.05, cz - 4.6, cz - 0.4, (170, 178, 186), "Metal", collide=False)
        r("SinkDrain", -39.2, -38.8, TOP - 0.55, TOP - 0.5, cz - 2.7, cz - 2.3, (60, 60, 66), "Metal", collide=False)
        for zz in (cz - 3.4, cz - 1.6):
            r("StainBar", -40.8, -37.2, TOP + 0.6, TOP + 0.75, zz - 0.08, zz + 0.08, (60, 64, 72), "Metal", collide=False)
        slot("tray", -39, TOP + 0.85, cz - 2.5, 3.0, 2.4)
        # microscope for the result
        microscope(-39.5, cz + 6, "")
        # shelf: the smear slide and the five bottles in protocol colours (the order is the player's job)
        with G.Group("Item|slide", "Model"):
            part("Handle", (0.9, 0.12, 2.6), (-42.5, TOP + 0.08, cz + 9.4), GLASS, "Glass", transp=0.4)
            part("Smear", (0.6, 0.04, 1.2), (-42.5, TOP + 0.16, cz + 9.6), (238, 232, 214), "SmoothPlastic")
            part("Frost", (0.9, 0.13, 0.6), (-42.5, TOP + 0.08, cz + 8.4), (250, 250, 250), "SmoothPlastic")
        for i, (item, col) in enumerate((("cv", (120, 50, 190)), ("iodine", (150, 90, 30)), ("alcohol", (200, 230, 250)),
                                         ("safranin", (210, 50, 80)), ("water", (170, 220, 255)))):
            bottle(item, -43.0, cz - 9 + i * 2.0, col, cap=(250, 250, 250) if item != "water" else (60, 160, 230))


def gel_bench(cz):
    with G.Group("Bench|gel", "Model"):
        bench(cz, "🧬 الفصل الكهربائي • Gel electrophoresis")
        # electrophoresis tank (long axis along z: wells at the north end, the far end is south)
        r("TankBody", -40.4, -37.6, TOP, TOP + 1.5, cz - 7.6, cz - 0.4, GLASS, "Glass", transp=0.55, collide=False)
        r("TankBase", -40.6, -37.4, TOP, TOP + 0.15, cz - 7.8, cz - 0.2, (40, 44, 50), "SmoothPlastic", collide=False)
        part("Liquid|buffer", (2.6, 0.02, 7.0), (-39, TOP + 0.2, cz - 4), (120, 190, 255), "Glass", transp=0.55, shadow=False)
        slot("tank", -39, TOP + 0.4, cz - 4, 2.4, 5.0)
        vc("Use|postNear", -39, TOP + 1.5, TOP + 2.1, cz - 7.3, 0.35, (30, 30, 34), "Metal")
        vc("Use|postFar", -39, TOP + 1.5, TOP + 2.1, cz - 0.7, 0.35, (30, 30, 34), "Metal")
        # power supply with its red lead (shown once connected)
        r("Use|power", -41.5, -36.8, TOP, TOP + 1.8, cz + 1.4, cz + 4.4, (60, 64, 72), "SmoothPlastic")
        part("Screen|power", (0.1, 0.8, 1.8), (-36.75, TOP + 1.1, cz + 2.9), (20, 40, 30), "SmoothPlastic", shadow=False,
             text=dict(face="Right", text="0 V", color=(110, 255, 150), bg=(20, 40, 30), bg_t=0.0))
        part("Lead|red", (0.15, 0.15, 0.15), (-39, TOP + 2, cz + 1), (220, 40, 40), "SmoothPlastic", transp=1, shadow=False)
        part("Lead|black", (0.15, 0.15, 0.15), (-39, TOP + 2, cz + 1), (20, 20, 22), "SmoothPlastic", transp=1, shadow=False)
        # UV transilluminator to read the gel
        r("UVBox", -40.8, -37.2, TOP, TOP + 1.0, cz + 6, cz + 10.4, (44, 40, 58), "Metal")
        part("Liquid|uv", (3.2, 0.06, 4.0), (-39, TOP + 1.03, cz + 8.2), (170, 110, 255), "Neon", transp=0.85, shadow=False)
        slot("uv", -39, TOP + 1.2, cz + 8.2, 2.4, 4.0)
        # the gel (in its casting tray), the running buffer, the pipette, ladder + sample tubes
        with G.Group("Item|gel", "Model"):
            part("Handle", (2.2, 0.35, 4.6), (-43.0, TOP + 0.2, cz + 7.5), (225, 236, 240), "Glass", transp=0.35)
            part("TrayRim", (2.5, 0.3, 4.9), (-43.0, TOP + 0.1, cz + 7.5), (200, 210, 220), "SmoothPlastic", transp=0.5)
            for n in (1, 2):
                part("Well|%d" % n, (0.5, 0.1, 0.25), (-43.5 + (n - 1) * 1.0, TOP + 0.38, cz + 5.6), (190, 200, 210),
                     "SmoothPlastic")
        bottle("buffer", -43.0, cz - 9, (150, 210, 255), cap=(40, 90, 200), h=2.2, d=1.2)
        pipette(-42.8, cz + 1.0)
        tube_rack("", -43.0, cz - 4.6, [("ladder", (60, 90, 220)), ("sample", (220, 80, 150))])


def pcr_bench(cz):
    with G.Group("Bench|pcr", "Model"):
        bench(cz, "🧬 تفاعل البوليميراز • PCR")
        # the PCR tube sits in a small rack at the front; it can be carried to the cycler
        r("PCRRack", -39.8, -38.2, TOP, TOP + 0.5, cz - 7.4, cz - 5.6, (90, 200, 240), "SmoothPlastic", collide=False)
        slot("rack", -39, TOP + 0.5, cz - 6.5, 1.2, 1.2)
        with G.Group("Item|tube", "Model"):
            part("Handle", (1.0, 0.36, 0.36), (-39, TOP + 1.0, cz - 6.5), (240, 246, 250), "Glass", shape="Cylinder",
                 rot=(0, 0, 90), transp=0.3)
            part("Liquid|tube", (0.06, 0.3, 0.3), (-39, TOP + 0.55, cz - 6.5), (250, 220, 120), "SmoothPlastic",
                 shape="Cylinder", rot=(0, 0, 90), transp=1)
        # thermocycler: lid, front button (Use|cycler) and its screen
        r("CyclerBody", -41.4, -36.6, TOP, TOP + 2.0, cz - 1, cz + 4.6, (226, 230, 236), "SmoothPlastic")
        r("CyclerLid", -41.4, -36.6, TOP + 2.0, TOP + 2.5, cz - 1, cz + 4.6, (190, 196, 204), "SmoothPlastic")
        slot("cycler", -39, TOP + 2.6, cz + 1.8, 1.4, 1.4)
        part("Screen|cycler", (0.1, 1.2, 2.6), (-36.55, TOP + 1.1, cz + 2.4), (16, 24, 34), "SmoothPlastic", shadow=False,
             text=dict(face="Right", text="READY", color=(110, 220, 255), bg=(16, 24, 34), bg_t=0.0))
        part("Use|cycler", (0.3, 0.6, 0.6), (-36.5, TOP + 1.1, cz + 0.4), (60, 200, 120), "Neon", shape="Cylinder",
             rot=(0, 0, 0), shadow=False)
        # ice bucket with Taq polymerase, and the reagent rack (template, primers, nucleotides, buffer)
        vc("IceBucket", -43, TOP, TOP + 1.3, cz + 8.4, 2.4, (90, 170, 230), "SmoothPlastic")
        vc("Ice", -43, TOP + 1.3, TOP + 1.4, cz + 8.4, 2.2, (230, 246, 255), "Ice")
        vc("Use|taq", -43, TOP + 1.2, TOP + 2.5, cz + 8.4, 0.5, (250, 250, 250), "Glass", transp=0.1)
        tube_rack("", -43.0, cz - 3.0, [("template", (240, 140, 90)), ("primers", (120, 200, 120)),
                                        ("dntp", (240, 210, 80)), ("pcrbuffer", (160, 200, 250))])
        pipette(-42.8, cz + 4.4)


def micro_bench(cz, samples):
    with G.Group("Bench|micro", "Model"):
        bench(cz, "🔬 المجهر الضوئي • Light microscopy")
        microscope(-39.5, cz - 2, "m")
        # slide box: one prepared slide per specimen
        r("SlideBox", -44, -41.6, TOP, TOP + 0.6, cz + 3, cz + 3.4 + len(samples) * 1.3, (120, 84, 52), "Wood",
          collide=False)
        for i, (sid, col) in enumerate(samples):
            z = cz + 4 + i * 1.3
            with G.Group("Item|slide_" + sid, "Model"):
                part("Handle", (2.2, 0.12, 0.9), (-42.8, TOP + 0.7, z), GLASS, "Glass", transp=0.4)
                part("Specimen", (0.8, 0.05, 0.6), (-42.6, TOP + 0.78, z), col, "SmoothPlastic")
        # the old quick "cell identification" quiz lives on as a slide-atlas screen at the end of this bench
        r("LabStation|microscope", -40.5, -37.5, TOP, TOP + 2.2, cz - 10.4, cz - 8.2, (40, 46, 52), "SmoothPlastic")
        part("AtlasScreen", (0.1, 1.6, 2.0), (-37.45, TOP + 1.2, cz - 9.3), (70, 200, 240), "Neon", transp=0.2, shadow=False)


def ppe_rack(x, z):
    """lab coats and goggles by the entrance: the first stop for every experiment"""
    with G.Group("PPERack", "Model"):
        r("RackFoot", x - 3, x + 3, 0, 0.3, z - 0.8, z + 0.8, (90, 96, 104), "Metal")
        vc("RackPole", x - 2.7, 0.3, 7, z, 0.3, STEEL, "Metal")
        vc("RackPole", x + 2.7, 0.3, 7, z, 0.3, STEEL, "Metal")
        r("RackBar", x - 2.8, x + 2.8, 6.8, 7.1, z - 0.1, z + 0.1, STEEL, "Metal")
        for q in range(3):
            xx = x - 1.8 + q * 1.8
            r("Coat", xx - 0.7, xx + 0.7, 2.6, 6.6, z - 0.35, z + 0.35, (248, 248, 246), "Fabric", collide=False)
            r("CoatCollar", xx - 0.5, xx + 0.5, 6.3, 6.7, z - 0.38, z + 0.38, (220, 224, 228), "Fabric", collide=False)
        r("GogglesShelf", x - 2.6, x + 2.6, 1.6, 1.8, z - 0.6, z + 0.6, STEEL, "Metal", collide=False)
        for q in range(3):
            part("Goggles", (1.0, 0.35, 0.4), (x - 1.6 + q * 1.6, 2.0, z), (190, 230, 250), "Glass", transp=0.3)
        part("Use|ppe", (6, 7, 2), (x, 3.5, z), (0, 0, 0), transp=1, shadow=False)


def build():
    """called from island11.research_lab() in place of the old menu stations"""
    gram_bench(-36)
    gel_bench(-12)
    pcr_bench(12)
    micro_bench(36, [("blood", (200, 90, 110)), ("elodea", (90, 170, 80)), ("cheek", (200, 170, 220)),
                     ("staph", (140, 70, 190))])
    ppe_rack(-18, 44)
