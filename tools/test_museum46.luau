local R = require("../kuwait-parkour/src/shared/MuseumRules")
local D = require("../kuwait-parkour/src/shared/MuseumData")
local P = require("../kuwait-parkour/src/server/PassportState")
local count = 0
for _, def in ipairs(D.Exhibits) do
	local s = R.start(def.id)
	assert(s and s.step == 1)
	local ok = R.act(s, "__forged__")
	assert(not ok and s.step == 1, "unknown action must preserve state")
	for _, step in ipairs(def.steps) do
		local before = s.step
		local wrong = step.options[1].id
		if wrong == step.correct then
			wrong = step.options[2].id
		end
		local correct = R.act(s, wrong)
		assert(not correct and s.step == before, "wrong action retry")
		assert(R.act(s, step.correct), "correct action advances")
	end
	assert(s.done and not R.act(s, def.steps[1].correct), "completed session cannot replay")
	count += 1
end
assert(count == 8 and not R.start("unknown"))
assert(not R.act(R.start("micro"), {}))
local a = { passport = {}, stage = 0, found = {} }
for _, d in ipairs(D.Exhibits) do
	P.record(a, "museum", d.id, 1792368000)
end
assert(P.summary(a, 1792368000).xp == 80, "eight balanced exhibit stamps")
P.record(a, "museum", "micro", 1792368000)
P.record(a, "museum", "forged", 1792368000)
assert(P.summary(a, 1792368000).xp == 80, "duplicates and forged exhibit denied")
local b = { passport = P.merge({}, a.passport, 1792368000) }
assert(P.summary(b, 1792368000).museum == 8 and P.summary(b, 1792368000).xp == 80, "save merge preserves evidence")
assert(P.summary({ passport = { stamps = { ["museum:forged"] = true } } }, 1792368000).xp == 0)
print("PASS museum46: eight interactive sequences, wrong/retry, invalid input, completion, XP idempotency and merge")
