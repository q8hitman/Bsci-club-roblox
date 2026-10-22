# Claude handoff: BSC Island v68 (2026-10-22)

Status and handoff only; this does NOT mean the game is finished or ready to release. Nothing has been published.

## 1. Where things are
| | |
|---|---|
| Repo | `C:\Users\User\Desktop\KuwaitParkour\BSC_project_full` (GitHub `q8hitman/Bsci-club-roblox`) |
| Branch | `dev/v63-release-polish` (pushed, clean). Not merged into `main`. |
| Latest build | `Desktop\KuwaitParkour\KuwaitParkour_v68.rbxlx` (v63..v67 and every older build untouched) |
| Studio | The owner's open session is **v63** with temporary hot-swapped v68 content. It must NOT be saved; open v68 from the File menu instead. |
| Older handoffs | `docs/CLAUDE_HANDOFF_v63_2026-10-22.md` (ChatGPT/Codex session), `docs/DEVELOPMENT_HANDOFF.md`, `docs/FINAL_VERSION_AUDIT_v62.md` |

## 2. Owner preferences (keep)
- Reply in simple Kuwaiti Arabic. One task at a time, then stop and report.
- Never publish (privately or publicly) without explicit approval. Never type passwords. Never overwrite a build; each build gets a new vN.
- Tycoons come only AFTER the final version (looks and gameplay settled), with their own events.
- Quality bar: top Roblox games (Pressure, Doors, top tycoons). The owner judges by looks in playtests and screenshots.
- On the map: names only. Explanations go on screen and fade in and out. No text clutter.
- Never build the horror world.

## 3. Done since v62 (all committed; most checked in Studio)
| Area | Change | Evidence |
|---|---|---|
| Audit A | Museum and cell-train spawns turned 180°; HQ and lab DNA helixes moved out of view lines; Game Show team screens on the side walls and the mascot moved; exam hall runner fixed and dressed; museum guide in teal | Studio captures from the spawns |
| Virus Tag | Infected-tissue arena (`extras10.virus_arena`): giant virus, red blood cells as cover, white blood cells, antibodies, membrane wall; spawn z+48 | Spawn-camera capture. **A full round (needs 2 players) has not been played.** |
| Racers lobby | Racing pit (`racers47.pit_lobby`): garage, display karts, track mini-maps, floodlights | Prompts verified |
| Laser Escape | Own briefing hall (`laser48.entrance_hall`); the arcade gateway is now `Portal|Laser` | Travel, gateway, door prompt and leaving all tested |
| Codex/ChatGPT work | Reviewed and committed: lab session guards, CellStops science, QuestionHistory counts and recency | All Lune tests, selene 0 errors, typecheck at its 61 baseline |
| Cell train | Tap-to-continue reading mode by default (tap / Space / Enter / gamepad A), toggle to timed 12 s | **Not tested in Studio** |
| Micro Racers | `car.paint` slot per car sent in snapshots; 8 distinct paints; colour dot on the leaderboard | Lune racing tests pass. **No race seen in Studio.** |
| Lab | Click or tap the object itself (ClickDetector `LabClick` in `Labs54.bind`, distance re-checked on the server); hover outline and label in `Bench54.client`; E range 9 → 7 | **Not tested in Studio** |
| Specialties Train | `tools/cart_biomes63.py`: per-valley skyline behind the walls, a designed ground, a themed midground (8 worlds) | Captures of all 8 valleys from the train |
| Micro valley | Glass petri-dish walls and rim, flat lobed colonies (`flat_colony` in `cart_tour53`), big 3D bacteria, biofilm, streak plates, membrane tunnel (`micro_tunnel`) | Captures; clearance 0/0 |

## 4. Open list (priority order)
1. **Museum** (owner: some exhibits make no sense or are unclear). Started in this session; see the commits after this file.
2. Test in Studio: tap reading on the cell train, kart colours in a real race, lab click-to-use.
3. Owner's feedback on the 8 valleys (micro was redone twice; the others have had one pass).
4. Phone performance. Micro is ~6.5k client parts and plant/agri ~5.5k; check FPS on a phone.
5. Multiplayer tests: Virus Tag, arcade, Game Show, Racers, Lab Rush, puzzle room.
6. Full Specialties ride (~32 min) and the cell-train nucleus detour while riding.
7. Then the final version, then tycoons.

## 5. How to work here (verified)
- Build: `python tools/genmap9.py`, then `git checkout -- kuwait-parkour/src/shared/LaserData.luau` (the generator only reformats it), then `tools/rojo/rojo.exe build kuwait-parkour/default.project.json -o ../KuwaitParkour_vNN.rbxlx`.
- Checks:
  - `selene src` (from `kuwait-parkour/`): baseline 0 errors / 27 warnings.
  - Lune tests: `test_questions63`, `validate_questions`, `test_passport45`, `test_museum46`, `test_racers47`, `test_racers60`, `test_laser48`.
  - `bash tools/typecheck.sh`: 61 known false positives.
- Hot swap into Studio:
  1. Run `scratchpad/swap.sh [map]`. It builds `.rbxm` files into `%LOCALAPPDATA%/Roblox/Versions/version-4f087c32742644ab/content/bsc`.
  2. In Edit mode, run `game:GetObjects("rbxasset://bsc/x.rbxm")` and swap the Map / Client / Server / Shared folders.
  3. Play.
  4. Delete `content/bsc` when done.
- Cart valleys stream on the client, built from `Shared/CartScenery/V1..8`. Edit only through the generators. The clearance filter prints `cart underground points` and `cart clearance`; both must be 0.
- Studio camera captures: bind a RenderStep at `Enum.RenderPriority.Last.Value + 10` that forces Scriptable every frame (the MCP resets the CameraType). Wait about 10–20 s for valley streaming.
- If the owner's Studio is in Play mode, ask before stopping it.
- In bash, heredocs with Python sometimes fail. Write scripts to the scratchpad with the Write tool and run them from there.

## 6. Not verified
A real phone, several players over a network, DataStore on a live server, the full Specialties ride, and the three playtest fixes that are not yet tested in Studio (cell-train tap reading, kart colours, lab click-to-use).
