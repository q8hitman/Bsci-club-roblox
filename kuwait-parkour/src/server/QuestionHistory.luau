-- v61 (owner: "questions repeat across modes"): one memory per player of the question texts they were shown this
-- session, shared by every mode (HQ quiz stations, Exam Hall, Science Challenge Center, Game Show). Pickers prefer
-- the questions the fewest present players have seen; a pool only repeats once everyone has seen all of it.
local Players = game:GetService("Players")

local H = {}
local seen = {} -- [Player] = { [question text] = true }

Players.PlayerRemoving:Connect(function(p)
	seen[p] = nil
end)

function H.mark(player, text)
	if player and text then
		seen[player] = seen[player] or {}
		seen[player][text] = true
	end
end

function H.markAll(players, text)
	for _, p in ipairs(players) do
		H.mark(p, text)
	end
end

local function timesSeen(players, text)
	local n = 0
	for _, p in ipairs(players) do
		if seen[p] and seen[p][text] then
			n += 1
		end
	end
	return n
end

-- n distinct items from pool, least seen by `players` first, random among equals.
-- textOf(item) gives the question text; filter(item) (optional) limits the pool; rng (optional) is a Random.
function H.pickMany(players, pool, n, textOf, rng, filter)
	local candidates = {}
	for _, item in ipairs(pool) do
		if not filter or filter(item) then
			table.insert(candidates, { item = item, seen = timesSeen(players, textOf(item)), r = 0 })
		end
	end
	for _, c in ipairs(candidates) do
		c.r = rng and rng:NextNumber() or math.random()
	end
	table.sort(candidates, function(a, b)
		if a.seen ~= b.seen then
			return a.seen < b.seen
		end
		return a.r < b.r
	end)
	local out = {}
	for i = 1, math.min(n, #candidates) do
		out[i] = candidates[i].item
	end
	return out
end

function H.pick(players, pool, textOf, rng, filter)
	return H.pickMany(players, pool, 1, textOf, rng, filter)[1]
end

return H
