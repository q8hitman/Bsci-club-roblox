-- Pure evidence/merge rules; no Instances, remotes, clocks, or datastore calls in this module.
local D = if script
	then require(game:GetService("ReplicatedStorage").Shared.PassportDefs)
	else require("../shared/PassportDefs")
local S = {}
function S.completionAllowed(kind, proof)
	if proof.departed then
		return false
	end
	if kind == "arcade" then
		return proof.active == true or proof.present == true or proof.returning == true
	end
	if kind == "show" then
		return proof.answered == true and proof.present == true
	end
	return false
end
local WEEK = 604800
local function tab(t)
	return if type(t) == "table" then t else {}
end
local function int(n, lo, hi)
	return type(n) == "number" and n == n and n >= lo and n <= hi and n % 1 == 0
end
function S.week(now)
	return math.floor((now + 259200) / WEEK) -- Monday 00:00 UTC, independent of client timezone
end
local function collectible(id)
	if type(id) ~= "string" then
		return false
	end
	local c, n = id:match("^([cs])(%d+)$")
	return id == "g1" or (c ~= nil and int(tonumber(n), 1, if c == "c" then 12 else 8))
end
local function weight(key)
	if type(key) ~= "string" or #key > 80 then
		return nil
	end
	local n = key:match("^stage:(%d+)$")
	if n and int(tonumber(n), 1, 100) then
		return D.StageXP
	end
	local id = key:match("^collect:(.+)$")
	local exhibit = key:match("^museum:(.+)$")
	local race = key:match("^race:(.+)$")
	if race and D.Races[race] then
		return D.RaceXP
	end
	if exhibit and D.Museum[exhibit] then
		return D.MuseumXP
	end
	if id and collectible(id) then
		return D.CollectXP
	end
	id = key:match("^activity:(.+)$")
	if id and D.Activities[id] then
		return D.ActivityXP
	end
	local week, challenge = key:match("^weekly:(%d+):(%a+)$")
	if week and int(tonumber(week), 0, 1000000) then
		for _, def in ipairs(D.Weekly) do
			if def.id == challenge then
				return def.xp
			end
		end
	end
	return nil
end
local function validSet(input, valid)
	local result = {}
	for key, value in pairs(tab(input)) do
		if value == true and valid(key) then
			result[key] = true
		end
	end
	return result
end
local function normalized(raw, now)
	raw = tab(raw)
	local w = tab(raw.weekly)
	if w.week ~= S.week(now) then
		w = {}
	end
	return {
		version = 1,
		stamps = validSet(raw.stamps, function(k)
			return weight(k) ~= nil
		end),
		visits = validSet(raw.visits, function(k)
			return D.Worlds[k] == true
		end),
		weekly = {
			week = S.week(now),
			visits = validSet(w.visits, function(k)
				return D.Worlds[k] == true
			end),
			stages = validSet(w.stages, function(k)
				return type(k) == "string" and int(tonumber(k), 0, 100)
			end),
			activities = validSet(w.activities, function(k)
				return D.Activities[k] == true
			end),
		},
	}
end
function S.sync(s, now)
	s.passport = normalized(s.passport, now)
	local p = s.passport
	local stage = if type(s.stage) == "number" and s.stage == s.stage
		then math.clamp(math.floor(s.stage), 0, 100)
		else 0
	for n = 1, stage do
		p.stamps["stage:" .. n] = true
	end
	for id, found in pairs(tab(s.found)) do
		if found == true and collectible(id) then
			p.stamps["collect:" .. id] = true
		end
	end
	return p
end
function S.record(s, kind, id, now)
	local p = S.sync(s, now)
	if kind == "visit" and type(id) == "string" and D.Worlds[id] then
		p.visits[id], p.weekly.visits[id] = true, true
	elseif kind == "activity" and type(id) == "string" and D.Activities[id] then
		p.stamps["activity:" .. id], p.weekly.activities[id] = true, true
	elseif kind == "checkpoint" and int(id, 0, 100) then
		p.weekly.stages[tostring(id)] = true
	elseif kind == "museum" and type(id) == "string" and D.Museum[id] then
		p.stamps["museum:" .. id] = true
	elseif kind == "race" and type(id) == "string" and D.Races[id] then
		p.stamps["race:" .. id] = true
	end
end
local function count(t)
	local n = 0
	for _ in pairs(t) do
		n += 1
	end
	return n
end
function S.claim(s, id, now)
	local p = S.sync(s, now)
	for _, def in ipairs(D.Weekly) do
		local key = "weekly:" .. p.weekly.week .. ":" .. def.id
		if id == def.id and not p.stamps[key] and count(p.weekly[def.field]) >= def.goal then
			p.stamps[key] = true
			return true
		end
	end
	return false
end
function S.summary(s, now)
	local p = S.sync(s, now)
	local xp = 0
	local museum = 0
	local races = 0
	for key in pairs(p.stamps) do
		xp += weight(key) or 0
		if key:match("^museum:") then
			museum += 1
		end
		if key:match("^race:") then
			races += 1
		end
	end
	local challenges = {}
	for _, def in ipairs(D.Weekly) do
		table.insert(challenges, {
			id = def.id,
			ar = def.ar,
			desc = def.desc,
			goal = def.goal,
			xp = def.xp,
			progress = math.min(def.goal, count(p.weekly[def.field])),
			claimed = p.stamps["weekly:" .. p.weekly.week .. ":" .. def.id] == true,
		})
	end
	return {
		xp = xp,
		museum = museum,
		races = races,
		level = 1 + math.floor(xp / D.LevelXP),
		progress = xp % D.LevelXP,
		nextXP = D.LevelXP,
		visits = count(p.visits),
		weekly = challenges,
		week = p.weekly.week,
		resetAt = (p.weekly.week + 1) * WEEK - 259200,
	}
end
function S.merge(old, current, now)
	local a, b = normalized(old, now), normalized(current, now)
	for key in pairs(b.stamps) do
		a.stamps[key] = true
	end
	for key in pairs(b.visits) do
		a.visits[key] = true
	end
	for _, field in ipairs({ "visits", "stages", "activities" }) do
		for key in pairs(b.weekly[field]) do
			a.weekly[field][key] = true
		end
	end
	return a
end
return S
