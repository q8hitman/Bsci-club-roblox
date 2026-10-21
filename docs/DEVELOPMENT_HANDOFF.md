# BSC Island: development handoff (v53, 2026-10-21)

For whoever continues: Claude Code, Codex, or a person. **Continue this project. Do not restart or redesign it.**

## 1. Where things are
| | |
|---|---|
| Repo | `C:\Users\User\Desktop\KuwaitParkour\BSC_project_full` (GitHub `q8hitman/Bsci-club-roblox`) |
| Branch | `dev/v53-release-push`, created from `dev/v52-world-structure` at `7172e2e` |
| Commits | `b48b181` Grand Tour → `30708f7` HUD/camera/cliffs → `2417726` Cell Train → `07c875e` Gram stain → `b83c473` First Day (`git log --oneline -8`) |
| Latest build | `Desktop\KuwaitParkour\KuwaitParkour_v53.rbxlx` (not published). v52 and every older build and backup are untouched. |
| Studio | One session titled `KuwaitParkour_v53.rbxlx`. Its scripts and map were hot-swapped to the latest code; **unsaved and not needed**, because the file on disk is newer. |

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
| **First Day at the College**:<br>• 4 optional steps (HQ, Arcade, Lab, train) with travel buttons<br>• `firstday` achievement (+50 coins, title) | Lune tests all PASS | Card shows `0000`; a real click on the HQ step travelled there and ticked it (`1000`) | no | Layout checked in the emulator only |

Smaller items:
- The welcome hint about a timer was replaced, because the owner removed the visible timer.
- `AreaAtmosphere` and `Feedback` now test the cart region before the cell world.

## 4. Partially done / known issues
- **Cart valleys are still fairly empty between the hero pieces** (flat floors). Next art steps:
  - rolling ground (half-buried large parts, or runtime Terrain like `CampusTerrain`);
  - denser props near the rails;
  - a petri-dish rim in Microbiology.
- **Cart part budget:** the place has about 32,000 parts (v52 had 28,200). Check frame rate on a real phone before adding more.
- **The Arabic Gram answer text** and the other lab text use two-line Arabic/English. Other panels may still mix both languages on one line, which garbles it; split those into two lines too.
- **Not tested at all:**
  - multiplayer (2+ clients) for any v53 change;
  - a real phone;
  - live DataStore persistence of the `firstday` achievement.
- **Not built** (the research proposals need owner approval or come later):
  - Calm Tour vs. Thrill Run;
  - Vesicle Express;
  - Biotechnology Studio;
  - shared friend carts;
  - continuing the ride from the last stage.

## 5. Next steps, in priority order
1. **Multiplayer check**: Studio → Test → Server + 2 Clients. Check:
   - two players riding the cart at once see each other's train;
   - the Cell Train;
   - the Gram stain for two players at once;
   - the First Day card.
2. **Cart world art pass:** ground relief, prop density, a petri rim. Keep the part budget in mind.
3. **Arcade minigames quality pass:** PetriFloor, ATPRush, EnzymeSweeper, LastCell, LabRush, Virus Tag, Exam Hall, Game Show, Puzzle Rooms, Micro Racers, Laser Escape. Cover the results screens, feedback and fairness. Don't merge or remove any of them.
4. **Gel electrophoresis and PCR deepening** (research update §3):
   - gel: load the wells, set the voltage, read the ladder;
   - PCR: a copy counter and primer choice.
5. **Lab room 3D dressing:** benches, pipettes, a centrifuge, a gel tank; move the sign off the benches.
6. **100-stage obby:** a stage-variety and clarity pass. Keep all 100 stages and no visible timer.
7. **Release checklist:**
   - phone test by the owner;
   - private publish, only with the owner's approval.

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
"C:\Users\User\AppData\Local\OpenAI\Codex\bin\896a0166b774037a\codex.exe" exec -C "C:\Users\User\Desktop\KuwaitParkour\BSC_project_full" "Continue BSC Island development. Read docs/DEVELOPMENT_HANDOFF.md first, then CLAUDE.md and BSC_RESUME.md. Work on branch dev/v53-release-push from the latest commit. Follow section 5 (next steps) in order, respect section 6 (owner decisions) and ask before anything in section 7. Build with the commands in section 2, never overwrite older .rbxlx builds (next build is KuwaitParkour_v54.rbxlx), commit after each verified milestone, and never publish."
```
Or paste the same text into the existing Codex thread `01a14bdc-a4d3-7360-a7e5-eacb9a8c4924` in the Codex app.
