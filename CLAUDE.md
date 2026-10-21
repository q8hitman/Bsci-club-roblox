# BSC Roblox project — handoff notes

Roblox game for the Kuwait University College of Science **Biological Sciences Club (BSC, نادي العلوم البيولوجية)**.
The user speaks Kuwaiti Arabic. Reply in Arabic, keeping it simple. Entertainment first, light and accurate education.

## Layout
- `kuwait-parkour/`: the main game (Rojo project). Scripts are in `src/server`, `src/client`, `src/shared`. The island model is `src/world/Island.rbxm`.
- `tools/`: generators.
  - `genmap9.py` is the main map generator; it imports parkour9, campus9, hq, hq_beauty, hq_fill, cartride, celltrain, collectibles9, extras10, island11.
  - `tools/world/*.luau` are Lune scripts that build `Island.rbxm` from the official Roblox Synty packs in `tools/packs`.
- `chaos-campus/`: a minigame prototype, already merged into the island Arcade.
- Tools:
  - `tools/rojo/rojo.exe` (7.7.1)
  - `tools/lune/lune.exe` (0.11.0)
  - `tools/stylua/stylua.exe` (2.5.2): formatter. Run `stylua src` from `kuwait-parkour/` (config: `stylua.toml`, tabs, width 120).
  - `tools/selene/selene.exe` (0.32.0): linter. Run `selene src` from `kuwait-parkour/` (`selene.toml` std=roblox, `roblox.yml` generated; `_G` globals allowed). 17 known `deprecated` warnings come from the `Instance.new(class, parent)` form and are harmless.
- Builds are copied to `Desktop\KuwaitParkour\KuwaitParkour_vNN.rbxlx`. The latest is **v37** (2026-10-18, not published; live game is still the v20+NPC update). Working status: docs/KNOWLEDGE_BASE.md.

## Build
1. `python tools/genmap9.py`: generates the Map.
2. `tools/lune/lune.exe run tools/world/island.luau`: builds Island.rbxm.
3. `tools/rojo/rojo.exe build kuwait-parkour/default.project.json -o <out>.rbxlx`

## World offsets (kept far apart so worlds aren't visible from each other)
| World | Offset |
|---|---|
| Campus | 0,0,0 |
| Course | 12000,0,0 |
| Cell train | -12000,0,0 |
| Cart | -9000,150,9000 |
| HQ | 0,600,-12000 |
| Virus | 0,600,-12600 |
| Island | 0,0,9000 |
| Exam | 6000,300,-6000 |
| Arcade | -6000,300,-6000 |

Portals are parts named `Portal|<Kind>`. `destinations` lives in `src/server/Main.server.luau`.

## Status
**Tested in Studio:** campus, HQ, 100-level parkour and its puzzles, cell train, cart ride, collectibles/shop/titles, graduation, virus banner, island spawn and visuals.

**NOT tested yet:**
- Flattened island terrain (`IslandTerrain.server.luau`).
- Building orientations (FACE yaws in `tools/world/island.luau`).
- Exam hall flow, Arcade on the island, NPC dialogue.
- Multiplayer, DataStore saving.

## Next steps
1. Open v19 in Studio and test the untested items above. Fix what breaks.
2. Polish visuals toward "Blox Fruits level".
3. Publish **privately (owner only)** so the user can test on their phone. Never make it public without the user's approval.

## Published (2026-10-15)
- "BSC Island - جزيرة نادي الأحياء", PRIVATE. PlaceId 97395090487008, UniverseId 10771032485. Published from v20.
- Link: https://www.roblox.com/games/97395090487008
- Update it with File > Publish to Roblox, choosing "Update existing experience". Studio logged "Error setting universe configuration info. HTTP 400" during publish, so check the Phone device setting in Creator Hub.
- Tested in v19/v20 before publishing:
  - Island flat ground, spawn, 9 NPCs, monument.
  - Exam hall round (question, timer, "nobody passed" message).
  - Arcade Petri round with the moon mutation (+2 coins).
  - No errors from our scripts (only Roblox CorePackages noise).
- Update 2: NPCs got free Roblox hair, face the path, turn toward the speaker, and their feet sit on the ground (raycast). Dialogue was tested via the prompt in the iPhone XR emulator. Republished.
- NOT tested: multiplayer, DataStore saving on live servers.
- A source backup is in `Desktop\KuwaitParkour\source_backup`.

## Rules from the user
- Never enter the user's passwords. Don't close Studio unnecessarily (login gets lost). Open files from Studio's File menu.
- The friend's analytical chemistry map: discuss it LAST, with the user. Don't search for it.
- Later: the user's own exam questions, virtual labs, Discord bot via proxy, official badges.

## v22 changes (2026-10-15, local only, NOT published)
- Question bank: 48 questions, each {q, right, wrong x3}; random FILLER removed from ExamHall. Validate: `tools/lune/lune.exe run tools/validate_questions.luau`.
- Arcade: death in an arena respawns at ArcadeSpawn (ArcadeReturn attribute + one CharacterAdded hook); leaving the arena drops out quietly; only survivors are teleported at round end.
- Main BindToClose waits for all saves (up to 25 s).
- Welcome text says island, not HQ.
- island11.py: exam_hall_dressing() and arcade_dressing(). CampusTerrain.server.luau paints the campus dunes at runtime.
- Backup before these changes: Desktop\KuwaitParkour\backup_before_v22_20261015

## v25 art pass (2026-10-15, local only, NOT published)
- tools/world/island.luau: FACE yaws were inverted (Synty fronts point along LookVector) -> fixed; every building now faces its street/plaza.
- Food street rebuilt as a continuous mixed-use street: 9 shops + 1-2 Bld_Apartment floors + roofs, rooftop LargeSigns, café tables, lamps/trees alternating; sidewalks are Concrete terrain strips.
- Plaza: paved (terrain fills are now 4 deep, top y=1, so they replace grass), 4 diagonal tree/flower beds with benches facing the monument, HQ front garden, 11 groves on the south lawns.
- Lighting warmed (ClockTime 16.3, denser warm Atmosphere, slight tint). Course cloud sea under the parkour (island11.course_backdrop).
- Shop names live in island11.py (names list) and must match island.luau "street" table.
- Visual review loop: start play, bind a RenderStep camera in the Client DataModel, then screen_capture (edit-time captures have no runtime terrain or SurfaceGui text).
## v28 gameplay pass (2026-10-16, local only, NOT published). Backup of v25: Desktop\KuwaitParkour\backup_v25_20261016
- Cart ride (CartRide.client): physics tuned with an offline sim of the real track (BRAKE 95, downhill pull x0.35 while braking, chain-lift 10 on hills, no braking/stall in loops -> section restart), HUD warns ~45 points ahead of sharp curves / jumps; speed label turns red. Curve 392 was unwinnable before (80 -> 40 in 45 studs).
- Cell train: Died handler, so a death mid-ride no longer leaves the camera locked / ride flag stuck.
- Puzzles (Obstacles): closed ghost bridges 0.9 transparent, open = solid, flicker the last 3 s; ordering puzzles keep correct presses lit; bridge stays 20 s.
- Course: finish arch + Portal|Island at Checkpoint_100 (island11.course_finish_exit); "رجوع للجزيرة" button (LeaveCourse.client + LeaveCourse remote in Main) while InCourse.
- Space: moon stages (genmap7.k_moon) get planet/stars/craters/sign with their own RNG (layout unchanged); Zones.client turns the sky to night inside LowGrav.
- Campus: stair_core built treads as solid blocks -> every flight below the top was sealed; now 1-stud treads. Lecture hall moved off the west core (x0 -68), trophy case moved off the east core, north columns skip stair cores, Salad counter x -38. Verified by walking a humanoid L1->L4 (south) and L2->L3 (north).
## v29 (2026-10-16, local only, NOT published). Backup of v28: Desktop\KuwaitParkour\backup_v28_20261016
- No visible parkour timer (server timing kept). Cart: no hard cap (quadratic drag, ceiling 220), BRAKE 110, LOOKAHEAD 55, smoothed tangent + eased rotation; Upg_mito +20% accel.
- AreaAtmosphere.client: per-world Lighting/Atmosphere/grade presets (island, campus, hq, exam, arcade, virus, cell, cart, lab, z1..z8).
- Island gateways slimmed (metal posts + small plaque). Research Institute (Synty office) on the island east lawn -> Portal|Lab -> lab world at (6000,300,6000).
- Lab: Lab.server/client, Shared/LabData (slides, gels, PCR, upgrades), Shared/Batches (admin-edited). Profiles: research, upgrades, batch (saved).
- Cell world: compact floating labels, smooth ER, peroxisomes, 2 more mitochondria with glowing matrix, 4-car train, brighter look.

## v30 (2026-10-16, local only, NOT published). Backup: Desktop\KuwaitParkour\backup_v30_20261016 (v29 backup: backup_v29_20261016)
- Rail hall (cartride.py cart_hall): 9 themed rooms under glass bio-dome membranes, tunnels at crossings, station hall; locomotive + 3 local trailing cars (CartRide.client placeCars, CAR_GAP 11); Shared/CartRooms.luau drives per-room atmosphere. Exit button moved to the right column (UpBtn/DownBtn/ExitBtn names); cell-train exit moved top-right.
- Arcade: tier 1-3 per consecutive round (resets after 30 s empty), research rewards (1 per round, 2+tier for winners). Petri "contamination" waves + antibiotic pads; ATP combo x3 + free radicals; Sweeper inhibitor pads, substrate coins, direction flips, 3 s warm-up (an arm used to start on spawn 1 and kill instantly).
- Science Challenge Center world at (0,300,-6000), Portal|Quiz gateway at island (146,108), building Bld_OfficeOld_Small at (172,108). QuizKiosk|1..8 specialties x 3 levels (L1 = Questions.luau, L2-3 = QuizBank.luau with explanations), QuizKiosk|9 = computed practicals (QuizPractical.luau). Unlock at 3/5, rewards coins = correct x level, RP for 4+/5, 20 s reward cooldown, answers <1 s count wrong. Best scores saved as s.quiz["spec:level"] (max-merge). Group play = Portal|Exam inside the center.
- Validator now also checks QuizBank (5+ per level, 6 fields) and 400 draws of each practical generator.
- Campus: facade perforations on a staggered grid (same rng consumption), duplicate 114 stone removed, HQ portal subtitle Arabic-only.

## v31 (2026-10-17, local only, NOT published). Backup: Desktop\KuwaitParkour\backup_v31_20261017 (pre-v31: backup_before_v31_20261016)
- Official specialty names everywhere (Microbiology مايكروبيولوجي, Biochemistry بايوكيمستري, Animal Biology بيولوجيا حيوان,
  Plant Biology بيولوجيا نبات, Molecular Biology مولكلر, Forensic Science الأدلة الجنائية, Agriculture الزراعة,
  Biotechnology البايوتكنولوجي). Zone/question ORDER is unchanged (parkour indexes depend on it); Map scanned for leftovers.
- Specialties Train (tools/cartride.py + CartRide.client/server): sightseeing tour, no coaster. Track = 8 rows in the
  official order, gentle S-bends/hills, helix around the DNA, wide U-turns, no loops/jumps/crash flags. Controls: ▶ once,
  ＋/－ cruise steps {15..90}, ⏸ smooth pause, auto-slow in bends (v^2/R <= 70) and a smooth stop at the end; end card
  "back to island" / "ride again". Server actions stop/station/island/again use Teleport. 15 landmarks (2 per room, 1 in
  molecular) beside the rails, kept off the glass partitions (CUTS). Auto facts per room (no questions).
  CartRooms.luau = { tops, zones }. Station portals now go to the Island. Cell section removed (Cell Train is separate).
- Teleport.luau (server) + TeleportSync.client: every server move of a character (portals, LeaveCourse, fall recovery,
  arcade, exam pit, cart actions) unseats, ground-raycasts from 4 studs above, zeroes velocity, syncs the client, rechecks.
- Exam hall (island11.exam_hall): the floor used to stop 17 studs short of the answer zones (walking there = pit). Apron,
  side floors, 28-wide zones with solid divider strips, front glass rail, floor letters, answer text on the boards;
  IslandHUD shows question + 4 options and "you are here". Tested: walk to zone, right answer stays, wrong drops + returns.
- Sequence puzzles (Obstacles + SeqButtons.client): button colours and the solved bridge are per player (client-side
  CanCollide on Ghost|id). Stage 54 = DNA complement puzzle q54 (CGCG). Tested: server sees bridge closed, solver stands on it.
- Laser stage (genmap6.k_laser): full-height blinking curtains + green safe zones (was a 0.5-stud hop-over beam).
- Food street: café tables moved to the street centre; order windows ShopOrder|1..9 (FoodStreet.server: free snack Tool +
  fact, equipped). HQ café: "100 fils" removed, ShopOrder|10..13 + two Seat sofas.
- Island: train station dressing (roof name board, platform, canopy, rails, display loco). tools/world/lib.luau place()
  now moves child parts with their parent (11 pack sub-parts were stranded inside the campus, e.g. a floating bus-stop glass).
- Campus: desert garden enriched (own RNG). Lab labels renamed (no Genetics/Botany). Lab mito upgrade -> +1 RP per arcade round.
- Cell train labels moved to radius 205 (three overlapped organelles).

## v32 (2026-10-17, local only, NOT published). Backup: Desktop\KuwaitParkour\backup_v32_20261017 (pre: backup_before_v32_20261017)
- Real-world College of Science likeness: tools/ku_science.py (hooks genmap5's south building + adds pieces after
  campus9). Research + sources: docs/science_research_v32.md, plan: docs/science_blockout_v32.svg.
- South: bronze perforated screen (folded corners, sloped crown, side wraps), entrance bay of tall white columns +
  louvred glazing, long low exterior wings (east to x 150, west to -128 to keep the desert garden open), warm pavers
  under the colonnade, beige plaza stripes, planters/bollards. genmap7 FacadeName band removed (not on the real facade).
- Between: raised Faculty Club (curved white balconies, roof garden) at (10, 80) on columns; garden trees within 46 of
  it are skipped (no RNG change). North: limestone "College of Science" wall + terracotta strip at the entrance.
- Interior: L1 east-wing loungers restyled (green/blue/orange) + red booths + cube poufs; auditorium wood wall, bands.
- Tested in Studio (solo): screenshots from the reference angles, walk plaza -> entrance -> lobby. Not tested: phone.

## v33 (2026-10-17, local only, NOT published). Backup: Desktop\KuwaitParkour\backup_v33_20261017 (pre: backup_before_v33_20261017)
- tools/ku_science33.py on top of ku_science.py (both hooked in genmap9.build_campus). Satellite correction: the centre
  of the college is a triangular ring around a green courtyard (apex south at the south building, top edge facing the
  north blocks), not a round pavilion. CentralRing: TRI (0,-24) (86,100) (-86,100), fillet 16, 20 deep, columns on
  both edges except near the garden walk / glass pavilion / Red Corridor, first floor = walkable glazed loop at y 24
  joined to the Red Corridor at its two crossings (BridgeGlass/Mull/BridgeCol opened there), three stepped bands above.
- Wings are enterable: hall + glass door (no column in front), notice board, benches; L1 corridor + classroom fronts
  ("قاعة دراسية", no invented numbers); doorways into the main building (G z -158..-148, L1 z -172..-162). No stairs in
  the wings (L1 is reached from the main building). West wing stops at x -110 (desert garden bed at -112).
- Main screen runs into the wings (corner folds removed, side wraps start at z -142), fold ridges + quasicrystal stars.
- Real names from Google Maps: Department of Biological Sciences + Student Guidance (north entrance), Department of
  Physics (south building back). Pick moved into the courtyard NE (30,72), Toby's moved east (110,-112), sail plaza
  moved south 50 (clear of the ring and the red block). Back-lit laser-cut stair screens (NBBJ) on all four cores.
- Campus trees: varied (round / date palm / sidr / cypress) by position hash, never the shared RNG.
- Tested (solo play, real humanoid MoveTo): both wings G + L1 from plaza and main building, full ring loop, garden walk,
  galleria to the north entrance. Not tested: phone, multiplayer.

## v34 (2026-10-18, local only, NOT published, FIRST DRAFT awaiting the user's review). Backup: Desktop\KuwaitParkour\backup_v34_20261018 (pre: backup_before_v34_20261018)
- tools/ku_science34.py: pre() before ku_science33.install() (smaller triangle TRI (0,-24) (+-66,62), silver palette into
  ku_science constants, Pick -> (22,44)), install() after it (mutes the old winding_garden + campus9.garden_life while keeping
  their RNG use, column joints, BSC office window/door gaps, dark south ground glass), build() (step ramps, garden walk
  north of the triangle: MAIN/ARC/EAST paths + PROMENADE band + mound + white faceted gym pavilion + Connect|North anchor,
  DeptBio/Guidance signs moved onto the triangle's north face, side doors + round soffit/lobby lights, BSC office furniture).
- Aerial refs saved in Desktop\KuwaitParkour\صور_اللعبة\v34_مراجع_جوية; report docs/science_v34_report.md (A/B/C grades).
- Tested solo: plaza -> lobby -> back exit -> courtyard -> garden -> inside north; arc, east, promenade; plaza -> BSC office
  (needed the invisible StepRamp). 60 fps. Not tested: phone, multiplayer, DataStore. Game-system fixes NOT started.
- Never run several screen_capture calls in parallel: Studio crashed once doing that.

## v35 (2026-10-18, local only, NOT published, south NOT final: awaiting the user's review). Backup: Desktop\KuwaitParkour\backup_v35_20261018 (pre: backup_before_v35_20261018)
- User principle: the KU campus must be as close to reality as possible; never invent room locations / building details;
  ask the user for photos instead (list in docs/science_v35_report.md section 7). Creative freedom = the other worlds.
- tools/ku_science34.py (v34+v35): garden per the satellite: wide paved band with tree planters along the north block,
  white faceted gym roof (WedgePart triangles, closed, not enterable, no interior) touching the triangle's NE, east plaza
  with tree grid, dense west planting; invented extras removed (shade canopies, fountain, east path, gym glass box,
  "Guidance" sign, ring building name). DeptBio = freestanding wayfinding sign at the triangle's north edge.
- Facade perforation: tiled Texture (Creator Store image rbxassetid://15484649855 "peg board", 12 studs) on the 17 screen
  parts; scattered ScreenCut/ScreenStar parts dropped (-803 campus parts). genmap.bidi_lines splits "Arabic | English"
  (and " • ") into separate lines in every SurfaceGui text.
- BSC office rebuilt (C5.club_room muted): room x 68..90, balcony 12 wide, desk 3.4 / seat 2, DNA board on the west wall
  (camera sat inside it on the north wall). Collectible c5 moved onto the new desk. AreaAtmosphere: campus_in preset.
- Tested solo: all routes, ring L1 loop, gym blocks entry, camera in the office, 0 script errors, portals 34 / collectibles
  21 (= v34). Not tested: phone, multiplayer, DataStore.

## v36 (2026-10-18, local only, NOT published, awaiting review). Backup: Desktop\KuwaitParkour\backup_v36_20261018 (pre: backup_before_v36_20261018)
- USER CORRECTION: the triangle IS the gym; the white folded roof covers the triangle. ku_science34.pre() disables
  K33.central_ring and K33.crossings_at (Red Corridor intact). gym(): GYM_EDGE (16 pts, eave y) + GYM_RIDGES (4), WedgePart
  triangles, opaque dark glass under eaves, invisible 20-stud GymBoundary fence (9 was climbed; roof was a ramp), no interior.
- Walks: MAIN = east (from the back door gap x 34..40: the PhotoShop kiosk blocks 40..64), WEST = west then the curve round
  the mound; both end at the real north entrance opening x -8..8 (NORTH_LINK (0,131)). Pick back at (106,-100). Collectible
  c1 moved to (-24,96). DeptBio sign removed.
- Tested both walks both directions, band, garden, east plaza, office, Red Corridor over the gym, 5 jump-entry attempts
  blocked; 0 script errors; portals 34, collectibles 21.

## v37 (2026-10-18, local only, NOT published). Git: branch dev/v37 of github.com/q8hitman/Bsci-club-roblox. Backup before: backup_v36_20261018
- Project docs at the repo root: BSC_MASTER_VISION / ARCHITECTURE / FEATURE_BACKLOG / RELEASE_CHECKLIST / PROGRESS / RESUME.
  Read BSC_RESUME.md first. Owner's limit is tight: inspect once, batch changes, no repeated Studio restarts/screenshots.
- Start point = CampusSpawn (south lobby); IslandSpawn disabled (destination only). WorldMenu.client + Main "Travel" remote.
- Gym: BridgeCol inside the gym dropped, BridgeGirder x2 (z 12..84). Arcade: Minigames/LastCell + ArcadeFX.client +
  chaos_gen.last_cell arena at (AX, AZ-300); Studio-only workspace attribute ArcadeForce forces a game.
- Horror/containment world is deferred: never build it.


## v38–v42 (2026-10-19, local only, NOT published). Details: BSC_PROGRESS.md, BSC_READINESS_v42.md
- **v38:** Lab Rush (co-op).
- **v39:** puzzle rooms (Cell Control Room).
- **v40:** BSC Game Show.
- **v41:** Light Microscopy lab.
- **v42:** phone, tablet and multiplayer pass:
  - Game Show HUD, readable toasts, and microscope touch controls;
  - the Game Show rewards only players who answered;
  - the stage counter shows only in the course;
  - the Game Show spawn was moved off the exit portal.
- Latest build: `Desktop\KuwaitParkour\KuwaitParkour_v42.rbxlx`. Branch `dev/v42`. Backup `backup_v42_20261019`.
- **Multiplayer test:**
  1. Test → Start Test Session → Server and Clients.
  2. In the server window, Test → Add Clients, once per client.
  3. Each window shows up as its own Studio id in the MCP tools.
- **Harness limits:**
  - In the Device Simulator, `user_mouse_input` x lands 47 px left.
  - In multi-client mode, scripted `InputHoldBegin` presses stop reaching the server after a few presses. Use real
    people for full co-op runs.
- The game is landscape-only (`LandscapeSensor`).

## v53 (2026-10-21, local only, NOT published). Branch dev/v53-release-push. Full state: docs/DEVELOPMENT_HANDOFF.md
- Cart Ride = tools/cart_tour53.py (genmap9 calls it; old hall code still in cartride.py): 8 open valleys along -X from
  (-9000,150,9000), ridges + tunnels, track data in Shared/CartTrack.luau (no CW parts), stage edges in CartRooms.edges.
- Cell Train: celltrain.py organelle pass + CellLife.client (vesicle traffic on CellPath|n anchors).
- Gram stain: reagent rack + decolouriser timing; server action gramView decides the observed colour.
- First Day questline: PassportService sets attribute FirstDay ("0000".."1111"), achievement firstday; FirstDay.client.
- Run selene from kuwait-parkour/ (root = false errors). Don't stylua generated shared/*.luau. Codex CLI is callable (handoff §9).

## v54 (2026-10-21, local only, NOT published). Branch dev/v54-labs-cartride. Full state: docs/DEVELOPMENT_HANDOFF.md
- Wet lab = tools/labs54.py + Labs54.server + Bench54.client (Item|/Slot|/Use| naming, Studio-only QA hook
  ServerStorage.Labs54QA). Cart Ride = grand valleys in cart_tour53 (LEGZ/CELLZ, 48k studs), captions instead of
  boards, CartTerrain blocks for rivers. Cart keys: Enter/V. Studio MCP Luau runs in a separate _G (use keys/clicks).

## v56 (2026-10-21, local only, NOT published). Branch dev/v54-labs-cartride. Full state: docs/DEVELOPMENT_HANDOFF.md
- Cart valleys stream on the client: cart_tour53.route_parts -> Shared/CartScenery/V1..8 (text lines), built by
  CartScenery.client (current +-1 valley). Server Map ~20.9k parts. Route 84k studs, ~32 min at default speed.
  Edit valleys only via tools/cart_tour53.py; server-needed valley parts must be listed in SERVER_KEEP.
- Help.client (؟ button) replaces how-to boards. DNA extraction bench (5th). Arcade vote (ArcadeVote.client).

## v57 (2026-10-21, local only, NOT published). Same branch. Research report: docs/BSC_CREATIVE_RESEARCH_AND_POLISH.md
- Cart resume (Profiles.cart, CartRide remote "progress"/"resume"), lab guide Highlight (Labs54 NEXT), arcade
  watch-only (ArcadeSpectate), Analytics.luau funnels. QA: V53/Labs54/Arcade53 2-client suites + 14-destination tour.

## v58 (2026-10-21, local only, NOT published). Same branch.
- luau-lsp 1.70.1 in tools/luau-lsp (git-ignored). `bash tools/typecheck.sh`; 61 known false positives listed in its header.
- Fix: Game Show team tie now rewards both teams (was always Blue).

## v59 (2026-10-21, local only, NOT published). Same branch. Owner playtest fixes: docs/DEVELOPMENT_HANDOFF.md section 000
- Moving platforms: MovingPlatforms.client (tag BSCMover). genmap5.rect sorts bounds (facade glass back).
- CampusTerrain FLAT includes the museum. arcade59.py gateways (scripted parts stay at the folder root!).
- Racers: steering sign, wall slide, petri-dish tracks. Game Show: glyph audit (no U+2794 / Unicode 12+ emoji).
- Hot swap: scratchpad swap.sh builds client/server/shared(/map) rbxm into Studio content/bsc; delete it after.

## v60 (2026-10-21, local only, NOT published). Micro Racers kart overhaul: docs/DEVELOPMENT_HANDOFF.md section 0000
- RacerMath is shared by server, client prediction and bots: keep it deterministic (no os.clock / random).
- Client sends one intent per 0.05 s tick with seq; server queues + acks. Studio-only RacerAutopilot / QA_Kart.
- Tests: tools/test_racers60.luau; Studio minimized = black 3D captures (restore the window).

## v61 (2026-10-22, local only, NOT published). Same branch. Owner notes: docs/DEVELOPMENT_HANDOFF.md section 00000
- Cart: FINALE per valley in cart_tour53 (spiral / beside / through), clearance envelope checks every build.
- Race tracks: tools/racetrack61.py (fillet corners). Puzzle room "Restart the Cell" + ServerStorage.PuzzleQA (Studio).
- Lab Rush is real science now; arenas themed. Shared QuestionHistory (server) for every quiz mode.

## v62 (2026-10-22, local only, NOT published). Same branch. docs/DEVELOPMENT_HANDOFF.md section 000000
- Cell Train: per-car placement (TrainTemplate/Loco,Car1..4), lessons in Shared/CellStops (map = names only).
- Specialties Train: WALLS theme per valley + tools/cart_concepts62.py theory sculptures. Final audit: docs/FINAL_VERSION_AUDIT_v62.md.
- Tycoons come after the final version (owner).
