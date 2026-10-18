-- سباق ATP: "Krebs cycle". Collect ATP orbs; grabbing the next one within 2 s raises your combo (x2, x3).
-- Free radicals (red, moving) steal 2 points and slow you down. In the last 10 s the cell bursts with gold ATP.
local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")

local M = {
	id = "ATPRush",
	ar = "⚡ سباق الـ ATP: دورة كربس",
	hint = "جمّع ATP بسرعة عشان الكومبو ×3… وتجنّب الجذور الحرة الحمرا!",
	duration = 45,
	mode = "score",
}

local MAX_ORBS = 12
local COMBO_WINDOW = 2

function M.start(ctx)
	local tier = ctx.tier or 1
	local t0 = os.clock()
	ctx.spots = {}
	for _, p in ipairs(ctx.arena:GetChildren()) do
		if p.Name == "OrbSpot" then
			table.insert(ctx.spots, p)
		end
	end
	ctx.orbs, ctx.radicals, ctx.combo = {}, {}, {}
	if #ctx.spots == 0 then
		return
	end

	local function collect(player, value)
		local c = ctx.combo[player] or { n = 0, at = 0 }
		local now = os.clock()
		c.n = (now - c.at <= COMBO_WINDOW) and math.min(c.n + 1, 3) or 1
		c.at = now
		ctx.combo[player] = c
		player:SetAttribute("Combo", c.n)
		ctx.addScore(player, value * c.n)
	end

	local function spawnOrb()
		local spot = ctx.spots[math.random(1, #ctx.spots)]
		for _, o in ipairs(ctx.orbs) do
			if o.Parent and (o.Position - spot.Position).Magnitude < 2 then
				return
			end
		end
		local burst = ctx.running and os.clock() - t0 > M.duration - 10
		local gold = math.random() < (burst and 0.45 or 0.15)
		local orb = Instance.new("Part")
		orb.Name = "ATPOrb"
		orb.Shape = Enum.PartType.Ball
		orb.Size = Vector3.new(2.2, 2.2, 2.2)
		orb.Material = Enum.Material.Neon
		orb.Color = gold and Color3.fromRGB(255, 210, 60) or Color3.fromRGB(120, 255, 200)
		orb.Anchored = true
		orb.CanCollide = false
		orb.CFrame = spot.CFrame
		orb.Parent = ctx.arena
		table.insert(ctx.orbs, orb)
		orb.Touched:Connect(function(hit)
			local player = Players:GetPlayerFromCharacter(hit.Parent)
			if player and orb.Parent and ctx.alive[player] and ctx.running then
				orb:Destroy()
				collect(player, gold and 3 or 1)
			end
		end)
	end

	-- free radicals: drift between orb spots; a hit costs 2 points and slows for 1.5 s
	local slowed = {}
	for _ = 1, 1 + tier do
		local r = Instance.new("Part")
		r.Name = "FreeRadical"
		r.Shape = Enum.PartType.Ball
		r.Size = Vector3.new(3, 3, 3)
		r.Material = Enum.Material.Neon
		r.Color = Color3.fromRGB(255, 50, 60)
		r.Anchored = true
		r.CanCollide = false
		r.CFrame = ctx.spots[math.random(1, #ctx.spots)].CFrame + Vector3.new(0, 1, 0)
		r.Parent = ctx.arena
		table.insert(ctx.radicals, r)
		r.Touched:Connect(function(hit)
			local player = Players:GetPlayerFromCharacter(hit.Parent)
			local hum = hit.Parent:FindFirstChildOfClass("Humanoid")
			if not (player and hum and ctx.running and ctx.alive[player]) or slowed[player] then
				return
			end
			slowed[player] = true
			ctx.addScore(player, -math.min(2, ctx.score[player] or 0))
			ctx.combo[player] = nil
			player:SetAttribute("Combo", nil)
			local before = hum.WalkSpeed
			hum.WalkSpeed = 8
			task.delay(1.5, function()
				if hum.Parent then
					hum.WalkSpeed = before
				end
				slowed[player] = nil
			end)
		end)
		task.spawn(function()
			while ctx.running and r.Parent do
				local target = ctx.spots[math.random(1, #ctx.spots)].Position + Vector3.new(0, 1, 0)
				local dist = (target - r.Position).Magnitude
				local tw = TweenService:Create(
					r,
					TweenInfo.new(dist / (9 + tier * 3), Enum.EasingStyle.Linear),
					{ Position = target }
				)
				tw:Play()
				tw.Completed:Wait()
			end
		end)
	end

	task.spawn(function()
		while ctx.running do
			local live = 0
			for _, o in ipairs(ctx.orbs) do
				if o.Parent then
					live += 1
				end
			end
			if live < MAX_ORBS then
				spawnOrb()
			end
			task.wait(os.clock() - t0 > M.duration - 10 and 0.25 or 0.5)
		end
	end)
end

function M.stop(ctx)
	for _, o in ipairs(ctx.orbs or {}) do
		if o.Parent then
			o:Destroy()
		end
	end
	for _, r in ipairs(ctx.radicals or {}) do
		r:Destroy()
	end
	for p in pairs(ctx.combo or {}) do
		if p.Parent then
			p:SetAttribute("Combo", nil)
		end
	end
end

return M
