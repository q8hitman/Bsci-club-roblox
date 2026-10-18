-- سباق ATP: glowing energy orbs keep appearing; grab the most before time runs out. Gold orbs are worth 3.
local M = {
	id = "ATPRush",
	ar = "⚡ سباق الـ ATP",
	hint = "جمّع أكثر طاقة ATP… الذهبية بـ 3 نقاط!",
	duration = 45,
	mode = "score",
}

local MAX_ORBS = 12

function M.start(ctx)
	ctx.spots = {}
	for _, p in ipairs(ctx.arena:GetChildren()) do
		if p.Name == "OrbSpot" then
			table.insert(ctx.spots, p)
		end
	end
	ctx.orbs = {}
	local function spawnOrb()
		if #ctx.spots == 0 then
			return
		end
		local spot = ctx.spots[math.random(1, #ctx.spots)]
		for _, o in ipairs(ctx.orbs) do
			if o.Parent and (o.Position - spot.Position).Magnitude < 2 then
				return
			end
		end
		local gold = math.random() < 0.15
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
		local light = Instance.new("PointLight")
		light.Color = orb.Color
		light.Range = 10
		light.Parent = orb
		table.insert(ctx.orbs, orb)
		orb.Touched:Connect(function(hit)
			local player = game:GetService("Players"):GetPlayerFromCharacter(hit.Parent)
			if player and orb.Parent and ctx.alive[player] then
				orb:Destroy()
				ctx.addScore(player, gold and 3 or 1)
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
			task.wait(0.5)
		end
	end)
end

function M.stop(ctx)
	for _, o in ipairs(ctx.orbs or {}) do
		if o.Parent then
			o:Destroy()
		end
	end
end

return M
