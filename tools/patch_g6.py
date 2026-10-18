p = "tools/genmap6.py"
s = open(p, encoding="utf-8").read()

# k_leaves: correct cylinder orientation
old = '''        disc("Leaf", x, c["y"] - 0.5, z, d, 0.7, (96, 190, 100), "Grass") if False else None
        box("Bounce|58", (d, 0.7, d), (x, c["y"] - 0.35, z), (104, 196, 104), "Grass", shape="Cylinder", rot=(0, 0, 90))'''
new = '''        box("Bounce|58", (0.7, d, d), (x, c["y"] - 0.35, z), (104, 196, 104), "Grass", shape="Cylinder", rot=(0, 0, 90))'''
assert old in s
s = s.replace(old, new, 1)

# k_helix: clean walk bookkeeping
a = s.index("def k_helix(c, th, t, k):")
b = s.index("def k_molecule(c, th, t, k):")
helix = '''def k_helix(c, th, t, k):
    R, w = 10.0, 5.5
    cx = c["x"]
    cz = c["z"] + c["sz"] / 2 + R + 2.0
    vcyl("Core", cx, M2.SEA, c["y"] + 18, cz, 1.6, (255, 255, 255), "Neon", collide=False, shadow=False)
    for i in range(7):
        a_ = math.radians(180 + i * 45)
        x, z = cx + R * math.sin(a_), cz + R * math.cos(a_)
        y = c["y"] + 2.0 * (i + 1)
        col, mat = th["main"] if i % 2 == 0 else th["alt"]
        disc("Rung", x, y - 0.5, z, w, 1, col, mat)
        disc("RungEdge", x, y + 0.02, z, w + 0.2, 0.12, th["edge"], "Neon", collide=False, shadow=False)
        M2.walk.append(("c", x, z, y, w, w))
    top = c["y"] + 14
    x_l, z_l = cx + R + 8.5, cz
    M2.slab(th, x_l, top, z_l, 10, 10)
    M2.walk.append(("brk",))
    M2.set_c(c, x_l, top, z_l, 10)


'''
s = s[:a] + helix + s[b:]
open(p, "w", encoding="utf-8").write(s)
print("ok")
