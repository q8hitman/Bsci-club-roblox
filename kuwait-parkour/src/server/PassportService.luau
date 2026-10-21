-- Server-only bridge from verified gameplay to the cosmetic evidence ledger. No grant-XP remote exists.
local Profiles = require(script.Parent.Profiles)
local State = require(script.Parent.PassportState)
local Analytics = require(script.Parent.Analytics)
local Service = {}
function Service.refresh(player)
	local s = Profiles.state[player]
	if not s then
		return nil
	end
	local data = State.summary(s, os.time())
	player:SetAttribute("PassportXP", data.xp)
	player:SetAttribute("PassportLevel", data.level)
	if Profiles.award then
		for _, pair in ipairs({
			{ "activity:arcade", "arcade_play" },
			{ "activity:lab", "lab_first" },
			{ "activity:show", "show_first" },
		}) do
			if s.passport.stamps[pair[1]] then
				Profiles.award(player, pair[2])
			end
		end
		if data.visits >= 5 then
			Profiles.award(player, "explorer5")
		end
		if data.level >= 5 then
			Profiles.award(player, "passport5")
		end
		if data.museum == 8 then
			Profiles.award(player, "museum8")
		end
		if s.passport.stamps["escape:laser48"] then
			Profiles.award(player, "laser48")
		end
		if data.races == 2 then
			Profiles.award(player, "racer2")
		end
		if s.passport.stamps["puzzle:CellControl"] then
			Profiles.award(player, "puzzle_master")
		end
	end
	-- v53 "First Day at the College": four short optional steps, read from the stamps the game already verifies.
	-- FirstDay = "1010"-style string for FirstDay.client (HQ visit, arcade round, lab experiment, a train ride).
	local st = s.passport.stamps
	local steps = { -- booleans: a nil would end ipairs early
		(s.passport.visits or {}).HQ ~= nil,
		st["activity:arcade"] ~= nil,
		st["activity:lab"] ~= nil,
		st["train:cart"] ~= nil or st["train:cell"] ~= nil,
	}
	local flags, done = "", 0
	for _, ok in ipairs(steps) do
		flags ..= ok and "1" or "0"
		done += ok and 1 or 0
	end
	player:SetAttribute("FirstDay", flags)
	Analytics.onboarding(player, 1, "Joined")
	for i = 1, done do
		Analytics.onboarding(player, i + 1, ("FirstDay %d/4"):format(i))
	end
	if done == #steps and Profiles.award then
		Profiles.award(player, "firstday")
	end
	return data
end
function Service.record(player, kind, id)
	local s = Profiles.state[player]
	if not s then
		return
	end
	State.record(s, kind, id, os.time())
	Service.refresh(player)
end
function Service.claim(player, id)
	local s = Profiles.state[player]
	if not s or type(id) ~= "string" then
		return false
	end
	local granted = State.claim(s, id, os.time())
	Service.refresh(player)
	return granted
end
function Service.complete(player, kind, proof)
	if State.completionAllowed(kind, proof) then
		Service.record(player, "activity", kind)
	end
end
Profiles.on("loaded", Service.refresh)
Profiles.on("stage", function(player)
	Service.refresh(player)
end)
return Service
