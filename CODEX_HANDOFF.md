# Handoff to Codex (from Claude Code)

## Current handoff: v44 (2026-10-19)
- The owner explicitly authorized a modular north-building development prototype after v43. No publish/merge approval.
- Branch `dev/v44`; local build `Desktop\KuwaitParkour\KuwaitParkour_v44.rbxlx`.
- Before-edit full backup `Desktop\KuwaitParkour\backup_before_v44_20261019` includes the v43 build.
- New generator `tools/north_campus44.py`: seven named modules, photo17 flat classroom and photo16 tiered lecture,
  skylit atrium and reference-inspired envelope. Evidence values distinguish visual references from C game placements.
- Kept inherited footprint, floor levels and stair locations. No real room numbers or new elevator/club locations.
- Only south change: opened the pre-existing blocked red-bridge junction at x=-50..-30, y=24..36, z=-30.
  The reason was explained to the owner before editing. All other south, garden and other-world geometry is unchanged.
- Studio restarted with owner authorization when MCP had no connection; no new login. Current target tab is
  `KuwaitParkour_v43.rbxlx`, containing v44 geometry and unchanged v43 scripts, in Edit mode with default viewport.
  Do not close Studio. Match the title with list_roblox_studios; session IDs are temporary.
- Studio QA: both classrooms, both garden routes, both stair cores all floors up/down without jumping, red bridge
  both directions, 12 atrium-edge collision tests, 5 camera positions and real seats passed. All12 Travel destinations
  reached their spawn; stage/coins remained0. No new game-script errors; known DataStore/UIBlox/asset warnings remain.
- North863 parts vs756, net+107; 951 descendants. All63 script sources match v43. StreamingEnabled remains false.
- Detailed results, performance limits and photos: `docs/north_v44_report.md`; supervisor report: `REPORT_FOR_CHATGPT.md`.
- Direct ChatGPT communication was actually verified through the existing browser chat after the earlier uncertain
  tool-only attempt: https://chatgpt.com/c/6ad11a54-7d40-83ed-988d-0252db67c42b . Existing session, no API key/new login.
  Browser is reliable here; read_thread can lag or show placeholders. Keep the Git report as the durable fallback.
- Codex can run local commands, Studio MCP and browser tools. Gemini contact was not tested in this version.
- Next: **wait for the emperor's prototype feedback. Do not add features.** Real-phone, multiplayer and published
  persistence tests are outstanding; private publishing still needs explicit approval.

Read `BSC_RESUME.md`, `BSC_ARCHITECTURE.md` and `BSC_MASTER_VISION.md` first. The owner's rules always win:
- never publish;
- never merge;
- never delete existing systems;
- no horror world.

## Where things are
- **Full local working copy** (code, Git, and the Rojo/Lune/StyLua/selene binaries):
  `C:\Users\User\Desktop\KuwaitParkour\BSC_project_full`.
  - Work there. It is on branch `dev/v44`.
  - Rebuild with the commands in `CLAUDE.md` § Build, run from that folder.
- **Branch:** `dev/v44`. Branches are stacked: v37 → v38 → v39 → v40 → v41 → v42 → v43 → v44.
- **Latest tested local build:** `Desktop\KuwaitParkour\KuwaitParkour_v44.rbxlx`.
- **Backups:** `Desktop\KuwaitParkour\backup_v42_20261019`. Make a new backup before you change anything.
- **Not in Git:** the tool binaries (Rojo 7.7.1, Lune 0.11.0, StyLua 2.5.2, selene 0.32.0), the generated
  `Map.rbxmx` and `Island.rbxm`, and the packs. Regenerate them with the commands in BSC_ARCHITECTURE.md.

## Done so far (each tested solo in Studio; see BSC_PROGRESS.md)
- **v37:** start in the south lobby, world menu, gym and Red Corridor fix, Last Cell Standing.
- **v38:** Lab Rush (co-op) and the arcade co-op mode. The Last Cell Standing shield was verified.
- **v39:** the puzzle-room framework and the first room, "Cell Control Room".
  - Each room is defined in `PuzzleRoomDefs/`, and puzzle types live in `PuzzleTypes/`.
  - **To add a room:** create a `PuzzleRoom_<id>` map folder (see `chaos_gen.cell_control_room`) and a def module.

- **v40:** BSC Game Show studio with Guess the picture and Category challenge. The content bank is
  `GameShowBank.luau`.

## Team
- **Gemini** (desktop app) reviews ideas and writes content. It cannot edit files.
- **ChatGPT** supervises.
- **Codex** is the primary developer after Claude's handoff.
- Never let two agents edit the same files at the same time.

- **v41:** the Light Microscopy lab: `LightMicroscope.client`, `shared/MicroscopyData` and `Lab.server` lm* actions.
  Tested with real clicks (see BSC_PROGRESS.md).

- **v42:** phone pass. Readable hint toasts, Game Show HUD, bigger microscope controls and drag-to-pan.
- **Codex check (2026-10-19, ChatGPT desktop app → Codex → "This computer", Full access):**
  - Codex runs local commands: `git log`, `rojo --version`, `selene --version`.
  - It read `CODEX_HANDOFF.md` from `BSC_project_full`.
  - It reached Roblox Studio through MCP: it listed `KuwaitParkour_v37.rbxlx` and ran read-only Luau in Edit mode
    (Map descendants = 27366).
  - So Codex can fully take over the coding and Studio work.

## Next steps after v42 (supervisor's order, 2026-10-19)
Done in v42: the phone pass and Gemini's science review of the microscope.

Next:
1. **Real multiplayer:** mostly done in v42 (see BSC_PROGRESS.md). Still open: a full co-op Lab Rush, a full two-player
   puzzle solve, and real disconnects. To run it in Studio: Test → Start Test Session → Server and Clients, then in
   the server window Test → Add Clients, once per client.
   - Check the Arcade games, puzzles, Game Show and microscope.
   - Check joining and leaving mid-round, sync, rewards with no doubles, and round reset.
   - This needs the Studio UI. It was blocked this session because a Windows TextInputHost popup was in front.
2. **Portrait and tablet:** done in v42. iPad is OK, and portrait does not apply because the game is landscape-only.
3. **Final QA:**
   - all portals and the world menu;
   - saving;
   - performance;
   - errors in Output.

   Then write a release-readiness report for the owner. No publish and no merge.

## Next task (supervisor, 2026-10-19)
Test v39–v41 on a phone and with real teams, fix what breaks, and improve the whole experience. Do not open new
side projects.

Testing the UI needs real clicks: `execute_luau` cannot click, so use the Studio MCP tool `user_mouse_input` with
viewport coordinates (AbsolutePosition, without the gui inset).

## (done in v41) Light Microscopy lab (directive section 7)
Extend the existing Lab world: `Lab.server`/`Lab.client` and `shared/LabData`. Requirements:
- the microscope parts;
- slide handling;
- objective lenses and magnification;
- focus and light;
- samples;
- a notebook;
- mistakes explained;
- a practice mode and a test mode.

Use Arabic and English terms, and add a "simulation, not the real procedure" note. It needs expert review before
it's called final.

Also still open for the Game Show: the sound mode (licensed clips only) and the memory mode.

## (done in v40) BSC Game Show (directive section 6)
**Supervisor's direction (ChatGPT, 2026-10-19).** Do not build every mode at once.
1. **The studio itself:**
   - a host stage;
   - two team screens;
   - a big scoreboard;
   - lighting and effects;
   - a team and category system.
2. **Two complete modes:**
   - *Guess the picture:* a blurred poster or a licensed cartoon/science image that is revealed gradually.
   - *Category challenge:* mixed questions on games, consoles, science and general culture.
3. **Later:** guess the sound (licensed clips only), then memory.

**Rules:**
- Solo or team play.
- No forced timer.
- Arabic and English.
- The question/content bank stays separate from the code.
- Clear points and results.
- No protected images or music without a licence.

After that: the Light Microscopy lab.

## Open checks (supervisor)
- Two players solving the same puzzle at the same time, and a player leaving mid-puzzle.
- Hint text and prompt buttons on a phone screen.
- v39 is a stable checkpoint, but it is NOT release-ready until the phone and group tests pass.

## How to test (the owner can't watch)
- **Arcade:** the Studio-only workspace attribute `ArcadeForce = "<id>"` forces a game. Clear it afterwards.
- **Bot pattern:** from a client, move the character next to a ProximityPrompt, then call
  `prompt:InputHoldBegin()` / `InputHoldEnd()`. Read the board and screen TextLabels to decide what to press.
- **Hot-swap into an open Studio:** see BSC_RESUME.md.
- Before claiming anything is done, run the checklist in `BSC_RELEASE_CHECKLIST.md`.
