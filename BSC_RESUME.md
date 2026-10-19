# Resume here

## Current state (2026-10-19, v44)
- Work only in `C:\Users\User\Desktop\KuwaitParkour\BSC_project_full`, branch `dev/v44`.
- Owner-authorized modular north prototype: separate flat/tiered classrooms, atrium, envelope, inherited stairs/levels.
  Visual references are documented; game layout is C, not a verified real room/stair/club plan.
- Backup: `Desktop\KuwaitParkour\backup_before_v44_20261019`. Build: `Desktop\KuwaitParkour\KuwaitParkour_v44.rbxlx`.
- North863 parts, net+107. Other worlds and scripts unchanged; south only has the necessary existing red-bridge opening.
- Studio solo QA passed rooms/garden paths/both stair cores/bridge/seats/rails/camera and all12 Travel routes.
  All63 script sources match v43. Full evidence and six screenshots: `docs/north_v44_report.md`.
- Studio was reopened with owner permission after MCP disconnected; tab `KuwaitParkour_v43.rbxlx` now has v44 geometry,
  unchanged v43 scripts, Edit mode and default viewport. Do not close Studio.
- Direct supervisor contact via existing ChatGPT browser session was verified; the Git report remains the fallback.
- **Wait for the emperor's prototype feedback. No further features, publishing, merging, or StreamingEnabled changes.**
- Outstanding: human multiplayer, real phone, published persistence, and real room/stair/elevator locations.

The older notes below are historical; the current state above and the owner's latest instructions take precedence.

## State (2026-10-18)
- **Version:** v41 on branch `dev/v41` (stacked: v37 → … → v41). It is stable; see BSC_PROGRESS.md. Codex handoff: CODEX_HANDOFF.md
- **Not published.** The live game is still the v20+NPC update (PRIVATE, PlaceId 97395090487008).
- **Studio:** two windows are open (v34, v35). The v35 window has the v37 map and scripts hot-swapped in, unsaved.
  Close those windows only if needed.

## Next steps, in order
1. **Owner:** review v37.
   - Run the manual tests in BSC_RELEASE_CHECKLIST.md: phone layout, and 2 players in Last Cell Standing.
   - Open the pull request from `dev/v37`.
2. ~~Lab Rush~~ done in v38. Next:
   - Reuse the Arcade loop: add a `mode = "coop"` path with a shared team score.
   - Add a new arena via chaos_gen.
3. ~~Puzzle rooms~~ done in v39 (Cell Control Room).
4. ~~Game Show (picture + category)~~ done in v40. Still to add: the sound and memory modes.
5. ~~Light Microscopy~~ done in v41. Next, per the supervisor: phone and team tests of v39–v41, fix bugs, polish the whole experience (no new side projects).

## How to hot-swap a build into the open Studio
1. Copy `Map.rbxmx` and a Folder-bundle `Scripts.rbxm` into `<Roblox version>/content/bsc/`.
2. Run `game:GetObjects("rbxasset://bsc/...")` and swap the result into the place.
3. Delete `content/bsc` afterwards.

Never run several screen captures in parallel: Studio crashed once doing that.

## Collaboration (owner, 2026-10-19)
- Codex (OpenAI) works on this project too. Codex thread id: `01a14bdc-a4d3-7360-a7e5-eacb9a8c4924`.
  When Claude's limit is close, hand off to that thread: point it at BSC_RESUME.md and the dev branch. Also ask it which
  Roblox plugins/skills it recommends.
- The regular ChatGPT conversation is the supervisor (ideas, finds problems). The owner briefs it first; Claude contacts it
  only after the owner says so. Its advice never overrides the owner's rules (no publish, no deleting systems, no horror world).
- Gemini (Gemini desktop app, chat "التحكم في الحاسوب الشخصي") is on the team as a reviewer/content writer: it cannot touch local files or the private repo. It wrote the Game Show question bank.
