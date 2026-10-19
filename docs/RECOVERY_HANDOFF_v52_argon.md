# Recovery handoff: Argon's unfinished v51/v52 work (2026-10-20, Claude)

Antigravity/Argon hit its quota mid-edit. Nothing has been published or merged. No Argon change was reverted.

## Preservation
- **Recovery branch:** `recovery/v51-argon-wip`, pushed. Commit `4a5331a` holds all 26 uncommitted Argon files as-is.
  - It sits on top of `aa909c8` (v50). Argon's original branch, `dev/v51-milestone1`, still points at v50.
- **File copy:** `Desktop\KuwaitParkour\backup_argon_wip_20261020`.
  - It holds every changed file and `argon_uncommitted.diff` (2026 lines).
  - It also holds `Map_before_regen.rbxmx`, the generated map from 00:44, before my check.
- **Builds:** `KuwaitParkour_v51.rbxlx` (00:45) is untouched, in both the Desktop and the project folders.

## What Argon completed (Milestone 1)
These changes are in the v51 build (00:45). They match `BSC_PROGRESS.md` v51 and `docs/v51_milestone1_verification.json`.
- **Campus cleanup:**
  - The DeptPhysics sign and the invented commercial cafés were removed.
  - The WalkNote signs were removed.
  - The L3 doors were changed to the 8 specialties.
- **Museum:** botanical landscaping, and the FictionNotice wall removed.
- **Puzzles:** `pressSeq` made idempotent (pressing a lit tile twice no longer resets it), with a `solvedUntil` grace window.
  - Stage 54 now has no repeated DNA bases next to each other.
  - `G.sign` defaults to `collide=False`, and the boards were raised.
- **Spawning and returns:**
  - An IslandFoundation slab under the island spawn.
  - Tighter Teleport ground clearance, plus a second safety check.
  - LeaveCourse and the Cart returns now go to the hub.
- **Other games:**
  - 3D cart buttons.
  - Cell Train free-look camera and a membrane tunnel.
  - Automatic lab coat in the Research Lab.
  - Virus Tag: no repeated Patient Zero, and a solo drone mode.
  - Exam: a 2 s answer lock-in.
- **Evidence:** Argon's JSON reports server and client checks passing. No screenshots were recorded. I did not re-verify
  these visually.

## What was unfinished (v52, "retire the Island")
These five files were edited at 01:19–01:25, after the v51 build. They are not in any build.
- **`tools/island11.py`:**
  - `island_layer()` no longer builds the island plaza. An invisible `IslandSpawn` stays at the campus (0,0.5,70) as a
    fallback.
  - New `CampusHubMigration` group:
    - 8 gateways in HQ;
    - 8 gateways on the campus at x ±56, z 48..96;
    - the 9 food kiosks (ShopOrder|1..9) moved to campus x ±38, z 50..96;
    - 8 NPC markers moved to HQ and campus.
  - The exits from Exam, Arcade, Lab and the Course finish now go to HQ and Campus instead of the Island.
  - Research-lab dressing added: ducts, pipette stands, ice bucket, UV transilluminator.
  - `ExamActiveBarrier` was added **with no code**. It is invisible and non-colliding, so it is inert.
- **`tools/cartride.py`:** labelled "Science Express coaster-tour". The changes visible in the diff are darker, thicker
  supports and over-track portals for each specialty. The track itself is unchanged (cart points 1144, clashes 0).
- **`NPCs.server.luau`:** NPC lines rewritten for the campus and HQ. The 30 s wait for `IslandReady` was replaced by
  0.5 s.
- **`Main.server.luau`:** the `Island` destination now resolves to HQSpawn (or CampusSpawn).
- **`PassportDefs.luau`:** `Island` was removed from the explore worlds, and the label was renamed.

## Errors and risks found (not fixed, because they need design decisions)
1. **CRITICAL (visual and design): the migrated campus pieces sit inside the gym.** The gym is the triangle TRI (0,-24),
   (±66,62); the owner said it is closed and cannot be entered. The overlap scan in Play found 15 overlaps:
   - kiosks (KioskBack, ShopCounter) inside GymRoof, GymGlass and GymBoundary at x ±38..40, z 50..73;
   - gateways at (56,48) and (-56,53) through GymRoof and GymBoundary;
   - one counter overlapping `Campus.Lawn`;
   - the NPCs `dr_sara` (-16,24), `noura` (16,24), `yousef` (-46,78), `chef` (32,68), `lifeguard` (12,98) and
     `cat_lady` (74,58), all on or inside the gym footprint or the garden walks.
2. **HQ overlaps:** gateways cross `HQFill.CafeCounter` and `CafeTop` at (-74,-12019), and `ClubHQ.PortalPost` at
   (74,-12014).
3. **Conflict with the owner's realism rule:** Milestone 1 removed the invented cafés from campus, and v52 puts nine café
   kiosks and 8 gateways back into the real College of Science campus. **The owner should decide where these go**
   (for example, HQ only).
4. **The Island model and terrain are still loaded.** `workspace.Island` and `IslandTerrain` still run. Only the
   gameplay layer was moved. Nothing reachable sends players there now, so it is dead weight unless it is removed on
   purpose.
5. **NPCs no longer wait for the island terrain.** This is harmless now that the markers are on campus and HQ: in my run,
   all 9 spawned at their markers. Placement is still wrong (see 1).
6. **`Virus` is not in the `TRAVEL` whitelist.** This was already true before Argon's edits; it is reachable by portal
   only.

## Checks I actually ran (on the recovery branch, without changing Argon's code)
- `python tools/genmap9.py`: OK. 28,831 parts, 0 stair violations, cart points 1144, 0 clashes.
- `stylua`: only touched generated RacerData formatting, which I restored. `selene src`: 0 errors, 26 known warnings,
  0 parse errors.
- `validate_questions.luau`: OK. `test_laser48.luau`: PASS.
- `rojo build`: OK (41.3 MB, to a scratch file; no Desktop build was written).
- **Studio, Play Solo** (the WIP map and scripts hot-swapped into the open v51 tab, in memory only):
  - Travel to all 15 menu destinations landed on solid floors. `Island` now lands at HQ (0,604,-11970).
  - 9 NPCs spawned. There were 48 Portal parts.
  - **No errors from our scripts.** The only warnings were the known DataStore, UIBlox, `203785492` and `81504106`
    asset messages.
  - The overlap scan is the source of risks 1 and 2.
- **Not verified:** screenshots, the visual quality of the campus, HQ or lab, multiplayer, the phone, and DataStore.
- **Warning:** the Studio tab named `KuwaitParkour_v51.rbxlx` now holds the WIP content in memory. **Do not save it.**
  Close it without saving, or reopen v51 from the file.

## Exact next steps (resume Milestone 2)
1. **Owner decision:** where do the migrated kiosks, gateways and NPCs go? HQ only, or campus spots outside the gym?
   Do not invent campus details.
2. Move every `CampusHubMigration` piece off the gym footprint, the garden walks and the HQ café and portal posts. Re-run
   the overlap scan (a `GetPartBoundsInBox` per collidable part of the group) until it reports 0.
3. Either finish `ExamActiveBarrier` (close it when Q1 locks, in `ExamHall.server`) or remove it.
4. Decide whether to stop loading the Island model and terrain, then remove both together.
5. Finish or revert the cartride "coaster" dressing, and verify the Specialties Train ride.
6. Bump to v52 and build `KuwaitParkour_v52.rbxlx`. Do a Studio walk test, take screenshots, and update
   BSC_PROGRESS.md. Commit on a `dev/v52` branch created from `recovery/v51-argon-wip`.
7. Then continue the roadmap Milestone 2: the Specialty Showcase rooms on the cart track, Cell Train shaders, and a
   multi-client Arcade stress test.
