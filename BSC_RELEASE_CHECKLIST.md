# Release checklist (every version)

## Before changing anything
- [ ] Back up to `Desktop\KuwaitParkour\backup_before_vNN_<date>`.
- [ ] Work on a Git branch, not `main`.

## Static checks
- [ ] `stylua src` and `selene src` pass with 0 errors.
- [ ] `tools/lune/lune.exe run tools/validate_questions.luau` passes.
- [ ] `genmap9.py` reports `violations: 0` and `clashes: 0`.

## Studio, solo Play
- [ ] There are 0 errors from our scripts in the Output.
- [ ] Portal and collectible counts match the previous version, unless a change was intended.
- [ ] Walk tests pass on every changed route, in both directions where relevant.
- [ ] No collectible is buried or floating.
- [ ] Closed buildings can't be entered, even by jumping.
- [ ] The world menu can reach every destination.

## Studio, Test tab (manual; the agent tools cannot do these)
- [ ] Device emulator: phone layout.
- [ ] Clients and Servers with 2 players: arcade rounds and the group exam.

## After publishing (owner only)
- [ ] DataStore save and load on a live server.

## Finishing the version
- [ ] Report what was tested and what was not tested.
- [ ] Before/after screenshots.
- [ ] Update `BSC_PROGRESS.md` and `BSC_RESUME.md`.
- [ ] Open a pull request for review. Never merge or publish without the owner.
