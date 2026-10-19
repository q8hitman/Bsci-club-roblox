-- غرفة التحكم بالخلية: the first puzzle room (idea: the ChatGPT supervisor, 2026-10-19). Two puzzles each reveal a
-- symbol; the core needs both symbols. Steps are solved in any order by anyone in the room.
return {
	id = "CellControl",
	symbolSlots = 2,
	steps = {
		{ type = "Circuit", rows = 3, cols = 4, symbolSlot = 1 },
		{ type = "Specimens", count = 4, symbolSlot = 2 },
		{ type = "Core", needs = { 1, 2 }, slots = { 1, 2 } },
	},
}
