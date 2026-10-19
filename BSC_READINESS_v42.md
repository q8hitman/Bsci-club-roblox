# Release readiness: v42 (2026-10-19)

**Owner's decision needed.** Nothing has been published or merged.

## Build
| Item | Value |
|---|---|
| File | `Desktop\KuwaitParkour\KuwaitParkour_v42.rbxlx` |
| Backup | `Desktop\KuwaitParkour\backup_v42_20261019` |
| Branch | `dev/v42` on github.com/q8hitman/Bsci-club-roblox |
| Stack | v37 → v38 → v39 → v40 → v41 → v42 |
| Live game | The v20+NPC update. Private: PlaceId 97395090487008 |

## Verdict
- **Ready for the owner's private test: YES.**
  - Open the v42 file in Studio and play solo or with the Test tab.
  - Or publish it to the existing **private** place, but only after the owner approves.
- **Ready to publish publicly: NO.** These items block it:
  1. **DataStore saving has never been tested on a live server.** It cannot be tested without publishing.
     - The first private publish must check: join, earn coins, leave, rejoin, and confirm the coins are still there.
  2. **No real phone test yet.** Only the Studio Device Simulator (iPhone XR, iPad 10th Generation) was used.
  3. **Performance on weak phones is unknown.**
     - The game has about 25.4k parts and 80k instances, and `StreamingEnabled` is off.
     - The PC holds 60 fps everywhere.
     - Consider turning streaming on in a separate, tested step. Some client scripts look up far-away map parts, so
       they would need checking first.
  4. **Remaining multiplayer gaps** are listed under "Not tested" below.

## Tested (all in Studio)
- **Static checks:** selene 0 errors; question bank validator OK. The map was not regenerated in v42.
- **All 37 portals:** each one, stood on in Play, moves the player to the right world.
  - Zone portals 2–8 refuse with the "locked until stage N" message, as designed.
- **World menu:** all 12 destinations. Tested in v37–v40, and v42 changed no destinations.
- **Phone layout (iPhone XR, landscape):**
  - The world menu fits.
  - Puzzle hints were unreadable; fixed.
  - The Game Show main screen was unreadable; a HUD was added.
  - Microscope controls were too small; enlarged, with drag-to-pan added.
- **Tablet layout (iPad):** the microscope and the Game Show HUD are good.
- **Portrait:** does not apply; the game is LandscapeSensor.
- **Microscope:**
  - Gemini's science review was applied.
  - The oil dead-end at 100× was fixed (100× now turns straight to 4×).
  - The full procedure was clicked through: 4×, 10×, 40×, 100× with oil, back to 4×, clean.
- **Multiplayer (1 server + 2 clients):**
  - Game Show teams, scores, rewards and cooldown work. A player leaving mid-show was tested.
  - Fixed: a player who left before answering got the +3 reward.
  - Last Cell elimination and win.
  - The Lab Rush goal scales to 7 with two players.
  - Puzzle hints and tile state are shared between players.
- **Frame rate:** 60 fps on the PC in the campus, island, arcade, lab, show and train.

## Not tested
- A real phone or a weak device.
- DataStore on a live server.
- A full co-op Lab Rush finish with 2 real players. The 2.5 s reactor window was verified with 2 clients; scripted
  prompt presses stop reaching the server after a few presses in multi-client mode, which is a harness limit.
- A full two-player puzzle-room solve with the reward for both.
- Real disconnects. Leaving was simulated by travelling away.
- 3 or more players.
- The new-player experience with a real first-time player.

## Known issues (not blockers)
- Fixed after the first version of this report:
  - the Game Show host covering the screen;
  - the stage counter showing in every world;
  - the screen turning cyan when arriving at the Game Show.
- Duplicate portals (5 HQ, 8 Island) are still there, waiting for the owner's decision (backlog #5).
- Asset `rbxassetid://203785492` logs "Asset type does not match" in Studio. It is not one of our scripts' errors.

## Still missing from the BSC Island vision (backlog)
- Biology Discovery Museum.
- BSC Passport: XP, titles, badges, weekly.
- Game Show sound and memory modes.
- More arcade games: Micro Racers, Laser Escape, Tower Defense, Rhythm, Bosses.
- More labs.
- Photo mode.
- Optional Discord roles.
- Fewer duplicate portals.
- A slightly higher gym roof.
- **Deferred by the owner:** the horror world.
