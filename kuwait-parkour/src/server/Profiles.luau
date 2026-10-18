-- Server-only shared player state. Main.server owns loading/saving; other server scripts read and
-- change it through this module and listen to events via hooks:
--   Profiles.on("stage", fn(player, stage))      after a stage is applied
--   Profiles.on("practice", fn(player, total))   after a correct quiz-corner answer
--   Profiles.on("loaded", fn(player))            after the profile is loaded (or defaulted)
local Profiles = {
	state = {}, -- [Player] = { stage, respawn, coins, redeemed, loaded, found, owned, equip, best, ach, stats }
	hooks = {},
}

function Profiles.on(event, fn)
	Profiles.hooks[event] = Profiles.hooks[event] or {}
	table.insert(Profiles.hooks[event], fn)
end

function Profiles.fire(event, ...)
	for _, fn in ipairs(Profiles.hooks[event] or {}) do
		task.spawn(fn, ...)
	end
end

function Profiles.blank()
	return {
		stage = 0,
		respawn = 0,
		coins = 0,
		redeemed = {},
		loaded = false,
		found = {}, -- collectible id -> true
		owned = {}, -- trail id -> true
		equip = {}, -- { trail = id?, title = achievementId? }
		best = {}, -- zone index (string) -> best seconds
		ach = {}, -- achievement id -> true
		stats = { practice = 0 },
		daily = 0, -- last day number the daily challenge was completed
		research = 0, -- research points (spendable on lab projects)
		upgrades = {}, -- lab project id -> true
		batch = nil, -- chosen club batch id (Shared/Batches)
		quiz = {}, -- challenge center: "spec:level" -> best correct answers in one session (0..5)
	}
end

return Profiles
