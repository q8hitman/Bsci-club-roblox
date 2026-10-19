-- Physical avatar traversal; clients can request entry/retry/exit only. No progress or reward RPC.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local Run = game:GetService("RunService")
local D = require(RS.Shared.LaserData)
local R = require(RS.Shared.LaserRules)
local Teleport = require(script.Parent.Teleport)
local Passport = require(script.Parent.PassportService)
local Profiles = require(script.Parent.Profiles)
local world = workspace:WaitForChild("Map"):WaitForChild("Laser48")
local request = Instance.new("RemoteFunction")
request.Name = "LaserRequest"
request.Parent = RS
local event = Instance.new("RemoteEvent")
event.Name = "LaserState"
event.Parent = RS
local sessions, progress, rate = {}, {}, {}
local rigs = {}
local door = world.Room_3.SecurityDoor
local doorWindow = world.Room_3.DoorWindow
local doorBase, windowBase = door.CFrame, doorWindow.CFrame
local doorUntil = 0
local bridge = world.Room_4.MovingBridge
local bridgeBase = bridge.CFrame
local function root(p)
	return p.Character and p.Character:FindFirstChild("HumanoidRootPart")
end
local function healthy(p)
	local h = p.Character and p.Character:FindFirstChildOfClass("Humanoid")
	return h and h.Health > 0 and root(p)
end
for i in ipairs(D.Rooms) do
	local x, y, z = D.center(i)
	local list = {}
	for _, name in { "Hazard", "HazardB" } do
		local model = world["Room_" .. i]:FindFirstChild(name)
		if model then
			local parts = {}
			for _, part in model:GetChildren() do
				if part:IsA("BasePart") then
					table.insert(parts, { part = part, offset = CFrame.new(x, y, z):ToObjectSpace(part.CFrame) })
				end
			end
			table.insert(list, parts)
		end
	end
	rigs[i] = list
end
local function state(p, s)
	event:FireClient(p, {
		kind = "state",
		room = s.rules.room,
		zone = s.rules.zone,
		key = s.rules.key,
		failures = s.failures,
		finished = s.finished,
		elapsed = workspace:GetServerTimeNow() - s.started,
		phase = R.phase(workspace:GetServerTimeNow(), D.Rooms[s.rules.room]),
	})
end
local function close(p)
	sessions[p] = nil
	p:SetAttribute("InLaserEscape", nil)
	p:SetAttribute("LaserRoom", nil)
	p:SetAttribute("LaserZone", nil)
	if p.Parent then
		event:FireClient(p, { kind = "close" })
	end
end
local function checkpoint(p, s, now)
	local part = world["Room_" .. s.rules.room].Checkpoint
	Teleport.to(p, part)
	s.character = p.Character
	s.revision = p:GetAttribute("TeleportRevision")
	s.rules = R.start(s.rules.room, now)
	s.last = root(p).Position
	s.lastAt = now
	s.invUntil = now + 0.8
	state(p, s)
end
local function enter(p)
	local r = root(p)
	if
		not healthy(p)
		or p:GetAttribute("InArcadeRound")
		or p:GetAttribute("InMicroRace")
		or (r.Position - world.Entry.LaserEntrance.Position).Magnitude > 20
	then
		return { error = "اقترب من بوابة الليزر بعد إنهاء النشاط الحالي" }
	end
	local room = progress[p] or 1
	local now = workspace:GetServerTimeNow()
	local s = { rules = R.start(room, now), started = now, failures = 0 }
	sessions[p] = s
	p:SetAttribute("InLaserEscape", true)
	checkpoint(p, s, now)
	return { ok = true, room = room }
end
local function fail(p, s, now)
	if now < (s.invUntil or 0) then
		return
	end
	s.failures += 1
	checkpoint(p, s, now)
end
local function prompt(part, name, text, fn)
	local q = Instance.new("ProximityPrompt")
	q.Name = name
	q.ActionText = text
	q.ObjectText = "Laser Escape"
	q.MaxActivationDistance = 12
	q.RequiresLineOfSight = false
	q.Parent = part
	q.Triggered:Connect(fn)
end
prompt(world.Entry.LaserEntrance, "LaserEnter", "ابدأ أو أكمل الهروب", function(p)
	local r = enter(p)
	if r.error then
		event:FireClient(p, { kind = "error", message = r.error })
	end
end)
prompt(world.Room_5.ReturnConsole, "LaserReturn", "العودة للأركيد", function(p)
	if sessions[p] then
		close(p)
		Teleport.to(p, workspace.Map:FindFirstChild("ArcadeSpawn", true))
	end
end)
request.OnServerInvoke = function(p, action)
	if not Profiles.state[p] or type(action) ~= "string" then
		return { error = "طلب غير صالح" }
	end
	local now = workspace:GetServerTimeNow()
	if now - (rate[p] or -10) < 0.25 then
		return { error = "تمهّل قليلًا" }
	end
	rate[p] = now
	if action == "enter" then
		return enter(p)
	end
	local s = sessions[p]
	if not s or not healthy(p) or s.character ~= p.Character or s.revision ~= p:GetAttribute("TeleportRevision") then
		close(p)
		return { error = "افتح بوابة الليزر مجددًا" }
	end
	if action == "leave" then
		close(p)
		Teleport.to(p, workspace.Map:FindFirstChild("ArcadeSpawn", true))
		return { ok = true }
	end
	if action == "retry" and not s.finished then
		if now - (s.retryAt or -10) < 2 then
			return { error = "انتظر ثانيتين قبل الإعادة" }
		end
		s.retryAt = now
		checkpoint(p, s, now)
		return { ok = true }
	end
	if action == "replay" and s.finished then
		progress[p] = 1
		s.rules = R.start(1, now)
		s.finished = false
		s.failures = 0
		s.started = now
		checkpoint(p, s, now)
		return { ok = true }
	end
	return { error = "هذا الطلب غير متاح" }
end
Players.PlayerRemoving:Connect(function(p)
	close(p)
	progress[p] = nil
	rate[p] = nil
end)
local elapsed, broadcast = 0, 0
Run.Heartbeat:Connect(function(dt)
	elapsed += dt
	broadcast += dt
	if elapsed < 0.05 then
		return
	end
	elapsed = 0
	local now = workspace:GetServerTimeNow()
	local oldBridge = bridge.CFrame
	local bridgeX = R.platform(now)
	bridge.CFrame = bridgeBase + CFrame.new(bridgeX, 0, 0).Position
	local delta = bridge.Position - oldBridge.Position
	-- Conveyor-style carry: an anchored part with a velocity moves the humanoids standing on it through the engine,
	-- so riders keep full control. (Moving characters with PivotTo every tick fought client movement and pinned
	-- anyone at the deck edge.) The movement guard below still allows the carried distance.
	bridge.AssemblyLinearVelocity = Vector3.new((R.platform(now + 0.05) - R.platform(now - 0.05)) / 0.1, 0, 0)
	local carried = {}
	for p, s in pairs(sessions) do
		local r = root(p)
		if healthy(p) and s.rules.room == 4 and not s.finished then
			local q = oldBridge:PointToObjectSpace(r.Position)
			if
				math.abs(q.X) < 6
				and math.abs(q.Z) < 15
				and q.Y > 2
				and q.Y < 4.6
				and r.AssemblyLinearVelocity.Y < 3
			then
				carried[p] = delta.Magnitude
			end
		end
	end
	local holding = false
	for _, p in Players:GetPlayers() do
		local r = root(p)
		if
			r
			and math.abs(r.Position.Z - doorBase.Position.Z) < 5
			and math.abs(r.Position.X - doorBase.Position.X) < 28
		then
			holding = true
		end
	end
	-- a character in the doorway only keeps an already-open door open (no crush); it never opens a closed door
	if holding and now < doorUntil then
		doorUntil = math.max(doorUntil, now + 0.5)
	end
	local open = now < doorUntil
	door.CanCollide = not open
	door.CFrame = doorBase + Vector3.new(0, open and 12 or 0, 0)
	doorWindow.CFrame = windowBase + Vector3.new(0, open and 12 or 0, 0)
	for i, d in ipairs(D.Rooms) do
		local x, y, z = D.center(i)
		local gx, gz = 0, 0
		if i == 2 then
			gx, gz = R.grid(now)
		end
		local phase = R.phase(now, d)
		local color = phase == "danger" and Color3.fromRGB(242, 103, 121)
			or phase == "warning" and Color3.fromRGB(247, 192, 91)
			or Color3.fromRGB(83, 196, 214)
		for _, parts in rigs[i] do
			for _, record in parts do
				local part = record.part
				if i == 2 then
					part.CFrame = CFrame.new(x + gx, y, z + gz) * record.offset
				end
				if part.Name == "Beam" then
					part.Color = color
					part.Transparency = phase == "safe" and 0.86 or 0.1
				end
			end
		end
	end
	for p, s in pairs(sessions) do
		local r = root(p)
		if
			not p.Parent
			or not healthy(p)
			or s.character ~= p.Character
			or s.revision ~= p:GetAttribute("TeleportRevision")
		then
			close(p)
			continue
		end
		if s.finished then
			if broadcast >= 0.2 then
				state(p, s)
			end
			continue
		end
		local i = s.rules.room
		local x, y, z = D.center(i)
		local pos = r.Position
		local localX, localZ = pos.X - x, pos.Z - z
		local tickDt = now - s.lastAt
		local h = p.Character:FindFirstChildOfClass("Humanoid")
		if
			now >= (s.invUntil or 0)
			and (
				not R.motion(pos.X - s.last.X, pos.Z - s.last.Z, tickDt, h.WalkSpeed, carried[p])
				or math.abs(localX) > 30
				or localZ > 80
				or localZ < -40
				or pos.Y < y - 6
				or pos.Y > y + 20
			)
		then
			fail(p, s, now)
			continue
		end
		s.last = pos
		s.lastAt = now
		local room = D.Rooms[i]
		if
			R.phase(now, room) == "danger"
			and now % room.cycle >= room.safe + room.warning + 0.2
			and R.contact(i, localX, pos.Y - y, localZ, now)
		then
			fail(p, s, now)
			continue
		end
		local plate = world["Room_" .. i]:FindFirstChild("PressurePlate")
		if
			plate
			and (Vector2.new(pos.X, pos.Z) - Vector2.new(plate.Position.X, plate.Position.Z)).Magnitude < 5
			and math.abs(pos.Y - y) < 6
		then
			s.rules.key = true
			if i == 3 then
				doorUntil = now + 5
			end
		end
		if R.visit(s.rules, localZ, now, s.rules.key) then
			if i == 5 then
				s.finished = true
				progress[p] = nil
				Passport.record(p, "escape", "laser48")
				state(p, s)
			else
				progress[p] = i + 1
				s.rules = R.start(i + 1, now)
				s.invUntil = now + 0.15
				state(p, s)
			end
		end
		p:SetAttribute("LaserRoom", s.rules.room)
		p:SetAttribute("LaserZone", s.rules.zone)
		if broadcast >= 0.2 then
			state(p, s)
		end
	end
	if broadcast >= 0.2 then
		broadcast = 0
	end
end)
