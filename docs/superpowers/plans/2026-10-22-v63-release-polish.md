# BSC v63 Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans; maintain evidence below while executing.

**Goal:** Fulfil every area of the owner's release improvement objective in a new verified version.
**Architecture:** Keep generator-owned geometry and existing server-authoritative gameplay. Correct problems at their source and rebuild with Rojo; use Studio for runtime and visual evidence.
**Tech Stack:** Python generators, Luau, Lune, Rojo, Roblox Studio MCP.
**Spec:** ../specs/2026-10-22-v63-release-design.md

## Global constraints
Preserve inherited work and all 100 stages; no public/private publish in this work; no new economy or deleted systems; no tycoons; no visible parkour timer. Do not equate a local build with release readiness.

## Review focus
- Exhausted, duplicate, filtered and overlapping question banks; mixed player histories and abandoned sessions.
- Laboratory ownership/reward races and resets while holding equipment.
- Train text readability, death/exit cleanup and gaps on curved track.
- Arcade entry mixing with laser entry; multiplayer elimination/rejoin cleanup.
- Mobile controls and frame rate in dense areas, not just desktop screenshots.

## Task 1 — Current-state audit and questions
Files: server/QuestionHistory.luau, server/QuizCenter.server.luau, server/ExamHall.server.luau, tools/test_questions63.luau.
- [x] Snapshot current source and inherited modifications; identify Studio mode/version mismatch.
- [x] Reproduce repeated questions after exhaustion and duplicate text (four failing checks); locate premature batch marking.
- [x] Correct selection and exposure tracking, preserving pick/pickMany/mark/markAll interfaces.
- [x] Run deterministic regression tests and validate_questions.luau, lint changed scripts.
- [ ] Integration tests in Main.server.luau, GameShow.server.luau and QuizPractical, plus abandoned-quiz and partial-bank batch boundaries.
- [ ] Audit persistent cross-rejoin semantics and enlarge/review finite banks as needed.

## Task 2 — Laboratory
Files: server/Labs54.server.luau, client/Bench54.client.luau, shared/LabData.luau, tools/labs54.py, tools/studio_tests/labs54.server.luau.
- [ ] Read all bench transitions and compare scientific teaching with primary educational sources.
- [ ] Reproduce and fix concrete glitches with checks for order, cancellation, reward, distance, reset and concurrent owners.
- [ ] Runtime test all five benches and relevant older lab activities; inspect mobile presentation and PPE.

## Task 3 — Cell tour
Files: shared/CellStops.luau, client/CellTrain.client.luau, tools/celltrain.py.
- [ ] Correct sourced scientific inaccuracies and add readable learner-paced presentation.
- [ ] Verify every stop including nucleus, cars on curves, death/exit/reboard and touch controls.

## Task 4 — Specialty tour art
Files: tools/cart_tour53.py, tools/cart_concepts62.py, client/CartScenery.client.luau.
- [ ] Capture each valley from the train; identify silhouette, ground, scale and material issues.
- [ ] Improve each area's hero composition and ground treatment within streaming budget.
- [ ] Rebuild; verify clearance and complete full journey, then review each area visually.

## Task 5 — Minigames and parkour
Files: tools/chaos_gen.py, tools/arcade59.py, tools/laser48.py, tools/parkour9.py, existing corresponding server/client owners.
- [ ] Audit all activities; reproduce entry, lifecycle, mechanics and visual defects.
- [ ] Implement focused fixes and visual improvements; preserve existing rewards/interfaces.
- [ ] Play solo and multiplayer activities; traverse representative obstacle families and validate all stage transitions.

Named activity coverage: Petri Floor, ATP Rush, Enzyme Sweeper, Last Cell Standing, Lab Rush, Virus Tag, Micro Racers (both tracks), Laser Escape, Game Show, Cell Control Room, Exam Hall. For each record solo, multiplayer/lifecycle, touch and rider/player-view visual evidence as applicable.

## Task 6 — Build and release audit
- [ ] Complete and validate inherited museum/train spawn, guide, exam room and HQ changes.
- [ ] Generate Map.rbxmx, build KuwaitParkour_v63.rbxlx and run meaningful regression/lint checks.
- [ ] Load known build into target Studio, tour all destinations, collect visual and gameplay evidence.
- [ ] Write requirement-by-requirement completion report, explicitly keeping unresolved requirements open.

## Execution ledger
- 2026-10-22: Existing runtime v59 session lacks QuestionHistory and CellStops; do not use it as evidence for current sources. Another v58 session is in Edit.
- Ruling: work in the supplied existing repository with a full source snapshot and new development branch, preserving uncommitted v63 work and local generator assets.
- Ruling: owner directly authorized implementation and additions; proceed with corrections and existing art direction without an extra approval loop. Major artistic alternatives can be presented as reviewable scenes.
- Plugin Management: official Studio bridge, local art tools and web research already cover current needs; no duplicate Studio plugin installed.
- Builder check completed: strengthened question integrations/abandonment and cross-rejoin requirements, named activity checklist, all-eight-valley before/after rider views, optional deeper science detail, and exact-build identity evidence. None needs a user decision to proceed.
- Each of the eight valleys needs relevant hero subject, intentional ground/material transitions, clear sightlines and track clearance; no single valley substitutes for the complete art pass.
- Science accessibility: basic explanation plus optional deeper detail and learner-controlled reading. Laboratory simulation timings must be distinguished from authentic procedural order.
- 2026-10-22 first development build: ../KuwaitParkour_v63_dev.rbxlx SHA256 6F81045451EBB0B5F5E11121A71F88B400FD757E5B6BC1E3CF921CDDD63354C8. Opened via Studio File menu; new session 53282228-8c99-4579-8585-df3987a6db78. Confirmed QuestionHistory v63 and PauseReadingBtn source markers and CellStops. Later Labs54 edit is synced in Edit and requires a new disk build/hash.
- First Play: no observed project script exceptions; expected unpublished DataStore warning, Roblox UI warnings, asset failures 203785492 / 81504106 remain to audit.
- Cell tour: actual boarding works, corrected cytoplasm text captured; real PauseReadingBtn click freezes movement (0 studs over 1.2 seconds) with lesson visible. Exit while paused restores Custom camera, WalkSpeed 16, unanchors player, removes train and hides pause button. Full route, death/reboard, touch and optional detailed layer still open.
- Laboratory reproduction: duplicate gel buffer use raises surface an extra 0.5 studs; reset failed to restore position in source. Fix prevents duplicate fill, restores original CFrame, cancels fill tween on reset. Studio regression passed: repeatRise=0, resetError=0, height≈0.02.
- PCR lifecycle: reproduced an abandoned run awarding 8 research and overwriting the reset screen. Async work now verifies bench state, owner, living player and distance; delayed finish cannot reset a newer bench session. Added corresponding guards to gel/DNA delayed work. Studio PCR cancellation passed (0 research, READY), followed by successful completion (8 research) and completed-run restart rejection. Labs54 Selene: 0 errors/warnings/parse errors. Multiplayer ownership, death/respawn and full DNA/gel completion remain open.
- Offline checks passed: questions63 (6 groups), validate_questions (48 basic, 80 advanced, practical generators, Game Show banks), racers60, laser48, passport45; edited-script lint 0 errors/0 warnings. These do not substitute for runtime completion of the corresponding activities.

- Rebuilt v63_dev after laboratory lifecycle fixes: SHA256 45702B5C46B147F7B71FD9E1E272E5230A9F8EDEF3AFC1A395ACF8C1CFC92D78. Build passed; runtime evidence above used matching Labs54 source synced into Studio. Full rebuilt-place reload audit remains pending.

- Specialty art first pass: layered slate/concrete exhibit bases with specialty-coloured fascia, recessed joints and restrained footlights; reduced microbiology GrowthDot bloom. Generator-owned changes in cart_concepts62.py and cart_tour53.py, propagated to all eight V modules. Added 200 scenery parts total (34384); same 10704 route points, 84805 studs, 0 big clearance intruders, 0 uncovered underground points, parkour 0 violations. Existing WhaleTail small-part exclusion remains.
- Visual evidence: new v63 session f448a303-87e8-41f6-a0af-92e2a767631b, verified currentExperiment source marker and 26776 Map descendants. In Play, injected generated V1 exhibit rows only for visual QA; inspected growth exhibit from opposite side, rider-facing side and elevated three-quarter. Footing grounded, trim visible, no observed base clipping; this is ONE prototype review pass, not full all-valley approval. Full ground/hero art, remaining valley rider views, second clean pass and full journey remain open.
- Rebuilt development file after exhibit pass: SHA256 E8F424C2CEA232A75CC42155C364DD7FC7E4AC2AE74F729D6C93C670E1EA71D3. Studio Edit retains the pre-art loaded build; reload latest disk build for subsequent whole-place tests. Play-only ArtReview63 camera/UI changes are discarded when stopping Play.

- Owner requested one bounded task then stop to conserve usage. Completed PCR teaching-text clarification: accelerated simulation labelled on start and running screen, ideal amplification distinguished from absolute copy count and real efficiency. Selene 0/0/0; Rojo build passed; parsed built XML confirms all four new messages and removal of old absolute-count statement. This text-only change has not had a new visual/device review. Stopping here as requested; broader plan remains open.
- Verification correction: first XML check assumed ProtectedString and failed because Rojo stores Source as string. Corrected check compared both complete built script sources to disk and passed. The previous claim of a four-message XML check is superseded by this exact-source comparison.

- Next bounded task completed at owner request: corrected molecular specialty transcription/translation and stop-codon captions in generator source. Regenerated and rebuilt v63_dev; verified both captions occur once in CartTrack and built module exactly matches disk. Geometry checks unchanged: 0 big intruders, 0 uncovered underground points, 0 parkour violations. No new visual/readability run for this text-only change. Stop after this task; all broader open items remain open.
- XML verifier initially encountered a same-named object without a Source property. Corrected selection requires a Source property and passed the exact-module comparison; only the passing corrected check supports the result above.
