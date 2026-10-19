# Handoff to Codex (from Claude Code)

Read `BSC_RESUME.md`, `BSC_ARCHITECTURE.md` and `BSC_MASTER_VISION.md` first. The owner's rules always win:
- never publish;
- never merge;
- never delete existing systems;
- no horror world.

## Where things are
- **Branch:** `dev/v39`. Branches are stacked: v37 → v38 → v39.
- **Last stable build:** `Desktop\KuwaitParkour\KuwaitParkour_v39.rbxlx`.
- **Backups:** `Desktop\KuwaitParkour\backup_v39_20261019`. Make a new backup before you change anything.
- **Not in Git:** the tool binaries (Rojo 7.7.1, Lune 0.11.0, StyLua 2.5.2, selene 0.32.0), the generated
  `Map.rbxmx` and `Island.rbxm`, and the packs. Regenerate them with the commands in BSC_ARCHITECTURE.md.

## Done so far (each tested solo in Studio; see BSC_PROGRESS.md)
- **v37:** start in the south lobby, world menu, gym and Red Corridor fix, Last Cell Standing.
- **v38:** Lab Rush (co-op) and the arcade co-op mode. The Last Cell Standing shield was verified.
- **v39:** the puzzle-room framework and the first room, "Cell Control Room".
  - Each room is defined in `PuzzleRoomDefs/`, and puzzle types live in `PuzzleTypes/`.
  - **To add a room:** create a `PuzzleRoom_<id>` map folder (see `chaos_gen.cell_control_room`) and a def module.

## Next task: BSC Game Show (directive section 6)
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
