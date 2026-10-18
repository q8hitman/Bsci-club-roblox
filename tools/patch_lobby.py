p = "tools/genmap5.py"
s = open(p, encoding="utf-8").read()


def rep(old, new):
    global s
    assert old in s, old[:60]
    s = s.replace(old, new, 1)


# escalators move to the sides so the lobby centre is free
rep("    escalator(-7, -140, -104, 0, Y_1)\n    escalator(7, -140, -104, 0, Y_1)\n",
    "    escalator(-48, -140, -104, 0, Y_1)\n    escalator(48, -140, -104, 0, Y_1)\n")
rep('    sign("EscLabel", "الدرج المتحرك  ↑  Escalators", (0, 15, -143), (24, 3.4, 0.4), "Back", bg=(40, 60, 70))\n',
    '    for ex in (-48, 48):\n        sign("EscLabel", "الدور الأول ↑", (ex, 15, -143), (10, 2.6, 0.4), "Back", bg=(40, 60, 70))\n')
# only the front pair of steel drums stays
rep("    for x in (-40, 40):\n        for z in (-150, -112):\n            steel_drum(x, z, 0, Y_2, 6.0)\n",
    "    for x in (-34, 34):\n        for z in (-152,):\n            steel_drum(x, z, 0, Y_2, 6.0)\n")
# info desk out of the centre
rep('    rect("InfoDesk", -10, 10, 0, 3.8, -122, -118, WHITE, "Marble")\n', "")
rep('    sign("Info", "الاستعلامات | Information", (0, 7, -120), (14, 2.4, 0.4), "Back", bg=(50, 60, 70))\n', "")
# players spawn inside the shared lobby
rep('_base_part("CampusSpawn", (10, 1, 10), (0, 0.5, -215)', '_base_part("CampusSpawn", (10, 1, 10), (0, 0.5, -151)')
open(p, "w", encoding="utf-8").write(s)

p3 = "tools/genmap3.py"
s3 = open(p3, encoding="utf-8").read()
old = "        for j in range(1, 11):\n            th = M.THEMES[j - 1]\n            g = c[\"y\"] - 24"
assert old in s3
s3 = s3.replace(old, "        for j in range(1, len(M.SEQ) + 1):\n            th = M.THEMES[j - 1]\n            g = c[\"y\"] - 24", 1)
open(p3, "w", encoding="utf-8").write(s3)
print("lobby + zone-count patched")
