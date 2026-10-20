# BSC research update: owner's creative direction + hands-on Roblox research (2026-10-20)

**Scope:** research and assessment only. No script, generator or place file was changed, and nothing was published or
merged. This update corrects and replaces parts of [BSC_RESEARCH_STUDY_2026-10.md](BSC_RESEARCH_STUDY_2026-10.md):
§3.2 (the Cart Ride), §3.3 (the Cell Train), and Parts 4–6 (the priorities, roadmap and first milestone).

## 1. Corrected vision (confirmed)

### 1.1 Specialties Cart Ride
- **The ride:** a very long scenic adventure where the journey itself is the experience.
- **Eight stages:** eight large, memorable themed environments, one per specialty and in the official order. They are
  stages of one epic ride, not small glass rooms.
- **Environment:**
  - long track with tunnels, climbs, drops, viewpoints and landmarks;
  - environmental events;
  - calm stretches alternating with exciting sequences.
- **Controls and camera:**
  - physical onboard controls: press to accelerate, press to brake, and stop, without holding W;
  - free camera.
- **Rules:**
  - movement must be smooth, and the ride must work with several players at once;
  - **never** derail, kill or force a restart for going too fast. That was rejected before and stays rejected.

### 1.2 Cell Train
- **First improve the existing train:**
  - scientific accuracy;
  - realistic organelle shapes and relative scale;
  - animation, lighting and smooth movement;
  - free camera and events;
  - teaching woven into the ride, not just labels.
- **Avoid:** "glowing blobs with a name board".
- **Vesicle Express:** future idea only. It is **not** to be built now, and §3.3 of the study is withdrawn as a near-term
  item.

### 1.3 Unchanged rules
- Improve what exists before adding.
- Keep the approved attractions.
- No Arcade merge or delete without approval.
- The university connections stay as approved: the Red Corridor plus the east ground walk.
- No return to the old Island.

## 2. Hands-on Roblox research: feasibility and honest findings

### 2.1 Feasibility
**Possible, but limited.** On this PC the Roblox Player is installed and the owner's account is already signed in, so I
could launch public experiences with `roblox://experiences/start?placeId=…` and control them with computer-use. I found
current place IDs with Roblox's public search API; the older IDs I knew were gone (join error 524).

**Limits I hit:**
- Screenshot-driven play is slow, so I can't "play for 30 minutes" the way a person does.
- Paid pads and Robux prompts sit next to the free ones in these games. I opened one purchase prompt by accident in
  Bobsled and closed it with X; **nothing was bought**. After that I stopped exploring to avoid any further risk.
- I did not chat, contact players, change settings or spend Robux.

### 2.2 What I actually experienced (firsthand, nothing more)
| Game | What I did | Firsthand observations |
|---|---|---|
| Natural Disaster Survival | Entered the lobby only | 4-line welcome card: short and clear |
| cart ride around nothing | Spawned a cart and rode briefly | Troll/gamepass culture (bomb, flight potion, hacker and race carts); free green spawn pads beside red paid pads; **the cart moves only while W is held** and stops on release; my character died and then walked off an edge; a huge track network overhead creates curiosity |
| Cart Ride Down A Mountain | **Rode about 1.5 minutes** (distance 1.72) | Clean modern UI: cart spawner menu, **distance counter**, cash per distance; on-screen ↓ / Stop-Start / ↑ buttons, cart stopped by default, speed 40 (buttons only worked after the middle toggle); scenery river → cliffs → **dark smoky tunnel** with other players' carts; **a crash killed me**, and the death screen offered *Revive for 29 Robux*, a free revive via an ad, or back to spawn |
| Cart Ride Into Rdite | Spawn area only | Paid pads at spawn (sabotage player, magic carpet, admin commands, boombox); the camera clipped into objects |
| Bobsled | Village/spawn only | Polished village, one centred instruction, Friend Boost, Sleds/Rebirth/Shop menus, a **scheduled weather event timer** ("Blood Moon"); paid pads close to the free pad (my accidental prompt) |

**Not experienced:** I did not finish any long cart ride, so I can't speak firsthand about the late game, pacing past
about 2 minutes, or replay loops. Those points in the study come from published sources and are labelled that way there.

### 2.3 Lessons for BSC (what to copy and what to avoid)
**Copy:**
1. One clear sentence at the start ("Press ▶ to start, ＋/－ for speed").
2. A **distance or progress counter** that keeps players riding ("Stage 3 of 8 · 42%").
3. **On-screen buttons** that work with touch and need no held key, which suits phones.
4. **Tunnels for contrast:** dark → bright reveals are the strongest scenery moment I saw.
5. **Scheduled environmental events** (Bobsled's timer): a reason to stay and come back.
6. Seeing other players' carts on the same track makes the world feel alive.

**Avoid:**
1. Death by speed, plus paid revives. This is exactly what the owner rejected.
2. Troll or sabotage tools and paid pads next to free ones.
3. Holding W to move.
4. Camera clipping into scenery.

## 3. Lab audit (read from code plus one 3D screenshot; nothing modified)

The labs are in the Research Lab world (6000,300,6000). Prompts named `LabStation|<kind>` open the panels, and
`Lab.server` checks the answer and gives the reward (`LabData.REWARD`: microscope 4, gel 4, pcr 8, gram 6;
cooldown 6 s).

| Station | What it really is | Physical in 3D? | Real process or menu? | Accuracy | Weak or unfinished |
|---|---|---|---|---|---|
| **Light Microscopy** (`LightMicroscope.client`, 893 lines, v41) | Full 2D microscope simulation: coarse/fine focus, light, objectives 4×–100×, oil, notebook | No. A 2D panel opened from the bench | **Real process.** You must focus, choose the objective and add oil at 100× | Good | The strongest lab. Only the 3D bench around it is primitive |
| **Cell identification** (`microscope` mode) | Text quiz: a slide description and 4 buttons (plant, animal, bacteria, fungus) | No | Menu quiz, **no image** | Correct but shallow | Duplicates Light Microscopy at a lower level; it needs a real image or should merge into it (owner decision) |
| **Gel electrophoresis** (`gel`) | Pick the fragment that travels farthest; the bands animate by log(bp) **after** you answer | No | Quiz with an animation | Physics right (small fragments move farther) | No loading wells, no voltage, no ladder reading |
| **PCR** (`pcr`) | Timing needle into a green zone for 92–98 / 50–60 / 68–76 °C × 3 cycles | No | Half process: the temperatures are right, but it plays as a timing mini-game | Temperatures correct | No primers, polymerase or copy counter (2→4→8) |
| **Gram stain** (`gram`) | One button steps through 4 fixed steps while the slide changes colour, then you pick positive or negative | No | **Click-through.** The order can't be wrong | The steps and the 4 samples are correct | No real choice of reagent or timing; the decolouriser step, the key one, has no risk |
| **Computer** (upgrades) | Upgrade shop with RP | No | Menu | n/a | Fine as a shop |
| **Batch** | Admin-edited batch content | No | Menu | Depends on content | n/a |

**3D quality (screenshot):**
- primitive blocks and cylinders, flat colours;
- a green sign board blocking the benches;
- a ball-and-stick DNA model.

The lab *works* but does not *look* like a lab.

**Summary:** 1 real process (the microscope), 2 half processes (PCR, gel), 2 superficial (cell ID, Gram), and none is
physical in 3D.

**Recommended improvements, in order:**
1. Gram as a real procedure. Choose each reagent from the bench; the decolouriser time decides the result (too long
   makes a positive look negative). It's cheap and teaches the most important idea.
2. Gel: load the wells yourself, set the voltage, read the ladder.
3. PCR: show the copy count doubling, and require choosing the primers.
4. Cell ID: either merge it into Light Microscopy (real slides) or show an actual image. **Owner decision.**
5. 3D dressing of the room: real-looking benches, a pipette rack, a centrifuge, a gel tank, move the sign off the
   benches. These are visual only and change no logic.

**Biotechnology Studio** (study §3.4) stays a **separate future proposal**. It is not part of this audit and not part of
the first milestone.

## 4. Revised Cart Ride direction ("Specialties Grand Tour")

### 4.1 Current state (from the v52 test and code)
- One continuous ride of about 3 minutes, roughly 1144 track points (about 6,000 studs) at about 35 studs/s.
- The 8 specialties are glass bio-dome rooms with 2 landmarks each, plus a helix around the DNA.
- Controls already exist: ▶ / ＋ / － / ⏸, with no held key, auto-slowing in bends and a smooth stop.
- **There is no derail and no death today.** That stays.
- **The gap against the vision:** the ride is short, each room is small and similar, and there are few tunnels or
  reveals and no events.

### 4.2 Target
| Item | Proposal |
|---|---|
| **Length** | **12–15 minutes** at cruise speed, built in stages. One stage of 90–120 s per specialty, plus a prologue and a finale. (20–25 min at 35 studs/s would need about 45,000 studs of track. That is possible later, but I'd prove 12–15 first.) |
| **Structure per stage** | Approach tunnel (dark) → **reveal** (big vista) → calm sightseeing stretch → **one event** → exit portal or tunnel into the next stage |
| **Stage scale** | Each specialty is its own open landscape (about 600–1000 studs), not a dome room. Example: Microbiology inside a giant Petri dish with colonies as hills; Plant Biology through a leaf with the stomata as gates; Forensic Science as a night crime-scene street; Agriculture as farm fields and a greenhouse; Biotechnology as a bioreactor hall |
| **Events (no death)** | Lights flicker in a tunnel, a pollen storm, a bacterial colony grows in real time, a gate opens only after a short fact, a scheduled "event of the hour" (like Bobsled's timer) |
| **Controls** | Physical onboard console and matching on-screen buttons: ▶ start, ＋ accelerate, － brake, ⏹ stop. No held key. The speed ceiling is **comfort-limited, never punished**: in a sharp bend the cart slows itself smoothly |
| **Camera** | Free orbit by default, plus a "cinematic" button at the reveal points |
| **Multiplayer** | Each player's cart runs on the client (as today) and other players' carts are visible; optional shared carts for friends (stage 2 of the work) |
| **Progress** | "Stage 3/8 · Biochemistry · 42%" bar, a stamp in the Passport per completed stage, continue from the last stage |
| **Teaching** | One short spoken or text fact at each reveal; no quizzes during the ride |

### 4.3 How to build it without breaking what works
Keep the existing engine (the client spline over `CW|i|flags|label`) and its controls. Grow the track **one stage at a
time**: first one stage as a prototype (Microbiology), reviewed by the owner, then the rest.

## 5. Cell Train improvements (existing train, no Vesicle Express)

### 5.1 Current state (from `tools/celltrain.py` and `CellTrain.client.luau`)
- **World:** one 640 × 640 × 240 purple room at (-12000,0,0), with a single track loop at radius 235 (about
  1,500 studs).
- **Stops and labels:** 11 stops with Arabic captions and floating name boards (v31: radius 205).
- **Organelle shapes:**
  - the nucleus is a sphere 120 across;
  - the mitochondria are cylinders with flat crista slabs;
  - the rough ER is wavy sheets with ribosome balls;
  - the Golgi is stacked discs;
  - lysosomes and peroxisomes are glass balls;
  - there are centrioles and cytoskeleton strands.
- **Features already there:**
  - the v50 camera toggle (cinematic or free) and speed toggle;
  - a stop progress badge;
  - the v51 bilayer entry tunnel;
  - the v28 death handler.
- **Weaknesses:**
  - everything floats in one room;
  - almost nothing moves;
  - the scale is uniform;
  - the "cytoplasm" is a stop with nothing to see;
  - no events;
  - the labels do the teaching instead of the scenery.

### 5.2 Improvements (in order)
1. **Shapes and accuracy:**
   - **Mitochondria:** a double membrane with folded cristae (an inner surface, not slabs).
   - **Nucleus:** a double envelope with real pores, chromatin inside, and the rough ER continuous with the envelope.
   - **Golgi:** curved cisternae with a cis and a trans face, and vesicles budding.
   - **Lysosomes:** smaller than mitochondria.
   - **Ribosomes:** tiny, and many.
2. **Motion:** vesicles travelling from the ER to the Golgi to the membrane along microtubules, motor proteins
   "walking", mitochondria slowly moving, cytoplasm particles drifting.
3. **The route goes *through* things, not around:** along the ER, past the nuclear pore (looking in), under the Golgi.
   Keep the loop and the stations; reshape the path.
4. **Light:** dimmer cytoplasm with each organelle lit by its own colour; less Neon, more soft glow.
5. **Teaching moments:** at 3–4 points, a short "watch": a protein leaves the ribosome → ER → Golgi → secreted. The
   scenery tells the story and the caption only names it.
6. **Free camera stays; movement must be smooth** (check for spline jitter at the stops).

## 6. Updated roadmap and first improvements

| # | Step | Why first |
|---|---|---|
| **1** | **Cart Ride, stage-1 prototype (Microbiology as a full stage)** plus the progress bar and the ＋/－/⏹ console checked on phone | It is the owner's #1 vision; one stage proves the scale, pacing and controls before building 8 |
| **2** | **Cell Train accuracy and motion pass** (shapes, vesicle traffic, route through organelles, lighting) | The train already exists; quality per hour of work is highest here |
| **3** | **Gram stain → real procedure** and the lab room's 3D dressing | Cheapest lab fix, turns a click-through into real learning |
| 4 | Cart Ride stages 2–8 (one per review cycle) | Only after stage 1 is approved |
| 5 | Gel and PCR deepening; the cell-ID decision | Medium value |
| 6 | Scheduled ride events, shared friend carts | Polish and social |
| Later | Biotechnology Studio, Vesicle Express | Separate proposals; not now |

The study's "Milestone A" (Truth + First Ten Minutes) still applies for onboarding. It can run in parallel because it
touches different files.

## 7. Questions for the owner
1. **Ride length:** is a 12–15 min first target OK, or do you want 20+ min from the start?
2. **Stage-1 specialty:** Microbiology (first in the official order), or another one?
3. **Speed ceiling:** comfort auto-slowing in bends only, or should the player keep full control everywhere (no auto
   slowing at all)?
4. **Shared carts:** should friends sit in the same cart, or is it enough that each has their own and they see each
   other?
5. **Cell ID station:** merge it into Light Microscopy, or keep it and add real images?
6. **Lab look:** is a visual-only pass (benches, equipment) acceptable before the logic changes?
7. **Cell type:** stay with the animal cell, or add a plant-cell section later (chloroplast, cell wall, vacuole)?
