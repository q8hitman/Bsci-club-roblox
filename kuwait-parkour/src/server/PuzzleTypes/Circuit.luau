-- Energy Circuit (v61: ATP from the mitochondrion = CircuitSource): a rows x cols grid of floor tiles
-- (CircuitTile|r|c), each a straight or corner pipe. Tap a tile to
-- turn it 90°. Energy enters row "entry" from the west (CircuitSource) and must leave row "exit" to the east
-- (CircuitSink). The powered part of the chain lights up as you go, so progress is always visible.
-- Every reset builds a new random solvable layout and scrambles it.
local Circuit = {}
Circuit.__index = Circuit

local DIRS = { Vector3.new(0, 0, -1), Vector3.new(1, 0, 0), Vector3.new(0, 0, 1), Vector3.new(-1, 0, 0) } -- N E S W
local DR = { -1, 0, 1, 0 }
local DC = { 0, 1, 0, -1 }
local OFF = Color3.fromRGB(150, 156, 170)
local ON = Color3.fromRGB(120, 255, 200)

local function openings(piece, rot)
	local base = piece == "straight" and { 0, 2 } or { 0, 1 }
	return { (base[1] + rot) % 4, (base[2] + rot) % 4 }
end

function Circuit.new(room, cfg, index)
	local self = setmetatable({ room = room, cfg = cfg, index = index, tiles = {}, solved = false }, Circuit)
	for r = 1, cfg.rows do
		self.tiles[r] = {}
		for c = 1, cfg.cols do
			local part = room.folder:FindFirstChild(("CircuitTile|%d|%d"):format(r, c))
			local t = { part = part, piece = "straight", rot = 0, arms = {} }
			self.tiles[r][c] = t
			if part then
				room.makePrompt(part, "لفّ القطعة", "⚡").Triggered:Connect(function(player)
					if self.solved or not room.isInside(player) then
						return
					end
					t.rot = (t.rot + 1) % 4
					self.dirty = true
					self:draw()
					self:check()
				end)
			end
		end
	end
	self.sink = room.folder:FindFirstChild("CircuitSink")
	return self
end

-- a random simple path from (entry, 1) to (exit, cols), as a list of {r, c, inDir, outDir}
function Circuit:makePath()
	local rows, cols = self.cfg.rows, self.cfg.cols
	for _ = 1, 200 do
		local r, c = math.random(1, rows), 1
		local exitRow = math.random(1, rows)
		local seen = { [r .. ":" .. c] = true }
		local path = { { r = r, c = c, inDir = 3 } }
		local ok = false
		for _ = 1, 40 do
			if c == cols and r == exitRow then
				ok = true
				break
			end
			local options = {}
			for d = 0, 3 do
				local nr, nc = r + DR[d + 1], c + DC[d + 1]
				if d ~= 3 and nr >= 1 and nr <= rows and nc >= 1 and nc <= cols and not seen[nr .. ":" .. nc] then
					table.insert(options, d)
					if d == 1 then
						table.insert(options, d) -- lean eastwards
					end
				end
			end
			if #options == 0 then
				break
			end
			local d = options[math.random(1, #options)]
			path[#path].outDir = d
			r, c = r + DR[d + 1], c + DC[d + 1]
			seen[r .. ":" .. c] = true
			table.insert(path, { r = r, c = c, inDir = (d + 2) % 4 })
		end
		if ok then
			path[#path].outDir = 1
			self.entry, self.exit = path[1].r, exitRow
			return path
		end
	end
	return nil
end

function Circuit:reset()
	self.solved, self.dirty = false, false
	local path = self:makePath()
	self.onPath = {}
	for r = 1, self.cfg.rows do
		for c = 1, self.cfg.cols do
			local t = self.tiles[r][c]
			t.piece = math.random() < 0.5 and "straight" or "corner"
			t.rot = math.random(0, 3)
		end
	end
	for _, step in ipairs(path) do
		local t = self.tiles[step.r][step.c]
		local a, b = step.inDir, step.outDir
		if (a + 2) % 4 == b then
			t.piece = "straight"
			t.goalRots = a % 2 == 0 and { 0, 2 } or { 1, 3 }
		else
			t.piece = "corner"
			-- the corner rotation whose openings are {a, b}
			t.goalRots = {}
			for rot = 0, 3 do
				local o = openings("corner", rot)
				if (o[1] == a and o[2] == b) or (o[1] == b and o[2] == a) then
					table.insert(t.goalRots, rot)
				end
			end
		end
		self.onPath[t] = true
		-- scramble: never start in a solved rotation
		repeat
			t.rot = math.random(0, 3)
		until not table.find(t.goalRots, t.rot)
	end
	-- the source and the device sit beside the entry/exit rows
	local src = self.room.folder:FindFirstChild("CircuitSource")
	local first, last = self.tiles[self.entry][1].part, self.tiles[self.exit][self.cfg.cols].part
	if src and first then
		src.CFrame = CFrame.new(first.Position + Vector3.new(-5.5, 1.3, 0))
	end
	if self.sink and last then
		self.sink.CFrame = CFrame.new(last.Position + Vector3.new(5.5, 1.8, 0))
		self.sink.Color = Color3.fromRGB(80, 90, 110)
		self.sink.Material = Enum.Material.SmoothPlastic
	end
	for _, row in ipairs(self.tiles) do
		for _, t in ipairs(row) do
			local hl = t.part and t.part:FindFirstChild("PathHint")
			if hl then
				hl:Destroy()
			end
		end
	end
	self:draw()
end

-- follow the energy; returns the set of powered tiles and whether it reached the east edge on the exit row
function Circuit:trace()
	local powered = {}
	local r, c, from = self.entry, 1, 3
	for _ = 1, self.cfg.rows * self.cfg.cols + 1 do
		local t = self.tiles[r] and self.tiles[r][c]
		if not t or powered[t] then
			return powered, false
		end
		local o = openings(t.piece, t.rot)
		local out
		if o[1] == from then
			out = o[2]
		elseif o[2] == from then
			out = o[1]
		else
			return powered, false
		end
		powered[t] = true
		if c == self.cfg.cols and out == 1 then
			return powered, r == self.exit
		end
		r, c, from = r + DR[out + 1], c + DC[out + 1], (out + 2) % 4
	end
	return powered, false
end

function Circuit:draw()
	local powered = self:trace()
	for _, row in ipairs(self.tiles) do
		for _, t in ipairs(row) do
			for _, a in ipairs(t.arms) do
				a:Destroy()
			end
			table.clear(t.arms)
			if t.part then
				local color = powered[t] and ON or OFF
				local mat = powered[t] and Enum.Material.Neon or Enum.Material.SmoothPlastic
				local hub = Instance.new("Part")
				hub.Name = "Arm"
				hub.Anchored, hub.CanCollide, hub.CanQuery = true, false, false
				hub.Size = Vector3.new(1.4, 0.3, 1.4)
				hub.CFrame = t.part.CFrame + Vector3.new(0, 0.35, 0)
				hub.Color, hub.Material = color, mat
				hub.Parent = t.part
				table.insert(t.arms, hub)
				for _, d in ipairs(openings(t.piece, t.rot)) do
					local arm = Instance.new("Part")
					arm.Name = "Arm"
					arm.Anchored, arm.CanCollide, arm.CanQuery = true, false, false
					local dir = DIRS[d + 1]
					arm.Size = Vector3.new(math.abs(dir.X) > 0 and 2.6 or 1.1, 0.3, math.abs(dir.Z) > 0 and 2.6 or 1.1)
					arm.CFrame = t.part.CFrame + Vector3.new(0, 0.35, 0) + dir * 1.35
					arm.Color, arm.Material = color, mat
					arm.Parent = t.part
					table.insert(t.arms, arm)
				end
			end
		end
	end
end

function Circuit:check()
	local _, done = self:trace()
	if done and not self.solved then
		self.solved = true
		if self.sink then
			self.sink.Color = ON
			self.sink.Material = Enum.Material.Neon
		end
		self.room.reveal(self.cfg.symbolSlot)
		self.room.tell("⚡ الطاقة (ATP) وصلت! طلع حرفين من شيفرة DNA على شاشة ⚡")
		self.room.changed()
	end
end

function Circuit:hint(level)
	if level == 1 then
		return "الطاقة تطلع من الميتوكوندريا البرتقالية وتروح للجهاز الثاني. لفّ القطع لين يمشي الضو بالخط"
	elseif level == 2 then
		for t in pairs(self.onPath) do
			if t.part and not t.part:FindFirstChild("PathHint") then
				local hl = Instance.new("Highlight")
				hl.Name = "PathHint"
				hl.FillTransparency = 1
				hl.OutlineColor = Color3.fromRGB(255, 220, 90)
				hl.Parent = t.part
			end
		end
		return "القطع اللي حولها إطار أصفر هي طريق الطاقة"
	end
	-- level 3: fix the first wrong tile along the solution
	for _, row in ipairs(self.tiles) do
		for _, t in ipairs(row) do
			if self.onPath[t] and not table.find(t.goalRots, t.rot) then
				t.rot = t.goalRots[1]
				self:draw()
				self:check()
				return "صحّحت لك قطعة وحدة من الطريق 😉"
			end
		end
	end
	return "الطريق كله صحيح، تأكد من اتجاه آخر قطعة"
end

return Circuit
