-- Execute the real module with only Roblox's PlayerRemoving event substituted.
local fs = require("@lune/fs")
local luau = require("@lune/luau")
local source = fs.readFile("kuwait-parkour/src/server/QuestionHistory.luau")
local removed
local H = luau.load(source, { environment = {
	game = { GetService = function(_, name)
		assert(name == "Players")
		return { PlayerRemoving = { Connect = function(_, callback) removed = callback end } }
	end },
}, injectGlobals = true })()
local failures = 0
local function test(name, fn)
	local ok, err = pcall(fn)
	print((ok and "PASS " or "FAIL ") .. name .. (ok and "" or (": " .. tostring(err))))
	if not ok then failures += 1 end
end
local function textOf(q) return q end
local function firstBias()
	local i = 0
	return { NextNumber = function() i += 1 return i / 100 end }
end

test("exhausted bank continues balancing actual exposures", function()
	local p = {}
	H.mark(p, "A") H.mark(p, "B") H.mark(p, "C")
	H.mark(p, "A") H.mark(p, "A")
	assert(H.pick({p}, {"A", "B", "C"}, textOf, firstBias()) ~= "A", "overexposed question repeated")
end)
test("duplicate question text is drawn once", function()
	local out = H.pickMany({{}}, {"same", "same", "other"}, 5, textOf, firstBias())
	assert(#out == 2, "duplicate rows leaked into one session")
end)
test("cycle boundary avoids immediate repetition", function()
	local p = {}
	H.mark(p, "older") H.mark(p, "latest")
	assert(H.pick({p}, {"latest", "older"}, textOf, firstBias()) == "older", "last question immediately repeated")
end)
test("many complete cycles stay unique within each cycle", function()
	local p = {}
	for _ = 1, 5 do
		local cycle = {}
		for _ = 1, 4 do
			local q = H.pick({p}, {"A", "B", "C", "D"}, textOf, firstBias())
			assert(not cycle[q], "repeated before bank exhausted")
			cycle[q] = true H.mark(p, q)
		end
	end
end)
test("filter empty singleton and player removal", function()
	local p = {}
	H.mark(p, "A")
	assert(H.pick({p}, {}, textOf) == nil)
	assert(H.pick({p}, {"A", "B"}, textOf, firstBias(), function(q) return q == "B" end) == "B")
	assert(H.pick({p}, {"A"}, textOf) == "A")
	removed(p)
	assert(H.pick({p}, {"A", "B"}, textOf, firstBias()) == "A", "departing player history leaked")
end)
test("mixed histories prefer unseen questions for the group", function()
	local p, q = {}, {}
	H.mark(p, "A") H.mark(q, "B")
	assert(H.pick({p,q}, {"A", "B", "C"}, textOf, firstBias()) == "C")
end)
assert(failures == 0, tostring(failures) .. " question-history regression(s)")
