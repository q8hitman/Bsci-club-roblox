local fs = require("@lune/fs")
local luau = require("@lune/luau")
local batches = luau.load(fs.readFile("kuwait-parkour/src/shared/Batches.luau"))()
local ids = {}
for _, batch in ipairs(batches) do
	assert(not ids[batch.id], "duplicate cohort id")
	ids[batch.id] = batch
	assert(#batch.achievements == 0, "unverified achievement in cohort data")
end
for year = 1980, 2026 do
	assert(ids[tostring(year)], "missing year " .. year)
end
assert(ids.alumni and ids.before1980)
assert(#batches == 49)
assert(ids["2026"].color[1] == 46 and ids["2025"].color[1] == 70 and ids["2024"].color[1] == 180)
print("PASS: 47 years, earlier/alumni choices, stable legacy IDs/colours, no invented achievements")
