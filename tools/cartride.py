"""Cart Ride Into the Cell (+ every BSC specialty) — a "Cart Ride Into ..." style track.

The track is generated with a turtle (straights, turns, slopes, helixes, loops, jumps) and written as
invisible waypoints  CW|<i>|<flags>|<label>  whose own rotation carries the track's right-hand vector.
Flags:  s<n> section start (respawn point)   b booster   g in the air (no rails)
        j<v> needs at least v studs/s here (jumps, loops)   x<v> derails above v studs/s (sharp curves)
The client (CartRide.client.luau) drives the cart along these points; the server (CartRide.server.luau)
spawns a real cart welded to the player so everyone sees each other riding.
"""
import math
import random

import genmap as G
import genmap5 as C5
import bsc_art as A

box, vcyl, disc, ball, sign = G.box, G.vcyl, G.disc, G.ball, G.sign
rect = C5.rect
rng = random.Random(77)

CART_OFFSET = (-9000.0, 150.0, 9000.0)
STEP = 5.0
ISLAND_Y = -60.0
_section = [0, []]


# ====================================================================== the cart
def cart_model(x, y, z, name="CartTemplate", yaw=0):
    """open cart, front toward local -Z (the seat's look direction). yaw only rotates the display copy."""
    r = math.radians(yaw)

    def P(dx, dz):
        return (x + dx * math.cos(r) + dz * math.sin(r), z - dx * math.sin(r) + dz * math.cos(r))
    with G.Group(name, "Model"):
        sx, sz = P(0, 0)
        G.part("Seat", (3.4, 1, 3.4), (sx, y + 2.0, sz), (40, 40, 48), "SmoothPlastic", cls="Seat", rot=(0, yaw, 0))
        bx, bz = P(0, 0.4)
        G.part("CartFloor", (5.6, 0.6, 8.4), (bx, y + 1.3, bz), (250, 250, 248), "SmoothPlastic", rot=(0, yaw, 0))
        for s_ in (-1, 1):
            px, pz = P(s_ * 2.9, 0.4)
            G.part("CartSide", (0.5, 2.6, 8.4), (px, y + 2.6, pz), (240, 110, 200), "SmoothPlastic", rot=(0, yaw, 0))
            px, pz = P(s_ * 3.0, 0.4)
            G.part("CartStripe", (0.3, 0.5, 8.6), (px, y + 3.0, pz), (60, 220, 255), "Neon", rot=(0, yaw, 0))
        fx, fz = P(0, -3.9)
        G.part("CartFront", (5.8, 3.4, 0.6), (fx, y + 3.0, fz), (120, 64, 176), "SmoothPlastic", rot=(0, yaw, 0))
        ex, ez = P(0, 4.4)
        G.part("CartBack", (5.8, 3.0, 0.5), (ex, y + 2.8, ez), (120, 64, 176), "SmoothPlastic", rot=(0, yaw, 0))
        lx, lz = P(0, -4.25)
        G.part("CartBadge", (2.6, 2.6, 0.2), (lx, y + 3.2, lz), (255, 255, 255), "SmoothPlastic", rot=(0, yaw, 0),
               text=dict(face="Front", text="🧬", color=(20, 20, 20), bg=(250, 222, 170), bg_t=0.0))
        for wx in (-2.6, 2.6):
            for wz in (-2.8, 3.4):
                cx_, cz_ = P(wx, wz)
                G.part("CartWheel", (0.8, 2.0, 2.0), (cx_, y + 1.0, cz_), (40, 40, 46), "SmoothPlastic", shape="Cylinder",
                       rot=(0, yaw, 0))
        hx, hz = P(0, -4.3)
        G.part("CartLight", (1.0, 0.6, 0.3), (hx, y + 1.8, hz), (255, 250, 220), "Neon", rot=(0, yaw, 0))
        # v30: locomotive dress (nose, cab roof on posts, twin headlights, club livery); all welded to the seat by the server
        nx_, nz_ = P(0, -6.0)
        G.part("LocoNose", (5.4, 2.8, 3.0), (nx_, y + 2.6, nz_), (24, 80, 56), "SmoothPlastic", rot=(0, yaw, 0))
        for s_ in (-1, 1):
            hx2, hz2 = P(s_ * 1.8, -7.55)
            G.part("LocoHeadlight", (1.0, 1.0, 0.3), (hx2, y + 3.0, hz2), (255, 246, 210), "Neon", rot=(0, yaw, 0))
            px2, pz2 = P(s_ * 2.6, 2.2)
            G.part("CabPost", (0.4, 4.6, 0.4), (px2, y + 5.4, pz2), (30, 34, 40), "Metal", rot=(0, yaw, 0))
            px3, pz3 = P(s_ * 2.6, -2.6)
            G.part("CabPost", (0.4, 4.6, 0.4), (px3, y + 5.4, pz3), (30, 34, 40), "Metal", rot=(0, yaw, 0))
        rx2, rz2 = P(0, -0.2)
        G.part("CabRoof", (6.4, 0.5, 6.4), (rx2, y + 7.9, rz2), (24, 80, 56), "SmoothPlastic", rot=(0, yaw, 0))
        G.part("CabRoofStripe", (6.5, 0.2, 6.5), (rx2, y + 8.2, rz2), (255, 214, 90), "Neon", rot=(0, yaw, 0))


def cart_car_model(x, y, z, name="CartCarTemplate", yaw=0):
    """v30: passenger car the rider's client hooks behind the locomotive (local decoration, follows the rail)"""
    r = math.radians(yaw)

    def P(dx, dz):
        return (x + dx * math.cos(r) + dz * math.sin(r), z - dx * math.sin(r) + dz * math.cos(r))
    with G.Group(name, "Model"):
        bx, bz = P(0, 0)
        G.part("CarBody", (5.6, 0.6, 9.6), (bx, y + 1.3, bz), (250, 250, 248), "SmoothPlastic", rot=(0, yaw, 0), collide=False)
        for s_ in (-1, 1):
            px, pz = P(s_ * 2.9, 0)
            G.part("CarSide", (0.5, 2.4, 9.6), (px, y + 2.6, pz), (24, 80, 56), "SmoothPlastic", rot=(0, yaw, 0), collide=False)
            px, pz = P(s_ * 3.0, 0)
            G.part("CarStripe", (0.3, 0.4, 9.8), (px, y + 3.1, pz), (255, 214, 90), "Neon", rot=(0, yaw, 0), collide=False)
        for dz_ in (-2.2, 2.2):
            sx_, sz_ = P(0, dz_)
            G.part("CarBench", (4.6, 1.0, 2.0), (sx_, y + 2.1, sz_), (120, 64, 176), "Fabric", rot=(0, yaw, 0), collide=False)
        for wx in (-2.6, 2.6):
            for wz in (-3.4, 3.4):
                cx_, cz_ = P(wx, wz)
                G.part("CarWheel", (0.8, 2.0, 2.0), (cx_, y + 1.0, cz_), (40, 40, 46), "SmoothPlastic", shape="Cylinder",
                       rot=(0, yaw, 0), collide=False)


# ====================================================================== track turtle
class Turtle:
    def __init__(self):
        self.p = [0.0, 0.0, 0.0]
        self.yaw = 0.0
        self.pts = []          # (x, y, z, yaw, flags:list, label)
        self.sections = []

    def f(self, yaw=None):
        r = math.radians(self.yaw if yaw is None else yaw)
        return math.sin(r), math.cos(r)

    def r(self, yaw=None):
        r = math.radians(self.yaw if yaw is None else yaw)
        return math.cos(r), -math.sin(r)

    def emit(self, flags=(), label=""):
        self.pts.append((self.p[0], self.p[1], self.p[2], self.yaw, list(flags), label))

    def section(self, name):
        self.sections.append((len(self.pts), name))
        self.emit(["s%d" % len(self.sections)], name)
        self.marks = getattr(self, "marks", {})

    def straight(self, L, dy=0.0, flags=()):
        n = max(1, int(math.ceil(L / STEP)))
        x0, y0, z0 = self.p
        fx, fz = self.f()
        for i in range(1, n + 1):
            s = i / n
            self.p = [x0 + fx * L * s, y0 + dy * (1 - math.cos(math.pi * s)) / 2, z0 + fz * L * s]
            self.emit(flags)

    def turn(self, ang, R, dy=0.0, flags=()):
        arc = abs(math.radians(ang)) * R
        n = max(2, int(math.ceil(arc / STEP)))
        sgn = 1 if ang > 0 else -1
        rx, rz = self.r()
        cx, cz = self.p[0] + rx * R * sgn, self.p[2] + rz * R * sgn
        self.last_center = (cx, self.p[1], cz)
        y0, yaw0 = self.p[1], self.yaw
        for i in range(1, n + 1):
            s = i / n
            self.yaw = yaw0 + ang * s
            rx, rz = self.r()
            self.p = [cx - rx * R * sgn, y0 + dy * s, cz - rz * R * sgn]
            self.emit(flags)

    def loop(self, R, shift=12.0, need=0):
        n = int(math.ceil(2 * math.pi * R / STEP))
        x0, y0, z0 = self.p
        fx, fz = self.f()
        rx, rz = self.r()
        for i in range(1, n + 1):
            th = 2 * math.pi * i / n
            side = shift * (th - math.sin(th)) / (2 * math.pi)
            self.p = [x0 + fx * R * math.sin(th) + rx * side, y0 + R * (1 - math.cos(th)), z0 + fz * R * math.sin(th) + rz * side]
            self.emit(["j%d" % need] if (i == 1 and need) else [])

    def jump(self, L, h, need, drop=0.0):
        n = max(3, int(math.ceil(L / STEP)))
        x0, y0, z0 = self.p
        fx, fz = self.f()
        for i in range(1, n + 1):
            s = i / n
            self.p = [x0 + fx * L * s, y0 + 4 * h * s * (1 - s) - drop * s, z0 + fz * L * s]
            fl = ["g"] if i < n else []
            if i == 1:
                fl.append("j%d" % need)
            self.emit(fl)


# ====================================================================== sections
# v31: a classic sightseeing train, not a coaster. The eight official specialties in their official order, one room each;
# smooth S-bends and gentle hills only (no loops, jumps or crash curves). The cell world has its own train elsewhere.
SECTIONS = [
    ("المحطة", "Station"),
    ("مايكروبيولوجي 🦠", "Microbiology"),
    ("بايوكيمستري ⚗️", "Biochemistry"),
    ("بيولوجيا حيوان 🐢", "Animal Biology"),
    ("بيولوجيا نبات 🌿", "Plant Biology"),
    ("مولكلر 🧬", "Molecular Biology"),
    ("الأدلة الجنائية 🔎", "Forensic Science"),
    ("الزراعة 🌴", "Agriculture"),
    ("البايوتكنولوجي 🧪", "Biotechnology"),
]
SECTION_KEYS = ["micro", "biochem", "animal", "plant", "molecular", "forensic", "agri", "biotech"]
# index of each section in the parkour zone list (Shared/Zones) -> AreaAtmosphere reuses those looks
SECTION_ZONE = {"plant": 1, "animal": 2, "micro": 3, "biochem": 4, "molecular": 5, "agri": 6, "forensic": 7, "biotech": 8}


def build_track():
    """a snake of rows: every specialty runs along its own row, rows are joined by wide U-turns.
    Each row is a gentle S-bend with one soft hill, so the train glides past the landmarks."""
    t = Turtle()
    t.yaw = 90.0                               # rows run along +X / -X
    t.marks = {}
    t.emit(["s0"], "المحطة")
    t.straight(50)
    t.straight(60, dy=-12)
    side = [1]

    def uturn():
        t.straight(30)
        t.turn(180 * side[0], 70)
        side[0] = -side[0]
        t.straight(30)

    def tour_row(hill):
        t.straight(50)
        t.turn(20, 140)
        t.turn(-20, 140)
        t.straight(70, dy=hill)
        t.turn(-20, 140)
        t.turn(20, 140)
        t.straight(70, dy=-hill)
        t.straight(40)

    for k, key in enumerate(SECTION_KEYS, start=1):
        name = SECTIONS[k][0] + " " + SECTIONS[k][1]
        t.section(name)
        if key == "molecular":
            # a slow climb around the giant DNA helix and back down the other side
            t.straight(40)
            t.turn(360 * side[0], 30, dy=30)
            t.marks["dna"] = t.last_center
            t.straight(80)
            t.turn(-360 * side[0], 30, dy=-30)
            t.straight(40)
        else:
            tour_row({"micro": 8, "biochem": -6, "animal": 10, "plant": -8, "forensic": 0, "agri": 6, "biotech": -6}[key])
        if key == "biotech":
            t.straight(50, dy=10)
            t.emit(["end"], "🎉 خلصت الرحلة! نادي العلوم البيولوجية يشكرك")
        else:
            uturn()
    return t


def check(t, min_d=11.0):
    """no two distant parts of the track may come close (keeps loops/helixes from clipping)"""
    pts = t.pts
    bad = 0
    grid = {}
    for i, p in enumerate(pts):
        key = (int(p[0] // 20), int(p[1] // 20), int(p[2] // 20))
        grid.setdefault(key, []).append(i)
    for i, p in enumerate(pts):
        kx, ky, kz = int(p[0] // 20), int(p[1] // 20), int(p[2] // 20)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    for j in grid.get((kx + dx, ky + dy, kz + dz), ()):
                        if j > i + 12:
                            q = pts[j]
                            if math.dist(p[:3], q[:3]) < min_d:
                                bad += 1
    return bad


# ====================================================================== rendering
def draw_track(t):
    pts = t.pts
    with G.Group("CartTrack"):
        for i, (x, y, z, yaw, flags, label) in enumerate(pts):
            G.part("CW|%d|%s|%s" % (i + 1, ",".join(flags), label), (1, 1, 1), (x, y, z), (0, 0, 0), "SmoothPlastic", transp=1,
                   collide=False, shadow=False, rot=(0, yaw, 0))
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            if "g" in a[4] or "g" in b[4]:
                continue    # in the air over a jump: no rails
            dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
            yaw = a[3]
            ry = math.radians(yaw)
            h = dx * math.sin(ry) + dz * math.cos(ry)
            L = math.sqrt(dx * dx + dy * dy + dz * dz)
            pitch = -math.degrees(math.atan2(dy, h))
            rx, rz = math.cos(ry), -math.sin(ry)
            # loops twist the rails: their "down" follows the loop, so offset along the track normal
            mx, my, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2
            nlen = L or 1
            tx, ty, tz = dx / nlen, dy / nlen, dz / nlen
            ux, uy, uz = ty * rz, tz * rx - tx * rz, -ty * rx      # up = tangent x right (right is horizontal)
            ul = math.sqrt(ux * ux + uy * uy + uz * uz) or 1
            ux, uy, uz = ux / ul, uy / ul, uz / ul
            for s_ in (-1, 1):
                box("Rail", (0.5, 0.5, L + 0.3), (mx + rx * s_ * 2.4 - ux * 0.3, my - uy * 0.3, mz + rz * s_ * 2.4 - uz * 0.3),
                    (210, 214, 222), "Metal", rot=(pitch, yaw, 0), collide=False, shadow=False)
            if i % 2 == 0:
                box("Tie", (6.4, 0.4, 1.0), (mx - ux * 0.9, my - uy * 0.9, mz - uz * 0.9),
                    (120, 64, 176) if "b" not in a[4] else (255, 200, 60), "SmoothPlastic" if "b" not in a[4] else "Neon",
                    rot=(pitch, yaw, 0), collide=False, shadow=False)
            if i % 8 == 0 and uy > 0.9 and y_above(a) > 6:
                vcyl("Support", a[0], ISLAND_Y, a[1] - 1.2, a[2], 1.0, (200, 200, 210), "Metal", collide=False, shadow=False)
            if "b" in a[4] and i % 2 == 0:
                box("Boost", (4, 0.2, 2.2), (a[0], a[1] - 0.3, a[2]), (255, 210, 60), "Neon", rot=(0, yaw, 0), collide=False,
                    shadow=False)


def y_above(p):
    return p[1] - ISLAND_Y


def signs(t):
    """warning boards before jumps/loops/sharp curves"""
    seen = set()
    for i, (x, y, z, yaw, flags, label) in enumerate(t.pts):
        for fl in flags:
            if fl[0] in "jx" and fl[1:].isdigit() and int(fl[1:]) > 0 and (fl, i // 30) not in seen:
                seen.add((fl, i // 30))
                k = max(0, i - 9)
                px, py, pz, pyaw = t.pts[k][:4]
                rx, rz = math.cos(math.radians(pyaw)), -math.sin(math.radians(pyaw))
                txt = ("🚀 تحتاج سرعة %s+" % fl[1:]) if fl[0] == "j" else ("⚠️ خفّف! أقصى سرعة %s" % fl[1:])
                col = (40, 120, 60) if fl[0] == "j" else (170, 60, 30)
                G.part("CartWarn", (14, 3.4, 0.4), (px + rx * 9, py + 6, pz + rz * 9), col, "SmoothPlastic",
                       rot=(0, pyaw + 180, 0), collide=False,
                       text=dict(face="Front", text=txt, color=(255, 255, 255), bg=col, bg_t=0.0))
                vcyl("WarnPost", px + rx * 9, py - 4, py + 4.3, pz + rz * 9, 0.5, (80, 80, 86), "Metal", collide=False)


# ====================================================================== themed scenery
def section_bounds(t):
    out = []
    starts = [s for s, _ in t.sections] + [len(t.pts)]
    for k in range(len(t.sections)):
        seg = t.pts[starts[k]:starts[k + 1]]
        xs, zs = [p[0] for p in seg], [p[2] for p in seg]
        out.append((min(xs), max(xs), min(zs), max(zs), seg))
    return out


class Clear:
    """keeps scenery away from the track"""
    def __init__(self, pts, d):
        self.d = d
        self.grid = {}
        for p in pts:
            self.grid.setdefault((int(p[0] // 30), int(p[2] // 30)), []).append(p)

    def ok(self, x, z, r=0.0):
        # v31: never across a glass partition between two rooms (CUTS = the partition lines, filled by scenery())
        if any(abs(z - c) < r + 3 for c in CUTS):
            return False
        kx, kz = int(x // 30), int(z // 30)
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                for p in self.grid.get((kx + dx, kz + dz), ()):
                    if math.hypot(p[0] - x, p[2] - z) < self.d + r:
                        return False
        return True


def scatter(clear, discs, n, r, fn):
    placed = 0
    for _ in range(n * 30):
        if placed >= n:
            break
        cx, cz, R = rng.choice(discs)
        a, d = rng.uniform(0, 2 * math.pi), R * math.sqrt(rng.random()) * 0.85
        x, z = cx + d * math.cos(a), cz + d * math.sin(a)
        if clear.ok(x, z, r):
            fn(x, z)
            placed += 1


def island(cx, cz, R, col, mat, rim=None):
    """a chain of floating islands under the section's track; returns the discs for scatter()"""
    k = _section[0]
    seg = _section[1]
    discs = []
    for i in range(0, len(seg), 10):
        px, py, pz = seg[i][:3]
        rr = rng.uniform(38, 58)
        ox, oz = rng.uniform(-12, 12), rng.uniform(-12, 12)
        discs.append((px + ox, pz + oz, rr))
        y = ISLAND_Y - 2 - (i % 30) * 0.05 - k * 0.3
        disc("Island", px + ox, y, pz + oz, rr * 2, 4, col, mat)
        disc("IslandRock", px + ox, y - 7, pz + oz, rr * 1.6, 10, (120, 110, 100), "Rock", collide=False)
        if rim:
            disc("IslandRim", px + ox, y + 1.5, pz + oz, rr * 2 + 0.8, 0.8, rim, "Neon", collide=False, shadow=False)
    return discs


def room_cuts(t):
    """z of the glass partitions: halfway between consecutive sections' rows (same rule as cart_hall)"""
    b = section_bounds(t)
    out = []
    for k in range(0, len(b) - 1):
        z_this = sum(p[2] for p in b[k][4]) / len(b[k][4])
        z_next = sum(p[2] for p in b[k + 1][4]) / len(b[k + 1][4])
        out.append((z_this + z_next) / 2)
    return out


CUTS = []


def scenery(t):
    CUTS[:] = room_cuts(t)
    clear = Clear(t.pts, 14)
    Y = ISLAND_Y
    b = section_bounds(t)
    for k, (x0, x1, z0, z1, seg) in enumerate(b, start=1):
        _section[0] = k
        _section[1] = seg
        key = SECTION_KEYS[k - 1]
        cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
        R = max(x1 - x0, z1 - z0) / 2 + 50
        with G.Group("CartScene%d" % k):
            if key == "plant":
                discs = island(cx, cz, R, (110, 170, 90), "Grass")
                scatter(clear, discs, 10, 16, lambda x, z: _leaf(x, Y, z))
                scatter(clear, discs, 12, 8, lambda x, z: _flower(x, Y, z))
                scatter(clear, discs, 2, 22, lambda x, z: _chloroplast(x, Y + 30, z))
                landmark(clear, seg, 0.3, 46, 22, _lm_flower, "🌸 زهرة عملاقة: البتلات تجذب الملقّحات")
                landmark(clear, seg, 0.72, 46, 20, _lm_roots, "🌱 الجذور تمتص الماء والأملاح من التربة")
            elif key == "animal":
                discs = island(cx, cz, R, (210, 190, 140), "Sand")
                scatter(clear, discs, 2, 26, lambda x, z: _turtle(x, Y, z))
                scatter(clear, discs, 3, 16, lambda x, z: _camel(x, Y, z))
                scatter(clear, discs, 5, 10, lambda x, z: _falcon(x, Y + rng.uniform(30, 60), z))
                scatter(clear, discs, 6, 10, lambda x, z: _cactus(x, Y, z))
                landmark(clear, seg, 0.32, 50, 30, _lm_whale, "🐋 هيكل حوت: أكبر حيوان عاش على الأرض")
                landmark(clear, seg, 0.75, 44, 16, _lm_heart, "❤️ قلب الإنسان: 4 حجرات")
            elif key == "micro":
                discs = island(cx, cz, R, (240, 228, 170), "SmoothPlastic", rim=(200, 230, 255))
                for (dx_, dz_, dr_) in discs:
                    disc("PetriWall", dx_, Y + 1.5, dz_, dr_ * 2 + 1, 3, (200, 230, 240), "Glass", transp=0.6, collide=False)
                scatter(clear, discs, 12, 10, lambda x, z: _bacterium(x, Y + rng.uniform(3, 30), z))
                scatter(clear, discs, 6, 10, lambda x, z: _virus(x, Y + rng.uniform(10, 40), z))
                scatter(clear, discs, 14, 6, lambda x, z: disc("Colony", x, Y + 0.2, z,
                        rng.uniform(4, 9), 0.6, rng.choice([(250, 240, 200), (240, 200, 120), (230, 150, 160)]), "SmoothPlastic",
                        collide=False))
                landmark(clear, seg, 0.3, 46, 22, _lm_microscope, "🔬 مجهر ضوئي: يكبّر حتى 1000 مرة")
                landmark(clear, seg, 0.72, 50, 34, _lm_petri, "🧫 طبق بتري: مستعمرات بكتيرية تنمو على الآجار")
            elif key == "biochem":
                discs = island(cx, cz, R, (230, 232, 240), "Marble", rim=(170, 90, 255))
                scatter(clear, discs, 6, 18, lambda x, z: _molecule(x, Y + rng.uniform(20, 45), z))
                scatter(clear, discs, 6, 8, lambda x, z: _tube(x, Y, z))
                landmark(clear, seg, 0.3, 46, 22, _lm_enzyme, "🧩 إنزيم: المادة المتفاعلة تدخل الموقع النشط")
                landmark(clear, seg, 0.72, 46, 30, _lm_krebs, "🔄 دورة كربس: طاقة من الغذاء")
            elif key == "molecular":
                discs = island(cx, cz, R, (30, 40, 70), "SmoothPlastic", rim=(80, 255, 150))
                dx_, dy_, dz_ = t.marks["dna"]
                _dna(dx_, Y, dz_, 130, r=14, ball_d=4.2)
                scatter(clear, discs, 3, 16, lambda x, z: _dna(x, Y, z, 70))
                scatter(clear, discs, 8, 6, lambda x, z: sign("Codon",
                        rng.choice(["AUG", "UUU", "GGC", "UGG", "TATA", "A-T", "G-C"]), (x, Y + rng.uniform(15, 40), z), (8, 3, 0.4),
                        "Front", bg=(20, 60, 50), color=(120, 255, 180)))
                landmark(clear, seg, 0.9, 44, 24, _lm_translation, "🧬 الترجمة: الريبوسوم يقرا mRNA ويبني بروتين")
            elif key == "forensic":
                discs = island(cx, cz, R, (96, 98, 110), "Slate", rim=(255, 214, 60))
                scatter(clear, discs, 6, 12, lambda x, z: _tape(x, Y, z))
                scatter(clear, discs, 3, 18, lambda x, z: _print(x, Y, z))
                scatter(clear, discs, 2, 18, lambda x, z: _magnifier(x, Y, z))
                landmark(clear, seg, 0.4, 44, 26, _lm_fingerprint, "🔎 البصمة: نمطها يختلف من شخص لشخص")
                landmark(clear, seg, 0.78, 44, 22, _lm_evidence_lab, "🧪 تحليل الأدلة: عيّنات وجهاز DNA")
            elif key == "agri":
                discs = island(cx, cz, R, (150, 112, 72), "Ground")
                for (dx_, dz_, dr_) in discs[::2]:
                    for q in range(-2, 3):
                        xx = dx_ + q * 7
                        if clear.ok(xx, dz_, 6):
                            rect("CropRow", xx - 1.6, xx + 1.6, Y, Y + 2.2, dz_ - dr_ * 0.5, dz_ + dr_ * 0.5,
                                 (110, 170, 80) if q % 2 else (220, 190, 90), "Grass", collide=False)
                scatter(clear, discs, 10, 10, lambda x, z: _palm(x, Y, z))
                scatter(clear, discs, 1, 30, lambda x, z: _windmill(x, Y, z))
                scatter(clear, discs, 1, 20, lambda x, z: _greenhouse(x, Y, z))
                landmark(clear, seg, 0.25, 40, 12, _lm_pivot, "💧 ري محوري: يسقي الحقل بدائرة كاملة")
                landmark(clear, seg, 0.74, 44, 22, _lm_silo_tractor, "🌾 صومعة الحبوب والجرار")
            elif key == "biotech":
                discs = island(cx, cz, R, (236, 240, 244), "SmoothPlastic", rim=(60, 220, 255))
                scatter(clear, discs, 5, 10, lambda x, z: _bioreactor(x, Y, z))
                scatter(clear, discs, 6, 10, lambda x, z: _jelly(x, Y + rng.uniform(20, 50), z))
                landmark(clear, seg, 0.3, 46, 24, _lm_pcr, "🧬 جهاز PCR: ينسخ DNA ملايين المرات")
                landmark(clear, seg, 0.7, 46, 22, _lm_crispr, "✂️ كريسبر: مقص جيني يعدّل DNA بدقة")
            # the section sign near the section start (never on the floor)
            sx, sy, sz, syaw = seg[0][:4]
            rx, rz = math.cos(math.radians(syaw)), -math.sin(math.radians(syaw))
            name = SECTIONS[k][0]
            G.part("SectionSign", (26, 6, 0.6), (sx + rx * 12, sy + 10, sz + rz * 12), (30, 30, 40), "SmoothPlastic",
                   rot=(0, syaw + 180, 0), collide=False,
                   text=dict(face="Front", text="%d) %s\n%s" % (k, name, SECTIONS[k][1]), color=(255, 255, 255), bg=(30, 40, 60),
                             bg_t=0.0))


# ---- v31 landmarks: one or two giant, readable set pieces per room, placed beside the rails (never on them)
LANDMARKS = []   # (key, label, x, z) for the build report


def _yaw_to(x, z, tx, tz):
    """rotation (degrees) for a part whose Front face should look at (tx, tz)"""
    return math.degrees(math.atan2(-(tx - x), -(tz - z)))


def landmark(clear, seg, frac, dist, r, fn, label):
    """put fn(x, z, ty) beside the track at fraction `frac` of the section, `dist` studs to one side, with a label
    board facing the rails. Tries both sides and a few distances so it never overlaps the track."""
    p = seg[min(len(seg) - 1, int(len(seg) * frac))]
    x, y, z, yaw = p[:4]
    rx, rz = math.cos(math.radians(yaw)), -math.sin(math.radians(yaw))
    for d in (dist, dist + 8, dist + 16, dist - 6, dist + 24):
        for s_ in (1, -1):
            lx, lz = x + rx * s_ * d, z + rz * s_ * d
            if clear.ok(lx, lz, r):
                fn(lx, lz, y)
                bx, bz = x + rx * s_ * 12, z + rz * s_ * 12
                G.part("LandmarkLabel", (24, 3.6, 0.4), (bx, y + 12, bz), (24, 28, 40), "SmoothPlastic",
                       rot=(0, _yaw_to(bx, bz, x, z), 0), collide=False, shadow=False,
                       text=dict(face="Front", text=label, color=(255, 255, 255), bg=(24, 28, 40), bg_t=0.1))
                LANDMARKS.append((fn.__name__, label, lx, lz))
                return True
    LANDMARKS.append((fn.__name__, "NOT PLACED", x, z))
    return False


def _lm_microscope(x, z, ty):
    Y = ISLAND_Y
    W, K = (238, 240, 244), (40, 44, 52)
    box("ScopeBase", (30, 5, 22), (x, Y + 2.5, z), W, "SmoothPlastic", collide=False)
    box("ScopePillar", (7, ty - Y + 20, 7), (x, (Y + ty + 20) / 2, z + 7), W, "SmoothPlastic", collide=False)
    box("ScopeStage", (22, 2, 18), (x, ty - 6, z - 2), K, "Metal", collide=False)
    ball("ScopeLamp", x, ty - 12, z - 2, 5, (255, 250, 200), "Neon", collide=False, shadow=False)
    box("ScopeArm", (7, 7, 20), (x, ty + 22, z + 1), W, "SmoothPlastic", collide=False)
    G.part("ScopeTube", (26, 7, 7), (x, ty + 14, z - 6), K, "Metal", shape="Cylinder", rot=(0, 0, 90), collide=False)
    G.part("ScopeEyepiece", (10, 4.4, 4.4), (x, ty + 30, z - 8), K, "Metal", shape="Cylinder", rot=(0, 90, 70), collide=False)
    for q, c in enumerate(((220, 60, 60), (60, 160, 220), (240, 200, 60))):
        G.part("ScopeObjective", (6, 2.4, 2.4), (x - 3 + q * 3, ty - 1, z - 6), c, "Metal", shape="Cylinder",
               rot=(0, 0, 90), collide=False)
    G.part("ScopeSlide", (8, 0.4, 3), (x, ty - 4.8, z - 2), (190, 230, 255), "Glass", transp=0.3, collide=False)


def _lm_petri(x, z, ty):
    Y = ISLAND_Y
    h = ty - Y - 6
    vcyl("PetriStand", x, Y, Y + h, z, 10, (200, 204, 210), "Metal", collide=False)
    disc("PetriDish", x, Y + h, z, 64, 3, (200, 230, 245), "Glass", transp=0.45, collide=False)
    disc("Agar", x, Y + h + 0.6, z, 60, 1.6, (236, 214, 140), "SmoothPlastic", collide=False)
    for q in range(9):
        a = q * 0.7
        rr = 8 + (q % 4) * 5
        disc("BigColony", x + rr * math.cos(a), Y + h + 1.6, z + rr * math.sin(a), 6 + (q % 3) * 3, 0.8,
             [(250, 245, 220), (240, 190, 110), (220, 140, 170)][q % 3], "SmoothPlastic", collide=False)
    # a rod bacterium hovering over the dish, flagella trailing
    by = Y + h + 18
    G.part("RodBody", (30, 9, 9), (x, by, z), (120, 200, 120), "SmoothPlastic", shape="Cylinder", collide=False)
    for s_ in (-1, 1):
        ball("RodCap", x + s_ * 15, by, z, 9, (120, 200, 120), "SmoothPlastic", collide=False)
    for q in range(4):
        box("Flagellum", (12, 0.5, 0.5), (x - 24 - q * 1.5, by - 3 + q * 2, z + (q - 1.5) * 2), (180, 255, 180), "Neon",
            rot=(0, 0, (-1) ** q * 15), collide=False, shadow=False)


def _lm_enzyme(x, z, ty):
    Y = ISLAND_Y
    cy = ty + 6
    vcyl("EnzymeStem", x, Y, cy - 14, z, 3, (90, 80, 120), "Metal", collide=False)
    ball("Enzyme", x, cy, z, 30, (150, 90, 210), "SmoothPlastic", collide=False)
    ball("ActiveSite", x, cy + 4, z - 12, 13, (60, 30, 90), "SmoothPlastic", collide=False)
    ball("Substrate", x, cy + 4, z - 17, 9, (255, 170, 60), "Neon", collide=False, shadow=False)
    for q in range(3):   # products leaving
        ball("Product", x + 10 + q * 6, cy + 14 + q * 5, z - 16, 4, (255, 210, 120), "SmoothPlastic", collide=False)


def _lm_krebs(x, z, ty):
    Y = ISLAND_Y
    cy = ty + 8
    R = 22
    vcyl("RingPost", x, Y, cy - R, z, 3, (90, 80, 120), "Metal", collide=False)
    cols = [(255, 120, 120), (255, 180, 90), (250, 230, 90), (140, 220, 110), (90, 200, 220), (110, 140, 255),
            (180, 120, 255), (240, 120, 210)]
    prev = None
    for q in range(9):
        a = q * math.pi / 4
        px, py = x + R * math.cos(a), cy + R * math.sin(a)
        if q < 8:
            ball("KrebsStep", px, py, z, 7, cols[q], "Neon", collide=False, shadow=False)
        if prev:
            mx, my = (px + prev[0]) / 2, (py + prev[1]) / 2
            ang = math.degrees(math.atan2(py - prev[1], px - prev[0]))
            box("KrebsLink", (math.hypot(px - prev[0], py - prev[1]), 1, 1), (mx, my, z), (230, 230, 240), "SmoothPlastic",
                rot=(0, 0, ang), collide=False)
        prev = (px, py)
    ball("ATPCore", x, cy, z, 8, (255, 220, 80), "Neon", collide=False, shadow=False)


def _lm_whale(x, z, ty):
    Y = ISLAND_Y
    cy = ty + 6
    BONE = (236, 230, 214)
    for q in range(-1, 2):
        vcyl("WhaleStand", x + q * 30, Y, cy - 6, z, 2, (90, 90, 96), "Metal", collide=False)
    box("WhaleSkull", (16, 8, 10), (x - 44, cy - 1, z), BONE, "SmoothPlastic", collide=False)
    box("WhaleJaw", (18, 2, 9), (x - 45, cy - 6, z), BONE, "SmoothPlastic", rot=(0, 0, -8), collide=False)
    for q in range(16):
        vx = x - 34 + q * 5
        vy = cy + 2 * math.sin(q / 15 * math.pi)
        ball("Vertebra", vx, vy, z, 3.4 - q * 0.1, BONE, "SmoothPlastic", collide=False)
        if 1 <= q <= 9:
            L = 12 - abs(q - 5) * 0.9
            for s_ in (-1, 1):
                box("Rib", (1, L, 1), (vx, vy - L / 2 + 1, z + s_ * 3.5), BONE, "SmoothPlastic", rot=(s_ * 22, 0, 0),
                    collide=False)
    box("WhaleTail", (2, 1, 18), (x + 47, cy + 2, z), BONE, "SmoothPlastic", collide=False)


def _lm_heart(x, z, ty):
    Y = ISLAND_Y
    cy = ty + 4
    RED, DARK = (200, 40, 50), (130, 20, 30)
    vcyl("HeartStand", x, Y, cy - 10, z, 3, (90, 90, 96), "Metal", collide=False)
    for s_ in (-1, 1):
        ball("HeartLobe", x + s_ * 5, cy + 3, z, 14, RED, "SmoothPlastic", collide=False)
    G.part("HeartTip", (10, 14, 10), (x, cy - 5, z), RED, "SmoothPlastic", shape="Ball", collide=False)
    G.part("Aorta", (12, 4, 4), (x - 2, cy + 12, z), DARK, "SmoothPlastic", shape="Cylinder", rot=(0, 0, 80), collide=False)
    G.part("Vessel", (10, 3, 3), (x + 5, cy + 11, z), (60, 90, 200), "SmoothPlastic", shape="Cylinder", rot=(0, 0, 100),
           collide=False)


def _lm_flower(x, z, ty):
    Y = ISLAND_Y
    top = ty + 16
    vcyl("GiantStem", x, Y, top, z, 4, (70, 150, 60), "SmoothPlastic", collide=False)
    for s_ in (-1, 1):
        box("StemLeaf", (16, 1, 7), (x + s_ * 8, top - 30 + s_ * 6, z), (80, 170, 70), "Grass", rot=(0, 0, s_ * 25),
            collide=False)
    for q in range(8):
        a = q * math.pi / 4
        box("Petal", (13, 1.2, 6), (x + 9 * math.cos(a), top + 1.5, z + 9 * math.sin(a)), (250, 120, 180), "SmoothPlastic",
            rot=(0, -math.degrees(a), 18), collide=False)
    ball("FlowerCentre", x, top + 2, z, 8, (250, 210, 60), "SmoothPlastic", collide=False)
    for q in range(6):   # pollen
        ball("Pollen", x - 5 + (q * 37 % 11), top + 6 + q * 2, z - 5 + (q * 53 % 11), 1.2, (255, 230, 90), "Neon",
             collide=False, shadow=False)


def _lm_roots(x, z, ty):
    Y = ISLAND_Y
    soil = ty - 10
    box("SoilColumn", (22, soil - Y, 22), (x, (Y + soil) / 2, z), (150, 110, 70), "Glass", transp=0.45, collide=False)
    box("SoilTop", (22, 1, 22), (x, soil, z), (110, 80, 50), "Ground", collide=False)
    for q in range(7):
        a = q * 2 * math.pi / 7
        L = 14 + (q % 3) * 5
        box("Root", (1.2, L, 1.2), (x + 3 * math.cos(a), soil - L / 2, z + 3 * math.sin(a)), (230, 210, 170), "SmoothPlastic",
            rot=(25 * math.sin(a), 0, 25 * math.cos(a)), collide=False)
    vcyl("Sapling", x, soil, soil + 14, z, 2, (90, 160, 70), "SmoothPlastic", collide=False)
    ball("SaplingCrown", x, soil + 17, z, 10, (100, 180, 80), "Grass", collide=False)


def _lm_translation(x, z, ty):
    Y = ISLAND_Y
    cy = ty + 8
    vcyl("RiboStand", x, Y, cy - 10, z, 3, (60, 70, 100), "Metal", collide=False)
    ball("RiboLarge", x, cy, z, 18, (110, 140, 220), "SmoothPlastic", collide=False)
    ball("RiboSmall", x, cy - 9, z, 12, (160, 190, 250), "SmoothPlastic", collide=False)
    cols = {"A": (240, 90, 90), "U": (240, 200, 70), "G": (90, 200, 110), "C": (90, 150, 240)}
    for q, ch in enumerate("AUGGCUUACGGA"):   # mRNA threading through the small subunit
        ball("mRNA", x - 26 + q * 4.4, cy - 11 + math.sin(q * 0.8) * 1.2, z, 2.6, cols[ch], "Neon", collide=False, shadow=False)
    for q in range(10):            # the protein chain growing out of the top
        a = q * 0.9
        ball("AminoAcid", x + 4 * math.cos(a), cy + 10 + q * 2.4, z + 4 * math.sin(a), 3.2,
             [(255, 140, 90), (120, 220, 160), (200, 140, 255)][q % 3], "SmoothPlastic", collide=False)


def _lm_fingerprint(x, z, ty):
    Y = ISLAND_Y
    cy = ty + 6
    box("PrintPanel", (36, 40, 2), (x, cy, z), (20, 22, 30), "SmoothPlastic", collide=False)
    vcyl("PrintStand", x, Y, cy - 20, z, 3, (70, 70, 76), "Metal", collide=False)
    for ring in range(5):
        rx_, ry_ = 4 + ring * 3, 6 + ring * 3.6
        n = 10 + ring * 2
        for q in range(n):
            a = q * 2 * math.pi / n
            if ring >= 3 and 4.2 < a < 5.2:
                continue   # the open "loop" pattern
            for s_ in (-1, 1):   # both faces of the panel
                box("Ridge", (1.4, 0.5, 0.6), (x + rx_ * math.cos(a), cy + ry_ * math.sin(a), z + s_ * 1.2), (255, 214, 60),
                    "Neon", rot=(0, 0, math.degrees(a) + 90), collide=False, shadow=False)


def _lm_evidence_lab(x, z, ty):
    Y = ISLAND_Y
    deck = ty - 8
    vcyl("LabStand", x, Y, deck, z, 6, (70, 70, 76), "Metal", collide=False)
    disc("LabDeck", x, deck, z, 34, 1.4, (50, 52, 60), "Slate", collide=False)
    box("Analyser", (12, 9, 8), (x - 6, deck + 5, z), (220, 224, 230), "SmoothPlastic", collide=False)
    for s_ in (-1, 1):
        box("AnalyserScreen", (8, 4, 0.3), (x - 6, deck + 7, z + s_ * 4.2), (60, 220, 160), "Neon", collide=False, shadow=False)
    for q in range(5):     # sample tubes in a rack
        vcyl("SampleTube", x + 5 + q * 2.4, deck + 1.5, deck + 8, z + 2, 1.6, (210, 230, 245), "Glass", transp=0.3,
             collide=False)
        vcyl("SampleLiquid", x + 5 + q * 2.4, deck + 1.6, deck + 4.5, z + 2, 1.2,
             [(200, 50, 60), (240, 220, 90), (90, 160, 230)][q % 3], "SmoothPlastic", collide=False)
    for q in range(3):     # numbered evidence markers
        box("EvidenceMarker", (2.4, 2.6, 2.4), (x - 10 + q * 7, deck + 1.4, z + 10), (250, 210, 40), "SmoothPlastic",
            collide=False)


def _lm_pivot(x, z, ty):
    Y = ISLAND_Y
    h = Y + 16
    vcyl("PivotTower", x, Y, h + 4, z, 4, (200, 204, 210), "Metal", collide=False)
    box("PivotTruss", (80, 2, 2), (x + 40, h, z), (190, 196, 204), "Metal", collide=False)
    for q in range(1, 4):
        tx = x + q * 20
        for s_ in (-1, 1):
            box("PivotLeg", (1, 17, 1), (tx, Y + 8, z + s_ * 3), (170, 176, 184), "Metal", rot=(s_ * 10, 0, 0), collide=False)
        G.part("PivotWheel", (1.2, 5, 5), (tx, Y + 2.5, z), (40, 40, 44), "SmoothPlastic", shape="Cylinder", collide=False)
    for q in range(12):
        ball("Spray", x + 6 + q * 6.4, h - 3, z, 1.6, (120, 200, 255), "Neon", collide=False, shadow=False, transp=0.3)


def _lm_silo_tractor(x, z, ty):
    Y = ISLAND_Y
    vcyl("Silo", x, Y, Y + 46, z, 16, (220, 220, 214), "Metal", collide=False)
    ball("SiloDome", x, Y + 46, z, 16, (180, 60, 50), "Metal", collide=False)
    tx = x + 18
    box("TractorBody", (12, 5, 6), (tx, Y + 5, z), (200, 50, 40), "SmoothPlastic", collide=False)
    box("TractorCab", (5, 6, 5.4), (tx + 2, Y + 10.5, z), (180, 220, 240), "Glass", transp=0.3, collide=False)
    for (dx_, d_) in ((-3.5, 8), (4.5, 5)):
        for s_ in (-1, 1):
            G.part("TractorWheel", (2, d_, d_), (tx + dx_, Y + d_ / 2, z + s_ * 3.6), (30, 30, 34), "SmoothPlastic",
                   shape="Cylinder", rot=(0, 90, 0), collide=False)


def _lm_pcr(x, z, ty):
    Y = ISLAND_Y
    deck = ty - 10
    vcyl("PCRStand", x, Y, deck, z, 6, (90, 100, 110), "Metal", collide=False)
    box("PCRBody", (28, 12, 20), (x, deck + 6, z), (232, 236, 240), "SmoothPlastic", collide=False)
    box("PCRLid", (28, 2, 20), (x, deck + 18, z + 8), (200, 206, 214), "SmoothPlastic", rot=(-40, 0, 0), collide=False)
    for i in range(6):
        for j in range(4):
            vcyl("PCRWell", x - 10 + i * 4, deck + 12, deck + 13, z - 6 + j * 4, 2,
                 (80, 220, 255) if (i + j) % 2 else (255, 120, 200), "Neon", collide=False, shadow=False)
    for s_ in (-1, 1):
        box("PCRScreen", (10, 4, 0.3), (x, deck + 7, z + s_ * 10.2), (60, 255, 160), "Neon", collide=False, shadow=False)


def _lm_crispr(x, z, ty):
    Y = ISLAND_Y
    _dna(x, Y, z, ty - Y + 30, r=6, ball_d=2.6)
    cy = ty + 6
    for s_ in (-1, 1):
        box("ScissorBlade", (26, 2, 3), (x, cy, z - 9), (60, 140, 255), "Metal", rot=(0, 0, s_ * 22), collide=False)
        ball("ScissorRing", x - 14, cy + s_ * 5, z - 9, 5, (60, 140, 255), "Neon", collide=False, shadow=False)
    ball("GuideRNA", x + 6, cy, z - 9, 3, (255, 120, 200), "Neon", collide=False, shadow=False)


# ---- scenery helpers (all non-colliding)
def _mito(x, y, z):
    yaw = rng.uniform(0, 180)
    ry = math.radians(yaw)
    ux, uz = math.cos(ry), -math.sin(ry)
    G.part("Mito", (34, 14, 14), (x, y, z), (250, 150, 80), "SmoothPlastic", shape="Cylinder", rot=(0, yaw, 0), collide=False)
    for e in (-1, 1):
        ball("MitoEnd", x + e * ux * 17, y, z + e * uz * 17, 14, (250, 150, 80), "SmoothPlastic", collide=False)


def _er(x, y, z):
    for q in range(4):
        box("ER", (18, 2, 6), (x, y + 10 + q * 5, z + q * 2), (120, 140, 230), "SmoothPlastic", rot=(0, q * 12, 0), collide=False)


def _leaf(x, y, z):
    h = rng.uniform(20, 45)
    vcyl("Stem", x, y, y + h, z, 1.4, (80, 130, 60), "Grass", collide=False)
    G.part("Leaf", (0.8, 22, 22), (x, y + h, z), (90, 180, 80), "Grass", shape="Cylinder", rot=(0, rng.uniform(0, 180), 80),
           collide=False)


def _flower(x, y, z):
    h = rng.uniform(8, 18)
    vcyl("Stem", x, y, y + h, z, 0.8, (80, 140, 60), "Grass", collide=False)
    col = rng.choice([(250, 120, 160), (250, 220, 70), (190, 120, 240), (255, 160, 80)])
    for q in range(6):
        a = q * math.pi / 3
        ball("Petal", x + math.cos(a) * 2.2, y + h, z + math.sin(a) * 2.2, 3, col, "SmoothPlastic", collide=False)
    ball("Core", x, y + h, z, 2.4, (250, 200, 60), "SmoothPlastic", collide=False)


def _chloroplast(x, y, z):
    G.part("Chloroplast", (40, 16, 16), (x, y, z), (90, 190, 90), "SmoothPlastic", shape="Cylinder", transp=0.2, collide=False)
    for q in range(5):
        for k in range(3):
            disc("Granum", x - 14 + q * 7, y - 2 + k * 1.6, z, 5, 1.2, (40, 120, 50), "SmoothPlastic", collide=False)


def _turtle(x, y, z):
    ball("Shell", x, y + 6, z, 22, (90, 150, 110), "SmoothPlastic", collide=False)
    disc("ShellRim", x, y + 4, z, 23, 1.6, (200, 180, 120), "SmoothPlastic", collide=False)
    ball("THead", x, y + 6, z + 14, 7, (150, 200, 140), "SmoothPlastic", collide=False)
    for dx, dz in ((-8, 7), (8, 7), (-8, -7), (8, -7)):
        box("Flipper", (6, 1.2, 3), (x + dx, y + 2, z + dz), (150, 200, 140), "SmoothPlastic", collide=False)


def _camel(x, y, z):
    box("CBody", (5, 5, 11), (x, y + 10, z), (200, 160, 100), "Fabric", collide=False)
    ball("Hump", x, y + 13.5, z, 5.5, (200, 160, 100), "Fabric", collide=False)
    for dx, dz in ((-1.8, -4), (1.8, -4), (-1.8, 4), (1.8, 4)):
        box("CLeg", (1.2, 8, 1.2), (x + dx, y + 4, z + dz), (190, 150, 92), "Fabric", collide=False)
    box("CNeck", (1.6, 6, 1.6), (x, y + 14, z + 6.5), (200, 160, 100), "Fabric", collide=False, rot=(-25, 0, 0))
    box("CHead", (2.2, 2.2, 4), (x, y + 17, z + 8.6), (200, 160, 100), "Fabric", collide=False)


def _falcon(x, y, z):
    ball("FBody", x, y, z, 3, (130, 100, 70), "SmoothPlastic", collide=False)
    for s_ in (-1, 1):
        box("Wing", (6, 0.3, 2.4), (x + s_ * 3.6, y + 0.4, z), (110, 84, 60), "SmoothPlastic", collide=False, rot=(0, 0, s_ * 12))


def _cactus(x, y, z):
    h = rng.uniform(8, 14)
    vcyl("Cactus", x, y, y + h, z, 2.4, (70, 140, 80), "Grass", collide=False)
    vcyl("Arm", x + 2, y + h * 0.5, y + h * 0.8, z, 1.4, (70, 140, 80), "Grass", collide=False)


def _bacterium(x, y, z):
    yaw = rng.uniform(0, 180)
    col = rng.choice([(240, 140, 170), (120, 200, 120), (250, 200, 90), (150, 130, 230)])
    G.part("Bacillus", (14, 5, 5), (x, y, z), col, "SmoothPlastic", shape="Cylinder", rot=(0, yaw, 0), collide=False)
    ry = math.radians(yaw)
    for e in (-1, 1):
        ball("BEnd", x + e * 7 * math.cos(ry), y, z - e * 7 * math.sin(ry), 5, col, "SmoothPlastic", collide=False)
    G.part("Flagellum", (8, 0.4, 0.4), (x - 11 * math.cos(ry), y, z + 11 * math.sin(ry)), (90, 90, 100), "SmoothPlastic",
           rot=(0, yaw, 10), collide=False)


def _virus(x, y, z):
    ball("Capsid", x, y, z, 7, (230, 90, 90), "SmoothPlastic", collide=False)
    for q in range(10):
        a, b_ = rng.uniform(0, 6.28), rng.uniform(-1.2, 1.2)
        ball("Spike", x + 4.4 * math.cos(a) * math.cos(b_), y + 4.4 * math.sin(b_), z + 4.4 * math.sin(a) * math.cos(b_), 1.4,
             (250, 220, 120), "Neon", collide=False, shadow=False)


def _molecule(x, y, z):
    cols = [(224, 70, 70), (244, 244, 244), (80, 82, 92), (70, 120, 230)]
    pts = [(x, y, z)]
    ball("Atom", x, y, z, 7, cols[2], "SmoothPlastic", collide=False)
    for q in range(4):
        a, b_ = q * 1.57 + 0.4, (q % 2) * 0.8 - 0.4
        px, py, pz = x + 9 * math.cos(a), y + 9 * math.sin(b_), z + 9 * math.sin(a)
        ball("Atom", px, py, pz, 5, cols[q % 4], "SmoothPlastic", collide=False)
        mx, my, mz = (x + px) / 2, (y + py) / 2, (z + pz) / 2
        dx, dy, dz = px - x, py - y, pz - z
        L = math.sqrt(dx * dx + dy * dy + dz * dz)
        box("Bond", (1, 1, L), (mx, my, mz), (200, 200, 206), "SmoothPlastic", collide=False,
            rot=(-math.degrees(math.atan2(dy, math.hypot(dx, dz))), math.degrees(math.atan2(dx, dz)), 0))


def _tube(x, y, z):
    h = rng.uniform(16, 26)
    vcyl("Tube", x, y, y + h, z, 5, (210, 235, 245), "Glass", transp=0.5, collide=False)
    vcyl("Liquid", x, y, y + h * 0.6, z, 4.2, rng.choice([(80, 255, 150), (255, 120, 190), (110, 190, 255)]), "Neon",
         collide=False, shadow=False)


def _dna(x, y, z, h, r=7.0, ball_d=2.4):
    step = ball_d
    for q in range(int(h / step)):
        a = q * 0.45
        yy = y + q * step
        ax, az = x + math.cos(a) * r, z + math.sin(a) * r
        bx, bz = x - math.cos(a) * r, z - math.sin(a) * r
        ball("A", ax, yy, az, ball_d, (255, 90, 170), "Neon", collide=False, shadow=False)
        ball("B", bx, yy, bz, ball_d, (60, 220, 255), "Neon", collide=False, shadow=False)
        if q % 2 == 0:
            box("Pair", (2 * r, ball_d * 0.25, ball_d * 0.25), (x, yy, z), (240, 240, 240), "SmoothPlastic", collide=False,
                rot=(0, -math.degrees(a), 0))


def _palm(x, y, z):
    h = rng.uniform(14, 20)
    vcyl("PalmTrunk", x, y, y + h, z, 1.6, (150, 118, 82), "Wood", collide=False)
    for a in range(8):
        yaw = a * 45.0
        L = 8.0
        dx = math.sin(math.radians(yaw)) * (L / 2) * 0.9
        dz = math.cos(math.radians(yaw)) * (L / 2) * 0.9
        box("Frond", (2.4, 0.25, L), (x + dx, y + h - 1.6, z + dz), (82, 150, 78), "Grass", collide=False, rot=(26, yaw, 0))


def _windmill(x, y, z):
    vcyl("Tower", x, y, y + 40, z, 4, (240, 240, 236), "SmoothPlastic", collide=False)
    for q in range(3):
        box("Blade", (2, 24, 0.6), (x, y + 40, z + 2.5), (250, 250, 250), "SmoothPlastic", collide=False, rot=(0, 0, q * 120))


def _greenhouse(x, y, z):
    box("Greenhouse", (30, 14, 18), (x, y + 7, z), (200, 235, 220), "Glass", transp=0.5, collide=False)
    for q in range(4):
        rect("Bed", x - 13 + q * 7, x - 9 + q * 7, y, y + 2, z - 7, z + 7, (90, 160, 80), "Grass", collide=False)


def _tape(x, y, z):
    for s_ in (-1, 1):
        vcyl("Cone", x + s_ * 7, y, y + 3, z, 1.4, (250, 120, 40), "SmoothPlastic", collide=False)
    box("Tape", (14, 1, 0.2), (x, y + 2.6, z), (250, 214, 50), "SmoothPlastic", collide=False,
        text=dict(face="Front", text="CRIME SCENE", color=(20, 20, 20), bg=(250, 214, 50), bg_t=0.0))


def _print(x, y, z):
    for q, d in enumerate((20, 15, 10, 5)):
        G.part("Print", (0.4 + q * 0.1, d, d), (x, y + 14, z + q * 0.12), (60, 220, 255) if q % 2 == 0 else (30, 40, 70),
               "Neon" if q % 2 == 0 else "SmoothPlastic", shape="Cylinder", rot=(0, 90, 0), collide=False, shadow=False)


def _magnifier(x, y, z):
    G.part("Lens", (1, 14, 14), (x, y + 20, z), (200, 230, 255), "Glass", shape="Cylinder", rot=(0, 90, 0), transp=0.5,
           collide=False)
    G.part("LensRim", (1.5, 15, 15), (x, y + 20, z), (40, 40, 46), "Metal", shape="Cylinder", rot=(0, 90, 0), transp=0.0,
           collide=False)
    box("Handle", (2, 12, 2), (x, y + 8, z), (90, 60, 40), "Wood", collide=False)


def _bioreactor(x, y, z):
    vcyl("Tank", x, y, y + 22, z, 9, (220, 226, 232), "Metal", collide=False)
    vcyl("TankGlow", x, y + 6, y + 18, z, 9.3, (80, 255, 150), "Neon", transp=0.5, collide=False, shadow=False)
    ball("TankTop", x, y + 22, z, 9, (220, 226, 232), "Metal", collide=False)


def _jelly(x, y, z):
    ball("Bell", x, y, z, 8, (120, 255, 160), "Neon", transp=0.3, collide=False, shadow=False)
    for q in range(5):
        a = q * 1.25
        box("Tentacle", (0.3, 8, 0.3), (x + math.cos(a) * 2.4, y - 6, z + math.sin(a) * 2.4), (120, 255, 160), "Neon",
            transp=0.4, collide=False, shadow=False)


# ====================================================================== stations
def stations(t):
    sx, sy, sz, syaw = t.pts[0][:4]
    with G.Group("CartStation"):
        rect("StationDeck", sx - 30, sx + 30, sy - 2.4, sy - 1.4, sz - 34, sz + 14, (236, 226, 208), "WoodPlanks")
        for zz in (sz - 34, sz + 14):
            rect("DeckEdge", sx - 30, sx + 30, sy - 1.4, sy - 1.3, zz - 0.4, zz + 0.4, (240, 110, 200), "Neon", collide=False)
        G.part("CartStart", (8, 0.4, 8), (sx - 9, sy - 1.2, sz - 4), (240, 110, 200), "Neon", transp=0.1, shadow=False)
        sign("CartStartSign", "🚆 دوس هنا عشان تركب القطار\nبعدها اضغط ▶ انطلاق مرة وحدة واستمتع", (sx - 9, sy + 6, sz - 8.4), (16, 5, 0.4), "Back",
             bg=(120, 40, 110))
        sign("CartTitle", "🚆 قطار التخصصات الثمانية  •  BSC Science Express", (sx, sy + 16, sz - 33.4), (56, 5, 0.6),
             "Back", bg=(80, 40, 130))
        A.logo_board(sx + 22, sy + 30, sz - 33.0, R=1.5, nx=0.0, nz=1.0)
        G.part("CartSpawnPoint", (6, 1, 6), (sx - 9, sy - 1.2, sz - 22), (0, 0, 0), "SmoothPlastic", transp=1, collide=False)
        G.part("Portal|Island", (0.6, 12, 10), (sx - 29.4, sy + 4.6, sz - 18), (120, 255, 200), "Neon", transp=0.45, collide=False,
               shadow=False)
        sign("BackHQ", "↩ الجزيرة", (sx - 29.2, sy + 12.4, sz - 18), (0.4, 2.4, 10), "Right", bg=(24, 80, 56))
        cart_model(sx + 12, sy - 1.4, sz - 6)
        cart_car_model(sx + 22, sy - 1.4, sz - 6)   # template for the trailing cars (cloned locally by CartRide.client)
        rect("Canopy", sx - 30, sx + 30, sy + 20, sy + 21, sz - 34, sz - 10, (120, 64, 176), "SmoothPlastic", transp=0.1)
        for xx in (sx - 28, sx + 28):
            for zz in (sz - 32, sz - 12):
                vcyl("CanopyPost", xx, sy - 1.4, sy + 20, zz, 1.2, (90, 60, 140), "SmoothPlastic", collide=False)
    ex, ey, ez, eyaw = t.pts[-1][:4]
    fx, fz = math.sin(math.radians(eyaw)), math.cos(math.radians(eyaw))
    rx, rz = math.cos(math.radians(eyaw)), -math.sin(math.radians(eyaw))
    with G.Group("CartFinish"):
        for s_ in (-1, 1):
            vcyl("ArchPost", ex - fx * 10 + rx * s_ * 9, ey - 4, ey + 20, ez - fz * 10 + rz * s_ * 9, 2.4, (240, 110, 200), "Neon",
                 collide=False)
        A.logo_board(ex - fx * 10, ey + 34, ez - fz * 10, R=1.4, nx=-fx, nz=-fz)
        cx, cz = ex + fx * 18, ez + fz * 18
        rect("FinishDeck", cx - 18, cx + 18, ey - 2.4, ey - 1.4, cz - 18, cz + 18, (236, 226, 208), "WoodPlanks")
        G.part("Portal|Island", (10, 12, 0.6), (cx, ey + 4.6, cz + fz * 14), (120, 255, 200), "Neon", transp=0.45, collide=False,
               shadow=False, rot=(0, eyaw, 0))
        G.part("CartFinishPoint", (6, 1, 6), (cx, ey - 1.2, cz), (0, 0, 0), "SmoothPlastic", transp=1, collide=False)


# ====================================================================== v30: the enclosed rail hall
# One huge indoor building around the whole ride: every section becomes its own room (floor, walls, ceiling, light),
# rooms are separated by partition walls and the track passes between them through lit tunnels. The main station
# gets a tall glass-roofed hall. Room z-boundaries are written to Shared/CartRooms.luau for the client lighting.
ROOM_STYLE = [
    # floor colour/material, wall colour, ceiling colour, light colour (same order as SECTION_KEYS)
    ((210, 228, 236), "SmoothPlastic", (220, 236, 244), (200, 226, 240), (220, 245, 255)),  # micro: clean lab
    ((200, 196, 220), "Marble", (190, 170, 220), (120, 90, 170), (240, 210, 255)),        # biochem
    ((214, 188, 132), "Sand", (230, 200, 150), (170, 200, 230), (255, 236, 200)),         # animal
    ((86, 150, 80), "Grass", (150, 200, 140), (120, 180, 220), (255, 250, 220)),          # plant
    ((24, 32, 60), "SmoothPlastic", (40, 60, 110), (14, 20, 44), (150, 200, 255)),        # molecular
    ((78, 80, 92), "Slate", (104, 106, 120), (46, 48, 60), (235, 225, 255)),               # forensic (v31: brighter)
    ((140, 104, 66), "Ground", (210, 190, 140), (150, 200, 230), (255, 240, 190)),        # agri
    ((226, 236, 240), "SmoothPlastic", (200, 236, 240), (40, 90, 100), (150, 255, 240)),  # biotech
]
HALL_FLOOR, HALL_CEIL = -86.0, 112.0


def _crossings(t, zc):
    """x, y and heading of every track crossing of the line z = zc"""
    out = []
    for a, b in zip(t.pts, t.pts[1:]):
        if (a[2] - zc) * (b[2] - zc) < 0:
            s = (zc - a[2]) / (b[2] - a[2])
            out.append((a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s, a[3]))
    return out


def cart_hall(t):
    b = section_bounds(t)
    xs = [p[0] for p in t.pts]
    zs = [p[2] for p in t.pts]
    X0, X1 = min(xs) - 60, max(xs) + 60
    Z0, Z1 = min(zs) - 60, max(zs) + 70
    # room boundaries: halfway between the end of one section and the start of the next (rows run along x)
    cuts = []
    for k in range(0, len(b) - 1):   # b[0] is the cell section (the station is not a section)
        z_this = sum(p[2] for p in b[k][4]) / len(b[k][4])
        z_next = sum(p[2] for p in b[k + 1][4]) / len(b[k + 1][4])
        cuts.append((z_this + z_next) / 2)
    bands = [Z1] + cuts + [Z0]   # descending z
    with G.Group("CartHall"):
        H = HALL_CEIL - HALL_FLOOR
        # outer shell (one part per face; ceilings/floors split per room below)
        rect("HallWallW", X0 - 2, X0, HALL_FLOOR, HALL_CEIL, Z0, Z1, (50, 40, 70))
        rect("HallWallE", X1, X1 + 2, HALL_FLOOR, HALL_CEIL, Z0, Z1, (50, 40, 70))
        rect("HallWallS", X0, X1, HALL_FLOOR, HALL_CEIL, Z1, Z1 + 2, (50, 40, 70))
        rect("HallWallN", X0, X1, HALL_FLOOR, HALL_CEIL, Z0 - 2, Z0, (50, 40, 70))
        rooms = []
        for i in range(len(bands) - 1):
            k = min(i, len(ROOM_STYLE) - 1)   # first band = station + the first specialty
            fcol, fmat, wcol, ccol, lcol = ROOM_STYLE[k]
            za, zb = bands[i + 1], bands[i]
            rooms.append(zb)
            rect("RoomFloor", X0, X1, HALL_FLOOR - 2, HALL_FLOOR, za, zb, fcol, fmat)
            rect("RoomCeiling", X0, X1, HALL_CEIL, HALL_CEIL + 2, za, zb, ccol, "SmoothPlastic")
            for x0_, x1_ in ((X0, X0 + 0.6), (X1 - 0.6, X1)):
                rect("RoomWallSkin", x0_, x1_, HALL_FLOOR, HALL_CEIL, za, zb, wcol, "SmoothPlastic", collide=False)
            # a band of light along each side wall + two real lights per room (kept few for performance)
            for x0_, x1_ in ((X0 + 0.6, X0 + 1.4), (X1 - 1.4, X1 - 0.6)):
                rect("RoomGlow", x0_, x1_, HALL_CEIL - 22, HALL_CEIL - 20, za + 4, zb - 4, lcol, "Neon", collide=False, shadow=False)
            for q in (0.33, 0.66):
                box("RoomLight", (6, 1, 6), (X0 + (X1 - X0) * q, HALL_CEIL - 1, (za + zb) / 2), lcol, "Neon", collide=False,
                    shadow=False, light=(1.6, 60, lcol))
            # ceiling "sky" panels give each room a readable roof pattern
            for q in range(4):
                xm = X0 + (X1 - X0) * (q + 0.5) / 4
                rect("CeilingPanel", xm - 40, xm + 40, HALL_CEIL - 0.4, HALL_CEIL, za + 10, zb - 10,
                     tuple(min(255, c + 30) for c in ccol), "Neon" if SECTION_KEYS[k] in ("molecular", "forensic", "biotech") else "SmoothPlastic", transp=0.3,
                     collide=False, shadow=False)
        # partitions between rooms are tinted glass "membranes" on metal ribs (bio-domes): every room keeps its own
        # identity, but the hall reads as one huge connected world instead of a row of closed corridors.
        # The track passes between domes through solid lit tunnels.
        def membrane(x0, x1, y0, y1, zc, col):
            if x1 - x0 > 0.5 and y1 - y0 > 0.5:
                rect("Membrane", x0, x1, y0, y1, zc - 0.4, zc + 0.4, col, "Glass", transp=0.62, shadow=False)
        for i, zc in enumerate(cuts):
            a = ROOM_STYLE[min(i, len(ROOM_STYLE) - 1)][2]
            c = ROOM_STYLE[min(i + 1, len(ROOM_STYLE) - 1)][2]
            col = tuple((p + q) // 2 for p, q in zip(a, c))
            holes = sorted(_crossings(t, zc), key=lambda h: h[0])
            x = X0
            for (cx, cy, cyaw) in holes:
                w = 16.0
                membrane(x, cx - w, HALL_FLOOR, HALL_CEIL, zc, col)
                membrane(cx - w, cx + w, cy + 22, HALL_CEIL, zc, col)
                membrane(cx - w, cx + w, HALL_FLOOR, cy - 14, zc, col)
                for dz in (-12, -4, 4, 12):
                    for s_ in (-1, 1):
                        box("TunnelWall", (2, 34, 8), (cx + s_ * (w - 1), cy + 4, zc + dz), (54, 46, 74), "SmoothPlastic",
                            collide=False)
                    box("TunnelRoof", (2 * w, 2, 8), (cx, cy + 21, zc + dz), (54, 46, 74), "SmoothPlastic", collide=False)
                    box("TunnelRing", (2 * w - 3, 0.4, 0.6), (cx, cy + 19.6, zc + dz + 3.6), (255, 220, 140), "Neon",
                        collide=False, shadow=False)
                x = cx + w
            membrane(x, X1, HALL_FLOOR, HALL_CEIL, zc, col)
            # ribs: vertical every ~70 studs + two horizontal bands (the dome frame)
            xr = X0 + 35
            while xr < X1 - 10:
                if all(abs(xr - h[0]) > 20 for h in holes):
                    rect("DomeRib", xr - 0.8, xr + 0.8, HALL_FLOOR, HALL_CEIL, zc - 0.9, zc + 0.9, (70, 74, 84), "Metal")
                xr += 70
            for yb in (HALL_FLOOR + (HALL_CEIL - HALL_FLOOR) * 0.33, HALL_FLOOR + (HALL_CEIL - HALL_FLOOR) * 0.66):
                rect("DomeBand", X0, X1, yb - 0.7, yb + 0.7, zc - 0.9, zc + 0.9, (70, 74, 84), "Metal", collide=False)
        # the main station hall over the start: tall glass roof on columns, departures board and clock
        sx, sy, sz = t.pts[0][:3]
        for xx in range(-36, 37, 18):
            for zz in (-40, 18):
                vcyl("StationColumn", sx + xx, sy - 2.4, sy + 44, sz + zz, 3.4, (230, 226, 216), "Marble")
        rect("StationRoofBeam", sx - 40, sx + 40, sy + 44, sy + 46, sz - 42, sz + 20, (200, 196, 186), "Concrete")
        rect("StationGlassRoof", sx - 38, sx + 38, sy + 46, sy + 46.6, sz - 40, sz + 18, (190, 220, 240), "Glass", transp=0.5,
             collide=False)
        sign("Departures", "🚆 المحطة الرئيسية | Grand Station\nالرحلة: 8 قاعات • مايكروبيولوجي ← البايوتكنولوجي",
             (sx, sy + 34, sz - 39.4), (44, 8, 0.6), "Back", color=(255, 220, 120), bg=(16, 18, 26))
        disc("StationClock", sx + 30, sy + 26, sz - 39.6, 9, 0.8, (250, 250, 246), "SmoothPlastic", collide=False)
    return rooms


def write_rooms_module(rooms, path):
    """world-space z boundaries of the rail-hall rooms (descending), for AreaAtmosphere"""
    oz = CART_OFFSET[2]
    with open(path, "w", encoding="utf-8") as f:
        f.write("-- Generated by tools/cartride.py: rail-hall rooms in ride order (room 1 = station + first specialty).\n")
        f.write("-- tops = world-z upper bound of each room (descending), zones = index into Shared/Zones for its look.\n")
        f.write("return {\n\ttops = { %s },\n" % ", ".join("%.1f" % (z + oz) for z in rooms))
        f.write("\tzones = { %s },\n}\n" % ", ".join(str(SECTION_ZONE[k]) for k in SECTION_KEYS))


ROOMS = []


def build():
    t = build_track()
    bad = check(t)
    with G.Group("CartRide"):
        draw_track(t)
        signs(t)
        scenery(t)
        stations(t)
        ROOMS[:] = cart_hall(t)
    missing = [lm for lm in LANDMARKS if lm[1] == "NOT PLACED"]
    print("rail hall: %d landmarks placed, %d not placed %s" % (len(LANDMARKS) - len(missing), len(missing),
                                                                  [m[0] for m in missing]))
    return len(t.pts), bad
