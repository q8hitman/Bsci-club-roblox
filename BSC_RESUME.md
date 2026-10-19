# Resume here

## Current state (2026-10-19, v47)
- Repo only; dev/v47. Backup backup_before_v47_20261019. Supervisor accepted v46 and selected Micro Racers.
- Two-track manual racing,3laps, AI/multiplayer, boost/shield/spores/recovery/results/replay, server intent-only simulation.
- One-time20XP per track and racer2 title.326parts/386descendants added; old Workspace identical after excluding Racers47.
- Keyboard3laps both, XR actual Touch3laps cell, two actual clients/full races/replay/lifecycle/security/timeout passed.
- Fresh build KuwaitParkour_v47.rbxlx opened in NEW Studio titledv47, Edit/default viewport. Prefer it; keep all old sessions open.
-75sources, no test fixtures in build/Studio, Streaming=false. Static/Lune/question banks passed; selene0errors/26knownwarnings.
- Docs/photos/raw results: docs/racers_v47_report.md and docs/v47/. No live persistence or real-phone claim.
- Direct report to supervisor for review and v48 scope. No publish/main merge, secrets, horror or old-system deletion.

## Historical state (2026-10-19, v46)
- Work only in `C:\Users\User\Desktop\KuwaitParkour\BSC_project_full`, branch `dev/v46`.
- v45 was accepted developmentally; supervisor selected Museum46. Owner authorized continued development and direct reports.
- Backup `backup_before_v46_20261019`; local build `Desktop\KuwaitParkour\KuwaitParkour_v46.rbxlx`.
- Eight fictional museum exhibits connected east of Campus, server-verified one-time10XP each and all-eight cosmetic title.
- Evidence/science/photos/limits: `docs/museum_v46_report.md`, `docs/museum_v46_science.md`, `docs/v46/`.
- Solo/UI/phone, two actual clients80XP vs10XP, death+travel session rejection, ground-level route and all12 destinations passed.
- NEW v46 Studio session renders normally; old v43 session has black3D. Both remain open in Edit; v46 uses the default viewport.
  Prefer v46 by title, obtain current IDs from list_roblox_studios. Do not close either session.
- Original Workspace unchanged excluding added Museum46;216newparts,71script sources. No QA scripts left. Streaming false.
- Source fixtures tools/studio_tests/museum46.*.luau use ExecuteMultiplayerTestAsync(2,"Museum46").
- Gemini received request but returned no usable review; supervisor approved alternative scientific text review.
- Send direct supervisor report and choose next authorized feature. No publishing/merging/real secrets/horror.

## Historical state (2026-10-19, v45)
- Owner explicitly said to send the report to the supervisor and continue; this supersedes the previous wait state.
- Work only in `C:\Users\User\Desktop\KuwaitParkour\BSC_project_full`, branch `dev/v45`.
- BSC Passport implemented in the existing Profile menu: cosmetic XP/levels, five new achievements/titles, optional
  existing batch selection, and three Monday00:00UTC weekly challenges. No new coin/research economy or geometry.
- Backup `backup_before_v45_20261019`; build `Desktop\KuwaitParkour\KuwaitParkour_v45.rbxlx`.
- Solo, two Studio clients, iPhoneXR UI, migration/merge/rollover/duplicate claims and all12 Travel routes passed.
- Evidence/limits/photos: `docs/passport_v45_report.md`. Published DataStore and real phone remain untested.
- Studio stays open in Edit/default viewport: titlev43, geometryv44, scriptsv45. No QA scripts remain in the place.
- Send report directly to ChatGPT supervisor and continue one complete feature at a time. No publishing/merging.
- StudioTestService:ExecuteMultiplayerTestAsync now verified; see tools/studio_tests/passport45.*.luau for test fixture.
  Studio MCP command-context require can see a separate module cache: use a normal temporary Script to inspect game Profiles.

## Historical state (2026-10-19, v44)
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
