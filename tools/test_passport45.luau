local S = require("../kuwait-parkour/src/server/PassportState")
local monday = 1792368000 -- 2026-10-19 00:00 UTC
assert(not S.completionAllowed("arcade", { departed = true, active = false, present = false }), "abandoned arcade denied")
assert(not S.completionAllowed("show", { answered = true, present = false }), "abandoned show denied")
assert(S.completionAllowed("arcade", { active = true }), "active finisher accepted")
assert(S.completionAllowed("arcade", { present = true }), "eliminated spectator in lobby accepted")
assert(S.completionAllowed("show", { answered = true, present = true }), "show finisher accepted")
local function equal(a, b, why)
	assert(a == b, (why or "mismatch") .. ": " .. tostring(a) .. " ~= " .. tostring(b))
end
local old = { stage = 3, found = { c1 = true, s1 = true }, coins = 97, research = 8, ach = { first = true } }
S.sync(old, monday)
equal(S.summary(old, monday).xp, 80, "old progress migrates")
S.sync(old, monday)
equal(S.summary(old, monday).xp, 80, "migration idempotent")
equal(old.coins, 97, "coins preserved")
equal(old.research, 8, "research preserved")
local a, b = {}, {}
S.record(a, "activity", "lab", monday)
S.record(a, "activity", "lab", monday)
equal(S.summary(a, monday).xp, 40, "first lab XP once")
S.record(a, "activity", "forged", monday)
equal(S.summary(a, monday).xp, 40, "unknown activity denied")
equal(S.claim(a, "activities", monday), false, "premature weekly denied")
S.record(a, "activity", "show", monday)
equal(S.claim(a, "activities", monday), true, "earned weekly claim")
equal(S.claim(a, "activities", monday), false, "weekly double claim denied")
equal(S.summary(a, monday).xp, 155, "XP sums finite evidence")
for i = 1, 4 do S.record(a, "visit", "HQ", monday) end
equal(S.summary(a, monday).weekly[1].progress, 1, "duplicate visits don't count")
for _, id in ipairs({ "Campus", "Lab", "Course", "Arcade" }) do S.record(a, "visit", id, monday) end
equal(S.claim(a, "explore", monday), true, "five worlds")
for _, n in ipairs({ 1, 1, 2, 3 }) do S.record(a, "checkpoint", n, monday) end
equal(S.claim(a, "parkour", monday), true, "three distinct checkpoints")
local xp = S.summary(a, monday).xp
equal(S.summary(a, monday+604799).weekly[1].claimed, true, "last second same week")
equal(S.summary(a, monday+604800).weekly[1].progress, 0, "Monday reset")
equal(S.claim(a, "explore", monday+604800), false, "old proof cannot claim new week")
equal(S.summary(a, monday+604800).xp, xp, "reset preserves earned XP")
S.record(b, "activity", "arcade", monday+604800)
local merged = S.merge(a.passport, b.passport, monday+604800)
local loaded = { passport = merged }
equal(S.summary(loaded, monday+604800).xp, xp+40, "merge unions evidence")
equal(S.summary(loaded, monday+604800).weekly[3].progress, 1, "newest week kept")
local mergedAgain = { passport = S.merge(merged, a.passport, monday+604800) }
equal(S.summary(mergedAgain, monday+604800).xp, xp+40, "stale save cannot duplicate or lose XP")
equal(S.summary(b, monday+604800).xp, 40, "player profiles isolated")
local corrupt = { passport = { stamps = { ["activity:hack"] = true }, weekly = "bad", visits = "bad" } }
equal(S.summary(corrupt, monday).xp, 0, "invalid evidence ignored")
print("PASS Passport: migration, idempotency, UTC rollover, claims, persistence merge and isolation")
