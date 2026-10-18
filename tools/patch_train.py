p = "tools/genmap8.py"
s = open(p, encoding="utf-8").read()

# lobby: drop the small train pad, point to the real station instead
a = s.index("    # cell train station (east side of the lobby)")
b = s.index("    # club banner over the lobby")
s = s[:a] + '''    # the Cell Train has its own station on the east lawn
    sign("TrainDirection", "🚋 محطة قطار الخلية ← اطلع من الباب الخلفي للحديقة الشرقية", (40, 9, -104.4), (26, 3, 0.4), "Front",
         bg=(110, 50, 150))
''' + s[b:]

# use the new station + cell world module
s = s.replace("import genmap as G  # noqa: E402\n", "import genmap as G  # noqa: E402\nimport celltrain  # noqa: E402\n", 1)
s = s.replace("        G7.building_details()\n", "        G7.building_details()\n        celltrain.train_station()\n", 1)
s = s.replace("    C5._off[0], C5._off[1], C5._off[2] = CELL_OFFSET\n    cell_world()\n",
              "    C5._off[0], C5._off[1], C5._off[2] = celltrain.CELL_OFFSET\n    celltrain.cell_world()\n", 1)
assert "celltrain.cell_world()" in s and "celltrain.train_station()" in s
open(p, "w", encoding="utf-8").write(s)
print("train hooked")
