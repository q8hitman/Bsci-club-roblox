# Micro Racers v47 — development report

2026-10-19. Branch `dev/v47`, parent v46 `73d3b4c`. Supervisor selected the scope after accepting v46. Full backup `backup_before_v47_20261019` includes the previous build. No publish or main merge.

## Delivered

A separate race entrance inside the existing Arcade leads to an independent lobby. Two original primitive-built tracks: **حلبة الخلية** has broad turns; **منعطفات الجزيئات** has a narrow optional shortcut between two required gates. Three ordered laps, five-second grid, up to eight human racers, AI fills a small roster, ranks, results, replay and track selection. The AI uses the same steering/acceleration/braking and corridor constraints as players.

Vehicles use authoritative planar simulation at20Hz, client interpolation and a chase/high camera. This deliberately prevents flipping and falling from the road. Humans supply throttle/brake/steering inputs; there is no automatic player route following. Temporary boost, one-obstacle shield, spore slowdown and checkpoint recovery are implemented. All geometry and driving data come from tools/racers47.py. Client clones are visual vehicles; characters remain safely in the race lobby.

Server accepts only finite clamped intent with a race ID and increasing sequence. It owns positions, ordered gates, laps and finishes. Missing input brakes. Life/character/travel/distance invalidate sessions. Departure releases avatar, GUI and camera; terminal results release anchoring and movement while retaining the chase view behind results. Queue compaction reclaims departed slots before capacity/grid/AI fill.

One-time20 cosmetic XP per track,40 total, and all-two title **سائق الجزيئات** use the existing Passport evidence/save merge. No coin/research reward or changes to old weekly tasks. No client XP-grant endpoint.

A race-only daylight preset improves vehicle readability. Existing world lighting presets are unchanged. Existing overlapping HUDs are temporarily hidden and restored to their saved Enabled state, including a late-created welcome GUI. No existing GUI/system was removed.

## Executed verification

- Solo Play, real VirtualInput keyboard events through the production controller: three laps on cell118.8s, helix122.7s (includes pauses for inspection). All AI cars finished, first stamp20XP, both40XP. Results released root anchoring and enabled PlayerModule controls.
- iPhone XR landscape801x413: track choice and all HUD text fit; real emulated Touch input activated throttle, steering, brake, boost, recover and camera. Throttle moved15.36studs and steering changed heading0.502rad in the focused input check. Completed three cell laps using only screen buttons; result159.6s and20XP. Actual simulator input requires compensating the tool's47px horizontal offset. This is test input calibration, not an in-game button offset.
- Server/two actual clients: PASSED. Both finished cell and helix; the replay kept XP20, then helix raised it to40 and awarded racer2. Recorded player1 times56.0s/56.2s/90.8s, with two or three AI finishers. Death/respawn, disconnect, queue reclamation/AI fill, malformed/forged progress, recovery, exit and timeout anchoring/control release passed. [Raw results](v47/multiplayer-results.json). Isolated StudioTestService fixtures call the production request/input remotes. Test driving supplies intents only; no source position, gate or lap is advanced by the fixture. The final timeout-only stage shortens the runtime duration after normal complete races; shipped duration remains180s.
- Fresh clean v47 build: all12 Travel destinations reached their expected spawn coordinates and Stage/Coins stayed0. Museum micro sequence completed for10XP and rejected token replay. A late-created background GUI hid/restored correctly; travel from queued race to HQ closed race UI, restored controls/camera and unanchored root. Actual HUD Exit restored WorldMenu and avatar camera.
- Static/pure: StyLua; selene0errors,26knownwarnings,0parse errors; Lune RacerMath/Passport/Museum; question banks48questions/8banks,80center questions and five generators x400 draws. AI three-lap simulation54.9s/86.2s. Boost cooldown, shield pickup/one-hit protection, unshielded slowdown and a complete ordered-gate shortcut route82.3s also passed. Finite-input, no auto throttle, braking/steering, gate order, recovery, immutable finish, invalid race stamp and duplicate/merge assertions passed.
- Independent read-only review found two P2 issues (departed queue capacity and timeout cleanup); both fixed and re-reviewed with no remaining actionable findings. Visual review corrected dark Arcade lighting, background GUI obstruction and outer-corner deck coverage.

## Geometry and performance

Build Workspace is byte-structure equivalent to v46 after excluding the new Map.Racers47 subtree (referent IDs normalized). Campus, Museum46, all old Arcade arenas and every other world are unchanged. Added326parts/386descendants. Build75script sources; StreamingEnabled=false. Four rendered racers add40local parts/56descendants. No external models or unlicensed assets.

Fresh v47 single Play racing sample after the temporary test windows closed:181frames/3s, mean16.66ms, p9518.23ms, approximately60FPS on this computer only.

Two-client background Studio sample:45frames over3s, mean66.69ms, p9567.89ms. This is approximately the editor background15FPS limit with multiple Studio windows, not a real-phone performance benchmark. Real phone/GPU/memory and long human play remain unverified. No high performance claim is made from this sample.

## Limits and evidence

No live DataStore or published server was tested. No new login, keys, publish, merge, horror world or old-system deletion. Real multitouch on physical hardware and extended human racing remain for owner testing. Existing unpublished DataStore protection, UIBlox/Foundation and asset203785492 warnings remain known. Travel also reported missing legacy asset81504106; neither asset is used by the new racers. No new game-script runtime errors were observed.

Pictures: [cell overview](v47/v47-cell-overview.jpg), [desktop driving](v47/v47-driving-desktop.jpg), [cell results](v47/v47-cell-results.jpg), [phone driving](v47/v47-driving-iphone-xr.jpg), [phone results](v47/v47-results-iphone-xr.jpg), [tracks](v47/v47-tracks-overview.jpg). Build is local outside Git: Desktop/KuwaitParkour/KuwaitParkour_v47.rbxlx. QA fixtures were removed from Studio before delivery and are not mapped into the build.

Build SHA256: `e2b58188e356c7f3023bec752d856f227b9ebf544e483591dffb9807c8811e64`. Final Studio title KuwaitParkour_v47.rbxlx, Edit/default viewport; all older sessions remain open.
