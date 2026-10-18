# BSC Island: architecture

## Source of truth
The source of truth is Git; Studio files are build outputs. A build is copied to
`Desktop\KuwaitParkour\KuwaitParkour_vNN.rbxlx`.

- `kuwait-parkour/`: the Rojo project.
  - `src/server`: authoritative game logic.
  - `src/client`: UI and effects.
  - `src/shared`: config and data modules.
  - `src/map/Map.rbxmx`: **generated**, not in Git.
  - `src/world/Island.rbxm`: **generated** from the Roblox Synty packs, not in Git.
- `tools/`: Python generators.
  - `genmap9.py` is the entry point; it imports the world modules (`campus9`, `ku_science*`, `island11`,
    `cartride`, ...).
  - `tools/world/*.luau` are Lune scripts that build the island.
- **Toolchain** (binaries are not in Git):
  - Rojo 7.7.1
  - Lune 0.11.0
  - StyLua 2.5.2
  - selene 0.32.0
  - Python 3.12 with Pillow

## Build
1. `PYTHONIOENCODING=utf-8 python tools/genmap9.py` builds `Map.rbxmx`.
2. `tools/lune/lune.exe run tools/world/island.luau` builds `Island.rbxm`. This needs `tools/packs`.
3. `tools/rojo/rojo.exe build kuwait-parkour/default.project.json -o out.rbxlx`

Before committing, run `stylua src` and `selene src` from `kuwait-parkour/`. The expected result is 0 errors and about
23 known warnings.

## One place, several worlds
**Decision (v37):** keep a single Roblox place for now. The worlds sit far apart in one place:

| World | Offset |
|---|---|
| Campus | 0,0,0 |
| Course | 12000,0,0 |
| Cell | -12000,0,0 |
| Cart | -9000,150,9000 |
| HQ | 0,600,-12000 |
| Island | 0,0,9000 |
| Exam | 6000,300,-6000 |
| Arcade | -6000,300,-6000 |
| Lab | 6000,300,6000 |
| Quiz | 0,300,-6000 |

**Why:**
- One DataStore profile, so there's no cross-place save hand-off.
- No TeleportService hops. Those can't be tested without publishing.
- The client already switches lighting and atmosphere per area (`AreaAtmosphere.client`).

**When to revisit:** when memory per server becomes a problem, measured on a phone. Then the first world to split
off is the Arcade, using TeleportService plus a profile save before the hop.

## Movement and spawn
- **Start point:** `CampusSpawn`, in the south building lobby. It is the only enabled SpawnLocation. `IslandSpawn` is
  now a destination only.
- **Moving characters:** every server move goes through `server/Teleport.luau` (`Teleport.to`) and `TeleportSync.client`.
- **Destination table:** `destinations` in `Main.server.luau`, keyed by the portal kind.
- **Portals:** parts named `Portal|<Kind>` call `onPortal`.
- **World menu:** `WorldMenu.client` fires the `Travel` remote. The server accepts only the keys in its whitelist and
  reuses `onPortal` (2 s cooldown). "Course" continues the parkour from the saved stage.

## Saving and progress
- `Profiles.luau` holds the in-memory state.
- `Main.server` loads and saves via DataStore, with retries. BindToClose waits up to 25 s.
- `Progression.server` and `shared/Progression` handle achievements, titles, shop and collectibles.
- The DataStore is unavailable in an unpublished Studio, so the game stays playable there without saving.

## Arcade
- `server/Arcade.server.luau` runs the round loop. Each game is a module in `server/Minigames/*.luau` with a matching
  `Arena_<id>` in the map.
- Existing games: PetriFloor, ATPRush, EnzymeSweeper.
- **To add a game:** add one module and one arena. Do not change the loop.
