#!/usr/bin/env bash
# Type-check the game with luau-lsp (official release 1.70.1 in tools/luau-lsp, git-ignored like rojo/lune).
# Setup once: download luau-lsp-win64.zip from github.com/JohnnyMorganz/luau-lsp/releases/tag/1.70.1 into tools/luau-lsp/
# and scripts/globalTypes.None.d.luau from the same tag next to it.
# Known false positives (fields added at runtime, not bugs): Profiles.award, Arcade ctx.teamDone, PetriFloor tile fields,
# Teleport BasePart casts, CartScenery tonumber(), Lab/Labs54 "over"/"under", Racers PlayerModule, PassportState Lune path.
set -u
cd "$(dirname "$0")/../kuwait-parkour"
../tools/rojo/rojo.exe sourcemap default.project.json -o sourcemap.json
../tools/luau-lsp/luau-lsp.exe analyze --platform roblox --sourcemap sourcemap.json \
	--defs @roblox=../tools/luau-lsp/globalTypes.None.d.luau src
