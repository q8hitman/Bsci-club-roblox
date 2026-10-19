# v52: migration inventory and layout plan (owner's final world structure directive)

**Branch:** `dev/v52-world-structure`, created from `recovery/v51-argon-wip` (commit `4a5331a`, plus the `d989493` handoff).
Backups `backup_argon_wip_20261020` and `KuwaitParkour_v51.rbxlx` are kept and will not be touched.

## 1. Audit of the old Island
| Item | Where | Decision |
|---|---|---|
| Synty island model (347 parts: Buildings, Nature, Props) | `src/world/Island.rbxm`, `default.project.json` → `Workspace.Island` | **Remove** from the project mapping, so it is not in the generated place |
| Island terrain (sea, beaches, lake, paths) painted at runtime | `server/IslandTerrain.server.luau` | **Remove** the script, so no terrain is generated and no `IslandReady` is set |
| Island gameplay layer (plaza monument, sign posts, 7 gateways, food street, NPC markers, subway sign, invisible fallback `IslandSpawn`) | `tools/island11.py` `island_layer()` (Argon's v52 `CampusHubMigration`) | **Remove** the call and the content (details in the rows below) |
| Activities that only *started* on the Island | Arcade, Exam, Lab, Quiz, Virus, Cart, Course, Museum, Show, Racers, Laser, Puzzle | **Preserved.** These are their own worlds; only the doors move (§4) |
| Cell Train start (`TrainStart`) | already on campus (150,2,-42) | Unchanged |
| 9 food kiosks (`ShopOrder|1..9`) | Island street / Argon's campus copies | **Remove.** The only gameplay is a free snack and a fact, and the HQ café already gives exactly this through `ShopOrder|10..13`. No quest, reward or Passport dependency was found. `FoodStreet.server` handles missing points |
| "Island" in the World Menu card, `TRAVEL`, `destinations`, and Passport explore worlds | `WorldMenu.client`, `Main.server`, `PassportDefs` | **Remove** (the Passport part was already done by Argon) |
| "Back to the island" labels | `CartRide.client/server` (`island` action), `LeaveCourse`, NPC lines | **Rename** to the hub (College of Science / HQ) |
| `Portal|Island` doors | HQ south wall, Cart station, any left in a world | Replaced by HQ or Campus doors |
| `AreaAtmosphere` `island` preset, and the `IslandHUD` name (it is really the Arcade/Exam HUD) | client | The preset is dropped. `IslandHUD` keeps its name (Racers refers to it), and only its comment is fixed |
| `tools/world/island.luau` (Lune builder) | tools | Kept on disk as history but no longer part of the build |

## 2. Main hub and spawn
- **Permanent spawn:** `CampusSpawn` (south lobby, already the only active SpawnLocation).
- **Return to hub:** the College of Science (Campus), with the Club HQ one portal away. The Cart "end of line" button,
  `LeaveCourse`, and the exits from the Exam, Arcade and Lab worlds go to the Campus or HQ.

## 3. Exactly ONE South–North connection: the original Red Corridor
- **Identified:** `genmap5.py` → `BridgeFloor`, `BridgeRoof`, `BridgeGlass`, `Mull`, `BridgeCol`, `BridgeLamp`,
  `BridgeSign` («الممر الأحمر | Red Corridor»), at x −50..−30, y 24, z −30 to 130.
  - Its junctions are the v44 south-face opening and the north L1.
  - The v37 girders carry it over the gym.
- **Measured in Studio:** it is the *only* raised walkway between the buildings (a scan of collidable floors at
  y 6–60 found only `BridgeFloor` and `BridgeRoof`).
- **Duplicates to remove** (ground walkways that link the south building's back doors to the north entrance):
  1. `GardenWalkV34` MAIN (east, curving) walk pavers;
  2. `GardenWalkV34` WEST walk pavers, plus the arc around the mound;
  3. `north_link()`: the forecourt, `Connect|North`, and the "↑ North Building" wayfinding sign;
  4. `Campus/GardenWalk`: the 12-wide straight path at x −146..−134 running z −182 → 250 past both buildings. It will be
     cut to the desert-garden beds only (z −40..88), so it no longer runs from one building to the other.
- **Kept:** the north `Promenade` band along the north face and the `EastPaving` plaza (both real, from v35). Neither one
  links the two buildings.
- **Not added:** any replacement connection.
- **Owner note:** the open lawn between the buildings stays walkable grass. Tell me if you also want a hedge line to
  physically stop that.

## 4. World Gateway Hall (in the Club HQ)
A new hall opens off the HQ's south wall, where the Island portal was, through a 24-wide doorway. Hall interior: local
x −48..48, z 72..152, height 30. It has one consistent portal style (`hq.portal`): 12 wide, 13 tall, posts and a lit
title.
| Wall | Portals |
|---|---|
| South end wall, facing the entrance | 🏛 College of Science (centre), 🔬 Research Lab, 🏺 Museum |
| West wall (Arcade cluster) | 🎮 Arcade, 🧩 Puzzle Rooms, 🏎 Micro Racers, ⚡ Laser Escape |
| East wall (knowledge and shows) | 📝 Exam Hall, 🎓 Challenge Center, 🎪 Game Show, 🦠 Virus Tag |

- The HQ keeps what it already has in place: the parkour zone gates and Continue on the north wall, and Cart + Cell Train
  on the east wall.
- The campus keeps its existing Portal|HQ doors in the south building.
- All of Argon's campus gateways (inside the gym) and his 8 HQ wall gateways (crossing the café and portal posts) are
  removed.
- The World Menu keeps one card per destination, minus Island (14 cards).

## 5. NPCs by role (one each; their lines are updated to remove the Island)
| NPC | Role | New place |
|---|---|---|
| د. سارة | Microbiology professor | Research Lab, near the entrance |
| أبو علي | HQ guard | HQ, beside the Gateway Hall doorway |
| نورة | New student | College of Science south lobby, near the spawn |
| يوسف | Exam champion | Science Challenge Center, near its spawn |
| الشيف بروتين | Snacks | HQ café counter (the real snack point) |
| ~~المنقذ / مشرف الساحة~~ | Beach role, now obsolete | Becomes **مرشد المتحف** (museum guide), near the Museum entrance |
| هيثم القيمر | Gamer | Arcade lobby |
| أم القطاوة | Campus cats | Garden lawn north of the gym, clear of the gym and the paths |
| المراقب | Exam | Exam hall (unchanged) |

## 6. Gym and collisions
- Removing every `CampusHubMigration` campus piece clears all 15 reported overlaps.
- A collision scan then checks the campus, the HQ and the new hall for collidable overlaps between different groups. The
  gym stays closed and is not repurposed.

## 7. Unfinished work
- `ExamActiveBarrier` is removed. The exam already has its 2 s lock-in; the barrier had no logic.
- **Cart coaster:**
  - The `b` "booster" flags are removed, because the client never boosts and the glowing pads would promise a fake
    feature.
  - The hill heights go back to the tested v31 values.
  - Argon's cosmetic upgrades are kept: the locomotive model, the 3D console buttons (built in v51), the rails, spine and
    supports, and the specialty gates over the track (non-colliding and above the cart).
  - The ride is verified in Studio.

## 8. Not touched
These systems stay as they are:
- the obby and its puzzles;
- the Cell Train;
- the Lab stations and the microscope;
- the Museum exhibits;
- the Arcade games;
- Virus Tag and the Exam logic;
- Micro Racers and Laser Escape;
- the Game Show and Puzzle Rooms;
- Passport and progression;
- DataStore and profiles.
