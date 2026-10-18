# KuwaitParkour — Knowledge Base (working notes)

Short, practical status for the next session. History of changes lives in `CLAUDE.md`.
Latest local build: `Desktop\KuwaitParkour\KuwaitParkour_v31.rbxlx` (not published). Source backup: `Desktop\KuwaitParkour\backup_v31_20261017`.

## Systems and their status
| System | Files | Status |
|---|---|---|
| Island hub (Synty art, street, plaza) | tools/world/island.luau, tools/island11.py, IslandTerrain.server | Tested in play (v25). Gateways slimmed in v29 (not re-screenshotted). |
| Per-area atmosphere | client/AreaAtmosphere | Tested: island, campus, HQ, lab, exam, course zone 7, cell switch correctly. |
| Parkour 100 levels + quizzes + fall recovery | parkour9.py, Main.server, Obstacles.server | Tested: automated run to stage 100, fall recovery zones 3-8. |
| Return from course | LeaveCourse.client, Main (LeaveCourse remote), island11.course_finish_exit | Button tested; finish portal built but not walked into. |
| Puzzles (order/simon/ghost bridges) | Obstacles.server | Tested: lit progress, solid bridge, 3 s flicker, closed 0.9. |
| Space stages | genmap7.k_moon, Zones.client | Tested: night sky + gravity 62 inside, restored outside. |
| Cart ride / rail hall (v30) | CartRide.client/server, cartride.py, Shared/CartRooms | Tested v30: boarding, 3 trailing cars 11/22/33 studs behind, glass-membrane rooms, curve warnings, exit button (moved right), avg 60 FPS / min 27 (one frame). Full ride end-to-end only in the offline sim. |
| Cell train | CellTrain.client, celltrain.py | Tested: 4 cars, moves ~16 studs/s, brighter world. New organelles not individually inspected. |
| Research lab (RP, projects, batches) | Lab.server/client, Shared/LabData, Shared/Batches, island11.research_lab | Tested: microscope/gel/PCR answers, token replay, cooldown, PCR anti-speed, buy + effect + respawn, batch tag, board. |
| Exam hall | ExamHall.server, Questions.luau | Tested v22. Validate questions with tools/validate_questions.luau. |
| Arcade (v30) | Arcade.server, Minigames/* | Tested v30 per module: ATP combo/radicals/cleanup, Sweeper 3 s warm-up + inhibitor pad + cooldown + substrate, Petri waves + antibiotic regrow. Tier 1-3 rises per round, resets after 30 s empty. Full multi-player rounds not tested. |
| Campus | genmap5.py, campus9.py | Stairs walked v28. v30: facade perforations on a grid (rng use unchanged, diff = only Stone114b removed), HQ portal subtitle Arabic-only. Restaurant layout NOT reworked (cafeteria z~130 is a glass line + garden, not open floor). |
| Challenge center (v30) | QuizCenter.server/client, QuizBank, QuizPractical, island11.quiz_center | Tested v30: 9 kiosks, menu/unlock/locked refusal/bad input, <1 s answer = wrong, token replay, 20 s reward cooldown, rewards + best saved in s.quiz, UI levels/question/feedback, portal in/out. |
| Saving | Main.server (UpdateAsync merge) | Never tested live (Studio has no DataStore for this unpublished file). research/upgrades/batch/quiz included in the merge (quiz = max per key). |

## Tools that are actually useful here
- Roblox Studio MCP (official): execute_luau (Edit/Server/Client), start_stop_play, screen_capture, user_keyboard_input, get_console_output, script_grep. Built-in skills: rbx-scene-analysis, rbx-perf-profiling, rbx-convert-to-streaming.
- Lune: offline place/model inspection (verify a build without Studio), question validator.
- StyLua + selene (19 known harmless `deprecated` warnings).
- Local skill: ~/.claude/skills/roblox-environment-art (art direction + loop, adapted from ColinEdw).
- No extra Roblox skills found in the user's skill catalog (search 2026-10-16).

## Decisions worth remembering
- Cart physics is client-side CFrame on RenderStepped (smoothest per DevForum); tune it with the offline track simulation before editing.
- Area looks are client-local Lighting tweens keyed by world position; space stages override while gravity < 100.
- Lab answers, costs and cooldowns are server-only; batches are edited only in Shared/Batches.luau (no in-game writes).
- Synty building fronts point along LookVector (FACE table in island.luau).
- Terrain fills that must replace grass need >= 4 studs depth.

## Known issues / not done (as of v30)
- Open: live DataStore + multiplayer (needs a private publish or Studio Server&Clients, which MCP cannot start), phone test, campus restaurant/corridor rework, museum / missions / discovery log, level-1 questions have no written explanation (shows the right answer only).
- StreamingEnabled is off (all worlds loaded); measure on a phone before changing.
- Two Roblox-side asset IDs fail to load (203785492, 81504106) — not referenced by our files.

## How to reproduce the key tests
- Load a new build into the open Studio WITHOUT the window (when another app covers it): copy Scripts.rbxm (rojo build of a Folder project with Server/Client/Shared) + Map.rbxmx into `<Studio version>\content\bsc\`, then Edit execute_luau `game:GetObjects("rbxasset://bsc/Map.rbxmx")[1]` and swap. Delete the folder afterwards. Never save over the newer file on disk from Studio.
- Minigames: Server execute_luau, require the module and call start(ctx) with a hand-made ctx {arena, alive, score, running, conns, tier, connect, addScore}.
- Challenge center: Client `ReplicatedStorage.QuizCenter:InvokeServer("start", spec, level)` then `("answer", token, index)` after >1 s.
- Play, then Server execute_luau: teleport onto `CartStart` to spawn a cart; Client: user_keyboard_input W to drive.
- Course run: Client auto-answer on `QuizAsk`, Server step through `Checkpoint_N` (land off-centre: some pads hold a Button).
- Lab: Client `ReplicatedStorage.Lab:InvokeServer("slide")` then `("answer", token, kind)`.

## v31 test log (2026-10-17, Studio solo play, real input via MCP mouse/keyboard)
- Specialties Train: one ▶ press -> 35 with no input; ＋x5 -> 90, auto-slowed to ~61 in a U-turn; ⏸ 72->0 in ~4 s, still
  seated, cars attached; resume + S x3 -> 45; full ride 135 s to an automatic stop + end card; avg 60 FPS (min 22.8, one
  frame); room facts fired in order; "back to island" -> spawn y 3.7; death mid-ride cleans train/cars/UI; Exit -> platform;
  "again" -> new train seated.
- Exam hall, sequence puzzle q54, food order, HQ café prompts/seats, LeaveCourse while falling, cell train exit: all passed.
- Not tested: multiplayer (MCP can only start solo play), live DataStore, phone, full parkour walk 0->100 after v31.

