-- أرضية بتري: hex tiles drop a moment after someone steps on them. Two layers. Last one standing wins.
local M = {
	id = "PetriFloor",
	ar = "🧫 أرضية بتري",
	hint = "البلاط يطيح بعد ما تدوس عليه… لا توقف بمكانك!",
	duration = 75,
	mode = "survive",
}

local DROP_DELAY = 0.45

function M.start(ctx)
	ctx.tiles = {}
	for _, tile in ipairs(ctx.arena:GetChildren()) do
		if tile.Name == "FallTile" then
			table.insert(ctx.tiles, { part = tile, color = tile.Color })
			local busy = false
			ctx.connect(tile.Touched:Connect(function(hit)
				if busy or not ctx.running or not hit.Parent:FindFirstChildOfClass("Humanoid") then
					return
				end
				busy = true
				tile.Color = Color3.fromRGB(255, 90, 90)
				task.delay(DROP_DELAY, function()
					tile.Transparency = 1
					tile.CanCollide = false
				end)
			end))
		end
	end
end

function M.stop(ctx)
	for _, t in ipairs(ctx.tiles or {}) do
		t.part.Transparency = 0
		t.part.CanCollide = true
		t.part.Color = t.color
	end
end

return M
