p = "tools/genmap5.py"
s = open(p, encoding="utf-8").read()

s = s.replace("COURSE_OFFSET = (3000.0, 0.0, 0.0)",
              "COURSE_OFFSET = (3000.0, 0.0, 0.0)\nNB_SHIFT = 110.0   # north building sits this far north so the garden walk can wind", 1)

garden_fn = '''
def _catmull(pts, per=14):
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(per):
            t = k / per
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(pts[-1])
    return out


def winding_garden():
    """long meandering stone path between the two buildings, planted like the photos"""
    ctrl = [(-40, -30), (-62, 4), (-34, 30), (14, 40), (58, 58), (74, 84), (44, 108), (10, 118), (8, 130)]
    path = _catmull(ctrl, 12)
    for a, b in zip(path, path[1:]):
        dx, dz = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dz)
        if L < 0.1:
            continue
        yaw = math.degrees(math.atan2(dx, dz))
        mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        box("PathStone", (13, 0.5, L + 1.2), (mx, 0.2, mz), (152, 150, 146), "Slate", rot=(0, yaw, 0), collide=False)
        for s_ in (-1, 1):
            nx, nz = math.cos(math.radians(yaw)) * s_ * 6.8, -math.sin(math.radians(yaw)) * s_ * 6.8
            box("Curb", (0.9, 0.9, L + 1.0), (mx + nx, 0.4, mz + nz), (214, 208, 196), "Concrete", rot=(0, yaw, 0), collide=False)
    for i in range(0, len(path), 3):
        px, pz = path[i]
        if i + 1 < len(path):
            dx, dz = path[i + 1][0] - px, path[i + 1][1] - pz
        else:
            dx, dz = 0, 1
        L = math.hypot(dx, dz) or 1
        nx, nz = dz / L, -dx / L
        for s_ in (-1, 1):
            off = rng.uniform(10, 24)
            bx, bz = px + nx * s_ * off, pz + nz * s_ * off
            r = rng.random()
            if r < 0.30:
                tree(bx, bz, rng.uniform(0.9, 1.4))
            elif r < 0.55:
                for _ in range(3):
                    ball("Shrub", bx + rng.uniform(-3, 3), 1.6, bz + rng.uniform(-3, 3), rng.uniform(3, 5.5),
                         (rng.randint(66, 92), rng.randint(128, 160), rng.randint(70, 90)), "Grass", collide=False)
                for _ in range(4):
                    ball("Bloom", bx + rng.uniform(-3, 3), 3.4, bz + rng.uniform(-3, 3), 1.0,
                         [(170, 110, 200), (236, 120, 170), (250, 220, 90)][rng.randint(0, 2)], "SmoothPlastic", collide=False)
            elif r < 0.80:
                for _ in range(3):
                    gray = rng.randint(170, 205)
                    ball("Rock", bx + rng.uniform(-4, 4), 1.0, bz + rng.uniform(-4, 4), rng.uniform(2.5, 6.0),
                         (gray, gray, gray - 4), "Slate", collide=False)
                box("Gravel", (9, 0.15, 7), (bx, 0.2, bz), (200, 196, 188), "Pebble", collide=False)
            else:
                yaw = math.degrees(math.atan2(dx, dz)) + (90 if s_ > 0 else -90)
                box("BenchSeat", (7, 0.6, 2.2), (px + nx * s_ * 8.4, 1.9, pz + nz * s_ * 8.4), (150, 100, 62), "WoodPlanks",
                    rot=(0, yaw, 0), collide=False)
                box("BenchBack", (7, 1.8, 0.4), (px + nx * s_ * 9.4, 3.0, pz + nz * s_ * 9.4), (140, 94, 58), "WoodPlanks",
                    rot=(0, yaw, 0), collide=False)
                box("BenchBase", (6, 1.6, 1.4), (px + nx * s_ * 8.4, 0.8, pz + nz * s_ * 8.4), (46, 48, 54), "SmoothPlastic",
                    rot=(0, yaw, 0), collide=False)
        if i % 9 == 0:
            for s_ in (-1, 1):
                C3.lamp_post(px + nx * s_ * 8.0, 0, pz + nz * s_ * 8.0, 10)
    cx, cz = 92, 70
    for dx, dz in ((-16, -12), (16, -12), (-16, 12), (16, 12)):
        vcyl("Mast", cx + dx, 0, 30, cz + dz, 1.0, (130, 134, 140), "SmoothPlastic")
    box("SailA", (44, 0.5, 30), (cx - 2, 27, cz - 6), (250, 250, 247), "Fabric", collide=False, transp=0.05, rot=(16, 0, 9))
    box("SailB", (40, 0.5, 26), (cx + 6, 24, cz + 10), (244, 244, 241), "Fabric", collide=False, transp=0.05, rot=(-14, 0, -7))
    box("SailC", (30, 0.5, 22), (cx - 14, 21, cz + 2), (248, 248, 245), "Fabric", collide=False, transp=0.05, rot=(6, 0, -12))
    sign("SailSign", "ساحة الاستراحة\\nThe Sail Plaza", (cx, 3.2, cz + 24), (14, 2.6, 0.5), "Back", bg=(50, 70, 80))
    box("RedBlock", (60, 30, 26), (150, 15, 62), (178, 92, 62), "Brick")
    for q in range(24):
        box("Louver", (0.5, 26, 1.2), (119.4, 15, 50 + q * 1.1), (150, 66, 44), "SmoothPlastic", collide=False)
    box("GlassPav", (26, 22, 24), (-92, 11, 70), (170, 210, 216), "Glass", transp=0.45)
    for q in range(10):
        box("Slats", (0.5, 22, 1.0), (-78.6, 11, 60 + q * 2.4), TIMBER, "WoodPlanks", collide=False)
    sign("WalkSign", "الممشى بين الحرمين | The Garden Walk", (-40, 5, -26), (16, 3, 0.5), "Back", bg=(40, 90, 70))


'''
marker = "# ====================================================================== OUTDOORS"
assert marker in s
s = s.replace(marker, garden_fn + marker, 1)

a = s.index("    # garden: red path, stone path, trees, rocks, sail")
b = s.index("    # red first-floor bridge between the buildings (y 24)")
s = s[:a] + "    winding_garden()\n" + s[b:]

s = s.replace("    z0, z1 = -30.0, 20.0\n", "    z0, z1 = -30.0, 20.0 + NB_SHIFT\n", 1)
old = '''    for z in (-24, 14):
        for x in (-48, -32):
            vcyl("BridgeCol", x, 0, 23, z, 2.4, CREAM, "Concrete")'''
new = '''    for z in range(-24, int(z1), 36):
        for x in (-48, -32):
            vcyl("BridgeCol", x, 0, 23, z, 2.4, CREAM, "Concrete")
    for z in range(-20, int(z1), 16):
        box("BridgeLamp", (6, 0.3, 1.5), (-40, 35.2, z), WARM, "Neon", collide=False, shadow=False)'''
assert old in s
s = s.replace(old, new, 1)
s = s.replace("for z in range(int(z0), int(z1) + 1, 5):", "for z in range(int(z0), int(z1) + 1, 8):", 1)

s = s.replace('rect("Lawn", -140, 140, -1, 0.15, -30, 24, (104, 160, 92), "Grass")',
              'rect("Lawn", -160, 160, -1, 0.15, -30, 24 + NB_SHIFT + 6, (112, 164, 98), "Grass")')
s = s.replace('rect("EastLawn", 90, 150, -1, 0.15, -170, 160, (100, 156, 88), "Grass")',
              'rect("EastLawn", 90, 170, -1, 0.15, -170, 160 + NB_SHIFT, (100, 156, 88), "Grass")')
s = s.replace('rect("WestLawn", -150, -90, -1, 0.15, -170, 160, (100, 156, 88), "Grass")',
              'rect("WestLawn", -170, -90, -1, 0.15, -170, 160 + NB_SHIFT, (100, 156, 88), "Grass")')
s = s.replace('kiosk(115, 70, 20, 12, (70, 130, 80), "Caribou Coffee")',
              'kiosk(115, 70 + NB_SHIFT, 20, 12, (70, 130, 80), "Caribou Coffee")')
s = s.replace("        for z in (-60, 0, 60, 120):\n            tree(x, z, 1.1)",
              "        for z in (-60, 0, 60, 120, 180, 240):\n            tree(x, z, 1.1)")

old = '''        south_building()
        north_building()'''
new = '''        south_building()
        _off[2] = NB_SHIFT
        north_building()
        _off[2] = 0.0'''
assert old in s
s = s.replace(old, new, 1)
open(p, "w", encoding="utf-8").write(s)
print("patched garden")
