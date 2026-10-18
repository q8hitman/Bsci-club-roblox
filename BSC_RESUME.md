# Resume here

## State (2026-10-18)
- **Version:** v37 on branch `dev/v37`. It is stable; every item in BSC_PROGRESS.md was tested.
- **Not published.** The live game is still the v20+NPC update (PRIVATE, PlaceId 97395090487008).
- **Studio:** two windows are open (v34, v35). The v35 window has the v37 map and scripts hot-swapped in, unsaved.
  Close those windows only if needed.

## Next steps, in order
1. **Owner:** review v37.
   - Run the manual tests in BSC_RELEASE_CHECKLIST.md: phone layout, and 2 players in Last Cell Standing.
   - Open the pull request from `dev/v37`.
2. **Batch 2: Lab Rush (co-op).**
   - Reuse the Arcade loop: add a `mode = "coop"` path with a shared team score.
   - Add a new arena via chaos_gen.
3. **Batch 2:** co-op puzzle rooms, as a data-driven room list.
4. **Batch 2:** BSC Game Show. Reuse `QuizBank` and `QuizCenter`, and add round formats.
5. **Batch 3:** Light Microscopy. Extend the Lab world (`Lab.server`/`Lab.client`, `shared/LabData`).

## How to hot-swap a build into the open Studio
1. Copy `Map.rbxmx` and a Folder-bundle `Scripts.rbxm` into `<Roblox version>/content/bsc/`.
2. Run `game:GetObjects("rbxasset://bsc/...")` and swap the result into the place.
3. Delete `content/bsc` afterwards.

Never run several screen captures in parallel: Studio crashed once doing that.
