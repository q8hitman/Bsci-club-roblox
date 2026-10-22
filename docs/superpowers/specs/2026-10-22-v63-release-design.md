# BSC v63 release improvement design

## Owner objective
Continue the existing BSC experience, preserve its accumulated work, and create a new version. Improve laboratory scientific correctness and glitches for school pupils through university students; improve the educational cell tour; make each specialty railway valley attractive and relevant with high quality ground treatment; improve minigame design/mechanics and parkour playability, enjoyment and educational value; prevent repetitive questions. Target release soon, with quality inspired by major Roblox experiences. A build is not a release approval.

## Source and preservation
Repository: BSC_project_full; initial branch dev/v54-labs-cartride. v62 is the latest disk build. Five inherited modified files contain Claude's partial v63 work and must survive. Snapshot: ../backup_before_codex_v63_20261022. Work on dev/v63-release-polish in place because this is the supplied active generator project with local ignored dependencies/assets. Generated Map.rbxmx and CartScenery must be rebuilt from their generators. Do not replace approved campus layout, delete activities, add tycoons, or publish.

## Design decisions (implementation judgment)
- Fix evidence-backed correctness and lifecycle failures first; preserve existing scientific benches, rewards, progression and 100 parkour stages.
- Laboratory: explicit observable steps and useful error feedback; accurate science with sources and clearly identified simulation simplifications. Review the actual server state machine and client actions; test wrong-order, cancellation, death, two owners, restart and reward boundaries.
- Cell tour: accurate short Arabic explanation plus English structure names; distinguish cytosol from cytoplasm, stop codons from amino-acid codons, and model scale from biological scale. Reading must be possible at the rider's pace, including touch.
- Specialty tour: preserve eight official specialties and route. Improve silhouettes, landscape material transitions and staged hero subjects per valley, using the existing art kit. Ground, path and prop collision must stay clear of the rider envelope. Review from the train, not only aerial views.
- Minigames: inspect each existing activity, reproduce failures, correct route/entry/state/UI problems, then improve visibly weak lobbies and arenas. Fun claims require actual play, including multiplayer where applicable.
- Parkour: retain 100 stages and no visible timer; verify reachable transitions, moving platforms, puzzle ownership and recovery. Improve confusing stages using visual cues and scientific explanations without blocking movement with text.
- Questions: count actual exposures rather than a permanent boolean. Deduplicate question text in a draw; avoid immediate repeats when another eligible item exists and cycle fairly after the finite bank is exhausted. Mark only questions actually displayed. Group modes minimize repeat burden; an unseen question for every mixed-history participant is not always possible. Persistent cross-rejoin history and bank expansion remain part of the audit, not silently claimed done.

## Evidence gates
1. Reproducible failing checks before gameplay fixes, then passing checks and relevant existing regression suites.
2. Science references recorded next to the reviewed content; distinguish modeled simplifications.
3. Fresh rebuilt v63, identify contents of target Studio before loading. Inspect Output and actual runtime hierarchy.
4. Relevant single-player/lifecycle/two-client/device checks; three useful visual angles for important areas, iterate on defects.
5. Completion matrix for every owner requirement, known issues, untested real phone and live persistence. Do not call the goal complete while any requested area is still unverified.
