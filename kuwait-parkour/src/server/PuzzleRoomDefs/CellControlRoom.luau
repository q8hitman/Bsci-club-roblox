-- أنقذ الخلية (Restart the Cell), map folder PuzzleRoom_CellControl. Power the nucleus (circuit) and identify the
-- cells under the microscope (specimens); each reveals two bases of a DNA strand, and the nucleus opens with the
-- complementary strand (A-T, G-C). Steps are solved in any order by anyone in the room.
return {
	id = "CellControl",
	symbolSlots = 2,
	objective = "🎯 شغّلوا نواة الخلية: ⚡ وصّلوا الطاقة، 🔬 تعرّفوا على الخلايا، 🧬 ادخلوا شيفرة DNA",
	steps = {
		{ type = "Circuit", rows = 4, cols = 5, symbolSlot = 1 },
		{ type = "Specimens", count = 4, symbolSlot = 2 },
		{ type = "Core", needs = { 1, 2 }, slots = { 1, 2 } },
	},
}
