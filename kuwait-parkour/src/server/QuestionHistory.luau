-- Shared session exposure history. Prefer the least displayed question, then the least recently displayed.
-- A finite pool cycles after exhaustion; mixed-history groups minimize total repeat burden.
local Players = game:GetService("Players")

local H = {}
local seen = {} -- [Player] = { [question text] = { count, last } }
local sequence = 0

Players.PlayerRemoving:Connect(function(p)
	seen[p] = nil
end)

function H.mark(player, text)
	if player and text then
		seen[player] = seen[player] or {}
		local previous = seen[player][text]
		sequence += 1
		seen[player][text] = { count = previous and previous.count + 1 or 1, last = sequence }
	end
end

function H.markAll(players, text)
	for _, p in ipairs(players) do
		H.mark(p, text)
	end
end

local function exposure(players, text)
	local n, last = 0, 0
	for _, p in ipairs(players) do
		local entry = seen[p] and seen[p][text]
		if entry then
			n += entry.count
			last = math.max(last, entry.last)
		end
	end
	return n, last
end

-- n distinct items from pool, least seen by `players` first, random among equals.
-- textOf(item) gives the question text; filter(item) (optional) limits the pool; rng (optional) is a Random.
function H.pickMany(players, pool, n, textOf, rng, filter)
	local candidates = {}
	local included = {}
	for _, item in ipairs(pool) do
		if not filter or filter(item) then
			local text = textOf(item)
			if text and not included[text] then
				included[text] = true
				local count, last = exposure(players, text)
				table.insert(candidates, { item = item, seen = count, last = last, r = 0 })
			end
		end
	end
	for _, c in ipairs(candidates) do
		c.r = rng and rng:NextNumber() or math.random()
	end
	table.sort(candidates, function(a, b)
		if a.seen ~= b.seen then
			return a.seen < b.seen
		end
		if a.last ~= b.last then
			return a.last < b.last
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
