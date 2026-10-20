# v52 report: Owner's Final World Structure & Recovery Directive

**For independent review by ChatGPT.** ChatGPT has not seen or approved this work yet. Nothing is published, and nothing
is merged into `main`.

| | |
|---|---|
| Branch | `dev/v52-world-structure`, created from `recovery/v51-argon-wip` (`4a5331a` plus the handoff commit `d989493`). Both are kept. |
| Plan | [v52_MIGRATION_AND_SPATIAL_PLAN.md](v52_MIGRATION_AND_SPATIAL_PLAN.md), committed before any destructive change |
| Build | `Desktop\KuwaitParkour\KuwaitParkour_v52.rbxlx`, 35.1 MB (v51 was 38.7 MB) |
| Backups kept | `backup_argon_wip_20261020`, `KuwaitParkour_v51.rbxlx`, and every earlier backup |
| Screenshots | `docs/v52/01..09` (real Studio captures; see §9) |

## 1. Old Island: removed completely
- **Removed:**
  - The `Workspace.Island` Synty model (347 parts), unmapped in `default.project.json`.
  - `IslandTerrain.server.luau`, which painted the sea, beaches, lake and paths at runtime. It is deleted.
  - The island gameplay layer in `tools/island11.py`: plaza monument, sign posts, 7 gateways, food street, NPC markers,
    and the fallback `IslandSpawn`.
  - Argon's `CampusHubMigration` (16 gateways, 9 kiosks, NPC markers).
- **References removed or renamed:**
  - The World Menu "Island" card. There are now 14 cards.
  - The `TRAVEL` whitelist and `destinations` entries, so a request for "Island" is now refused (tested).
  - The Passport explore world (Argon's change; the outdated unit test was fixed).
  - The `AreaAtmosphere` island preset.
  - The Cart end-of-line action `island`, now `hub` («🏛️ رجوع لكلية العلوم»).
  - The `LeaveCourse` label («🏛️ رجوع لكلية العلوم»).
  - NPC lines, script comments, and the `explorer5` achievement name, now «مستكشف العوالم».
  - Every `Portal|Island`: the HQ south wall, and the Cart station and Cart finish (both now `Portal|Campus`).
- **Verified in Play** (fresh map, island model and saved terrain cleared to match the build):
  - `workspace.Island` is absent.
  - 0 parts and 0 sampled terrain voxels remain in the old island area.
  - `IslandReady` is never set.
  - The built place contains no `Island` model and no `IslandTerrain` script.
  - The 117 parts named `Island` are the floating ground discs **under the Specialties Train track** (`cartride.island`),
    part of the approved ride, not the old world.

## 2. Main hub
- **Spawn:** `CampusSpawn` (College of Science south lobby) is the only SpawnLocation.
  - Tested spawn: (−1, 4, −147).
  - After a reset, the respawn was at (0, 3, −147).
- **Return to hub:** the Cart end card, `LeaveCourse`, and the Exam, Arcade, Lab, Quiz and Show exits lead to the College
  of Science or the HQ (all tested; §6).

## 3. South–North connections (updated after the owner's marked screenshot)
**Owner clarification:** keep the raised Red Corridor **and** the ground-level east garden walk, which matches the real
campus. Only the second (west) walk stays removed.
- **Restored:** the MAIN (east) walk pavers and curbs, plus its lamp posts.
  - Walk test in Play: south back door (42,−30) → past the gym → north entrance (20,135). All 10 waypoints were reached.
  - Um Al-Qatawa stands about 4.6 studs from the walk's edge, so she does not block it.
  - Screenshot: `docs/v52/10_campus_top_FINAL_corridor_plus_east_walk.jpg`.
- **Still removed:** the WEST walk with its arc bollards, the north_link forecourt and sign, and the desert-trail link
  into the north promenade.

### Original analysis (first pass)
- **Identified:** `genmap5.py` BridgeFloor, BridgeRoof, BridgeGlass, Mull, BridgeCol, BridgeLamp and BridgeSign, at
  x −50..−30, y 24, z −30 to 130.
  - A Studio scan of every collidable floor at y 6–60 between the buildings found only this corridor.
  - It was not rebuilt; its appearance is unchanged.
- **Removed duplicates (ground routes):**
  - the MAIN (east) and WEST paved garden walks, with their curbs;
  - the lamp posts and bollards lining them;
  - the `north_link` forecourt and the "↑ North Building" sign;
  - the desert-garden trail's link into the north promenade (`GardenWalkLink`). The trail is shortened to z ≤ 100, so it
    stays inside the desert garden.
- **Kept, because they do not link the two buildings:** the north `Promenade` band and the `EastPaving` plaza.
- **Fixed geometry:** the corridor column pair at z 12 was clipped by the gym roof eave. It moved to z 4 (clear of the
  gym), and the girders now run z 4..84. The scan was rerun.
- **Walk test in Play:** a real Humanoid `MoveTo` with no jumping.
  - South L1 (Marble) → corridor (Brick) along z −40..145 → north L1 (Marble).
  - Then back again the same way.
  - No blocking.
- **Screenshots:** `01` before and `02` after (top view; the two curving walks are gone), `03` exterior, `04` interior.
- **Owner note:** the open lawn between the buildings is still walkable grass. If you also want a hedge or fence to stop
  that physically, say so.

## 4. Food kiosks
- **Evaluated:** the 9 kiosks only gave a free snack Tool and a fact.
- **No dependencies found:** no quest, reward, Passport or progression system uses them. `FoodStreet.server` serves
  whichever `ShopOrder` parts exist.
- **All 9 removed.** The same interaction already exists at the HQ café counter (`ShopOrder|10..13`), with the chef NPC
  behind it. No new food area was built.

## 5. World Gateway Hall (HQ)
- **Layout:**
  - A 24-wide doorway in the HQ south wall leads to a 96 × 80 hall, 30 tall.
  - **One portal style:** `hq.portal`, 11 wide and 13 tall, 18 studs apart, with a coloured floor pad.
  - **West wall:** Arcade, Puzzle, Racers, Laser.
  - **East wall:** Exam, Quiz, Show, Virus.
  - **South end wall:** Lab, College of Science, Museum.
- **Removed:**
  - Argon's 8 HQ wall gateways (which crossed the café and the portal posts).
  - The old HQ west-wall Virus gate (it duplicated the hall and clipped a plant pot).
  - The decorative clouds that fell inside the hall.
- **Kept in place:** the north-wall parkour zone gates and the Cart and Cell Train portals on the HQ east wall.
- **Tests:**
  - All 11 hall portals were touched in Play and each landed in the right world.
  - The HQ and hall collision scan reports 0 overlaps (192 collidable parts).
  - Screenshots `05`–`07` and `09`.

## 6. Destinations and returns (Play, solo)
- **World Menu:** 14 cards, all 14 tested.
  - Every destination lands on solid floor.
  - "Island" is refused.
- **Return portals tested** (Portal|HQ and Portal|Campus inside the worlds):
  - Course finish, Cart station, Cart finish, Virus, Lab, Quiz, Show, Exam, Arcade. All correct.
  - The Exam hall result was rechecked with a 4 s wait because of the portal cooldown.
- **Worlds without a return portal:** the Cell Train, Micro Racers and Laser Escape use their own exit buttons (plus the
  World Menu). The puzzle rooms lead back to the Arcade.

## 7. NPCs (one each, placed by role; obsolete lines rewritten)
| NPC | New place |
|---|---|
| Abu Ali (guard) | HQ, beside the hall doorway |
| Chef | Behind the HQ café counter |
| Gamer | Arcade lobby |
| Dr. Sara | Research Lab entrance |
| Yousef | Challenge Center |
| Former beach "lifeguard" | Now **مرشد المتحف** (museum guide), at the Museum entrance |
| Noura | South lobby (moved after the first try put her on top of an InfoScreen) |
| Cat lady | East lawn by the campus cats (moved off a shrub) |
| Invigilator | Unchanged |

- All 9 spawned in Play, standing on their markers.
- Lines that described things that don't exist were removed: a museum whale skeleton, a spectator gate, and the café
  row.

## 8. Unfinished work handled
- **`ExamActiveBarrier`:** removed. It had no logic, and the exam keeps its 2 s lock-in.
- **Cart "coaster":**
  - The 7 `b` booster flags are removed: the client never boosts, so the glowing booster pads advertised a fake feature.
  - The hill heights are back to the tested values.
  - Argon's visuals are kept: the locomotive, the 3D console buttons from v51, the rails and spine, and the specialty
    gates over the track (non-colliding, above the cart).
  - **Full ride tested:** I stepped on the start pad, clicked ▶ with a real mouse click, and the ride ran the whole track
    (about 3 min, roughly 35 studs/s, slower on the helix climb) while seated.
  - The end card appeared, and «رجوع لكلية العلوم» returned the player to the College of Science.

## 9. Collisions
- **Campus-wide scan** (collidable parts from different groups; ground planes excluded): 9 overlaps, all structural joins:
  - office walls against the building's glass and floor slab;
  - a girder sitting on its column;
  - a door transom against a floor slab;
  - the museum approach against the parking surface.
- **Gym:** only the ground planes touch it. **No kiosks, gateways, NPCs or columns.**
- **HQ and hall:** 0 overlaps.

## 10. Static checks
- `genmap9`: 27,928 parts, 0 violations, cart points 1144, 0 clashes.
- `selene`: 0 errors, 26 known warnings.
- `validate_questions`: OK.
- Unit tests:
  - `test_laser48`: PASS.
  - `test_museum46`: PASS.
  - `test_racers47`: PASS.
  - `test_passport45`: PASS, after replacing its obsolete "Island" visit with "Lab".
- `rojo build`: OK.
- `stylua --check` only flags the generated `RacerData.luau` formatting, which is left as committed.

## 11. Not verified
- **Not tested:**
  - multiplayer;
  - a real phone or the device simulator, for the new menu or hall;
  - live DataStore;
  - performance on weak devices.
- **Not walked:** the Lab, Quiz, Museum, Show, Racers, Laser and Puzzle interiors were only reached by teleport, not
  walked through again. Their systems are unchanged.
- **Visual quality:** judged only from the 9 screenshots, not by a person playing.
- **Owner decision needed:** whether to physically block the lawn between the buildings (§3).
