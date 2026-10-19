# Resume here

## Current state (2026-10-19, v43)
- Work only in `C:\Users\User\Desktop\KuwaitParkour\BSC_project_full`, branch `dev/v43`.
- v43 adds Arabic activity descriptions to the 12 existing world-menu cards and marks Arcade **مقترح للبداية**.
- Backup: `Desktop\KuwaitParkour\backup_before_v43_20261019`. Build: `Desktop\KuwaitParkour\KuwaitParkour_v43.rbxlx`.
- Desktop and iPhone XR landscape passed; all 12 card routes and locked Zone 2-8 portals passed in solo Studio Play.
- Studio stays open on `KuwaitParkour_v37.rbxlx`, with v42 content plus the tested v43 WorldMenu script; currently Edit,
  default viewport. Do not close Studio.
- **Wait for the emperor's feedback. No further features, publishing, merging, or StreamingEnabled changes.**
- Reports: `BSC_PROGRESS.md` and `REPORT_FOR_CHATGPT.md`; the owner relays the supervisor's replies.

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
