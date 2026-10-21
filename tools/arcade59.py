"""v59 arcade lobby gateways (owner screenshot 9: cluttered lobby, Laser Escape impossible to find).

Every door out of the arcade lobby is now the same kind of gateway on one arc in front of the spawn, all facing the
lobby centre: club HQ, Micro Racers, Laser Escape (straight ahead), Puzzle Rooms, College of Science. The functional
part each gateway frames keeps its old name (Portal|HQ, RaceEntrance, LaserEntrance, Portal|Puzzle, Portal|Campus),
so the server scripts find them as before.
"""
import math

import genmap as G

AX, AY, AZ = -6000.0, 300.0, -6000.0
R = 37.0
WHITE = (236, 238, 242)
DARK = (24, 28, 40)

# key -> (angle from +z in degrees, colour, Arabic title, English title)
GATES = {
    "HQ": (-64, (90, 220, 170), "مقر النادي", "BSC HQ"),
    "Racers": (-32, (83, 232, 196), "سباق العالم المجهري", "MICRO RACERS"),
    "Laser": (0, (255, 90, 90), "هروب الليزر", "LASER ESCAPE"),
    "Puzzle": (32, (255, 200, 90), "غرف الألغاز", "PUZZLE ROOMS"),
    "Campus": (64, (255, 170, 110), "كلية العلوم", "COLLEGE OF SCIENCE"),
}


def spot(key):
    """(x, z, yaw) of a gateway: on the arc, its Front face (-Z) toward the lobby centre"""
    a = math.radians(GATES[key][0])
    x, z = AX + R * math.sin(a), AZ + R * math.cos(a)
    yaw = math.degrees(math.atan2(-(AX - x), -(AZ - z)))
    return x, z, yaw


def gateway(key, portal_name, portal_size=(9, 11, 0.6)):
    """frame + glowing doorway + title plate; the doorway part is named portal_name (touch portal or prompt part)"""
    _, color, ar, en = GATES[key]
    x, z, yaw = spot(key)
    rad = math.radians(yaw)
    rx, rz = math.cos(rad), -math.sin(rad)          # local +X (right) in world space
    w = portal_size[0]
    # the doorway part stays in the caller's folder: scripts index it directly (world.Entry.LaserEntrance)
    G.part(portal_name, portal_size, (x, AY + portal_size[1] / 2 + 0.5, z), color, "Neon", rot=(0, yaw, 0), transp=0.55,
           collide=False, shadow=False)
    with G.Group("Gateway_" + key):
        for side in (-1, 1):
            G.box("GatePillar", (1.6, 13, 1.6), (x + rx * side * (w / 2 + 0.8), AY + 6.5, z + rz * side * (w / 2 + 0.8)),
                  WHITE, "SmoothPlastic", rot=(0, yaw, 0))
        G.box("GateLintel", (w + 4.8, 1.6, 2), (x, AY + 13.8, z), WHITE, "SmoothPlastic", rot=(0, yaw, 0))
        G.box("GateBand", (w + 3.2, 0.4, 2.1), (x, AY + 12.8, z), color, "Neon", rot=(0, yaw, 0), collide=False, shadow=False)
        G.box("GateTitle", (w + 6, 3.4, 0.4), (x, AY + 16.6, z), DARK, "SmoothPlastic", rot=(0, yaw, 0), collide=False,
              text=dict(face="Front", text=ar + "\n" + en, color=(255, 255, 255), bg=DARK, bg_t=0.0))
        G.disc("GatePad", x - math.sin(rad) * 3, AY + 0.05, z - math.cos(rad) * 3, 10, 0.1, color, "SmoothPlastic",
               transp=0.35, collide=False, shadow=False)
