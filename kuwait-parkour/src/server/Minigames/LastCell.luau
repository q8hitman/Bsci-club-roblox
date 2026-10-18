-- آخر خلية صامدة (Last Cell Standing): survival on a round "cell" whose membrane rings drop from the outside in.
-- Hazards are telegraphed, never instant: spore bursts (red warning circle, then a push), cilia waves (a bar that
-- sweeps across; jump it or get pushed) and lysosome bubbles (touch = a 5 s shield against pushes, +1 point).
-- Falling off is handled by Arcade.server (KillFloor|LastCell). Last survivors win; points break ties.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

-- the client applies pushes to its own character (it owns its physics); see ArcadeFX.client
local knock = ReplicatedStorage:FindFirstChild("ArcadeKnock")
if not knock then
	knock = Instance.new("RemoteEvent")
	knock.Name = "ArcadeKnock"
	knock.Parent = ReplicatedStorage
end

local M = {
	id = "LastCell",
	ar = "🦠 آخر خلية صامدة",
	hint = "الغشاء يطيح من برّا لجوّا! انتبه للدواير الحمرا وموجة الأهداب ⬆️ والفقاعة البنفسجية 🛡 تحميك",
	duration = 90,
	mode = "survive",
}

local WARN = Color3.fromRGB(255, 220, 60)
local SPORE = Color3.fromRGB(255, 70, 70)
local SHIELD = Color3.fromRGB(190, 110, 255)

local function rootOf(player)
	local char = player.Character
	return char and char:FindFirstChild("HumanoidRootPart")
end

local function shielded(player)
	return (player:GetAttribute("ShieldUntil") or 0) > os.clock()
end

local function push(ctx, player, vel)
	if ctx.alive[player] and not shielded(player) then
		knock:FireClient(player, vel)
	end
end

function M.start(ctx)
	local tier = ctx.tier or 1
	local arena = ctx.arena
	local nucleus = arena:FindFirstChild("Nucleus")
	local center = nucleus.Position -- generated with the arena (tools/chaos_gen.py last_cell)
	local floorY = center.Y + 1
	ctx.rings = {}
	ctx.hazards = {}
	for _, p in ipairs(arena:GetChildren()) do
		local k = tonumber(p.Name:match("^MembraneSeg|(%d)$"))
		if k then
			ctx.rings[k] = ctx.rings[k] or {}
			table.insert(ctx.rings[k], { part = p, color = p.Color })
		end
	end
	local outer = #ctx.rings
	local radius = { 14, 22, 30, 38 }
	local standingRadius = radius[outer] or 38

	local function hazard(props)
		local p = Instance.new("Part")
		p.Anchored = true
		p.CanCollide = false
		p.CanQuery = false
		p.CastShadow = false
		for k, v in pairs(props) do
			p[k] = v
		end
		p.Parent = arena
		table.insert(ctx.hazards, p)
		return p
	end

	-- 1) the membrane drops ring by ring (warning flash first); timings shrink with the tier
	local scale = ({ 1, 0.85, 0.72 })[tier] or 0.72
	local schedule = { 22 * scale, 44 * scale, 66 * scale } -- ring 4, 3, 2 (ring 1 + nucleus stay)
	task.spawn(function()
		local t0 = os.clock()
		for i, at in ipairs(schedule) do
			local k = outer - i + 1
			if k < 2 then
				break
			end
			while ctx.running and os.clock() - t0 < at - 3 do
				task.wait(0.2)
			end
			if not ctx.running then
				return
			end
			for blink = 1, 6 do
				for _, s in ipairs(ctx.rings[k]) do
					s.part.Color = blink % 2 == 1 and WARN or s.color
				end
				task.wait(0.5)
			end
			if not ctx.running then
				return
			end
			for _, s in ipairs(ctx.rings[k]) do
				s.part.Transparency = 1
				s.part.CanCollide = false
			end
			standingRadius = radius[k - 1] or 14
		end
	end)

	-- 2) hazards
	local every = ({ 4.5, 3.6, 2.8 })[tier] or 2.8
	local function randomPoint(maxR)
		local a = math.random() * 2 * math.pi
		local r = math.sqrt(math.random()) * maxR
		return center + Vector3.new(math.cos(a) * r, 1, math.sin(a) * r)
	end

	local function spore()
		local pos = randomPoint(standingRadius - 3)
		local warn = hazard({
			Name = "SporeWarn",
			Shape = Enum.PartType.Cylinder,
			Size = Vector3.new(0.2, 14, 14),
			CFrame = CFrame.new(pos.X, floorY + 0.12, pos.Z) * CFrame.Angles(0, 0, math.rad(90)),
			Color = SPORE,
			Material = Enum.Material.Neon,
			Transparency = 0.45,
		})
		task.wait(1.6)
		if not ctx.running then
			return
		end
		warn.Transparency = 0.1
		for p in pairs(ctx.alive) do
			local root = rootOf(p)
			if root then
				local d = Vector3.new(root.Position.X - pos.X, 0, root.Position.Z - pos.Z)
				if d.Magnitude < 7.5 then
					local dir = d.Magnitude > 0.1 and d.Unit or Vector3.new(1, 0, 0)
					push(ctx, p, dir * 70 + Vector3.new(0, 42, 0))
				end
			end
		end
		task.wait(0.3)
		warn:Destroy()
	end

	local function ciliaWave()
		local a = math.random() * 2 * math.pi
		local dir = Vector3.new(math.cos(a), 0, math.sin(a))
		local side = Vector3.new(-dir.Z, 0, dir.X)
		local startPos = center - dir * (standingRadius + 4) + Vector3.new(0, 1.2, 0)
		local endPos = center + dir * (standingRadius + 4) + Vector3.new(0, 1.2, 0)
		local look = CFrame.lookAt(Vector3.zero, side)
		local bar = hazard({
			Name = "CiliaWave",
			Size = Vector3.new(1.2, 2.2, standingRadius * 2 + 8),
			CFrame = CFrame.new(startPos) * look.Rotation,
			Color = Color3.fromRGB(120, 255, 200),
			Material = Enum.Material.Neon,
			Transparency = 0.15,
		})
		local travel = 3.2
		TweenService
			:Create(
				bar,
				TweenInfo.new(travel, Enum.EasingStyle.Linear),
				{ CFrame = CFrame.new(endPos) * look.Rotation }
			)
			:Play()
		local hitAlready = {}
		local t0 = os.clock()
		while ctx.running and os.clock() - t0 < travel do
			for p in pairs(ctx.alive) do
				local root = rootOf(p)
				if root and not hitAlready[p] then
					local rel = root.Position - bar.Position
					local along = rel:Dot(dir)
					-- a jump clears it: only feet below the bar top count
					if math.abs(along) < 1.6 and root.Position.Y - 3 < bar.Position.Y + 1.1 then
						hitAlready[p] = true
						push(ctx, p, dir * 62 + Vector3.new(0, 26, 0))
					end
				end
			end
			task.wait(0.05)
		end
		bar:Destroy()
	end

	local function bubble()
		local pos = randomPoint(standingRadius - 4)
		local b = hazard({
			Name = "LysosomeBubble",
			Shape = Enum.PartType.Ball,
			Size = Vector3.new(3.2, 3.2, 3.2),
			CFrame = CFrame.new(pos.X, floorY + 2.2, pos.Z),
			Color = SHIELD,
			Material = Enum.Material.Neon,
			Transparency = 0.25,
		})
		b.CanTouch = true
		local taken = false
		ctx.connect(b.Touched:Connect(function(hit)
			local p = Players:GetPlayerFromCharacter(hit.Parent)
			if taken or not p or not ctx.alive[p] then
				return
			end
			taken = true
			p:SetAttribute("ShieldUntil", os.clock() + 5)
			local hl = Instance.new("Highlight")
			hl.Name = "LysosomeShield"
			hl.FillColor = SHIELD
			hl.FillTransparency = 0.6
			hl.OutlineColor = Color3.new(1, 1, 1)
			hl.Parent = p.Character
			task.delay(5, function()
				hl:Destroy()
			end)
			ctx.addScore(p, 1)
			b:Destroy()
		end))
		task.delay(9, function()
			if b.Parent then
				b:Destroy()
			end
		end)
	end

	task.spawn(function()
		task.wait(3)
		local n = 0
		while ctx.running do
			n += 1
			local r = math.random()
			if n % 3 == 0 then
				task.spawn(bubble)
			end
			if r < 0.55 then
				task.spawn(spore)
				if tier >= 2 and math.random() < 0.4 then
					task.spawn(spore)
				end
			else
				task.spawn(ciliaWave)
			end
			task.wait(every)
		end
	end)

	-- survival points: everyone still standing gets +1 every 10 s (tie-break)
	task.spawn(function()
		while ctx.running do
			task.wait(10)
			for p in pairs(ctx.alive) do
				if ctx.running then
					ctx.addScore(p, 1)
				end
			end
		end
	end)
end

function M.stop(ctx)
	for _, ring in pairs(ctx.rings or {}) do
		for _, s in ipairs(ring) do
			s.part.Transparency = 0
			s.part.CanCollide = true
			s.part.Color = s.color
		end
	end
	for _, h in ipairs(ctx.hazards or {}) do
		if h.Parent then
			h:Destroy()
		end
	end
	for _, p in ipairs(Players:GetPlayers()) do
		p:SetAttribute("ShieldUntil", nil)
		local hl = p.Character and p.Character:FindFirstChild("LysosomeShield")
		if hl then
			hl:Destroy()
		end
	end
end

return M
