-- Optional cohort labels, selected in the lab or profile. No free-text entry.
-- Keep existing string IDs stable for saved profiles.
local batches = {
	{
		id = "2026",
		ar = "دفعة 2026",
		color = { 46, 140, 90 },
		achievements = {},
	},
	{
		id = "2025",
		ar = "دفعة 2025",
		color = { 70, 110, 200 },
		achievements = {},
	},
	{
		id = "2024",
		ar = "دفعة 2024",
		color = { 180, 90, 160 },
		achievements = {},
	},
	{
		id = "alumni",
		ar = "الخريجين 🎓",
		color = { 200, 160, 60 },
		achievements = {},
	},
}
-- Optional year labels, not claims about club membership or achievements.
-- Existing string IDs and colours remain compatible with saved profiles.
for year = 2023, 1980, -1 do
	table.insert(batches, #batches, {
		id = tostring(year),
		ar = "دفعة " .. year,
		color = { 46, 110, 100 },
		achievements = {},
	})
end
table.insert(batches, #batches, {
	id = "before1980",
	ar = "قبل 1980",
	color = { 70, 120, 130 },
	achievements = {},
})
return batches
