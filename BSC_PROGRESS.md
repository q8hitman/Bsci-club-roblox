# v48 — Laser Escape — 2026-10-19 (finished by Claude after Codex's limit ran out)

Branch `dev/v48`; before-edit backup `backup_before_v48_20261019` (Codex). Five fictional timing rooms at (-6000,300,-8000..-8400),
entrance gate in the Arcade lobby (`Laser48.Entry`). Codex wrote the plan, generator, rules, server and client; Claude
tested them in Studio and fixed what broke:
- **Room 4 (moving bridge) could not be crossed.** The server "carried" riders with `PivotTo` every 0.05 s, which fought
  client movement: MoveDirection dropped to 0 and anyone at the deck edge was dragged sideways. Now the anchored bridge
  gets a real `AssemblyLinearVelocity` (conveyor style) so the engine carries riders and they keep control; the movement
  guard still allows the carried distance.
- **Room 3 door opened for anyone who walked up to it** (the anti-crush "hold" also opened a closed door), making the
  pressure plate pointless. Now a character only keeps an already-open door open.
- **Room 3 door had a 3-stud gap at each side** (52 wide between walls 58 apart): widened to 57.8.
- **Plate signs in rooms 3 and 5 were solid at waist height** and blocked the walk from the checkpoint to the plate:
  raised above head height.

Tested in Studio (solo, real Humanoid walking, no teleports): full run rooms 1→5 with 0 failures (64 s); +40 Passport XP
once, coins/research unchanged; replay finished again (47 s) with XP still 40; standing in a red beam sends you back
to the room checkpoint (+1 retry); "الأركيد" exit returns to ArcadeSpawn and clears the HUD. Pure tests pass;
selene 0 errors / 26 known warnings; validator OK. No new game errors.
Not tested: two real clients in Laser Escape, phone layout of the Laser HUD, real phone, live DataStore.
Build `Desktop\KuwaitParkour\KuwaitParkour_v48.rbxlx`. Not published, not merged.

---

# v47 — Micro Racers — 2026-10-19

Supervisor accepted v46 and selected two-track racing. `dev/v47`; full before-edit backup `backup_before_v47_20261019`.
Two drivable tracks, Solo AI/multiplayer, three ordered laps, boost/shield/spores, recovery, ranks/results/replay.
Authoritative intent-only simulation; one-time20XP per track and racer2 title. Campus/old Workspace unchanged except the additive Racers47 subtree.
Keyboard Solo both tracks completed; phone XR actual Touch screen-button three-lap cell race completed. Two actual clients passed full races/replay/no duplicate XP, death/respawn/disconnect, queue reclamation, forgery denial and terminal cleanup. Timeout-only fixture shortened runtime duration; shipped races180s.
Source/static/pure checks passed; independent review P2s fixed/re-reviewed. Detailed report `docs/racers_v47_report.md` and images `docs/v47/`.
No publish/main merge; no real-phone/live persistence claim. Existing Studio sessions remain open. Local build KuwaitParkour_v47.rbxlx,75sources/326newparts; fresh titlev47 in Edit/default viewport. Test fixtures removed. Final racing sample~60FPS on this PC only; old worlds/Travel12/Museum regression passed.

---

# Progress log

## v46 (2026-10-19), branch `dev/v46`, NOT published or merged

Supervisor accepted v45 and selected the Biology Discovery Museum. Backup `backup_before_v46_20261019` includes v45.
Full report/photos: [museum_v46_report](docs/museum_v46_report.md); scientific review: [museum_v46_science](docs/museum_v46_science.md).

- Added fictional independent pavilion east of Campus and lit approach around parking;216parts/261descendants,58collidable.
- Eight playable model assemblies: microbes, enzyme, adaptation, photosynthesis, DNA, fictional patterns, agriculture, biotechnology.
- Balanced one-time10XP per exhibit and all-eight cosmetic title integrated into existing Passport; no currency/weekly changes.
- Server-bound life/proximity/character/token/step/expiry/teleport revision; old sessions rejected after actual death+respawn and HQ travel.
- Eight actual Solo UI completions, wrong/retry and replay;80XP/title. iPhoneXR all eight/TextFits, status, auto result scroll and close passed.
- Two real clients without accelerated rules: eight completions80XP vs one10XP, independent achievement/progress, token replay denied.
- Ground-level walk through entry/aisles and back to campus plaza succeeded;3D camera/visual checks and three architectural angles verified.
- Old Studio's3D went black; new v46 session rendered normally. Original left open; no login or restart required.
- Review defects fixed/re-reviewed: specific assembly visuals and server session invalidation. Viewport pivot orientation bug fixed after visual QA.
- Gemini request delivered but review empty; supervisor accepted alternative text review. Primary educational sources recorded; wording corrections applied.
- All12 destinations, pure Museum/Passport rules, question banks, StyLua, Rojo pass; selene0errors/26known warnings/0parse errors.
- Full original Workspace equals v45 after excluding Museum46;71script sources. StreamingEnabled remains false. No new game errors.
- Build `KuwaitParkour_v46.rbxlx`,37,774,929bytes; SHA256 a023a406a47b7a7db462fa736488282bbd1c8da6e741d111ea6376ff459397d1.
- Both Studio sessions left Edit; the new v46 viewport is default and fixtures are removed. Published persistence, real phone and long human session untested.
- Next: send report directly for supervisor review, then next authorized feature. No publish/merge permission.

## v45 (2026-10-19), branch `dev/v45`, NOT published or merged

Supervisor accepted v44 development and selected BSC Passport after the owner's explicit instruction to continue.
Full report: [passport_v45_report](docs/passport_v45_report.md). Backup: `backup_before_v45_20261019` (includes v44).

- Extended the existing Profile/Shop menu: overview, achievements, collections, cosmetics, times, weekly, optional batch.
- Added cosmetic XP/levels from server-owned, one-time evidence: stage10, collectible25, first arcade/lab/show40,
  weekly75; 100XP per level. Five cosmetic achievements/titles, no changes to existing coin/research rewards.
- Backward-compatible passport ledger under existing Profiles/DataStore. Failed-load save guard retained; set-union
  merge and Monday00:00UTC rollover tested. No client XP-grant API. Batch choices reuse the existing Lab whitelist.
- Real solo lab token completed; replay denied. Real arcade round and full six-round Game Show completed. Real
  stages1–3 and cat c1 collected; three weekly claims through UI. Total400XP -> level5; title equipped through UI.
- Forged XP, unearned/repeated weekly claims, locked title and unknown batch denied. Batch2026->2025->none through
  phone UI preserved XP400/stage3. Re-entered test fixtures only, not a live DataStore persistence claim.
- Two real Studio clients via StudioTestService: finisher80XP, departing client0XP; distinct profiles,7tabs each,
  forged/locked requests denied. This test shortened runtime rounds to6seconds; shipped durations unchanged.
- Independent review found abandonment-credit issues in Arcade/Show; fixed, re-reviewed, runtime-tested. Old currency
  eligibility/rewards unchanged. Five-level title and all12 Travel destinations passed; course resumed stage3.
- iPhoneXR landscape801x413: all7pages clicked, all label TextFits checks passed; scrolling/claims/batch worked.
  Close initially hit CoreGui; moved to eighth navigation slot and actual phone click verified. Default viewport restored.
- Pure migration/merge/rollover/idempotency/isolation tests and question banks pass. StyLua check passes; selene
  0errors/26known warnings/0parse errors. Fresh Play has no new game-script errors; known engine/asset/Datastore warnings remain.
- Final build: `Desktop/KuwaitParkour/KuwaitParkour_v45.rbxlx`,37,414,836bytes,66script sources.
  XML Workspace matches v44 exactly (Map and Island); no geometry or StreamingEnabled changes.
- Studio remains open, Edit/default viewport, v43 tab with v44 geometry and v45 scripts. Temporary QA scripts removed.
- Next: send report directly to supervisor for review, then continue the next authorized feature. Publishing/merging
  still require owner approval. Real-phone and published persistence remain outstanding.

## v44 (2026-10-19), branch `dev/v44`, NOT published or merged

Owner-authorized modular north-building development prototype. Full report and six Play screenshots:
[north_v44_report](docs/north_v44_report.md).

- Full before-edit backup `Desktop/KuwaitParkour/backup_before_v44_20261019`; new branch from v43.
- `tools/north_campus44.py` replaces only legacy north generation and preserves its RNG advancement.
  Seven modules, explicit A/B visual evidence and C placement notes; distinct flat18-seat and tiered35-seat rooms.
- Kept inherited footprint, levels, stairs, cafes/games and collectibles. No actual room-number/club/elevator claims.
- Necessary south edit explained before implementation: opening the existing red-bridge junction through the old solid
  cladding at x=-50..-30,y24..36,z=-30; corresponding window/mullion split only. All other south geometry unchanged.
- Studio MCP reconnected by reopening the installed Studio with the owner's authorization. Current v43 tab has v44
  geometry, unchanged scripts, Edit mode; app remains open and device simulator reset to default.
- Solo R15 MoveTo tests without jumping: rooms19 goals; east garden20; west garden23; stairs25+25 all levels; bridge10.
  Twelve atrium-edge collision tests, five camera collision checks, sitting/getting up in both room types passed.
- All12 Travel remote routes reached their exact horizontal spawn coordinates; coins/stage stayed0. Real menu clicks
  and progression locks were already tested in v43, not repeated as v44 UI acceptance tests.
- Final fresh Play: no new game-script errors. Known unpublished DataStore, UIBlox and asset203785492 messages remain.
- Visual QA: exterior garden/rear, flat classroom, lecture and atrium refined and captured. iPhone XR landscape801x413
  visually reviewed; this is not a real-phone performance test.
- North863 BaseParts vs756, +107; descendants951; seats53; PointLights18. Whole generated Map25941 parts.
  Three desktop180-frame samples averaged59.97–60.02FPS, p95=17.95–18.19ms; no measured v43 FPS baseline.
- Fixed QA issues: stair-sign collision, legacy extra roof cutout, exposed lawn at floor, lighting and obstructive sign.
  Independent final review confirmed the roof fix and had no remaining findings.
- Static preservation validator passes all other worlds/garden/markers and exact allowed bridge edits; 0 generator
  violations/clashes. StyLua check passes; selene0 errors/27 known warnings/0 parse errors (warnings cause exit1).
  Question banks pass. Final Rojo build has exactly the same63 script sources as v43; StreamingEnabled remains false.
- Build: `Desktop/KuwaitParkour/KuwaitParkour_v44.rbxlx` (37,399,642bytes; excluded from Git).
- Direct ChatGPT contact was verified through the existing browser conversation; earlier tool-only uncertainty in v43
  is superseded. No new login/key. Gemini contact untested. Durable report: `REPORT_FOR_CHATGPT.md`.
- Next: owner prototype review. No further features, publishing or merging. Human multiplayer/real phone/cloud saves
  and additional architectural references remain outstanding.

## v43 (2026-10-19), branch `dev/v43`, NOT published or merged
**Done: descriptions inside the existing world-menu cards (supervisor's single-task directive).**

- First confirmed in source and running Studio that all 12 cards had names but no activity descriptions.
- Backup made before edits: `Desktop\KuwaitParkour\backup_before_v43_20261019` (full working copy and v42 build).
- Only gameplay source changed: `kuwait-parkour/src/client/WorldMenu.client.luau`.
- Added short Arabic activity descriptions to all 12 destinations. Arcade includes **مقترح للبداية** in a warm highlight.
- Kept the same grid (`CellSize = 0.155, 0.46`), card colours, Arabic/English names, destinations and activation logic.
  Adjusted the space inside each card for the two-line description. No tutorial or new window.

**Executed in Studio 0.743.0.7431133, solo Play, one client:**
- Existing `KuwaitParkour_v37.rbxlx` session with v42 content; updated only its existing WorldMenu LocalScript from disk.
- Before/after screenshots reviewed via MCP (captures `v42_menu_before_unobstructed`, `v43_menu_tablet_first`,
  `v43_menu_iphone_xr`, `v43_menu_desktop`; captures are session evidence, not files committed to Git).
- **iPhone XR, landscape, touch enabled, viewport 801x413:** all 12 descriptions and names fit. Assertions checked
  `TextFits`, containment inside each card, and no overlap between text/icon label rectangles. Description glyph bounds
  were 24-26 px high for two lines. Arcade recommendation is visible.
- **Average Laptop, viewport 1365x768:** all 12 cards and descriptions fit; screenshot reviewed. Additional smoke check
  passed in the default desktop viewport (1096x457). iPad (1179x819) was also visually reviewed.
- **All 12 destinations clicked using MCP mouse input**, through the real WorldMenu buttons. Each arrived at its
  expected spawn (horizontal distance 0 for the measured routes), and the menu closed. Course continued at stage 0.
- **Zone portals 2-8:** moved the stage-0 test character onto each actual portal. All seven produced the locked message,
  stayed outside the course, and kept stage 0. These are progression portals, not additional world-menu cards.
- Coins, research and stage stayed at 0 throughout the route/lock checks. Reward and profile code was not changed.
- Fresh final Play Output: no errors from game scripts. Existing unpublished-place DataStore warnings, Roblox UIBlox
  warnings, and asset `203785492` type-mismatch messages remain. Earlier test probes had two harness-only failures
  (Welcome had already closed; an isolated Profiles lookup returned no state); neither was a gameplay error, and neither
  recurred in the fresh final smoke session.
- Stopped Play and returned Studio to Edit with the default viewport. Studio remains open. StreamingEnabled remains false.

**Static/build checks:**
- StyLua format and `--check src` passed after generation (the generator emits CRLF in two shared files).
- selene: 0 errors, 27 existing warnings, 0 parse errors; WorldMenu alone: 0 warnings.
- Question validator: 48 base questions, 80 challenge questions, 5 practical generators x 400 draws passed.
- `genmap9.py`: 0 violations, 0 clashes; regenerated Map SHA256 matches the pre-v43 backup exactly.
- Rojo built `Desktop\KuwaitParkour\KuwaitParkour_v43.rbxlx` successfully.
- Compared sources in the v42/v43 builds: 63 scripts in each; only WorldMenu changed. Its built source matches the
  source loaded and tested in Studio. The other 62 script sources match v42.

**Not tested / next:** real phone, live DataStore, full human multiplayer and weak-device performance remain as in v42.
No new feature work: wait for the emperor's feedback. No publish, merge, or streaming change. Supervisor report:
`REPORT_FOR_CHATGPT.md` (owner relays it; direct ChatGPT messaging was not verified).

## v42 (2026-10-19), branch `dev/v42`, NOT published
**Done: phone pass** (Studio Device Simulator, iPhone XR landscape, viewport 801×413, touch on).

**Checked on the phone screen:**
- **World menu:** all 12 cards fit and are readable. No change needed.
- **Puzzle room:** the room and the prompts were fine. Hint messages were not:
  - **Problem:** hints are long sentences, but the toast stayed one scaled line, so the text came out about 8 px.
    It also closed after 2.6 s.
  - **Fix** (`Feedback.client`): the toast now wraps, is taller, and keeps its text between 11 and 30 px. It stays
    up about 1 s per 14 characters, capped at 9 s.
- **Game Show:** the main screen is 70 studs from the spawn, which is unreadable on a phone.
  - **Fix:** new `GameShowHUD.client`, used only inside StudioBounds. It copies the main-screen and scoreboard text
    into a panel on the right, so the picture and the pods in the middle stay visible. It is read-only; the server
    still owns the show.
- **Microscope:** the controls were about 20 px tall, too small for a finger.
  - **Fix:** every control is now 12% of the column height (about 35 px).
  - The stage buttons are in one row.
  - New: drag the picture to move the slide, for touch and mouse.

**Tested (Studio, solo, Device Simulator):**
- Screenshots of every screen above, before and after each fix.
- Drag with real mouse input moved the sample both ways, and it follows the finger.
- A Game Show round shows on the HUD: the picture round with A–D and the score.
- selene: 0 errors.

**Microscope science review (Gemini) and a bug it led to:**
- **Wording fixes:**
  - Red cells: "biconcave, no nucleus".
  - Platelets: "fragments or tiny dots between the cells".
  - Bacteria: "no true nucleus (prokaryotes)".
  - Condenser: "light and contrast".
  - Oil: "matches the refractive index of glass".
- **Resolution note:** at 100× the screen now says that 1000× is near the light microscope's limit of about 0.2 µm,
  so more magnification is empty.
- **Bug: oil at 100× was a dead end.** 40× was blocked with oil on, 100× could not turn to 4×, and cleaning needed 4× or
  10×.
  - **Fix:** the nosepiece is a ring, so 100× now turns straight to 4×. Going up still has to go one step at a time.
  - Cleaning is allowed only at 4× or 10×.
- **Fix:** cells are drawn only when they sit fully inside the round field. Before, they spilled past its edge, because
  the CanvasGroup does not clip to the circle.
- **Tested with real clicks:**
  - The full blood procedure: 4× 93%, centred by dragging, 10× 94%, 40× fine focus 69%, 100× with oil 97%.
  - 40× was refused with the new message, 100×→4× worked with its message, and cleaning worked.
  - 0 errors from our scripts.
- **Test-harness note:** in the Device Simulator, `user_mouse_input` x lands 47 px left. Add 47 to x.

**Multiplayer test (Studio Server & Clients, 1 server + 2 clients, scripted bots on each client):**
- **Game Show:**
  - 2 players were split Red and Blue, and a full 6-round show completed.
  - Team scores were correct: 10 for an early picture answer, 8 for difficulty 2, 10 for difficulty 3. Red won 20–18.
  - Rewards: the loser got +3; the winner got +13 coins and +2 research.
  - A player left mid-show: the show continued and finished with the remaining player.
  - A third show inside the cooldown paid nothing.
- **Bug fixed** (`GameShow.server`): a player who walked out before answering still got the +3 participation reward.
  - Now only players who answered at least once (`show.played`) are rewarded.
  - Re-tested: the leaver got 0, and the winner got +13 coins and +2 research.
- **Last Cell Standing:** P2 was eliminated, so P1 was the last survivor and the round ended at once.
  - P1 got +22 coins and +4 research. P2 got the participation reward (+2 coins, +1 research) and respawned in the arcade.
- **Lab Rush:** with 2 players the goal shows 0/7, matching the rule 4 + 2 per extra player + tier 1.
- **Puzzle room:** a hint asked for by P1 reached P2 too. A tile turned by P2 matched on the server and on P1.

**Lab Rush co-op, 2 clients (second session):**
- The goal is 4 + 2 per extra player + tier (6 at tier 1, 8 at tier 3).
- The reactor needs a player on each lever within the 2.5 s window, and it completed orders several times.
- Station presses from each player reached the server; the team reached 4/8 in one round.
- **Harness limit:** in Server & Clients, a client's scripted `InputHoldBegin` reaches the server for the first few
  presses, then stops reaching it. The client-side Triggered still fires, but the server receives nothing.
  - The press was at 4.8 studs, the prompt was shown, and the camera faced it.
  - Solo Play in v38 finished full rounds with the same bot, so this looks like a limit of scripted prompt input
    across several windows, not a game bug.
  - A full co-op finish needs two real people.

**Not tested in multiplayer:**
- A full co-op Lab Rush finish by two real people.
- A full two-player puzzle solve with a reward for both players.
- Real disconnects. Leaving was simulated by travelling out.

**Tablet and orientation:**
- **iPad 10th Generation (1179×819):** the microscope is clear and roomy. On the Game Show HUD the maximum text size
  was raised from 24 to 32 so it fills the panel.
- **Portrait does not apply:** `StarterGui.ScreenOrientation` is LandscapeSensor, so phones always show the game in
  landscape.

**Final-QA fixes (supervisor's list):**
- **Stage counter** (`HUD.client`): "المرحلة N/100" now shows only while `InCourse`.
  - Tested: hidden on the campus, shown in the course, hidden in the show.
- **Game Show host** (`tools/gameshow.py`): the mascot moved to the right end of the stage (x +25), clear of the main
  screen (x -20..20).
- **Game Show spawn:** moved from SZ+30 to SZ+18.
  - Before, the default camera sat inside Portal|Campus on the studio's back wall, 11 studs behind the spawn, and the
    whole screen turned cyan on arrival.
  - Tested: on arrival in all 12 world-menu destinations, the camera is not inside any portal.
- **All 37 portals:** each one, stood on in Play, sends the player to the right world. Zones 2–8 are locked by stage,
  as designed.
- **Performance:** 60 fps on the PC in 6 worlds. The game has about 25.4k parts and 80k instances, with
  StreamingEnabled off. Streaming is deferred to a separate tested step.

**Not tested:**
- A real phone.
- A small Android phone.
- Real multiplayer.

## v41 (2026-10-19), branch `dev/v41`, NOT published
**Done: the Light Microscopy lab** (the first complete lab, built to the supervisor's requirements).

**Where and which files:**
- A new bench in the Research Lab, `LabStation|lightmicro`.
- Client: `LightMicroscope.client.luau`. Data: `shared/MicroscopyData.luau`. Grading: `Lab.server` (`lmStart` and
  `lmSubmit`).

**The microscope:**
- Four objectives: 4×, 10×, 40× and 100× with oil. The total magnification shown is eyepiece 10× × objective.
- The nosepiece turns one step at a time.
- Coarse and fine focus. Each lens has its own depth of field.
- Light control: higher magnification needs more light, and both too dark and too bright are shown.
- The slide can be moved, and the sample starts off-centre so you have to find it at 4×.
- An immersion-oil drop and a "clean" button.

**The procedure is enforced, and every mistake is explained:**
- No skipping lenses.
- You can't go up until the sample is centred and in focus.
- Coarse focus is blocked at 40× and 100×.
- Without oil, 100× stays blurry.
- With oil on the slide, you can't swing back to 40×.

**The samples:**
- Four representative drawings: a blood smear, an Elodea leaf, cheek cells and Gram-positive cocci.
- Red blood cells are drawn with NO nucleus. White cells have purple lobed nuclei.
- Detail appears only at the right magnification.

**The notebook and the other tabs:**
- The notebook is graded on the server. You must have actually seen the sample, centred, at the required
  magnification (with oil for bacteria).
- Every wrong item comes with an explanation.
- **Practice mode:** a step guide that ticks itself off.
- **Assessment mode:** a reward of +6 research and +5 coins, once per sample every 10 minutes for this session.
- A "Microscope parts" tab with 8 parts, in Arabic and English, with what each one does.
- A note on screen: "a simplified simulation, not a real lab procedure".

**Tested in Studio, solo, with real clicks through the Studio mouse tool:**
- **Focus:** coarse focus reached 87% clarity at 4×. The light step showed ✅.
- **Finding the sample:** the slide moved until the sample was found (✅).
- **Lenses:** 4×→40× was refused. 10× worked, fine focus reached 92%, 40× worked, and the light had to go up.
- **Coarse at 40×:** blocked, with a message.
- **Clarity:** 94% at 400×.
- **Notebook:** 3 correct notes in assessment mode → "Excellent +6".
- **Oil:** at 100× without oil, clarity was capped at 30% with a warning. After oil it rose to 69%. Going back to 40× was
  blocked.
- **Bugs found and fixed:** the round-view clipping (cells spilled out of the round view) and the notebook text wrap.
- 0 errors on the server and client.

**Not tested:**
- Phone layout. The screen is dense, so it needs a check on a small device.
- The elodea and cheek samples at 400×. Only blood was clicked through end to end.
- Expert review of the science. It is required before calling the lab final.

## v40 (2026-10-19), branch `dev/v40`, NOT published
**Done:**
- **BSC Game Show studio** at (0, 300, -7000).
  - Built in `tools/gameshow.py`, run by `server/GameShow.server.luau`.
  - Stage with the host mascot, a main screen, a scoreboard, two team screens, a picture board with a 5×5 cover,
    and four answer podiums (taps, so it works on phones).
- **Two complete formats** (the supervisor's plan):
  - **Guess the picture:** the cover tiles fall away over time. Answering earlier scores more (10 down to 3).
  - **Category challenge:** players vote a category on the podiums, then answer a question from it. Points are
    5 / 8 / 10 by difficulty.
- **Rounds:** a show has 6 rounds alternating between the two formats.
- **Teams and timing:**
  - Solo play, or Red/Blue teams when there are 2 or more players. Late joiners are added to a team.
  - A question closes as soon as everyone has answered. The 40 s limit only stops an AFK player from stalling it.
- **Rewards:** +3 coins for everyone, +13 coins and +2 research for winners, once per player every 10 minutes.
- **Content bank** in `server/GameShowBank.luau`, separate from the code:
  - 24 category questions written by **Gemini** (team member). Claude checked them and fixed one wrong-answer label.
  - 18 emoji pictures. They're free to use, so no image licence is needed.
- **Display:** Arabic-only on screen. "(English)" parentheticals are hidden, because mixed lines render scrambled.
- **Access:** world menu card "Show" (12 cards), and a `Portal|Campus` exit in the studio.

**Tested (Studio, solo, client bot):**
- **First full show:** all 6 rounds completed and the participation reward was paid (+3).
- **Second show:** no reward was paid, which confirms the cooldown.
- **Logged run:**
  - The rounds alternated picture → category.
  - The vote picked biology, and the questions came from biology.
  - 4/25 covers were off after 3 s.
  - Wrong answers scored 0. A correct picture answer scored +9 (it was early), and a correct biology answer scored +5.
    The final score was 14.
- 0 errors.
- The host mascot was moved after the screenshot showed it covering the main screen.

**Not tested:**
- Real teams with 2+ players.
- Phone layout.
- Main-screen readability from the back of the studio.

## v39 (2026-10-19), branch `dev/v39`, NOT published
**Done:**
- **Puzzle-room framework:** `server/PuzzleRooms.server.luau` runs the rooms.
  - Each room is defined by one module in `PuzzleRoomDefs/`. Reusable puzzle types live in `PuzzleTypes/`: Circuit,
    Specimens and Core.
  - No timer.
  - 3 hint levels per step, from the Hint terminal.
  - A Reset terminal.
  - The room resets itself after 60 s empty.
  - Shared state with no owner, so nobody gets stuck when a teammate leaves.
  - The reward is +15 coins and +3 research, once per player every 15 minutes.
- **First room, "Cell Control Room"** (the supervisor's idea), next to the arcade:
  - Energy Circuit: a 3×4 grid of pipe tiles; a new random layout on every reset.
  - Specimen Detective: 4 fantasy creatures; the clue board gives colour + eye count, and only the combination is unique.
  - Core Activation: the two revealed symbols go on the panels, then the lever.
- **Access:** a `Portal|Puzzle` in the arcade lobby, plus a "Puzzle" card in the world menu (now 11 cards).
- Room lighting and name-tag size were fixed after reviewing the first screenshot.

**Tested (Studio, solo, client bot):**
- One manual tile turn, then the circuit was solved through hints. That was 8 presses; at level 3 each press fixes
  one tile.
- Specimens solved purely by observation: the bot read the clues and the creatures' colour and eyes, and got 4/4 names
  right.
- The core activated and the reward was paid (coins 0 → 15).
- The Reset terminal gave a new layout. The lever refused before solving and paid nothing.
- Leaving mid-puzzle: after 72 s empty, the room had reset.
- 0 errors.

**Not tested:**
- Two real players in one room.
- The phone layout.
- The reward cooldown on a second solve.

## v38 (2026-10-19), branch `dev/v38`, NOT published
**Done:**
- **Lab Rush (co-op):**
  - Four stations, all using ProximityPrompts: DNA Mixer, Mutation Machine, Sample Sorter, Lab Reactor.
  - An order board that always shows 3 orders.
  - The team goal is 4 + 2 per extra player + tier.
  - Solo play works.
  - The board says this is a fantasy lab.
- **Arcade co-op mode:** added to the round loop. **Last Cell Standing** has a fourth arena signpost and Lab Rush has a
  fifth, set on a diagonal.

**Tested (Studio, solo, with a client bot that reads the board and triggers the prompts):**
- **Round 1** (goal 4): finished in 9 s.
  - The win reward was paid: coins, plus research 1 + 3.
  - 0 prompts and 0 temporary parts were left over.
  - 0 errors.
- **Round 2** (goal 5): every station was used, including one deliberately wrong sort, and the team finished.
- **Shield in Last Cell Standing:** with the shield on for a whole round, 13 hazards produced 0 pushes. Without the
  shield, an earlier run produced 5 pushes.
- **World menu destinations:** none is inside a solid part. The island has terrain only at run time; travel there
  was confirmed in v37.

**Not tested:**
- 2 or more players: co-op with real teammates, and the 2.5 s reactor window.
- The phone layout of the prompts and the board.
- The board's readability from far away.

## v37 (2026-10-18), branch `dev/v37`, NOT published
**Backup:** `Desktop\KuwaitParkour\backup_v36_20261018`, which contains the last stable state before v37.
**Build:** `Desktop\KuwaitParkour\KuwaitParkour_v37.rbxlx`

### Done
- **Gym and Red Corridor:**
  - The corridor columns inside the gym outline are removed.
  - Two edge girders now carry the corridor across the gym, from z 12 to z 84.
- **Start point:** players now start in the south building lobby (CampusSpawn). The island spawn is disabled; the
  island is still a destination.
- **World menu:**
  - A "🌍 العوالم" button with 10 world cards.
  - It uses the server `Travel` remote, which reuses the portal logic and has a whitelist.
- **Welcome card:** rewritten for the new start. It has a "choose a world" button and an X to close it.
- **Last Cell Standing** (Arcade):
  - New files: `server/Minigames/LastCell.luau` and `client/ArcadeFX.client.luau`.
  - New arena: `chaos_gen.last_cell`.
  - Arcade signpost added.
  - A Studio-only `ArcadeForce` test hook in `Arcade.server`.
- **Git:**
  - A `.gitignore` that keeps out binaries, generated maps, rbxlx files and media.
  - The project documents.

### Tested (Studio, solo, 2026-10-18)
- **Spawn:** the player spawns at (-3, 4, -148), in the lobby, and the welcome card appears.
- **Travel:** all 10 menu destinations reach their spawn points. "Course" sets InCourse. An invalid key is ignored.
- **Gym:** the girders overlap no gym part, and no corridor columns are left inside the gym span.
- **Last Cell Standing**, one full round:
  - The outer ring dropped on schedule.
  - Hazards spawned: 4 spores, 6 cilia waves and 3 bubbles.
  - The client received 5 pushes.
  - Score went up, the player was eliminated and sent to the lobby, and the round ended.
  - The arena reset with 0 hidden segments and 0 leftover hazards.
- **Errors:** 0 from our scripts.
- **Static checks:** stylua and selene pass with 0 errors.

### Not tested
- Phone layout (device emulator), for the world menu and the arcade HUD.
- Two or more players: Last Cell Standing with real opponents, and win/lose with more than one survivor.
- The DataStore on a live server.
- The shield's protection was not confirmed visually; the bubble pickup was counted only through the score.

2026-10-19 supervisor review: v47 commit4406daf accepted developmentally, no mandatory correction. Selected v48 Laser Escape: five actual movement/timing rooms, fair telegraphed hazards, checkpoints/unlimited retries, solo and two-client independence, Passport reward, full Studio QA. Real-phone performance and human driving enjoyment remain owner release tests. No publish/merge approval.
