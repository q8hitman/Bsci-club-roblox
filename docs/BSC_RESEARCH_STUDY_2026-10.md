# BSC Island: game design research study and development direction

**Date:** 2026-10-20
**Author:** Claude, lead developer
**Scope:** research and planning only. No scripts, generators, places or branches were changed.
**Reviewers:** the owner, then ChatGPT as an independent second reviewer. ChatGPT has not reviewed this yet.

## 0. How this research was done, and how far to trust it

I am open about the evidence base, because the owner asked me to keep evidence separate from interpretation.

- **I did not play any of the Roblox games named here.** In this session I cannot run another creator's experience
  through Studio or watch gameplay video. Every statement about another game comes from written sources: official
  docs, developer interviews, GDC listings, academic papers, reviews and wikis. Where I go beyond the sources, the text
  says *"my interpretation"* or *"hypothesis"*.
- **Source quality varies a lot.** Searches about popular Roblox games mostly return auto-generated SEO pages. I only
  used points that also appear in a stronger source, or that I mark as weak.
  - **Strongest:** Roblox's own creator documentation, GDC listings, peer-reviewed papers, and named developer
    interviews.
  - **Weakest:** fan wikis and "why it's popular" articles.
- **What I know about BSC Island itself is first-hand.** I built and tested most of v37–v52 in Studio. I give those
  claims at the level they were actually tested: solo Studio play, scripted bots, two-client sessions, or not tested.

## Part 1: Research findings

### 1.1 The first minutes decide everything (onboarding)
- **Roblox's official FTUE guidance**
  ([onboarding docs](https://create.roblox.com/docs/production/game-design/onboarding)):
  - judge onboarding by Day-1 retention;
  - teach the essentials and "the core loop: what they are expected to do and *why*";
  - "get to the fun quickly";
  - give low early progression thresholds;
  - give visible short-, mid- and long-term goals;
  - end the onboarding with a deliberate "moment of joy".
- **The analytics docs** ([engagement](https://create.roblox.com/docs/production/analytics/engagement),
  [retention](https://create.roblox.com/docs/en-us/production/analytics/retention.md)):
  - they offer a *New User First Session Retention* chart, showing the share of new players still in the game after N
    minutes;
  - they suggest checking it whenever the 5-minute figure drops;
  - they add: if you add progression, "make sure there is still enough content available upfront".
- **Community guidance** ([creation.dev glossary](https://www.creation.dev/glossary/onboarding), weak source): teach
  in context, at the moment a mechanic is needed, instead of front-loading tutorials.
- **Why it matters for us:** BSC Island has a lot of content, but a new player is given a list (the 14-card World Menu)
  rather than a first goal. That is the opposite of "teach the core loop".

### 1.2 Round-based multiplayer: short, readable, varied, social
- **Epic Minigames / Natural Disaster Survival:** I only found weak sources. They consistently describe short timed
  rounds, a random game or disaster each round, and simple controls, so variety comes from rotation rather than from
  depth in any single game.
- **Fall Guys:** each level is "essentially an entirely new game mode", built around one readable gimmick (sweepers,
  launchers). A reviewer criticised it when some rounds "drag while others feel mind-numbingly easy", which is an
  argument for tuning every round, not just adding more.
  ([PlayStation blog](https://blog.playstation.com/?p=333768),
  [review](https://primagames.com/featured/fall-guys-ultimate-knockout-review))
- **Overcooked (co-op):** I trust this source more, because it quotes the developers.
  ([Co-Optimus interview](https://co-optimus.com/interview/1838/page/1/indie-ana-co-op-and-the-overcooked-interview.html),
  [SUPERJUMP analysis](https://superjumpmagazine.com/overcooked-how-design-creates-teamwork))
  - The designers wanted a game where "one person can't … carry the whole team".
  - They kept the inputs minimal so the kitchens and the player interaction could be complicated.
  - Each level deliberately turns into chaos part-way through, which forces the players to renegotiate roles.
  - The loop is "urgency, mistake, recovery".
- **Keep Talking and Nobody Explodes:** the information split *is* the mechanic. The defuser cannot see the manual
  and the experts cannot see the bomb.
  ([GDC Vault](https://gdcvault.com/play/1023113/Designing-Asymmetric-Gameplay-For-Keep))
  - Another team's critique: asymmetry creates tension, but it can leave one role passive.
    ([P1 Meltdown](https://mechanicsofmagic.com/2025/04/25/p1-meltdown/))
- **Flee the Facility (asymmetric hunter):** weak sources only. One hunter against several escapees, with randomly
  assigned roles and varied maps, gives replay value from role swaps.
  ([role summary](https://shapes.inc/fandom/flee-the-facility/roles))
- **Kart racing:** catch-up items help newcomers, but critics argue that a strong rubber band "punishes being good".
  ([Anil Dash, "Elastic Happiness"](https://anildash.com/2009/04/06/elastic-happiness/),
  [PopMatters](https://popmatters.com/183156-chaos-and-control-in-mario-kart-8-2495646194.html)) The design lesson:
  give gentle, visible catch-up, never invisible punishment.

### 1.3 Obbies: curve, checkpoints, fairness
- **Community guides** (weak to medium sources):
  ([creation.dev obby guide](https://www.creation.dev/blog/roblox-obby-design-guide),
  [gamertagmythras](https://gamertagmythras.com/blog/roblox/best-roblox-obby-games))
  - the first ~20% of stages should be easy for anyone;
  - the middle should add timing and precision;
  - the last ~30% should challenge skilled players;
  - add regular "breather" stages;
  - checkpoints about every 3–5 obstacles early on, widening later;
  - checkpoints should look different (pad, flag, particles);
  - "a hard obby with unfair hitboxes is poor design".
- **Tower of Hell** is a counter-model ([Pocket Tactics](https://www.pockettactics.com/tower-of-hell/visits)): no
  checkpoints, a randomly built tower every round, a timer, and racing against others. It is reported at over 22B
  visits.
  - *My interpretation:* it works because rounds are short and shared. A 100-stage linear obby with saved progress is a
    different product, and should borrow its social racing, not its punishment.

### 1.4 Rides: dark-ride and coaster craft
- **Dark-ride practice** ([Jora Vision](https://joravision.com/news/darkrides2017),
  [Blooloop](https://blooloop.com/how-to-design-dark-ride/), [Utrecht review](https://dspace.library.uu.nl/handle/1874/438505)):
  - the story comes first and leads every element;
  - scenery, sound, lighting and effects should be synchronised;
  - "strong theming and emotional impact beat expensive technology";
  - the experience rests on narrative transportation, presence, flow and emotion.
- **Coaster pacing** (community sources: [RCT forum](https://gog.com/forum/rollercoaster_tycoon_series/how_do_you_make_decent_rollercoasters),
  [rctspace tips](https://rctv1.rctspace.com/test/info/tips1.html),
  [ride review](https://behindthethrills.com/2021/06/jurassic-world-velocicoaster-review-new-islands-of-adventure-roller-coaster/2/)):
  - straights build anticipation, drops give the thrill, and camelback hills create airtime;
  - turns at the slow peaks of a "sine wave";
  - tunnels raise excitement;
  - too many strong forces become unpleasant;
  - one sustained "big moment" lands better than many small pops.
- **Roblox cart rides:**
  - *Cart Ride Into Rdite!* is listed at about 558M visits, released 2020 ([rotrends](https://rotrends.com/game/1681168130)).
  - Its specific mechanics are not documented in any source I found.
  - Listings of other cart rides mention a recurring classic: *going too fast on turns throws you off the rails*
    ([Roblox listings](https://www.roblox.com/games/7910903146/Generic-Cart-Ride)). *My interpretation:* risk-versus-speed
    is the genre's core toy.
- **Roblox train engineering** ([DevForum](https://devforum.roblox.com/t/how-would-you-handle-a-train-system/3363135),
  [smooth train](https://devforum.roblox.com/t/a-smooth-train-system/747831),
  [Lerp coaster](https://devforum.roblox.com/t/lerp-coaster-system/82319)):
  - move the train on the client, as a distance along a precomputed spline;
  - weld the cars to one root;
  - don't update each wagon separately, or they drift apart;
  - server CFrame updates every frame look choppy.
  - **We already do this**, which validates the v28–v31 architecture.

### 1.5 Cell journeys and science games
- **Two ways to do a cell journey:**
  - *The Body VR: Journey Inside a Cell* is a narrated, lightly interactive tour (under 30 min, free, aged 10+)
    ([UploadVR](https://www.uploadvr.com/body-vr-brings-vr-education-htc-vive-today/)).
  - *InCell VR* is a racing game along microtubules against a virus wave. Its reviewers found the science "a little
    whitewashed" by the mechanics ([Road to VR](https://roadtovr.com/?p=163692)).
  - Lesson: the science must be *the mechanic*, not decoration, but a pure tour is passive.
- **Foldit / Eterna** ([Foldit motivation study](https://oro.open.ac.uk/44708),
  [Stanford](https://news.stanford.edu/2019/07/21/contributing-science-games/)):
  - motivation comes from the challenge, the community and real contribution;
  - the designers iterated with both players and scientists;
  - a narrative wrapper increased time spent, but not progress through the tutorial.
- **Gamified labs (Labster)** ([Labster research](https://labster.com/research/improving-biotech-education-through-gamified-simulations),
  [McMaster SoTL](https://mi.mcmaster.ca/?p=26808)):
  - the published *Nature Biotechnology* 2014 study reports higher learning and motivation, especially when combined
    with teaching (the headline percentages come from Labster's own summary);
  - students lose motivation "when educational content and game activities are disconnected";
  - the "freedom to fail" with immediate feedback helps.
- **Niche** (genetics survival) ([Common Sense](https://www.commonsense.org/education/game/niche-a-genetics-survival-game)):
  - real dominant, recessive and co-dominant inheritance is "interwoven with the game mechanics";
  - weaknesses: too little in-game help and a steep curve.
- **Cell Lab** ([listing](https://www.taptap.io/app/16414)): you design a genome so that cells survive a challenge.
  The developer deliberately simplifies each cell to one function to keep it playable.
- **Kahoot research** ([Wang & Tahir review](https://research.gold.ac.uk/id/eprint/39435)):
  - points and audio raise engagement;
  - effects on learning are inconsistent;
  - **speed scoring encourages guessing and anxiety**.
  - This is directly relevant to our Exam Hall and Game Show.
- **Roblox in education** ([systematic review, 40 studies](https://doaj.org/article/b948d078c5cd41249b5410d88c47134d)):
  - benefits are strongest with social and collaborative learning;
  - the authors warn about weak teaching design;
  - the empirical evidence is still early.

### 1.6 Hubs, exploration, environment, tech
- **Quest-giver hubs (Bee Swarm Simulator wiki):**
  ([Bears](https://bee-swarm-simulator.fandom.com/wiki/Category:Bears))
  - permanent quest NPCs, each with a long questline;
  - early quests teach the basics;
  - most quests are optional, and only a couple gate progress.
  - *My interpretation:* NPCs become reasons to travel, not decoration.
- **Collectible hunts ("Find the Markers"):** weak sources only. They describe curiosity-led exploration, layered
  difficulty, and badges as status. We already have 12 cats and 8 specimens.
- **Environment art** ([Roblox environmental art curriculum](https://create.roblox.com/docs/tutorials/curriculums/environmental-art)):
  greybox, then a modular asset library, then assemble the world, then a performance pass.
  - That is exactly the pipeline we lack: we build final geometry directly from Python primitives.
- **Performance** ([Design for performance](https://create.roblox.com/docs/performance-optimization/design)):
  - pick a low-end baseline device early (the example budget is under 1,000 draw calls and 1M triangles);
  - the Studio emulator is **not accurate for memory**;
  - enable instance streaming for large experiences;
  - prefer built-in materials over custom textures.
- **Mobile UI** ([ScreenInsets](https://robloxapi.github.io/ref/enum/ScreenInsets.html),
  [UI guide](https://www.creation.dev/blog/roblox-ui-design-best-practices)):
  - use CoreUISafeInsets for button guis;
  - make touch targets at least 44–48 px;
  - mobile has no hover, so tooltips need a tap.
- **Atmosphere (Doors):** the only usable source was one article. It credits sound and lighting (clicks, a warning
  buzzer, flickering lights) for most of the tension. *My interpretation:* **sound is our most under-used tool.**

## Part 2: BSC Island assessment

### 2.1 Where we stand (honest)
| Area | What exists | Real test level | Main weakness against the research |
|---|---|---|---|
| First session | Spawn in the College lobby, welcome card, 14-card World Menu, Gateway Hall | Solo, scripted | No core loop and no first goal: a menu instead of a journey (§1.1) |
| Campus (south/north) | Big generated buildings, Red Corridor + east walk, gym, gardens, museum | Solo walk tests | Built straight from primitives with no modular kit; many text signs; a few areas still empty or flat; few sounds |
| HQ + Gateway Hall | Hall with 11 portals, quiz corner, café, office corner | Solo | Functional but generic; the HQ does not yet tell the club's story |
| Specialties Cart Ride | 8 themed rail-hall rooms, cruise controls, landmarks, end card | Full solo ride (v52) | A *tour* since v31: safe but low on thrill; the rooms are mostly boxes with props, without "big moments" (§1.4) |
| Cell Train | 12 organelle stops, free camera, labels | Solo | A passive tour, the *Body VR* model without its narration (§1.5) |
| 100-stage obby | 8 zones, puzzles every 5 stages, moon zone, laser stage | Stages walked at various times; never a full human run | No measured difficulty curve; difficulty spikes and signage were real problems before; checkpoints not readable enough |
| Arcade (5 arenas) | LastCell, LabRush, PetriFloor, ATPRush, EnzymeSweeper, tiers, mutations | Bots, 2 clients for some | Wide but shallow: no results screen, no spectating, little telegraphing; LabRush is a lighter Overcooked without the chaos phase |
| Virus Tag, Exam, Game Show, Puzzle Rooms, Micro Racers, Laser Escape | Each complete at a basic level | Mixed: bots, 2 clients, solo | The Exam and Game Show use time pressure that research links to guessing (§1.5); there is only one puzzle room |
| Labs (microscope, Gram, PCR, gel, light microscopy) | Real procedure simulations with grading | Solo, real clicks | Good science, but procedural ("follow the steps") rather than *play*; no Biotechnology design toy |
| Museum (8 exhibits) | Interactive exhibits plus Passport | Solo and 2 clients | Fine; could act as the bridge to the labs |
| Passport, titles, weekly | Server-verified XP | Pure tests plus solo | A strong foundation, not yet used to steer a new player |
| Tech | Rojo + Python generators, server-authoritative rewards, client-driven rides | Studio only | Never published for a real phone or multi-player session; streaming is off (~28k parts); DataStore is untested live |

### 2.2 Critical judgement
1. **We have built breadth, not depth.**
   - About 20 activities, each at a "works when a bot plays it" level.
   - The research consistently rewards a few polished, readable loops (Fall Guys round tuning, Overcooked escalation,
     Tower of Hell's single loop).
   - **Recommendation:** stop adding activities until the strongest few are excellent.
2. **The world is a menu.**
   - Most attractions are separate teleport destinations far from the campus.
   - That is fine technically, but the campus, the identity we care about most, is where players spend the least
     purposeful time.
3. **The v31 decision to make the Cart Ride a calm tour was right for comfort but wrong for the brand promise.**
   - The owner now calls it a "major attraction".
   - The genre's core toy is controllable speed with risk, and big set-pieces (§1.4).
   - Proposal: give it a Thrill mode while keeping the calm mode for younger or nervous players.
4. **The time pressure in the Exam and Game Show contradicts the evidence** that speed scoring causes guessing and
   anxiety (§1.5).
   - Accuracy should be worth more than speed.
   - Speed can stay as a small bonus or tie-breaker.
5. **The labs teach procedures; they need *goals*.**
   - Labster, Niche and Cell Lab all show that motivation comes from *designing something that must work*, not from
     following steps.
6. **Sound and art pipeline.**
   - We cannot hand-place art at quality from Python primitives forever.
   - The Roblox curriculum's modular-kit pipeline (§1.6), plus licensed Creator Store audio, is the realistic path to
     "professional".
7. **What is stronger than it looks:**
   - the server-verified Passport (a ready-made questline engine);
   - the client-spline ride engine (it can handle a thrill ride);
   - the Gateway Hall (a natural "lobby with live player counts");
   - a real university and real club, which give us authentic stories most Roblox games cannot have.

## Part 3: Creative opportunities (original ideas, with their inspiration)

Each idea names its inspiration, but the design is our own.

### 3.1 "First Day at the College" (onboarding questline)
- **Inspiration:** the FTUE docs and quest-giver hubs.
- **The questline:**
  1. Noura (the new student) meets you in the south lobby and asks you to help her find the club.
  2. You cross the Red Corridor, where she points out the north building and the club's room.
  3. At the HQ, Abu Ali gives you your **BSC Passport** with its first stamp.
  4. The Gateway Hall then glows on 3 starter portals: Specialties Express, Arcade and Museum.
- **Under 4 minutes**, every step with a "moment of joy" (confetti, a stamp sound).
- **Optional, and skippable at any point.**
- **Uses what we have:** NPCs, the Passport and the hall. No new world.

### 3.2 Specialties Express: "Ride and Thrill"
Two modes chosen at the station.
- **Calm Tour** (today's ride).
- **Thrill Run:**
  - The rider controls the throttle.
  - Taking a curve marked red at too high a speed derails the train back to the room's start, with a funny effect,
    not a punishment.
  - **Branch junctions:** press the switch in time to take the bonus tunnel.
  - One **signature set-piece per specialty** (all original):

| Specialty | Set-piece |
|---|---|
| Microbiology | Ride *through* a giant agar plate as colonies bloom; a flagellum spin tunnel |
| Biochemistry | Enzyme "lock and key" gates that open only at the right speed; a glowing substrate cascade drop |
| Animal Biology | A savanna diorama, then a dive into a whale-scale ribcage tunnel; flocks overhead |
| Plant Biology | Climb a giant stem through a stoma opening into the leaf; a chloroplast light show |
| Molecular Biology | The DNA helix spiral (already there) unzips as you pass; replication fork split tracks |
| Forensic Science | A crime-scene tunnel under UV light reveals hidden clues; the rider snaps evidence photos |
| Agriculture | Through a greenhouse, an irrigation canal splash, then a seed vault |
| Biotechnology | A bioreactor tank finale: the train rides a spiral inside a glass fermenter, and the rider's "product" is revealed |

- **Multi-seat carts** so friends ride together. A timer and a "perfect run" badge in Thrill mode only.
- **Tech:** reuse the client spline engine and the CW waypoint flags ("s" and the unused "g" already exist). Derailing
  is client-visual with a server-verified section restart.

### 3.3 Cell Train becomes "The Vesicle Express"
- **The core idea** (scientifically real): inside cells, cargo vesicles are carried along **microtubules by kinesin
  motor proteins** that "walk".
  - So the train *is* a vesicle, the track *is* a microtubule, and an animated kinesin walks it forward. No other ride
    has this; it is accurate and memorable.
- **The journey is a delivery route:**
  1. Pick up a protein at the **rough ER**.
  2. Get it packaged and tagged at the **Golgi**.
  3. Deliver it to the **cell membrane** by exocytosis: the vesicle fuses with the membrane in a finale where the
     membrane opens to the outside.
- **Short hop-off moments** (each 20–40 s, optional):
  - spin ATP synthase to power the train;
  - help a ribosome catch the correct tRNA codons;
  - squeeze through a nuclear pore.
- Combines the *Body VR* narration with the *InCell* ride energy (§1.5).

### 3.4 Biotechnology Studio (the flagship lab)
- **Inspiration:** Niche, Cell Lab and Labster's "freedom to fail".
- **Goal:** "Make insulin-producing bacteria for the clinic."
- **Steps:**
  1. Choose a **promoter strength**, a **gene** (the insulin gene) and an **antibiotic-resistance marker**, as snap-in
     cards.
  2. Transform *E. coli*.
  3. Plate on the antibiotic, so only transformed colonies grow, shown visibly.
  4. Scale up in a **bioreactor**, controlling temperature and pH.
  5. Purify the product.
- **Wrong choices give understandable, sometimes funny, outcomes:** no colonies (wrong marker), or a weak glow (weak
  promoter).
- **Replay:** other "orders" (a GFP glow-in-the-dark pet bacterium, an enzyme for detergent, a drought-tolerant plant
  via *Agrobacterium*).
- **Co-op version:** two players split the bench (bioreactor vs purification), following the Overcooked lessons.
- **Scientific review is required** before release.

### 3.5 "Outbreak Response" (deeper Virus Tag variant)
- **Inspiration:** KTANE's information split and Flee the Facility's roles.
- **The roles:**
  - One team plays **field epidemiologists** on the campus, collecting swabs and contact clues from NPC patients.
  - Another plays the **lab team** in the HQ lab, reading the samples on the microscope or PCR.
- Only by talking do they identify patient zero and the pathogen before the outbreak timer ends.
- **Uses existing labs and the campus**, and makes the campus a play space.
- **Replaces nothing:** it is offered as Virus Tag's "advanced" mode once Virus Tag itself is polished.

### 3.6 Field Notebook expedition (exploration)
- **Inspiration:** collectible hunts and the photo-safari genre (*my interpretation*, no source cited).
- **How it works:** the existing Photo Mode becomes a field camera, and the player photographs specimens hidden across
  the campus, the museum and the worlds: desert plants of Kuwait, campus cats, lab organisms.
- **Rewards:** each new entry fills a page in a field notebook (Passport tab) with a real fact.
- **Content:** Kuwait's native flora (العرفج، السدر، الطلح) is authentic, local, and already partly modelled in the
  desert garden.

### 3.7 Club life (social/community)
- **Club noticeboard** in the HQ (the weekly challenge plus the next real club event).
- **Party travel:** friends who join a "lab group" go through gateways together.
- **Gateway Hall live counts:** "3 players in Arcade".
- **Seasonal events tied to the real calendar:** orientation week, exam season (Exam Hall double XP), National Day.
- **Graduation:** as the 100-stage finale (the stage already exists), with a class photo.

## Part 4: Improvement priorities (ranked by player impact)

Complexity scale: **S** is a few days, **M** about 1–2 weeks of agent work, **L** several weeks, **XL** a multi-month
programme. "Agent work" assumes the current toolchain.

| # | Improvement | Impact | Complexity | Key risks | Depends on |
|---|---|---|---|---|---|
| 1 | Real playtest baseline: private publish + 4–6 club members on phones + Roblox analytics | Very high (tells us the truth) | S | Needs owner approval to publish privately; DataStore live | Existing private place |
| 2 | Onboarding questline "First Day" (§3.1) + clear first goal | Very high | M | Must stay skippable, with no mandatory text walls | NPCs, Passport, Gateway Hall |
| 3 | Specialties Express "Thrill Run" + 8 set-pieces (§3.2) | High (flagship) | L to XL (art-heavy) | Motion comfort, derail fairness, mobile FPS in big rooms, art pipeline | Ride engine, CartRooms |
| 4 | Sound and atmosphere pass (ambience per area, UI sounds, ride audio) | High per cost | S to M | Licensed audio only; volume balance | Creator Store audio |
| 5 | Arcade depth: results screen, spectating, telegraphs, LabRush chaos phase; merge 3 weak arenas into one rotating "Bio Party" | High | M | Balance needs real players | Arcade framework |
| 6 | Exam and Game Show: accuracy over speed; explanations after each question | Medium-high (learning) | S | Few | Existing banks |
| 7 | Obby audit: difficulty curve, breathers, readable checkpoints, per-zone signature mechanic, optional time trial | High (100 stages = long engagement) | M to L | Must keep owner rules (no visible timer unless approved) | Obby generator |
| 8 | Biotechnology Studio (§3.4) | High for the club mission | L | Scientific accuracy review; UI complexity on mobile | Lab framework, Passport |
| 9 | Vesicle Express rework of the Cell Train (§3.3) | Medium-high | L | Animation cost; scale and readability | Cell world |
| 10 | Art pipeline: modular kit library (walls, windows, lab furniture) + campus art pass + StreamingEnabled trial | High long-term | L to XL | Must not alter approved campus layout; streaming can break scripts that read far-away parts | Generators |
| 11 | Outbreak Response, Field Notebook, club social features (§3.5–3.7) | Medium | M each | Scope creep | Items above |

## Part 5: Development roadmap

The principle is **one flagship at a time, each gated by a real playtest**, so we never build on assumptions.

1. **Stage 0 "Truth" (item 1):**
   - Private publish (owner approval needed), then a phone and PC playtest with club members.
   - Collect first-session retention, where players get lost, and what they liked.
   - Fix only critical bugs found.
2. **Stage 1 "First Ten Minutes" (items 2, 4 and 6):** onboarding questline, sound pass on the campus, HQ and hall,
   and the Exam/Show scoring fix. Then a playtest.
3. **Stage 2 "Flagship Ride" (item 3):**
   - Build Thrill Run mechanics plus **2 rooms** to final quality as a vertical slice (Microbiology, Biochemistry).
   - Playtest; only if it lands, build the remaining 6 rooms.
4. **Stage 3 "Play Together" (item 5):** Arcade depth and consolidation, then a 4–8 player test session.
5. **Stage 4 "Signature Science" (items 8 and 9):** Biotechnology Studio first, then the Vesicle Express. Each needs a
   scientific review before release.
6. **Stage 5 "Long Game" (items 7, 10 and 11):** obby audit, art pipeline and campus art pass, then the community
   features.

**Never at the same time:** two big world-geometry changes, or any change to approved campus layout without the
owner's approval.

## Part 6: Recommended first milestone

**Milestone A: "Truth + First Ten Minutes" (Stage 0 + Stage 1).**

**Why first:**
1. Everything we know about BSC Island's quality comes from solo Studio tests and bots. Before investing weeks in a
   flagship ride, we need one real session on real phones with real club members. It is the cheapest, most decisive
   evidence available.
2. The research is unanimous that the first minutes decide retention (§1.1). Today a new player sees a menu, not a
   goal. A short questline that walks through the College, the Red Corridor and the HQ also *showcases the Kuwait
   University identity*, our unique asset, at the very moment players decide whether to stay.
3. The sound pass and the Exam fix are small, but they raise perceived quality everywhere.
4. It touches no approved geometry and keeps all systems.

**Done means:**
- New players can reach their first activity in under 4 minutes without help, judged by observation and the analytics
  funnel.
- No critical bugs from the playtest.
- The Exam and Game Show reward accuracy.
- The playtest report is shared with the owner and ChatGPT.

**Then:** Milestone B is the Specialties Express vertical slice (§3.2, 2 rooms).

## Part 7: Questions for the owner
1. **Private publish for playtesting:** may we update the existing private place, so that 4–6 club members can play on
   phones? This is needed to test multiplayer, DataStore and mobile for real.
2. **Cart Ride tone:** do you approve **two modes** (Calm Tour plus Thrill Run with throttle and derail)? In v31 you
   preferred a calm tour; this keeps it and adds thrill.
3. **Arcade consolidation:** may we merge PetriFloor, ATPRush and EnzymeSweeper into one rotating "Bio Party" playlist
   instead of polishing all five arenas separately? Nothing would be deleted until you decide.
4. **Exam / Game Show scoring:** accuracy first, with speed only as a small bonus?
5. **Obby timer:** v29 removed the visible timer at your request. Would an *optional* time-trial mode (off by default)
   be acceptable?
6. **Cell Train concept:** do you like the "Vesicle Express" (kinesin walking on a microtubule) direction?
7. **Biotechnology Studio:** which real products should we feature (insulin, GFP, detergent enzyme, drought-tolerant
   plant)? Can a faculty member or club expert review it?
8. **Campus reality:** can you share photos of the Biological Sciences department areas and the club room, so the
   onboarding route and art pass stay faithful?
9. **Audience:** is the primary audience university students, school students, or both? This sets the difficulty and
   the reading level.
10. **Audio:** may we use licensed Roblox Creator Store sounds and music (free, licensed for use)?

---

**Not done in this phase:** no scripts, generators, places, builds or branches were modified. Only this report file
was added.
