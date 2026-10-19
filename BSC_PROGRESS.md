# Progress log

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
