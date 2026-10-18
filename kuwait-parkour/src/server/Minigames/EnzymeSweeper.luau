-- الإنزيم الدوّار: "competitive inhibition". Kill arms sweep around the hub and speed up. Two inhibitor pads on the
-- floor slow the arms for 3 s when someone steps on one (shared 8 s cooldown) — like an inhibitor taking the enzyme's
-- active site. Substrate coins appear on the floor for points. Higher tiers: arms reverse direction (with a warning
-- flash) and a third arm joins. Last one(s) standing win; points break ties and feed the research reward.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local M = {
	id = "EnzymeSweeper",
	ar = "🌀 الإنزيم الدوّار: التثبيط",
	hint = "انقز فوق الذراع… دوس منصّة المثبّط 🟦 عشان تبطّئ الإنزيم!",
	duration = 60,
	mode = "survive",
}

local LENGTH = 33

local function makeBar(ctx, color)
	local bar = Instance.new("Part")
	bar.Name = "SweepBar"
	bar.Size = Vector3.new(LENGTH, 1.2, 1.2)
	bar.Material = Enum.Material.Neon
	bar.Color = color
	bar.Anchored = true
	bar.CanCollide = false
	bar.Parent = ctx.arena
	bar.Touched:Connect(function(hit)
		local hum = hit.Parent:FindFirstChildOfClass("Humanoid")
		local player = Players:GetPlayerFromCharacter(hit.Parent)
		-- harmless while warming up (the arms start right next to the ring of spawns)
		if hum and player and ctx.running and ctx.alive[player] and os.clock() >= (ctx.armedAt or 0) then
			hum.Health = 0
		end
	end)
	return { part = bar, color = color }
end

local function floorAt(pos, ignore)
	local params = RaycastParams.new()
	params.FilterDescendantsInstances = ignore
	local hit = workspace:Raycast(pos + Vector3.new(0, 8, 0), Vector3.new(0, -30, 0), params)
	return hit and hit.Position
end

function M.start(ctx)
	local hub = ctx.arena:FindFirstChild("SweepHub")
	if not hub then
		return
	end
	local tier = ctx.tier or 1
	ctx.armedAt = os.clock() + 3
	ctx.bars = { makeBar(ctx, Color3.fromRGB(255, 70, 90)) }
	ctx.extras = {}
	local t0 = os.clock()
	-- start between spawns (the 12 spawns sit every 30 degrees from angle 0)
	local angles = { math.rad(15), math.rad(195), math.rad(105) }
	local dirs = { 1, -0.8, 1.2 }
	local slowUntil, padReadyAt = 0, 0

	-- inhibitor pads on opposite sides of the floor
	for _, a in ipairs({ math.pi / 4, math.pi * 5 / 4 }) do
		local spot = hub.Position + Vector3.new(math.cos(a) * 24, 0, math.sin(a) * 24)
		local ground = floorAt(spot, { hub })
		if ground then
			local pad = Instance.new("Part")
			pad.Name = "InhibitorPad"
			pad.Size = Vector3.new(5, 0.4, 5)
			pad.Material = Enum.Material.Neon
			pad.Color = Color3.fromRGB(70, 140, 255)
			pad.Anchored = true
			pad.CanCollide = false
			pad.CFrame = CFrame.new(ground + Vector3.new(0, 0.2, 0))
			pad.Parent = ctx.arena
			table.insert(ctx.extras, pad)
			pad.Touched:Connect(function(hit)
				local player = Players:GetPlayerFromCharacter(hit.Parent)
				if not (player and ctx.running and ctx.alive[player]) or os.clock() < padReadyAt then
					return
				end
				padReadyAt = os.clock() + 8
				slowUntil = os.clock() + 3
				ctx.addScore(player, 2)
				for _, p in ipairs(ctx.extras) do
					if p.Name == "InhibitorPad" then
						p.Color = Color3.fromRGB(60, 60, 70)
					end
				end
				task.delay(8, function()
					for _, p in ipairs(ctx.extras) do
						if p.Name == "InhibitorPad" and p.Parent then
							p.Color = Color3.fromRGB(70, 140, 255)
						end
					end
				end)
			end)
		end
	end

	-- substrate coins
	task.spawn(function()
		while ctx.running do
			local a, r = math.random() * math.pi * 2, math.random(8, 28)
			local ground = floorAt(hub.Position + Vector3.new(math.cos(a) * r, 0, math.sin(a) * r), { hub })
			if ground then
				local coin = Instance.new("Part")
				coin.Name = "Substrate"
				coin.Shape = Enum.PartType.Ball
				coin.Size = Vector3.new(1.6, 1.6, 1.6)
				coin.Material = Enum.Material.Neon
				coin.Color = Color3.fromRGB(255, 220, 90)
				coin.Anchored = true
				coin.CanCollide = false
				coin.CFrame = CFrame.new(ground + Vector3.new(0, 1.2, 0))
				coin.Parent = ctx.arena
				table.insert(ctx.extras, coin)
				coin.Touched:Connect(function(hit)
					local player = Players:GetPlayerFromCharacter(hit.Parent)
					if player and coin.Parent and ctx.running and ctx.alive[player] then
						coin:Destroy()
						ctx.addScore(player, 1)
					end
				end)
			end
			task.wait(2.5)
		end
	end)

	local nextFlip = os.clock() + 12
	ctx.connect(RunService.Heartbeat:Connect(function(dt)
		if not ctx.running then
			return
		end
		local now = os.clock()
		local elapsed = now - t0
		local speed = 1.1 + elapsed * (0.03 + tier * 0.008)
		if now < slowUntil then
			speed *= 0.5
		end
		if elapsed > 25 and #ctx.bars == 1 then
			table.insert(ctx.bars, makeBar(ctx, Color3.fromRGB(255, 170, 40)))
		end
		if tier >= 3 and elapsed > 40 and #ctx.bars == 2 then
			table.insert(ctx.bars, makeBar(ctx, Color3.fromRGB(230, 90, 255)))
		end
		-- tier 2+: the arms reverse direction, flashing white for 1 s first
		local warning = tier >= 2 and nextFlip - now < 1
		if tier >= 2 and now >= nextFlip then
			for i in ipairs(dirs) do
				dirs[i] = -dirs[i]
			end
			nextFlip = now + math.random(9, 14)
		end
		local warming = now < ctx.armedAt
		for i, b in ipairs(ctx.bars) do
			angles[i] += speed * dirs[i] * dt
			b.part.Transparency = warming and 0.7 or 0
			b.part.Color = (now < slowUntil and Color3.fromRGB(70, 140, 255))
				or (warning and Color3.new(1, 1, 1))
				or b.color
			b.part.CFrame = CFrame.new(hub.Position + Vector3.new(0, -0.6, 0))
				* CFrame.Angles(0, angles[i], 0)
				* CFrame.new(LENGTH / 2, 0, 0)
		end
	end))
end

function M.stop(ctx)
	for _, b in ipairs(ctx.bars or {}) do
		b.part:Destroy()
	end
	for _, e in ipairs(ctx.extras or {}) do
		if e.Parent then
			e:Destroy()
		end
	end
end

return M
