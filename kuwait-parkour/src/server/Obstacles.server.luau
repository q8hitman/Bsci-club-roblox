-- One script drives every obstacle in the map. Behaviour is encoded in part names:
--   Move|dx,dy,dz|period|phase      KillMove|dx,dy,dz|period|phase
--   Kill    Bounce|vy    Crumble|delay|respawn    Conv|vx,vy,vz
--   Blink|on|off|phase              KillBlink|on|off|phase
--   Spin|speed            (kill bar turning around world Y)
--   Roto|speed|group      (rideable platforms turning around world Y, grouped)
--   Wheel|speed|group     (kill blades turning around world Z, grouped)
--   Log|speed             (cylinder rolling around its own length)
--   Tilt                  (free seesaw plank)
--   Ghost|id   Button|id|seconds   SeqKey|id|LETTERS   SeqBtn|id|LETTER
--   Gate|id               (solid wall that opens with its Button / solved puzzle)
--   SimonLamp|id|LETTER   (lamps that keep flashing the SeqKey pattern of their puzzle)
--   Swing|dx,dy,dz|deg|period|phase[|safe]   (pendulum around the path axis, pivot = position + d)
--   Orbit|dx,dy,dz|speed  (kill ball circling the point position + d)
local TweenService = game:GetService("TweenService")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local CollectionService = game:GetService("CollectionService")
local mapFolder = workspace:WaitForChild("Map")

-- tiny sound cues for puzzle feedback (played by Feedback.client)
local sfx = Instance.new("RemoteEvent")
sfx.Name = "Sfx"
sfx.Parent = ReplicatedStorage

local function humanoidFrom(hit)
	local model = hit:FindFirstAncestorOfClass("Model")
	local hum = model and model:FindFirstChildOfClass("Humanoid")
	return hum, model
end

local function nums(s)
	local t = {}
	for n in string.gmatch(s or "", "[%d%.%-]+") do
		t[#t + 1] = tonumber(n)
	end
	return t
end

local function makeKill(part)
	part.Touched:Connect(function(hit)
		local hum = humanoidFrom(hit)
		if hum and hum.Health > 0 then
			hum.Health = 0
		end
	end)
end

local function makeMove(part, args)
	local o = nums(args[2])
	local period = tonumber(args[3]) or 4
	local phase = tonumber(args[4]) or 0
	local goal = part.CFrame + Vector3.new(o[1] or 0, o[2] or 0, o[3] or 0)
	task.delay(phase, function()
		TweenService:Create(
			part,
			TweenInfo.new(period / 2, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, true),
			{ CFrame = goal }
		):Play()
	end)
end

-- Hinge helper: anchors an invisible axle at `pivot` and spins/frees `part` around `axis`
-- (axis is expressed as a CFrame rotation that maps the attachment X axis onto the wanted axis).
local function hinge(part, pivot, axis, speed, limits)
	local axle = Instance.new("Part")
	axle.Name = "Axle"
	axle.Anchored = true
	axle.CanCollide = false
	axle.CanQuery = false
	axle.CanTouch = false
	axle.Transparency = 1
	axle.Size = Vector3.new(0.4, 0.4, 0.4)
	axle.CFrame = CFrame.new(pivot)
	axle.Parent = part.Parent

	local a0 = Instance.new("Attachment")
	a0.CFrame = axis
	a0.Parent = axle
	local a1 = Instance.new("Attachment")
	a1.Parent = part -- parent first: WorldCFrame is only meaningful once attached to the part
	a1.WorldCFrame = axle.CFrame * axis

	local h = Instance.new("HingeConstraint")
	h.Attachment0 = a0
	h.Attachment1 = a1
	if speed then
		h.ActuatorType = Enum.ActuatorType.Motor
		h.MotorMaxTorque = 1e10
		h.MotorMaxAcceleration = 1e5
		h.AngularVelocity = speed
	end
	if limits then
		h.LimitsEnabled = true
		h.LowerAngle = -limits
		h.UpperAngle = limits
		h.Restitution = 0
	end
	h.Parent = part
	part.Anchored = false
	part:SetNetworkOwner(nil)
	return h
end

local AXIS_Y = CFrame.Angles(0, 0, math.rad(90)) -- attachment X -> world Y
local AXIS_Z = CFrame.Angles(0, math.rad(-90), 0) -- attachment X -> world Z

local function weldGroup(parts)
	local first = parts[1]
	for i = 2, #parts do
		local w = Instance.new("WeldConstraint")
		w.Part0 = first
		w.Part1 = parts[i]
		w.Parent = first
		parts[i].Anchored = false
	end
	return first
end

local function makeBounce(part, args)
	local vy = tonumber(args[2]) or 80
	local last = {}
	part.Touched:Connect(function(hit)
		local hum, model = humanoidFrom(hit)
		local root = model and model:FindFirstChild("HumanoidRootPart")
		if not (hum and root) then
			return
		end
		local now = os.clock()
		if last[model] and now - last[model] < 0.5 then
			return
		end
		last[model] = now
		local v = root.AssemblyLinearVelocity
		root.AssemblyLinearVelocity = Vector3.new(v.X, vy, v.Z)
	end)
end

local function makeCrumble(part, args)
	local delay = tonumber(args[2]) or 0.5
	local respawn = tonumber(args[3]) or 4
	local original = part.Transparency
	local busy = false
	part.Touched:Connect(function(hit)
		if busy or not humanoidFrom(hit) then
			return
		end
		busy = true
		task.delay(delay, function()
			part.Transparency = 1
			part.CanCollide = false
			task.delay(respawn, function()
				part.Transparency = original
				part.CanCollide = true
				busy = false
			end)
		end)
	end)
end

local function makeBlink(part, args, deadly)
	local on = tonumber(args[2]) or 2.5
	local off = tonumber(args[3]) or 1.5
	local phase = tonumber(args[4]) or 0
	local solid = part.Transparency
	task.spawn(function()
		task.wait(phase % (on + off))
		while part.Parent do
			part.Transparency = solid
			part.CanCollide = not deadly
			part.CanTouch = true
			task.wait(math.max(on - 0.48, 0.1))
			for _ = 1, 3 do -- warning flicker before it vanishes
				part.Transparency = 0.6
				task.wait(0.08)
				part.Transparency = solid
				task.wait(0.08)
			end
			part.Transparency = deadly and 1 or 0.85
			part.CanCollide = false
			part.CanTouch = false
			task.wait(off)
		end
	end)
end

-- ghost bridges (opened by a Button or a solved sequence)
local GHOST_CLOSED = 0.9
local ghosts = {}
local gates = {}
local open = {}

local function openGhosts(id, seconds)
	if open[id] then
		return
	end
	open[id] = true
	for _, g in ipairs(ghosts[id] or {}) do
		g.CanCollide = true
		g.Transparency = 0
	end
	for _, g in ipairs(gates[id] or {}) do
		g.CanCollide = false
		g.Transparency = 0.85
	end
	seconds = seconds or 14
	-- the last 3 seconds the bridge flickers so nobody is surprised when it closes under them
	task.delay(math.max(seconds - 3, 0), function()
		for _ = 1, 12 do
			if not open[id] then
				break
			end
			for _, g in ipairs(ghosts[id] or {}) do
				g.Transparency = g.Transparency == 0 and 0.55 or 0
			end
			task.wait(0.25)
		end
	end)
	task.delay(seconds, function()
		for _, g in ipairs(ghosts[id] or {}) do
			g.CanCollide = false
			g.Transparency = GHOST_CLOSED
		end
		for _, g in ipairs(gates[id] or {}) do
			g.CanCollide = true
			g.Transparency = 0.2
		end
		open[id] = nil
	end)
end

local function makeButton(part, args)
	part.Touched:Connect(function(hit)
		local _, model = humanoidFrom(hit)
		if model then
			local plr = not open[args[2]] and Players:GetPlayerFromCharacter(model)
			if plr then
				sfx:FireClient(plr, "sting")
			end
			openGhosts(args[2], tonumber(args[3]) or 14)
		end
	end)
end

-- sequence puzzle: press SeqBtn letters in the order stored on the hidden SeqKey part
local seqKeys = {}
local seqProgress = {} -- [id][player] = index reached

-- v31: the button colours are drawn per player (SeqButtons.client). The server used to recolour the shared parts, so
-- one player's correct presses turned the buttons green for everyone and anyone's wrong press wiped everyone's lights.
-- Progress was always per player; now the feedback is too. Opening the bridge stays shared (it helps, never hurts).
local seqEvent = Instance.new("RemoteEvent")
seqEvent.Name = "SeqState"
seqEvent.Parent = ReplicatedStorage

-- A press counts when a player steps ONTO a button (standing still on it never re-triggers),
-- so we poll which button each player stands on instead of trusting repeated Touched events.
local seqButtons = {} -- { part, id, letter }
local litFor = {} -- [player][id] = { parts lit for that player }
local solvedUntil = {} -- [player][id] = os.clock() + 20

local function pressSeq(btn, player)
	local id, letter, part = btn.id, btn.letter, btn.part
	local key = seqKeys[id]
	if not key then
		return
	end
	solvedUntil[player] = solvedUntil[player] or {}
	if solvedUntil[player][id] and os.clock() < solvedUntil[player][id] then
		return
	end
	seqProgress[id] = seqProgress[id] or {}
	litFor[player] = litFor[player] or {}
	local idx = (seqProgress[id][player] or 0) + 1
	if key:sub(idx, idx) == letter then
		local lit = litFor[player][id] or {}
		if not table.find(lit, part) then
			table.insert(lit, part)
		end
		litFor[player][id] = lit
		if idx == #key then
			seqProgress[id][player] = 0
			litFor[player][id] = nil
			solvedUntil[player][id] = os.clock() + 20
			-- v31: the bridge opens for the solver only (their client makes the ghost tiles solid for their own
			-- character, whose physics it owns), so nobody crosses a puzzle they did not solve
			sfx:FireClient(player, "sting")
			seqEvent:FireClient(player, "done", id, lit)
			seqEvent:FireClient(player, "open", id, { 20 })
		else
			sfx:FireClient(player, "click")
			seqProgress[id][player] = idx
			seqEvent:FireClient(player, "lit", id, lit)
		end
	else
		local existing = litFor[player][id]
		if existing and table.find(existing, part) then
			return
		end
		seqProgress[id][player] = 0
		litFor[player][id] = nil
		sfx:FireClient(player, "wrong")
		seqEvent:FireClient(player, "wrong", id, { part })
	end
end

local function resetPlayerSeq(player)
	for id in pairs(litFor[player] or {}) do
		seqEvent:FireClient(player, "wrong", id, {})
	end
	litFor[player] = nil
	solvedUntil[player] = nil
	for _, prog in pairs(seqProgress) do
		prog[player] = nil
	end
end
Players.PlayerAdded:Connect(function(player)
	player.CharacterAdded:Connect(function()
		resetPlayerSeq(player)
	end)
end)
for _, player in ipairs(Players:GetPlayers()) do
	player.CharacterAdded:Connect(function()
		resetPlayerSeq(player)
	end)
end

local function makeSeqBtn(part, args)
	table.insert(seqButtons, { part = part, id = args[2], letter = args[3] })
end

local standingOn = {} -- [Player] = button entry

task.spawn(function()
	while true do
		task.wait(0.1)
		for _, player in ipairs(Players:GetPlayers()) do
			local char = player.Character
			local root = char and char:FindFirstChild("HumanoidRootPart")
			local found = nil
			if root then
				local pos = root.Position
				for _, btn in ipairs(seqButtons) do
					local p = btn.part
					local d = pos - p.Position
					local h = p.Size / 2
					if math.abs(d.X) <= h.X + 0.6 and math.abs(d.Z) <= h.Z + 0.6 and d.Y > 0 and d.Y < 6 then
						found = btn
						break
					end
				end
			end
			if found ~= standingOn[player] then
				standingOn[player] = found
				if found then
					pressSeq(found, player)
				end
			end
		end
	end
end)

-- memory puzzle: the lamps replay the stored pattern forever
local simonLamps = {} -- [id][LETTER] = part

local function runSimon(id)
	local lamps = simonLamps[id]
	local key = seqKeys[id]
	if not (lamps and key) then
		return
	end
	local dim = {}
	for letter, lamp in pairs(lamps) do
		dim[letter] = lamp.Color
	end
	task.spawn(function()
		while true do
			for i = 1, #key do
				local letter = key:sub(i, i)
				local lamp = lamps[letter]
				if lamp then
					local c = dim[letter]
					lamp.Color = Color3.new(math.min(c.R * 4, 1), math.min(c.G * 4, 1), math.min(c.B * 4, 1))
					task.wait(0.55)
					lamp.Color = c
					task.wait(0.25)
				end
			end
			task.wait(2.2)
		end
	end)
end

-- anchored parts animated every frame (pendulums, orbiting electrons)
local animated = {}

local function addAnimated(part, args, kind)
	local d = nums(args[2])
	local pivot = CFrame.new(part.Position + Vector3.new(d[1] or 0, d[2] or 0, d[3] or 0))
	local a = { part = part, pivot = pivot, rel = pivot:Inverse() * part.CFrame, kind = kind }
	if kind == "swing" then
		a.amp = math.rad(tonumber(args[3]) or 50)
		a.period = tonumber(args[4]) or 2.5
		a.phase = tonumber(args[5]) or 0
	else
		a.speed = tonumber(args[3]) or 2
	end
	table.insert(animated, a)
	if args[6] ~= "safe" then
		makeKill(part)
	end
end

RunService.Heartbeat:Connect(function()
	local now = workspace:GetServerTimeNow()
	for _, a in ipairs(animated) do
		if a.kind == "swing" then
			local angle = a.amp * math.sin((now + a.phase) * 2 * math.pi / a.period)
			a.part.CFrame = a.pivot * CFrame.Angles(0, 0, angle) * a.rel
		else
			a.part.CFrame = a.pivot * CFrame.Angles(0, now * a.speed, 0) * a.rel
		end
	end
end)

local rotoGroups, wheelGroups = {}, {}

local function addGroup(groups, args, part)
	local id = args[3] or "_"
	groups[id] = groups[id] or { speed = tonumber(args[2]) or 0.5, parts = {} }
	table.insert(groups[id].parts, part)
end

for _, inst in ipairs(mapFolder:GetDescendants()) do
	if inst:IsA("BasePart") and string.find(inst.Name, "|", 1, true) then
		local args = string.split(inst.Name, "|")
		local kind = args[1]
		if kind == "Move" then
			-- v59: a server tween never carried the player standing on it. MovingPlatforms.client moves the platform
			-- from the shared server clock and carries the local character; the server copy stays still.
			local o = nums(args[2])
			inst:SetAttribute("MoveOffset", Vector3.new(o[1] or 0, o[2] or 0, o[3] or 0))
			inst:SetAttribute("MovePeriod", tonumber(args[3]) or 4)
			inst:SetAttribute("MovePhase", tonumber(args[4]) or 0)
			CollectionService:AddTag(inst, "BSCMover")
		elseif kind == "KillMove" then
			makeMove(inst, args)
			makeKill(inst)
		elseif kind == "Kill" then
			makeKill(inst)
		elseif kind == "KillBlink" then
			makeKill(inst)
			makeBlink(inst, args, true)
		elseif kind == "Blink" then
			makeBlink(inst, args, false)
		elseif kind == "Spin" then
			hinge(inst, inst.Position, AXIS_Y, tonumber(args[2]) or 2)
			makeKill(inst)
		elseif kind == "Roto" then
			addGroup(rotoGroups, args, inst)
		elseif kind == "Wheel" then
			addGroup(wheelGroups, args, inst)
			makeKill(inst)
		elseif kind == "Log" then
			-- the log's own X axis is its length; spin around it
			hinge(inst, inst.Position, inst.CFrame.Rotation, tonumber(args[2]) or 1)
		elseif kind == "Tilt" then
			inst.CustomPhysicalProperties = PhysicalProperties.new(0.05, 0.8, 0)
			hinge(inst, inst.Position, inst.CFrame.Rotation, nil, 22)
		elseif kind == "Bounce" then
			makeBounce(inst, args)
		elseif kind == "Crumble" then
			makeCrumble(inst, args)
		elseif kind == "Conv" then
			local v = nums(args[2])
			inst.AssemblyLinearVelocity = Vector3.new(v[1] or 0, v[2] or 0, v[3] or 0)
		elseif kind == "Ghost" then
			ghosts[args[2]] = ghosts[args[2]] or {}
			table.insert(ghosts[args[2]], inst)
			inst.Transparency = GHOST_CLOSED -- closed bridges must not look like platforms
		elseif kind == "Gate" then
			gates[args[2]] = gates[args[2]] or {}
			table.insert(gates[args[2]], inst)
		elseif kind == "SimonLamp" then
			simonLamps[args[2]] = simonLamps[args[2]] or {}
			simonLamps[args[2]][args[3]] = inst
		elseif kind == "Swing" then
			addAnimated(inst, args, "swing")
		elseif kind == "Orbit" then
			addAnimated(inst, args, "orbit")
		elseif kind == "Button" then
			makeButton(inst, args)
		elseif kind == "SeqKey" then
			seqKeys[args[2]] = args[3]
		elseif kind == "SeqBtn" then
			makeSeqBtn(inst, args)
		end
	end
end

for id in pairs(simonLamps) do
	runSimon(id)
end

for _, g in pairs(rotoGroups) do
	local first = weldGroup(g.parts)
	hinge(first, first.Position, AXIS_Y, g.speed)
end
for _, g in pairs(wheelGroups) do
	local first = weldGroup(g.parts)
	hinge(first, first.Position, AXIS_Z, g.speed)
end

Players.PlayerRemoving:Connect(function(player)
	standingOn[player] = nil
	litFor[player] = nil
	for _, t in pairs(seqProgress) do
		t[player] = nil
	end
end)
