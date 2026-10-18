# Handoff to Codex (from Claude Code)

Read `BSC_RESUME.md`, `BSC_ARCHITECTURE.md` and `BSC_MASTER_VISION.md` first. The owner's rules always win:
- never publish;
- never merge;
- never delete existing systems;
- no horror world.

## Where things are
- **Branch:** `dev/v38` (stacked on `dev/v37`). Last stable build: `Desktop\KuwaitParkour\KuwaitParkour_v38.rbxlx`.
- **Backups:** `Desktop\KuwaitParkour\backup_v37_20261018`. Make a new backup before you change anything.
- **Not in Git:** the tool binaries (Rojo 7.7.1, Lune 0.11.0, StyLua 2.5.2, selene 0.32.0), the generated
  `Map.rbxmx` and `Island.rbxm`, and the packs. Regenerate them with the commands in BSC_ARCHITECTURE.md.

## What v38 added (tested solo in Studio; see BSC_PROGRESS.md)
- **Lab Rush**, the co-op arcade game: `server/Minigames/LabRush.luau`, with the arena from `chaos_gen.lab_rush`.
- **Arcade co-op mode** (`mode = "coop"`): the round ends when `ctx.teamDone` is set, and every player wins together.
- **Last Cell Standing shield:** verified. With the shield on, 13 hazards hit the player and produced 0 pushes.

## Next task
Co-op puzzle rooms, as specified in the owner's directive section 5.C:
- data-driven rooms;
- a hint system;
- correct reset;
- no soft-lock when a team member leaves.

After that: the BSC Game Show, then the Light Microscopy lab.

## How to test (the owner can't watch)
- Studio-only hook: set the workspace attribute `ArcadeForce = "<id>"` to force a game, and clear it afterwards.
- Bot pattern: from a client, call `prompt:InputHoldBegin()` / `InputHoldEnd()` after moving the character next to the
  prompt. It reads the order board text.
- Before claiming anything is done, run the checklist in `BSC_RELEASE_CHECKLIST.md`.
