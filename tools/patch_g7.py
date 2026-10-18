p = "tools/genmap7.py"
s = open(p, encoding="utf-8").read()

start_fn = '''
def course_start():
    """bright start plaza for the obby (replaces the old dark hub room)"""
    with G.Group("CourseStart"):
        rect("StartDeck", -32, 32, -1, 0, -66, -8, (234, 230, 220), "Marble")
        for zz in (-66, -8):
            rect("DeckEdge", -32, 32, 0, 0.08, zz - 0.4, zz + 0.4, (90, 230, 160), "Neon", collide=False)
        for x in (-28, 28):
            for z in (-62, -12):
                vcyl("DeckLeg", x, -24, -1, z, 3, (226, 220, 206), "Concrete", collide=False)
        G.part("Checkpoint_0", (12, 1, 12), (0, 0.5, -26), (64, 140, 108), "SmoothPlastic",
               text=dict(face="Top", text="START", color=(255, 255, 255), bg=(36, 96, 74), bg_t=0.0))
        sign("StartTitle", "100 Level Parkour\\nابدأ من هنا ↑", (0, 13, -62), (30, 7, 0.6), "Back", bg=(24, 70, 48))
        names = "\\n".join("%d) %s" % (i + 1, M2.ZONE_NAMES[i][0]) for i in range(10))
        sign("ZoneList", names, (-31.4, 9, -40), (0.5, 15, 18), "Right", bg=(30, 40, 56))
        sign("Tips", "نصايح:\\n• السقوط يرجّعك لآخر نقطة\\n• كل 5 مراحل سؤال\\n• المنصات الشفافة تختفي وترجع",
             (31.4, 9, -40), (0.5, 12, 18), "Left", bg=(30, 40, 56))
        for s_ in (-1, 1):
            box("ExitPost", (1.2, 14, 1.2), (s_ * 7, 7, -57), (60, 64, 74), "SmoothPlastic", collide=False)
        G.part("Portal|Campus", (12.6, 12.5, 0.5), (0, 6.4, -57), (255, 190, 120), "Neon", transp=0.5, collide=False,
               shadow=False)
        sign("BackSign", "العودة لقاعة التحديات\\nBack to the College", (0, 15.6, -57.3), (15, 3.2, 0.5), "Back", bg=(110, 70, 30))
        for x in (-22, 22):
            C5.C3.planter(x, 0, -14, 10, 4)
            C5.C3.lamp_post(x, 0, -50, 10)


'''
marker = "# ====================================================================== campus additions"
assert marker in s
s = s.replace(marker, start_fn + marker, 1)

# use the new start plaza instead of the old hub
s = s.replace("    C3.build()\n", "    G.hub = course_start\n    C3.build()\n", 1)

# remove the old floating return portal lines from main
a = s.index('    C5._base_part("Portal|Campus"')
b = s.index("    gap, rise, bad, n = M2.validate()")
s = s[:a] + s[b:]

# smaller, tidier rules board in the Challenge Hall
s = s.replace('(x0 + 0.6, 9, (z0 + z1) / 2), (0.4, 6, 26), "Right", bg=(30, 40, 56))',
              '(x0 + 0.6, 8, (z0 + z1) / 2), (0.4, 3.6, 17), "Right", bg=(24, 70, 48))')
open(p, "w", encoding="utf-8").write(s)
print("ok")
