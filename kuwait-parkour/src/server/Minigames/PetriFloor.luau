-- أرضية بتري: "contamination". Tiles drop a moment after someone steps on them, contamination waves turn tile
-- clusters yellow and drop them (faster each tier), and antibiotic pads regrow the dropped tiles around them.
-- Last one(s) standing win; antibiotics also give points (tie-break + research reward via Arcade).
local Players = game:GetService("Players")

local M = {
	id = "PetriFloor",
	ar = "🧫 أرضية بتري: التلوث",
	hint = "البلاط يطيح بعد ما تدوس… والتلوث الأصفر ينتشر! المضاد الحيوي 💊 يرجّع البلاط",
	duration = 75,
	mode = "survive",
}

local WARN = Color3.fromRGB(255, 220, 60)
local HIT = Color3.fromRGB(255, 90, 90)
local PILL = Color3.fromRGB(80, 230, 255)

function M.start(ctx)
	local tier = ctx.tier or 1
	local dropDelay = ({ 0.45, 0.38, 0.32 })[tier] or 0.32
	local waveEvery = ({ 7, 5.5, 4.2 })[tier] or 4.2
	ctx.tiles = {}
	local function drop(t)
		if t.down then
			return
		end
		t.down = true
		t.part.Transparency = 1
		t.part.CanCollide = false
	end
	local function restore(t)
		t.down = false
		t.busy = false
		t.pill = false
		t.part.Transparency = 0
		t.part.CanCollide = true
		t.part.Color = t.color
	end
	for _, tile in ipairs(ctx.arena:GetChildren()) do
		if tile.Name == "FallTile" then
			local t = { part = tile, color = tile.Color }
			table.insert(ctx.tiles, t)
			ctx.connect(tile.Touched:Connect(function(hit)
				if not ctx.running or t.down or t.busy then
					return
				end
				local player = Players:GetPlayerFromCharacter(hit.Parent)
				if not player then
					return
				end
				if t.pill then
					-- antibiotic: regrow every dropped tile within 14 studs, the pad is used up
					t.pill = false
					t.part.Color = t.color
					for _, o in ipairs(ctx.tiles) do
						if o.down and (o.part.Position - tile.Position).Magnitude < 14 then
							restore(o)
						end
					end
					if ctx.alive[player] then
						ctx.addScore(player, 1)
					end
					return
				end
				t.busy = true
				tile.Color = HIT
				task.delay(dropDelay, function()
					if ctx.running then -- never drop a tile after the round has reset the floor
						drop(t)
					end
				end)
			end))
		end
	end
	-- contamination waves + antibiotic pads
	task.spawn(function()
		task.wait(4)
		while ctx.running do
			local standing = {}
			for _, t in ipairs(ctx.tiles) do
				if not t.down and not t.busy then
					table.insert(standing, t)
				end
			end
			if #standing > 0 then
				local seed = standing[math.random(1, #standing)]
				local cluster = {}
				for _, t in ipairs(standing) do
					if (t.part.Position - seed.part.Position).Magnitude < 7 + tier * 2 then
						t.busy = true
						t.part.Color = WARN
						table.insert(cluster, t)
					end
				end
				task.delay(1.2, function()
					for _, t in ipairs(cluster) do
						if ctx.running then
							drop(t)
						end
					end
				end)
				-- one fresh antibiotic pad on a healthy tile
				local candidates = {}
				for _, t in ipairs(standing) do
					if not t.busy and not t.pill then
						table.insert(candidates, t)
					end
				end
				if #candidates > 0 and math.random() < 0.7 then
					local p = candidates[math.random(1, #candidates)]
					p.pill = true
					p.part.Color = PILL
				end
			end
			task.wait(waveEvery)
		end
	end)
end

function M.stop(ctx)
	for _, t in ipairs(ctx.tiles or {}) do
		t.part.Transparency = 0
		t.part.CanCollide = true
		t.part.Color = t.color
	end
end

return M
