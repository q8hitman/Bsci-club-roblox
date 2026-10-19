# Progress log

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

**Not tested:**
- A real phone.
- Portrait orientation.
- Other device sizes (tablet, small Android).
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
