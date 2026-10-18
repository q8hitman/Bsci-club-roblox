p = "tools/genmap5.py"
s = open(p, encoding="utf-8").read()
a = s.index("    for s in (-1, 1):\n        box(\"PortalPost\"")
b = s.index("    box(\"Portal|Course\"")
b = s.index("\n", b) + 1
replacement = '''    # the challenge gates now live inside the building (Challenge Hall, ground floor)
    sign("ToHall", "قاعة التحديات داخل المبنى ←\\nChallenge Hall inside (G)", (40, 5, -200), (16, 4, 0.5), "Front",
         bg=(24, 80, 56))
    for s_ in (-1, 1):
        box("SignPost", (0.6, 3, 0.6), (40 + s_ * 7, 1.5, -200), (60, 64, 70), "SmoothPlastic", collide=False)
'''
s = s[:a] + replacement + s[b:]
open(p, "w", encoding="utf-8").write(s)
print("forecourt patched")
