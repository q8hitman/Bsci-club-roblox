-- الإنزيم الدوّار: kill bars sweep around the hub, getting faster; a second bar joins halfway. Jump to survive.
local RunService = game:GetService("RunService")

local M = {
	id = "EnzymeSweeper",
	ar = "🌀 الإنزيم الدوّار",
	hint = "انقز فوق الذراع… وكل شوي يسرع!",
	duration = 60,
	mode = "survive",
}

local LENGTH = 33

local function makeBar(ctx, color, height)
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
		local player = game:GetService("Players"):GetPlayerFromCharacter(hit.Parent)
		if hum and player and ctx.running and ctx.alive[player] then
			hum.Health = 0
		end
	end)
	return { part = bar, height = height }
end

function M.start(ctx)
	local hub = ctx.arena:FindFirstChild("SweepHub")
	if not hub then
		return
	end
	ctx.bars = { makeBar(ctx, Color3.fromRGB(255, 70, 90), 0) }
	local t0 = os.clock()
	local angle, angle2 = 0, math.pi
	ctx.connect(RunService.Heartbeat:Connect(function(dt)
		if not ctx.running then
			return
		end
		local elapsed = os.clock() - t0
		local speed = 1.1 + elapsed * 0.035 -- rad/s, speeds up over the round
		angle += speed * dt
		if elapsed > 25 and #ctx.bars == 1 then
			table.insert(ctx.bars, makeBar(ctx, Color3.fromRGB(255, 170, 40), 0))
		end
		angle2 -= speed * 0.8 * dt
		for i, b in ipairs(ctx.bars) do
			local a = i == 1 and angle or angle2
			b.part.CFrame = CFrame.new(hub.Position + Vector3.new(0, -0.6, 0)) * CFrame.Angles(0, a, 0)
				* CFrame.new(LENGTH / 2, 0, 0)
		end
	end))
end

function M.stop(ctx)
	for _, b in ipairs(ctx.bars or {}) do
		b.part:Destroy()
	end
end

return M
