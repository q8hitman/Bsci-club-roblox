# BSC Island: development handoff (v56, 2026-10-21)

For whoever continues: Claude Code, Codex, or a person. **Continue this project. Do not restart or redesign it.**

## 1. Where things are
| | |
|---|---|
| Repo | `C:\Users\User\Desktop\KuwaitParkour\BSC_project_full` (GitHub `q8hitman/Bsci-club-roblox`) |
| Branch | `dev/v54-labs-cartride`, created from `dev/v53-release-push` at `6aac766`. Neither branch is merged into `main`. |
| Latest build | `Desktop\KuwaitParkour\KuwaitParkour_v56.rbxlx` (not published). v55 and every older build and backup are untouched. |
| Studio | Session `KuwaitParkour_v53.rbxlx`, hot-swapped to the v54 code. It is unsaved; the file on disk is newer. |

## 0. v56 (same branch): what changed, and how it works
| Area | What | Evidence |
|---|---|---|
| **Cart Ride streaming** | The eight valleys are no longer in the Map:<br>• `tools/cart_tour53.route_parts` sends every valley part to `Shared/CartScenery/V1..8` (one text line per part, tab-separated)<br>• `CartScenery.client` builds the valley you are in plus its neighbours, 350 parts per frame, one valley at a time, and destroys the far ones<br>• the server keeps only the station, portals and the finish deck<br>• ride event props are looked up in `workspace.CartScenery` | Server Map: **40.4k → 20.9k parts** (Map.rbxmx 30 → 16 MB).<br>On the client, 2-3 valleys are loaded (about 6-13k parts).<br>Studio: 60 fps average, worst frame 25-28 ms while a valley builds. |
| **Route 84,181 studs** | Five legs per valley (`LEGZ` 900, `CELLZ` 1120):<br>• spiral climb and overlook<br>• the highline: a long high bridge over the river, two S-bends<br>• a slot canyon, then rolling hills<br>• the hero set piece and a mesa tunnel<br>• a double spiral home | 0 clashes.<br>`tools/cart_ride_time.py`: **41 min @35, 32 @45 (default), 24 @60, 17 @90, 14 @120** |
| **Walls and horizon** | Stepped three-layer strata cliffs with crags, layered ridges | Seen from the train in Studio |
| **Help instead of boards** | `Help.client`: a ؟ button with tips for the current area. The HQ, Arcade and Challenge Center how-to boards and the cart station controls board were removed | Code + lint |
| **DNA extraction (5th lab bench)** | Mash the strawberries with buffer, filter, layer ice-cold ethanol, DNA threads appear, wind them onto the rod | Studio QA hook: +6 research |
| **Petri Floor** | Tiles sink and fade instead of vanishing | lint |
| **Arcade vote** | `ArcadeVote.client`: during the break, players in the lobby vote between three games; the most votes wins | Studio: a real click voted for Last Cell, and Last Cell started |
| **Two clients on the streamed version** | `tools/studio_tests/v53.*` rerun | **Pass:** own carts, each client sees the other's cart moving (about 308 studs), Gram +6 each, First Day per player |
| **Pacing variants + slot canyons** | Per-world spiral turns, hill count and height (`VARIANT`); canyon walls with chockstones | Route 85,547 studs; canyon seen from the train in Studio |
| **Full ride on the 84k route** | | Studio at 120: all 8 valleys. The loaded window slid {1,2} → {2,3,4} → … → {6,7,8}; the end card took the player back to campus; valleys unloaded; 0 errors |

**Important for the next developer:**
- To edit a valley, edit `tools/cart_tour53.py` and regenerate. Never edit `Shared/CartScenery/*.luau` by hand.
- Anything a server script must touch inside a valley has to be named in `SERVER_KEEP`.

## 1a. Done in v55 (same branch `dev/v54-labs-cartride`)
| Feature | Static | Studio solo | Multiplayer | Phone |
|---|---|---|---|---|
| **Virus Tag solo opponent:** a virus particle (capsid + spike proteins) that:<br>• aims ahead of the player<br>• flashes red for 1 s, then dashes<br>• replicates halfway through<br>• is knocked back by the vaccine<br>• spawns far from the player<br>Rewards: 15 for surviving 45 s, otherwise 2 per 10 s | selene OK | **Standing still:** caught in 2.7 s<br>**Scripted fleeing player:** survived 23 s, saw the warning and the split | Rounds with 2+ players are unchanged | no |
| **Cart worlds art:**<br>• large ground patches<br>• one new themed district per world (streak plate, pH beakers, oasis + pond, giant tree grove, protein helices, police floodlights + cars, palm plantation + barn, greenhouse domes + solar field), each with a ride caption<br>• valley-scale date palms (40-56 studs) | 40.4k parts | Screenshot at bridge height in Animal Biology; 0 script errors | n/a | no |

## 1b. Done in v54 (all committed and pushed)
| Feature | Static | Studio solo | Multiplayer (2 clients) | Phone |
|---|---|---|---|---|
| **Hands-on 3D wet lab** (`tools/labs54.py`, `Labs54.server`, `Bench54.client`):<br>• lab coat and goggles at the entrance<br>• carry real equipment, place it on slots, pour, draw and connect<br>• one player per bench; others can watch | selene OK | **Gram:** refusals (no heat-fix, wrong reagent), colour changes, timed rinse, microscope, identify: +6<br>**Gel:** reversed electrode loses the DNA; correct run; reading under UV: +4<br>**PCR:** no Taq gives NO PRODUCT with the reason; complete run gives about a billion copies: +8<br>**Microscopy:** the placed slide opens the focus simulation<br>A real `E` press picks up an item | **Pass:** bench lock, two benches in parallel, bench freed when its user leaves (`tools/studio_tests/labs54.server.luau`) | no |
| **Massive Cart Ride**:<br>• 48,070 studs; per world: spiral climb, overlook pavilion, high bridge over a Terrain river, S-bends, big drop, hero run, tunnel through a mesa, double spiral around the world's tower | 0 clashes; ride-time sim: 23 min at 35, **18 at 45 (default)**, 14 at 60, 10 at 90, 8.6 at 120 (`tools/cart_ride_time.py`) | **Full ride at 120:** all 8 worlds, end card, back to campus, 0 errors, measured 94 studs/s | v53 test: each player sees the other's cart (cart system unchanged) | no; **perf risk:** 39k parts |
| **Text cleanup**:<br>• cart landmark boards become captions while passing<br>• obby LEVEL boards become small number plates<br>• slimmer Laser hints<br>• Cell Train name boards removed | genmap 0 violations | Captions seen during the ride | n/a | no |
| **Cell Train**:<br>• detour inside the nucleus through pores and around the nucleolus<br>• all 13 stop captions now show (half never did before) | n/a | Rode through the nucleus; the ride ended at the station | no | no |
| **Arcade**:<br>• 5 s start countdown on the HUD<br>• ATP combo shown | selene OK | Countdown in code only | v53 results-screen test | no |
| **Cart keys:** `Enter` start/pause, `V` camera (`P` and `C` belong to Photo Mode) | | Seen | | |

## 2. Build, lint and test commands (run from the repo root)
```
python tools/genmap9.py                      # Map.rbxmx + Shared/CartTrack, CartRooms, Zones, LaserData, RacerData
git checkout -- kuwait-parkour/src/shared/LaserData.luau kuwait-parkour/src/shared/RacerData.luau   # generator only reformats these
tools/rojo/rojo.exe build kuwait-parkour/default.project.json -o ../KuwaitParkour_vNN.rbxlx
cd kuwait-parkour && ../tools/stylua/stylua.exe <changed files> && ../tools/selene/selene.exe src
tools/lune/lune.exe run tools/test_passport45.luau      # also test_museum46, test_racers47, test_laser48, validate_questions
```
- **Run selene from `kuwait-parkour/`**: from the repo root it can't see its config and reports hundreds of false errors. Baseline is 0 errors and 27 known warnings.
- **Do not run stylua on all of `src`**: it reformats the generated `shared/*.luau` files.
- **Hot-swap into an open Studio** (no restart):
  1. Rojo-build each folder (`src/client`, `src/server`, `src/shared`) to `.rbxm`, plus `Map.rbxmx`, into `%LOCALAPPDATA%\Roblox\Versions\<studio>\content\bsc\`.
  2. In Edit, run `game:GetObjects("rbxasset://bsc/<file>")[1]` and replace the folder.
  3. Delete `content\bsc` afterwards.

## 3. Done in v53 (all committed)
| Feature | Code inspection / static | Studio solo playtest | Multiplayer | Phone |
|---|---|---|---|---|
| **Cart Ride Grand Tour**:<br>• 8 open valleys, ridges, tunnels, a hero set piece per world, 17,000-stud track (~8 min at default speed)<br>• progress bar, downhill speed feel<br>• events: colony growth, pollen storm, UV fingerprints<br>• 🎥 chase camera; gamepad R2/L2/X/Y | genmap 0 clashes, 14/14 landmarks, selene OK | **Full ride**:<br>• real ▶ click, all 8 stages<br>• colony and pollen events seen<br>• end card, «رجوع لكلية العلوم» returned to the campus<br>• camera restored, 0 script errors | no | Device-emulator layout only; buttons moved off the jump button |
| **Cell Train**:<br>• double-membrane mitochondria with cristae<br>• nucleus envelope, pores and chromatin<br>• RER joined to the nucleus<br>• curved cis→trans Golgi; smaller lysosomes<br>• microtubule secretion route<br>• `CellLife.client`: vesicles carried by kinesin, drifting mitochondria and cytosol | selene OK | Ride ran; organelles and moving vesicles captured; 0 script errors | no | no |
| **Gram stain** as a real procedure:<br>• reagent rack<br>• decolorizer timing band<br>• the server decides what the slide looks like; the answer stays server-side | selene OK | **Real clicks**:<br>• a wrong pick explains itself<br>• E. coli done right: +6 RP<br>• Bacillus over-decolorized: pink, rejected with the reason | no | no |
| **Gel electrophoresis** as a procedure:<br>• load the ladder and the sample<br>• place the + electrode<br>• run the gel and size the band against the ladder; positions come only from the server (`gelRun`) | selene OK | **Real clicks**:<br>• the wrong electrode is explained<br>• 150 bp read correctly from the ladder: +4 RP | no | no |
| **PCR**:<br>• primer choice by base pairing<br>• thermocycler with a doubling copy counter | selene OK | **Real clicks**:<br>• a wrong primer is explained<br>• the right primer opens the cycler (the timing part is unchanged since v50) | no | no |
| **Arcade results screen**:<br>• ranked players (score, or survival order)<br>• your rank, rewards and a next-round countdown<br>• replaces the old winner message | selene OK | Solo ATP Rush round (no-winner case) | **2 clients, a real Petri Floor round:** ranks 1/2, +12/+2 coins | no |
| **First Day at the College**:<br>• 4 optional steps (HQ, Arcade, Lab, train) with travel buttons<br>• `firstday` achievement (+50 coins, title) | Lune tests all PASS | Card shows `0000`; a real click on the HQ step travelled there and ticked it (`1000`) | no | Layout checked in the emulator only |

**Multiplayer (`StudioTestService` with 2 clients), passed.** Fixtures are in `tools/studio_tests/v53.*` and `arcade53.*`:
- Each player gets their own cart, both carts move about 250 studs, and each client sees the other's cart moving.
- Both players run the Gram stain at the same time: +6 each, the answer stays hidden, and `gramView` works only once.
- The First Day lab step ticks for each player separately.
- A Petri Floor round ranks both players correctly.

**Regression check:**
- All 14 World Menu destinations land on solid floor.
- Script errors after the tour: 0 (only "saving disabled", which is expected in Studio).
- The obby has all checkpoints 0..100, none floating; generator violations: 0.

Smaller items:
- **Cart terrain:** `CartTerrain.server` paints 578 balls from `Shared/CartTerrain`:
  - Limestone scree at the base of the cliffs and ridges;
  - Sand dunes (animals), LeafyGrass hills (plants), Ground hills (agriculture).
  - Seen in Play.
- **Fixed:** the mirrored −z side of the cart worlds had negative part sizes, so the south cliffs and the left tunnel walls were missing. `cart_tour53.rect` now sorts its bounds; 0 negative sizes remain in the cart worlds.
- The welcome hint about a timer was replaced, because the owner removed the visible timer.
- `AreaAtmosphere` and `Feedback` now test the cart region before the cell world.

## 4. Partially done / known issues
- **The cart worlds now have terrain and props near the rails,** but they are still simple primitive-style art. A later art pass could add:
  - Synty or Creator Store meshes (check their licences);
  - a petri-dish rim in Microbiology.
- **Pre-existing campus bug, not touched (approved geometry):** 134 `Mullion` and 15 `Ribbon` parts on the campus (x −1000..1000, z −1000..0) have negative sizes, so they probably render as nothing. Check what they were meant to look like before fixing them in their generator.
- **Cart part budget:** the place has about 32,900 parts (v52 had 28,200). Check frame rate on a real phone before adding more.
- **The Arabic Gram answer text** and the other lab text use two-line Arabic/English. Other panels may still mix both languages on one line, which garbles it; split those into two lines too.
- **Not tested:**
  - the Cell Train and the First Day card with 2+ clients (they run locally per player);
  - a real phone;
  - live DataStore persistence of the `firstday` achievement.
- **Not built** (the research proposals need owner approval or come later):
  - Calm Tour vs. Thrill Run;
  - Vesicle Express;
  - Biotechnology Studio;
  - shared friend carts;
  - continuing the ride from the last stage.

## 5. Next steps, in priority order (v54)
0. **Owner review of v54:** the lab feel, the ride length (18 min at the default speed), the part count on a phone.
   - If the phone struggles: lower `cart_tour53.DENSITY`, tie spacing, or `LEGZ`.
1. ~~Virus Tag solo opponent~~ done in v55.
2. **Cart worlds art:** v55 added districts and scale. Still possible: licensed meshes, a petri rim, strata on the cliffs.
3. **The campus and HQ** stay as the owner approved them. Sign redesign there needs the owner's OK.

## 5-old. Earlier next steps (v53)
1. **Owner tests on a real phone:**
   - the cart ride (buttons, progress bar, 🎥 camera);
   - the Gram, gel and PCR panels (text size);
   - the First Day card;
   - frame rate in the cart worlds.
2. **A private test publish, only with the owner's approval:**
   - check DataStore saving (`firstday`, Passport stamps);
   - check a real multiplayer server.
3. **Art pass on the cart worlds:** better props (licensed meshes) and a petri rim. Keep the part budget in mind.
4. **The other Arcade-area games:**
   - Virus Tag, Exam Hall, Game Show, Puzzle Rooms, Micro Racers and Laser Escape already have their own flows and results;
   - review them with real players;
   - fix only what playtesting shows.
5. **Light Microscopy vs. Cell ID:** the owner decides whether to merge them (research update §3).
6. **The 100-stage obby:** a variety and clarity pass on chosen stages after the owner's review. Keep all 100 stages and no visible timer.

## 6. Owner decisions already made (do not change)
- **Entertainment first, light and accurate science.** Reply to the owner in simple Kuwaiti Arabic.
- **Campus:**
  - the main hub is the College of Science South lobby (`CampusSpawn`);
  - the BSC HQ;
  - one elevated Red Corridor plus the **east** ground walk; the west walk stays removed;
  - the old Island stays removed;
  - no food kiosks or clutter.
- **The 8 specialties, in this official order:**
  1. Microbiology
  2. Biochemistry
  3. Animal Biology
  4. Plant Biology
  5. Molecular Biology
  6. Forensic Science
  7. Agriculture
  8. Biotechnology
- **Cart Ride:**
  - never derail, kill or force a restart because of speed;
  - no holding W.
- **Keep:** the 100-stage obby with no visible timer, and every approved minigame (no merges or deletions).
- **Never:**
  - publish publicly or privately without explicit approval;
  - spend money;
  - enter passwords;
  - build the horror world.

## 7. Needs owner approval
- Calm Tour vs. Thrill Run modes.
- Vesicle Express.
- Biotechnology Studio.
- Shared carts for friends.
- Merging the Cell ID station into Light Microscopy.
- Any campus layout change.
- Any publish.

## 8. Tools available and verified
| Tool | Status |
|---|---|
| Roblox Studio built-in MCP (`StudioMCP.exe`, `mcp__Roblox_Studio__*`) | Works: Play, run Luau, real mouse/key input, screenshots |
| Rojo 7.7.1, Lune 0.11, StyLua 2.5.2, Selene 0.32 | In `tools/`, all work |
| Codex CLI 0.163 (`C:\Users\User\AppData\Local\OpenAI\Codex\bin\896a0166b774037a\codex.exe`) | Callable (`--version` OK) |

**Not installed (would need the owner's OK to download):** `luau-lsp` (type checking, open source, JohnnyMorganz/luau-lsp). It is the most useful missing tool.

## 9. Exact prompt to start Codex
From the repo root:
```
"C:\Users\User\AppData\Local\OpenAI\Codex\bin\896a0166b774037a\codex.exe" exec -C "C:\Users\User\Desktop\KuwaitParkour\BSC_project_full" "Continue BSC Island development. Read docs/DEVELOPMENT_HANDOFF.md first, then CLAUDE.md and BSC_RESUME.md. Work on branch dev/v54-labs-cartride from the latest commit. Follow section 5 (next steps) in order, respect section 6 (owner decisions) and ask before anything in section 7. Build with the commands in section 2, never overwrite older .rbxlx builds (next build is KuwaitParkour_v57.rbxlx), commit after each verified milestone, and never publish."
```
Or paste the same text into the existing Codex thread `01a14bdc-a4d3-7360-a7e5-eacb9a8c4924` in the Codex app.
