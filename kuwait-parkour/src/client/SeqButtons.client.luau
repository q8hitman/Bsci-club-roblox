-- Per-player colours for the sequence puzzles (SeqBtn parts). Obstacles.server sends this player's own state only:
--   "lit"  (id, parts)  correct presses so far -> green
--   "done" (id, parts)  solved -> stay green 1.2 s, then back to normal
--   "wrong"(id, parts)  wrong press -> the pressed button flashes red, every light of that puzzle goes out
-- The colour is changed locally, so other players never see someone else's progress or mistakes.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local seqEvent = ReplicatedStorage:WaitForChild("SeqState", 60)
if not seqEvent then
	return
end

local GREEN = Color3.fromRGB(90, 255, 140)
local RED = Color3.fromRGB(255, 70, 70)
local original = {} -- [part] = colour from the map
local litById = {} -- [id] = { parts lit right now }

local function base(part)
	original[part] = original[part] or part.Color
	return original[part]
end

local function clear(id)
	for _, part in ipairs(litById[id] or {}) do
		if part.Parent then
			part.Color = base(part)
		end
	end
	litById[id] = nil
end

-- per-player bridges: Ghost|id tiles become solid (and Gate|id walls open) for this player only
local ghosts, gates = {}, {}
for _, inst in ipairs(workspace:WaitForChild("Map"):GetDescendants()) do
	if inst:IsA("BasePart") then
		local kind, id = inst.Name:match("^(%a+)|([^|]+)$")
		if kind == "Ghost" then
			ghosts[id] = ghosts[id] or {}
			table.insert(ghosts[id], inst)
		elseif kind == "Gate" then
			gates[id] = gates[id] or {}
			table.insert(gates[id], inst)
		end
	end
end
local openUntil = {} -- [id] = os.clock() when it closes again
local function setBridge(id, isOpen)
	for _, g in ipairs(ghosts[id] or {}) do
		g.CanCollide = isOpen
		g.Transparency = isOpen and 0 or 0.9
	end
	for _, g in ipairs(gates[id] or {}) do
		g.CanCollide = not isOpen
		g.Transparency = isOpen and 0.85 or 0.2
	end
end
local function openBridge(id, seconds)
	local closeAt = os.clock() + seconds
	openUntil[id] = closeAt
	setBridge(id, true)
	-- the last 3 seconds the tiles flicker so the player knows it is closing
	task.delay(math.max(seconds - 3, 0), function()
		for _ = 1, 12 do
			if openUntil[id] ~= closeAt then
				return
			end
			for _, g in ipairs(ghosts[id] or {}) do
				g.Transparency = g.Transparency == 0 and 0.55 or 0
			end
			task.wait(0.25)
		end
		if openUntil[id] == closeAt then
			openUntil[id] = nil
			setBridge(id, false)
		end
	end)
end

seqEvent.OnClientEvent:Connect(function(kind, id, parts)
	if typeof(id) ~= "string" or typeof(parts) ~= "table" then
		return
	end
	if kind == "open" then
		openBridge(id, tonumber(parts[1]) or 20)
		return
	end
	if kind == "lit" or kind == "done" then
		clear(id)
		for _, part in ipairs(parts) do
			if typeof(part) == "Instance" and part:IsA("BasePart") then
				base(part)
				part.Color = GREEN
			end
		end
		litById[id] = parts
		if kind == "done" then
			task.delay(1.2, function()
				if litById[id] == parts then
					clear(id)
				end
			end)
		end
	elseif kind == "wrong" then
		clear(id)
		for _, part in ipairs(parts) do
			if typeof(part) == "Instance" and part:IsA("BasePart") then
				local c = base(part)
				part.Color = RED
				task.delay(0.35, function()
					if part.Parent then
						part.Color = c
					end
				end)
			end
		end
	end
end)
