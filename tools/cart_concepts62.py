"""v62 Specialties Train: "theory sculptures" beside the rails (owner: fill the ride with beautiful things about each
specialty, theoretical things). Four giant, wordless models per valley, each one a core idea of that specialty
(growth curve, lock and key, energy pyramid, central dogma...). The map carries no text: the ride shows one short
caption on screen as you pass (cart_tour53.label -> CAPTIONS).

Every builder gets a frame: (x, z) the spot, Y the valley floor, u = unit vector along the track, n = unit vector
from the spot towards the track (the side the riders see). Builders use only their own RNG (never the shared one).
"""
import math
import random

import genmap as G

box, vcyl, disc, ball = G.box, G.vcyl, G.disc, G.ball
rnd = random.Random(6262)

EXHIBIT_ACCENTS = {
    "micro": (52, 143, 126), "biochem": (139, 104, 181),
    "animal": (179, 116, 66), "plant": (80, 137, 75),
    "molecular": (75, 166, 190), "forensic": (205, 160, 66),
    "agri": (129, 151, 70), "biotech": (48, 158, 171),
}


class F:
    """a local frame: a = along the track, b = towards the track, h = height above the floor"""

    def __init__(self, x, z, Y, u, n, specialty="micro"):
        self.x, self.z, self.Y = x, z, Y
        self.ux, self.uz = u
        self.nx, self.nz = n
        self.accent = EXHIBIT_ACCENTS[specialty]
        self.yaw_u = math.degrees(math.atan2(-self.uz, self.ux))   # local X along the track
        self.yaw_n = math.degrees(math.atan2(-self.nz, self.nx))   # local X towards the track
        wy = math.radians(self.yaw_n)
        self.wx, self.wz = math.sin(wy), math.cos(wy)              # local Z of the yaw_n frame (lies along +-u)

    def p(self, a, b, h):
        return (self.x + self.ux * a + self.nx * b, self.Y + h, self.z + self.uz * a + self.nz * b)

    def ring(self, name, a, b, h, R, n, size, col, mat="SmoothPlastic", **kw):
        """a ring standing upright, facing the track: n blocks (size = depth, radial, tangent)"""
        cx, cy, cz = self.p(a, b, h)
        for q in range(n):
            t = q * 360.0 / n
            tr = math.radians(t)
            pos = (cx + self.wx * R * math.sin(tr), cy + R * math.cos(tr), cz + self.wz * R * math.sin(tr))
            box(name, size, pos, col, mat, rot=(t, self.yaw_n, 0), collide=False, **kw)

    def vdisc(self, name, a, b, h, d, thick, col, mat="SmoothPlastic", **kw):
        """a disc standing upright, its face towards the track"""
        G.part(name, (thick, d, d), self.p(a, b, h), col, mat, shape="Cylinder", rot=(0, self.yaw_n, 0), collide=False,
               **kw)

    def slab(self, name, a, b, h, sa, sh, sb, col, mat="SmoothPlastic", **kw):
        """a box aligned with the track: sa along, sh high, sb deep"""
        box(name, (sa, sh, sb), self.p(a, b, h), col, mat, rot=(0, self.yaw_u, 0), collide=False, **kw)

    def ball(self, name, a, b, h, d, col, mat="SmoothPlastic", **kw):
        ball(name, *self.p(a, b, h), d, col, mat, collide=False, **kw)

    def post(self, name, a, b, h0, h1, d, col, mat="SmoothPlastic", **kw):
        x, _, z = self.p(a, b, 0)
        vcyl(name, x, self.Y + h0, self.Y + h1, z, d, col, mat, collide=False, **kw)

    def floor_disc(self, name, a, b, d, col, mat="SmoothPlastic", h=0.15, **kw):
        x, _, z = self.p(a, b, 0)
        disc(name, x, self.Y + h, z, d, 0.25, col, mat, collide=False, shadow=False, **kw)


def plinth(f, w, d, col=(236, 236, 240)):
    """Layered exhibition footing; all detail stays within the reserved footprint.

    Keep the top at h=2 so existing scientific models remain grounded.
    Broad matte surfaces and a coloured fascia read from the moving train.
    """
    f.slab("ConceptPlinth", 0, 0, 0.5, w, 1, d, (46, 59, 65), "Slate")
    f.slab("ConceptDeck", 0, 0, 1.5, w - 1.2, 1, d - 1.2, col, "Concrete")
    f.slab("ConceptFascia", 0, d / 2 - 0.15, 1.25, w - 2, 0.7, 0.3, f.accent)
    # Slim recessed joints break up the large slab without individual floor tiles.
    for a in (-w / 4, 0, w / 4):
        f.slab("ConceptDeckJoint", a, 0, 2.015, 0.12, 0.03, d - 1.3, (140, 151, 153), shadow=False)
    for side in (-1, 1):
        f.slab("ConceptCornerTrim", side * (w / 2 - 1.2), 0, 2.04, 0.7, 0.08, d - 2, f.accent, shadow=False)
        f.slab("ConceptFootlight", side * (w / 2 - 4), d / 2, 0.6, 3, 0.25, 0.15,
               (180, 211, 202), "Neon", shadow=False)


# ============================================================== microbiology
def growth_curve(f):
    plinth(f, 96, 26)
    hs = [6, 6, 8, 14, 24, 38, 46, 47, 47, 42, 32, 22]
    cols = [(150, 200, 255)] * 3 + [(120, 230, 140)] * 4 + [(250, 220, 90)] * 2 + [(240, 110, 110)] * 3
    for i, h in enumerate(hs):
        f.slab("GrowthBar", -44 + i * 8, 0, 2 + h / 2, 6, h, 6, cols[i])
        f.ball("GrowthDot", -44 + i * 8, 2, 2 + h + 2, 2.4, (244, 243, 228), shadow=False)


def binary_fission(f):
    plinth(f, 80, 24)
    for gen in range(4):
        n = 2 ** gen
        for k in range(n):
            h = 6 + k * 5.2
            f.slab("FissionRod", -30 + gen * 20, 0, h, 9, 3.6, 3.6, (120, 200, 120) if gen < 3 else (100, 190, 110))
            f.ball("FissionCap", -30 + gen * 20 - 4.5, 0, h, 3.6, (120, 200, 120))
            f.ball("FissionCap", -30 + gen * 20 + 4.5, 0, h, 3.6, (120, 200, 120))
        if gen < 3:
            f.slab("FissionArrow", -20 + gen * 20, 0, 6, 6, 1.2, 1.2, (255, 255, 255), "Neon", shadow=False)


def gram_walls(f):
    plinth(f, 90, 30)
    for side, wall, inner, outer in ((-1, (120, 50, 170), 9.0, None), (1, (235, 120, 170), 3.0, (250, 200, 120))):
        a = side * 24
        f.vdisc("CellInside", a, 0, 26, 30, 1.2, (250, 236, 220))
        f.ring("Peptidoglycan", a, 0.4, 26, 15 + inner / 2, 28, (2.4, inner, 4.6), wall)
        f.ring("InnerMembrane", a, 0.8, 26, 15, 28, (2.6, 1.2, 4), (240, 220, 120))
        if outer:
            f.ring("OuterMembrane", a, 1.2, 26, 15 + inner + 2.2, 32, (2.6, 1.4, 5), outer)


def size_scale(f):
    plinth(f, 80, 24)
    f.slab("BigBacterium", -10, 0, 14, 44, 18, 18, (150, 210, 130))
    f.ball("BigBacteriumCap", -32, 0, 14, 18, (150, 210, 130))
    f.ball("BigBacteriumCap", 12, 0, 14, 18, (150, 210, 130))
    for k in range(4):
        x = 24 + k * 4
        f.post("TinyPhageTail", x, 2, 2, 5, 0.6, (200, 205, 215), "Metal")
        f.ball("TinyPhageHead", x, 2, 6, 2, (210, 130, 235), "Neon", shadow=False)


# ============================================================== biochemistry
def lock_and_key(f):
    plinth(f, 80, 26)
    blue = (90, 130, 230)
    f.slab("EnzymeLeft", -14, 0, 18, 20, 30, 16, blue)
    f.slab("EnzymeRight", 14, 0, 18, 20, 30, 16, blue)
    f.slab("EnzymeBase", 0, 0, 7, 48, 8, 16, blue)
    f.slab("Substrate", 0, 0, 22, 8, 14, 12, (255, 210, 80))
    f.ball("SubstrateGlow", 0, 7, 28, 3, (255, 240, 160), "Neon", shadow=False)
    f.slab("ProductA", 32, 0, 6, 7, 7, 10, (255, 170, 80))
    f.slab("ProductB", 32, 0, 14, 7, 7, 10, (255, 120, 90))


def activation_energy(f):
    plinth(f, 100, 30, (40, 44, 60))
    for i in range(23):
        a = -44 + i * 4
        x = (i - 11) / 11.0
        tall = 10 + 40 * math.exp(-x * x * 6)
        low = 10 + 16 * math.exp(-x * x * 6)
        f.ball("EnergyNoEnzyme", a, -4, 2 + tall, 3.4, (240, 90, 90), "Neon", shadow=False)
        f.ball("EnergyEnzyme", a, 4, 2 + low, 3.4, (90, 230, 140), "Neon", shadow=False)
    f.slab("EnergyStart", -44, 0, 6, 6, 8, 20, (220, 220, 230))
    f.slab("EnergyEnd", 44, 0, 4, 6, 4, 20, (220, 220, 230))


def atp_model(f):
    plinth(f, 76, 24)
    f.slab("Adenine", -26, 0, 16, 12, 12, 6, (90, 140, 240))
    f.slab("Adenine2", -18, 0, 20, 8, 8, 6, (90, 140, 240))
    f.vdisc("Ribose", -6, 0, 14, 12, 4, (250, 160, 80))
    for k in range(3):
        f.ball("Phosphate", 8 + k * 10, 0, 14, 8, (250, 220, 70))
        f.slab("Bond", 3 + k * 10, 0, 14, 4, 1.4, 1.4, (255, 255, 255) if k < 2 else (255, 120, 60),
               "SmoothPlastic" if k < 2 else "Neon", shadow=False)
    f.ball("EnergySpark", 34, 2, 22, 4, (255, 140, 60), "Neon", shadow=False, light=(1.5, 24, (255, 160, 80)))


def protein_fold(f):
    plinth(f, 96, 26)
    cols = [(240, 110, 110), (250, 180, 80), (240, 230, 100), (110, 210, 120), (100, 170, 240), (180, 120, 230)]
    for i in range(10):
        f.ball("PrimaryBead", -44 + i * 4.2, 0, 6, 4, cols[i % 6])
    for i in range(16):
        t = i * 0.8
        f.ball("HelixBead", 4 + math.cos(t) * 4, math.sin(t) * 4, 6 + i * 2.2, 4, cols[i % 6])
    for i in range(22):
        r = 9 * (0.6 + 0.4 * rnd.random())
        t, s = rnd.uniform(0, 6.28), rnd.uniform(-1, 1)
        f.ball("FoldedBead", 34 + r * math.cos(t) * math.sqrt(1 - s * s), r * math.sin(t) * math.sqrt(1 - s * s),
               16 + r * s, 5, cols[i % 6])


# ============================================================== animal biology
def energy_pyramid(f):
    tiers = [(64, (90, 180, 80)), (48, (230, 200, 80)), (32, (230, 140, 70)), (16, (210, 80, 80))]
    for i, (w, col) in enumerate(tiers):
        f.slab("PyramidTier", 0, 0, 5 + i * 10, w, 10, w * 0.5, col)
        f.slab("PyramidEdge", 0, w * 0.25, 9.6 + i * 10, w, 0.6, 0.6, (255, 255, 255), "Neon", shadow=False)


def heart(f):
    plinth(f, 60, 30)
    red, blue = (210, 50, 60), (70, 100, 210)
    f.ball("RightAtrium", -9, 0, 30, 14, blue)
    f.ball("LeftAtrium", 9, 0, 30, 14, red)
    f.ball("RightVentricle", -7, 0, 15, 20, blue)
    f.ball("LeftVentricle", 7, 0, 14, 22, red)
    f.post("Aorta", 4, 0, 32, 46, 6, red)
    f.slab("AortaArch", 10, 0, 46, 16, 6, 6, red)
    f.post("PulmonaryArtery", -6, -3, 34, 44, 5, blue)
    f.slab("Septum", 0, 3, 18, 1.2, 26, 12, (250, 230, 230))


def frog_cycle(f):
    plinth(f, 90, 26, (120, 170, 210))
    for k in range(9):   # eggs
        f.ball("FrogEgg", -36 + (k % 3) * 3.4, (k // 3) * 3 - 3, 4, 3, (230, 240, 230), "Glass", transp=0.2)
    f.ball("TadpoleBody", -12, 0, 5, 6, (60, 70, 60))
    f.slab("TadpoleTail", -6, 0, 5, 8, 2, 0.6, (60, 70, 60))
    f.ball("FrogletBody", 12, 0, 6, 8, (90, 150, 70))
    f.slab("FrogletTail", 18, 0, 5, 5, 1.4, 0.6, (90, 150, 70))
    f.ball("FrogBody", 36, 0, 8, 12, (80, 160, 70))
    for s in (-1, 1):
        f.ball("FrogEye", 38, s * 3, 13, 3, (250, 250, 220))
        f.slab("FrogLeg", 32, s * 5, 4, 8, 2, 2.4, (70, 140, 60))
    for k in range(3):
        f.slab("CycleArrow", -24 + k * 24, 6, 4, 6, 1, 1, (255, 255, 255), "Neon", shadow=False)


def desert_food_chain(f):
    plinth(f, 100, 26, (220, 196, 150))
    for k in range(5):   # grass tufts
        f.slab("GrassBlade", -42 + k * 2, 0, 6, 1, 8, 1, (110, 170, 70))
    f.ball("Locust", -18, 0, 6, 5, (130, 170, 60))
    f.slab("LocustWing", -18, 0, 8, 7, 0.4, 3, (180, 200, 120))
    f.slab("DhubBody", 6, 0, 6, 14, 5, 6, (170, 140, 90))
    f.slab("DhubTail", 17, 0, 5, 10, 3, 3, (160, 130, 80))
    f.ball("FalconBody", 36, 0, 14, 9, (150, 110, 70))
    f.slab("FalconWings", 36, 0, 16, 4, 1, 26, (130, 95, 60))
    f.post("FalconPerch", 36, 0, 2, 9, 1.2, (110, 80, 50), "Wood")
    for k in range(3):
        f.slab("ChainArrow", -30 + k * 24, 5, 10, 6, 1, 1, (255, 255, 255), "Neon", shadow=False)


# ============================================================== plant biology
def photosynthesis(f):
    plinth(f, 100, 30, (110, 170, 90))
    f.ball("Sun", -40, 0, 46, 14, (255, 220, 90), "Neon", shadow=False, light=(2, 50, (255, 230, 150)))
    for k in range(4):
        f.slab("SunRay", -28 + k * 2, 0, 40 - k * 5, 14, 1, 1, (255, 230, 120), "Neon", shadow=False)
    f.slab("GiantLeaf", 0, 0, 20, 34, 2, 22, (70, 160, 60), "Grass")
    f.post("LeafStem", 0, 0, 2, 20, 2.4, (80, 140, 60))
    for k in range(3):   # CO2 in
        f.ball("CO2_C", -22, -8 + k * 8, 10, 3.6, (40, 40, 46))
        for s in (-1, 1):
            f.ball("CO2_O", -22 + s * 3.2, -8 + k * 8, 10, 3, (230, 60, 60))
    for k in range(3):   # O2 out
        for s in (-1, 1):
            f.ball("O2", 26 + s * 1.6, -6 + k * 7, 30 + k * 3, 3, (230, 60, 60))
    for k in range(6):   # glucose ring
        t = k * math.pi / 3
        f.ball("Glucose", 36 + math.cos(t) * 5, 0, 12 + math.sin(t) * 5, 3.4, (250, 250, 250))


def leaf_section(f):
    plinth(f, 84, 30)
    L = 70
    f.slab("Cuticle", 0, 0, 40, L, 1, 22, (230, 245, 220), "Glass", transp=0.3)
    f.slab("UpperEpidermis", 0, 0, 37.5, L, 4, 22, (200, 230, 180))
    for k in range(14):
        f.slab("Palisade", -32.5 + k * 5, 0, 29, 4, 12, 20, (60, 160, 60))
        f.ball("Chloroplast", -32.5 + k * 5, 10.5, 30, 2, (30, 120, 40))
    for k in range(18):
        f.ball("Spongy", -32 + (k % 9) * 8, -5 + (k // 9) * 10, 16 + (k % 2) * 4, 7, (110, 190, 100))
    f.slab("LowerEpidermis", 0, 0, 8, L, 4, 22, (200, 230, 180))
    for s in (-1, 1):
        f.ball("GuardCell", 6 + s * 2.6, 11, 8, 4, (60, 160, 60))


def xylem_phloem(f):
    plinth(f, 50, 26)
    for a, col, up in ((-10, (90, 170, 255), True), (10, (255, 170, 80), False)):
        f.post("VascularTube", a, 0, 2, 58, 12, (220, 240, 245), "Glass", transp=0.55)
        for k in range(8):
            f.ball("Flow", a, 0, 6 + k * 7, 4, col, "Neon", shadow=False)
        f.ball("FlowArrow", a, 0, 62 if up else 0.5, 6, col, "Neon", shadow=False)


def germination(f):
    plinth(f, 90, 24, (130, 96, 64))
    brown, green = (140, 100, 60), (90, 180, 70)
    f.ball("Seed", -36, 0, 4, 6, brown)
    f.ball("Seed2", -12, 0, 4, 6, brown)
    f.post("Radicle", -12, 0, -1, 3, 1, (240, 230, 200))
    f.ball("Seed3", 12, 0, 4, 6, brown)
    f.post("Shoot", 12, 0, 6, 14, 1.4, green)
    f.post("Seedling", 36, 0, 2, 24, 2, green)
    for s in (-1, 1):
        f.slab("CotyledonLeaf", 36 + s * 4, 0, 24, 8, 0.6, 5, green, "Grass")


# ============================================================== molecular biology
def central_dogma(f):
    plinth(f, 110, 26, (30, 36, 70))
    for i in range(16):
        t = i * 0.6
        for s, col in ((1, (90, 170, 255)), (-1, (255, 120, 200))):
            f.ball("DNABead", -46 + i * 1.6, s * 4 * math.cos(t), 14 + s * 4 * math.sin(t), 3, col, "Neon",
                   shadow=False)
    f.slab("DogmaArrow", -14, 0, 14, 8, 1.4, 1.4, (255, 255, 255), "Neon", shadow=False)
    for i in range(10):
        f.ball("mRNABead", -6 + i * 2, 0, 14 + math.sin(i) * 2, 2.6, (120, 240, 160), "Neon", shadow=False)
    f.ball("RibosomeLarge", 22, 0, 17, 12, (200, 160, 110))
    f.ball("RibosomeSmall", 22, 0, 8, 8, (220, 190, 140))
    f.slab("DogmaArrow2", 34, 0, 14, 6, 1.4, 1.4, (255, 255, 255), "Neon", shadow=False)
    for i in range(7):
        f.ball("ProteinBead", 42 + (i % 3) * 3, (i // 3) * 3 - 3, 8 + (i % 2) * 3, 4, (250, 200, 90))


def replication_fork(f):
    plinth(f, 100, 26, (30, 36, 70))
    for i in range(14):   # the closed helix
        t = i * 0.6
        for s, col in ((1, (90, 170, 255)), (-1, (255, 120, 200))):
            f.ball("ParentHelix", -44 + i * 2, s * 4 * math.cos(t), 24 + s * 4 * math.sin(t), 3, col, "Neon", shadow=False)
    for i in range(14):   # the fork: each old strand (bright) gets a new partner (white)
        spread = i * 1.4
        for s, col in ((1, (90, 170, 255)), (-1, (255, 120, 200))):
            f.ball("OldStrand", -14 + i * 3, 0, 24 + s * (4 + spread), 3, col, "Neon", shadow=False)
            if i > 2:
                f.ball("NewStrand", -14 + i * 3, 0, 24 + s * (spread - 0.5), 3, (240, 240, 250), "Neon", shadow=False)


def gel(f):
    plinth(f, 80, 24, (30, 36, 70))
    f.slab("GelSlab", 0, 0, 24, 64, 40, 3, (120, 160, 240), "Glass", transp=0.45)
    sizes = [36, 30, 26, 22, 18, 14, 10]
    for lane in range(6):
        a = -26 + lane * 10.4
        f.slab("GelWell", a, 1.6, 42, 6, 2, 1, (30, 30, 40))
        rows = sizes if lane == 0 else rnd.sample(sizes, 2)
        for h in rows:
            f.slab("GelBand", a, 1.8, 6 + h, 6.4, 1.2, 0.6, (255, 150, 230) if lane else (240, 240, 255), "Neon",
                   shadow=False)


def codon_wheel(f):
    plinth(f, 60, 20, (30, 36, 70))
    cols = [(240, 90, 90), (250, 200, 70), (90, 200, 110), (90, 140, 240)]
    for ring, R in enumerate((8, 15, 22)):
        f.ring("CodonRing", 0, 0, 30, R, 12 + ring * 8, (1.6 - ring * 0.2, 6, 2 * math.pi * R / (12 + ring * 8) + 0.4),
               cols[ring], "SmoothPlastic")
        f.ring("CodonTick", 0, 1, 30, R + 3.2, 4, (1.8, 0.6, 2), (255, 255, 255), "Neon", shadow=False)
    f.vdisc("CodonHub", 0, 0, 30, 6, 2, cols[3])


# ============================================================== forensic science
def fingerprint_types(f):
    f.floor_disc("PrintPad", 0, 0, 96, (40, 42, 52))
    neon = (90, 200, 255)
    for k in range(5):   # arch: stacked flat arcs
        for i in range(9):
            a = -36 + i * 3
            f.slab("ArchRidge", a - 0, k * 4 - 8, 0.5 + 6 * math.sin(math.pi * i / 8) * (1 - k * 0.12), 3.2, 0.6, 0.6,
                   neon, "Neon", shadow=False)
    for k in range(4):   # loop: nested U shapes
        r = 4 + k * 3
        for i in range(10):
            t = math.pi * i / 9
            f.ball("LoopRidge", math.cos(t) * r, -math.sin(t) * r + 4, 0.6, 1.2, neon, "Neon", shadow=False)
    for k in range(5):   # whorl: rings
        r = 2 + k * 3
        n = 8 + k * 4
        for i in range(n):
            t = 2 * math.pi * i / n
            f.ball("WhorlRidge", 34 + math.cos(t) * r, math.sin(t) * r, 0.6, 1.2, neon, "Neon", shadow=False)


def str_profile(f):
    plinth(f, 70, 20, (50, 52, 62))
    lanes = [(-20, (255, 200, 90)), (0, (240, 90, 90)), (20, (120, 230, 140))]
    pattern = {0: [10, 22, 31, 40], 1: [14, 22, 35, 44], 2: [14, 22, 35, 44]}   # the scene (middle) matches lane 3
    for li, (a, col) in enumerate(lanes):
        f.slab("ProfileBoard", a, 0, 28, 14, 48, 1, (24, 26, 34))
        for h in pattern[li]:
            f.slab("ProfileBand", a, 0.8, 4 + h, 11, 1.6, 0.6, col, "Neon", shadow=False)
    f.slab("MatchLink", 10, 0.9, 44, 20, 0.6, 0.4, (120, 230, 140), "Neon", shadow=False)


def blood_drops(f):
    f.floor_disc("DropPad", 0, 0, 70, (226, 226, 230))
    for k, stretch in enumerate((0.0, 1.0, 2.2, 3.6, 5.0)):   # 90 degrees (round) down to a shallow angle (long tail)
        a = -28 + k * 14
        f.floor_disc("BloodDrop", a, 0, 5, (150, 20, 30), h=0.3)
        if stretch:
            f.slab("BloodTail", a + 2 + stretch * 1.5, 0, 0.35, stretch * 3, 0.25, 2.2 - k * 0.2, (150, 20, 30), shadow=False)


def footprints(f):
    for k in range(10):
        side = 1 if k % 2 else -1
        x, _, z = f.p(-40 + k * 9, side * 3, 0)
        box("Footprint", (3, 0.2, 7), (x, f.Y + 0.2, z), (60, 50, 44), "SmoothPlastic", rot=(0, f.yaw_n, 0),
            collide=False, shadow=False)
        if k % 3 == 0:
            f.slab("EvidenceMarker", -40 + k * 9, 8, 2, 3, 4, 3, (250, 210, 40))


# ============================================================== agriculture
def nitrogen_cycle(f):
    f.floor_disc("CycleFloor", 0, 0, 90, (130, 96, 62), "Ground")
    f.ring("CycleArrowRing", 0, 0, 16, 34, 36, (1, 1.4, 5), (255, 255, 255), "Neon", shadow=False)
    for s in (-1, 1):
        f.ball("N2", -34 + s * 2, 0, 50, 4.4, (120, 160, 240))
    f.post("PlantStem", 34, 0, 0, 30, 2.4, (90, 170, 70))
    f.ball("PlantTop", 34, 0, 32, 12, (90, 170, 70), "Grass")
    for k in range(5):
        f.ball("RootNodule", 34 + rnd.uniform(-5, 5), 0, rnd.uniform(-1, 2), 2.6, (240, 140, 170))
    f.ball("Mushroom", 0, 0, 6, 10, (230, 210, 180))
    f.post("MushroomStem", 0, 0, 0, 5, 3, (240, 230, 210))
    f.ball("Nitrate", -14, 0, 2, 4, (250, 220, 90), "Neon", shadow=False)


def soil_profile(f):
    layers = [(6, (60, 40, 26)), (10, (110, 78, 48)), (12, (160, 100, 60)), (10, (180, 160, 130)), (8, (120, 116, 112))]
    h = 50
    for th, col in layers:
        f.slab("SoilLayer", 0, 0, h - th / 2, 36, th, 24, col, "Ground")
        h -= th
    for k in range(6):
        f.ball("SoilStone", rnd.uniform(-14, 14), 12.5, rnd.uniform(5, 14), rnd.uniform(3, 5), (150, 146, 140))
    f.post("SoilPlant", 0, 0, 50, 58, 1.4, (90, 170, 70))
    f.ball("SoilPlantTop", 0, 0, 59, 5, (90, 170, 70), "Grass")


def drip_irrigation(f):
    for row in range(3):
        b = -10 + row * 10
        f.slab("DripPipe", 0, b, 1, 80, 1, 1, (40, 40, 44))
        for k in range(8):
            a = -35 + k * 10
            f.ball("DripPlant", a, b, 4, 5, (90, 170, 70), "Grass")
            f.ball("WaterDrop", a + 2, b, 1.6, 1.2, (90, 170, 255), "Neon", shadow=False)


def hydroponics(f):
    plinth(f, 70, 20)
    for k in range(4):
        a = -24 + k * 16
        f.post("HydroTower", a, 0, 2, 40, 5, (236, 240, 244))
        f.post("HydroWater", a, 0, 2, 36, 3, (90, 170, 255), "Neon", transp=0.3, shadow=False)
        for j in range(5):
            for s in (-1, 1):
                f.ball("HydroLettuce", a + s * 3.6, 0, 8 + j * 7, 4, (110, 200, 90), "Grass")


# ============================================================== biotechnology
def plasmid(f):
    plinth(f, 80, 24)
    f.ring("Plasmid", -8, 0, 30, 20, 36, (2.4, 3, 4.2), (90, 160, 240))
    f.ring("InsertGene", -8, 0.6, 30, 20, 6, (2.6, 3.4, 4.3), (250, 200, 60), "Neon", shadow=False)
    for s in (-1, 1):   # restriction enzyme "scissors"
        box("ScissorBlade", (2, 1, 22), f.p(26, 0, 30 + s * 4), (200, 205, 215), "Metal", rot=(s * 20, f.yaw_n, 0),
            collide=False)
    f.ball("ScissorPivot", 26, 0, 30, 3, (60, 60, 70))


def pcr_cycle(f):
    plinth(f, 96, 24)
    for k, col in enumerate(((240, 80, 70), (80, 140, 240), (250, 160, 60))):
        a = -32 + k * 32
        f.slab("HeatBlock", a, 0, 5, 20, 6, 16, col)
        n = 2 ** k
        for j in range(n):
            h = 10 + j * 3.4
            f.slab("DNACopy", a, 0, h, 14, 1.2, 1.2, (90, 170, 255), "Neon", shadow=False)
            f.slab("DNACopy2", a, 0, h + 1.4, 14, 1.2, 1.2, (255, 120, 200), "Neon", shadow=False)


def insulin_tank(f):
    plinth(f, 60, 26)
    f.post("TankGlass", 0, 0, 2, 44, 26, (210, 236, 245), "Glass", transp=0.55)
    f.post("TankBroth", 0, 0, 3, 32, 24, (240, 210, 120), "SmoothPlastic", transp=0.4)
    for k in range(8):
        f.slab("ModBacterium", rnd.uniform(-7, 7), rnd.uniform(-7, 7), rnd.uniform(8, 28), 4, 1.6, 1.6, (120, 200, 120))
    for k in range(6):
        f.ball("Insulin", rnd.uniform(-8, 8), rnd.uniform(-8, 8), rnd.uniform(8, 30), 1.8, (255, 255, 255), "Neon",
               shadow=False)
    f.ball("TankLid", 0, 0, 44, 26, (190, 198, 210), "Metal")


def stem_cells(f):
    plinth(f, 80, 26)
    f.ball("StemCell", 0, 0, 14, 12, (240, 230, 250), "Neon", shadow=False, light=(1.2, 24, (240, 220, 255)))
    targets = [(-28, 30, (210, 50, 60)), (0, 40, (240, 190, 90)), (28, 30, (220, 120, 120))]
    for a, h, col in targets:
        steps = 6
        for s in range(1, steps):
            f.ball("Branch", a * s / steps, 0, 14 + (h - 14) * s / steps, 1.6, (255, 255, 255), "Neon", shadow=False)
    f.vdisc("RedBloodCell", -28, 0, 30, 9, 2.4, (210, 50, 60))
    f.ball("Neuron", 0, 0, 40, 6, (240, 190, 90))
    for s in (-1, 1):
        f.slab("NeuronArm", s * 6, 0, 42, 8, 0.8, 0.8, (240, 190, 90))
    f.slab("MuscleFibre", 28, 0, 30, 14, 4, 4, (220, 120, 120))


# ============================================================== the plan
# (builder, footprint radius, on-screen caption)
CONCEPTS = {
    "micro": [
        (growth_curve, 52, "📈 منحنى نمو البكتيريا: تأقلم، ثم تكاثر سريع، ثم ثبات، ثم موت"),
        (binary_fission, 44, "➗ الانشطار الثنائي: كل بكتيريا تنقسم لثنتين، فالعدد يتضاعف كل جيل"),
        (gram_walls, 48, "🟣 جرام موجبة: جدار سميك يمسك الصبغة • 🩷 جرام سالبة: جدار رقيق وغشاء خارجي"),
        (size_scale, 44, "📏 الفيروسات أصغر من البكتيريا بعشرات المرات"),
    ],
    "biochem": [
        (lock_and_key, 44, "🔑 القفل والمفتاح: موقع الإنزيم النشط يناسب مادة وحدة بس"),
        (activation_energy, 54, "⛰️ الإنزيم يخفض طاقة التنشيط (الأخضر)، فيصير التفاعل أسرع"),
        (atp_model, 42, "⚡ ATP: لما تنكسر رابطة الفوسفات الأخيرة تطلع طاقة للخلية"),
        (protein_fold, 52, "🧶 البروتين: سلسلة أحماض أمينية تلتف وتنطوي، وشكلها يحدد وظيفتها"),
    ],
    "animal": [
        (energy_pyramid, 40, "🔺 هرم الطاقة: كل مستوى ياخذ تقريباً 10% بس من طاقة اللي تحته"),
        (heart, 34, "❤️ قلب الثدييات 4 حجرات: الأيمن يضخ للرئة، والأيسر يضخ للجسم"),
        (frog_cycle, 48, "🐸 دورة حياة الضفدع: بيضة ← شرغوف ← ضفدع صغير ← ضفدع بالغ"),
        (desert_food_chain, 54, "🦅 سلسلة غذائية بالصحراء: نبات ← جرادة ← ضب ← صقر"),
    ],
    "plant": [
        (photosynthesis, 54, "☀️ البناء الضوئي: ثاني أكسيد الكربون + ماء + ضوء ← جلوكوز + أكسجين"),
        (leaf_section, 46, "🍃 مقطع ورقة: خلايا عمادية تمسك الضوء، وثغور تتبادل الغازات"),
        (xylem_phloem, 30, "💧 الخشب ينقل الماي للأعلى، واللحاء يوزع السكر بالنبتة"),
        (germination, 48, "🌱 الإنبات: بذرة ← جذر ← ساق ← بادرة"),
    ],
    "molecular": [
        (central_dogma, 58, "🧬 لصنع بروتين: تُنسخ معلومات الجين من DNA إلى mRNA، ثم تُترجم لبناء البروتين"),
        (replication_fork, 54, "🍴 تضاعف DNA: الشريط ينفك وكل نصف يبني شريك جديد"),
        (gel, 44, "🧪 الفصل الكهربائي: قطع DNA الصغيرة تمشي أبعد بالجل"),
        (codon_wheel, 34, "🎡 الكودون 3 قواعد في mRNA: يحدد حمضاً أمينياً أو يعطي إشارة توقف لبناء البروتين"),
    ],
    "forensic": [
        (fingerprint_types, 50, "🖐️ البصمات ثلاث أنماط: قوس، عروة، دوامة، وكل شخص بصمته غير"),
        (str_profile, 38, "🧬 البصمة الوراثية: نقارن أشرطة DNA من مسرح الجريمة مع المشتبه فيهم"),
        (blood_drops, 38, "🩸 شكل قطرة الدم يكشف زاوية سقوطها: مدورة = عمودية، طويلة = مايلة"),
        (footprints, 46, "👣 كل دليل ياخذ رقم وصورة قبل ما ينشال"),
    ],
    "agri": [
        (nitrogen_cycle, 48, "🔄 دورة النيتروجين: بكتيريا الجذور تثبّته، والنبات ياخذه، والمحلّلات ترجعه"),
        (soil_profile, 30, "🟫 طبقات التربة: دبال، تربة سطحية، تحت سطحية، صخور"),
        (drip_irrigation, 44, "💧 الري بالتنقيط: يوصل الماي للجذور ويوفّر بالمناطق الحارة مثل الكويت"),
        (hydroponics, 38, "🥬 الزراعة المائية: نباتات تنمو بمحلول مغذي بدون تربة"),
    ],
    "biotech": [
        (plasmid, 44, "🧬 الهندسة الوراثية: نقص البلازميد بإنزيم قطع ونلصق فيه جين جديد"),
        (pcr_cycle, 50, "🔥 PCR: تسخين ← ربط البادئات ← بناء، والعدد يتضاعف كل دورة"),
        (insulin_tank, 34, "💉 بكتيريا معدّلة وراثياً تصنع الإنسولين لمرضى السكري"),
        (stem_cells, 44, "🌟 الخلايا الجذعية تقدر تتحول لأنواع خلايا مختلفة"),
    ],
}
