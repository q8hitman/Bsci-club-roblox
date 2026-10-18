p = "tools/genmap6.py"
s = open(p, encoding="utf-8").read()

# helix: clockwise, 5 rungs, ends facing north so the path stays centred
a = s.index("def k_helix(c, th, t, k):")
b = s.index("def k_molecule(c, th, t, k):")
helix = '''def k_helix(c, th, t, k):
    R, w = 10.0, 5.5
    cx = c["x"]
    cz = c["z"] + c["sz"] / 2 + R + 2.0
    vcyl("Core", cx, M2.SEA, c["y"] + 16, cz, 1.6, (255, 255, 255), "Neon", collide=False, shadow=False)
    for i in range(5):
        a_ = math.radians(180 - i * 45)
        x, z = cx + R * math.sin(a_), cz + R * math.cos(a_)
        y = c["y"] + 2.2 * (i + 1)
        col, mat = th["main"] if i % 2 == 0 else th["alt"]
        disc("Rung", x, y - 0.5, z, w, 1, col, mat)
        disc("RungEdge", x, y + 0.02, z, w + 0.2, 0.12, th["edge"], "Neon", collide=False, shadow=False)
        M2.walk.append(("c", x, z, y, w, w))
    top = c["y"] + 11.0
    z_l = cz + R + 8.5
    M2.slab(th, cx, top, z_l, 10, 10)
    M2.walk.append(("brk",))
    M2.set_c(c, cx, top, z_l, 10)


'''
s = s[:a] + helix + s[b:]

old = '        x = M2.clampx(4.0 if i % 2 else -4.0)'
new = '        x = M2.clampx(c["x"] * 0.5 + (4.0 if i % 2 else -4.0))'
assert old in s
s = s.replace(old, new, 1)
open(p, "w", encoding="utf-8").write(s)
print("ok")
