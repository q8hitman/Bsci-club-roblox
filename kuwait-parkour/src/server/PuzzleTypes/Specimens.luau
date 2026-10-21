-- Microscope (v61, was "Specimen Detective" with made-up creatures): four real cells on the microscope stages
-- (Pedestal|1..4), picked from six types. The field guide on the wall (SpecimenClues) describes each type by what you
-- can see (shape, nucleus, chloroplasts...), so the players learn to recognise a cell by its shape. Tap a stage to
-- cycle its name tag; all four right = solved. Every reset picks new cells and shuffles the stages.
local Specimens = {}
Specimens.__index = Specimens

local function piece(m, shape, size, cf, color, mat, transp)
	local p = Instance.new("Part")
	p.Shape = shape
	p.Size = size
	p.Anchored, p.CanCollide, p.CanQuery = true, false, false
	p.CastShadow = false
	p.CFrame = cf
	p.Color = color
	p.Material = mat or Enum.Material.SmoothPlastic
	p.Transparency = transp or 0
	p.TopSurface, p.BottomSurface = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth
	p.Parent = m
	return p
end

local BALL, CYL, BLOCK = Enum.PartType.Ball, Enum.PartType.Cylinder, Enum.PartType.Block
local NEON, GLASS = Enum.Material.Neon, Enum.Material.Glass

-- each builder draws the cell around c (a CFrame at the centre above the stage, facing the room)
local CELLS = {
	{
		name = "بكتيريا عصوية",
		clue = "شكل عصا وفيها سوط",
		build = function(m, c)
			local col = Color3.fromRGB(120, 190, 110)
			piece(m, CYL, Vector3.new(3.6, 1.8, 1.8), c, col)
			piece(m, BALL, Vector3.new(1.8, 1.8, 1.8), c * CFrame.new(-1.8, 0, 0), col)
			piece(m, BALL, Vector3.new(1.8, 1.8, 1.8), c * CFrame.new(1.8, 0, 0), col)
			for k = 0, 2 do -- the flagellum: a short zigzag tail
				piece(
					m,
					BLOCK,
					Vector3.new(1.1, 0.18, 0.18),
					c
						* CFrame.new(3 + k, (k % 2 == 0) and 0.2 or -0.2, 0)
						* CFrame.Angles(0, 0, (k % 2 == 0) and 0.4 or -0.4),
					Color3.fromRGB(90, 140, 80)
				)
			end
		end,
	},
	{
		name = "بكتيريا كروية",
		clue = "كرات صغيرة مربوطة بسلسلة",
		build = function(m, c)
			for k = 0, 3 do
				local a = (k - 1.5) * 0.45
				piece(
					m,
					BALL,
					Vector3.new(1.3, 1.3, 1.3),
					c * CFrame.new(math.sin(a) * 3, math.cos(a) * 1.2 - 0.6, 0),
					Color3.fromRGB(160, 110, 210)
				)
			end
		end,
	},
	{
		name = "كرية دم حمراء",
		clue = "قرص أحمر مقعّر، بدون نواة",
		build = function(m, c)
			local disc = c * CFrame.Angles(0, math.pi / 2, 0)
			piece(m, CYL, Vector3.new(0.9, 3.6, 3.6), disc, Color3.fromRGB(210, 50, 60))
			for _, s in ipairs({ -1, 1 }) do -- the dimple on both faces
				piece(m, CYL, Vector3.new(0.2, 1.8, 1.8), disc * CFrame.new(s * 0.4, 0, 0), Color3.fromRGB(160, 30, 40))
			end
		end,
	},
	{
		name = "خلية نباتية",
		clue = "جدار مربّع وبلاستيدات خضراء",
		build = function(m, c)
			piece(m, BLOCK, Vector3.new(3.4, 3.4, 3.4), c, Color3.fromRGB(90, 170, 80), GLASS, 0.45)
			piece(
				m,
				BLOCK,
				Vector3.new(1.8, 1.8, 1.8),
				c * CFrame.new(0.3, 0.2, 0),
				Color3.fromRGB(170, 220, 240),
				GLASS,
				0.3
			)
			piece(m, BALL, Vector3.new(0.9, 0.9, 0.9), c * CFrame.new(-1, -0.9, 0.8), Color3.fromRGB(140, 90, 60))
			for k = 0, 5 do
				local a = k * math.pi / 3
				piece(
					m,
					BALL,
					Vector3.new(0.6, 0.6, 0.6),
					c * CFrame.new(math.cos(a) * 1.35, math.sin(a) * 1.35, 1.2),
					Color3.fromRGB(40, 140, 50)
				)
			end
		end,
	},
	{
		name = "خلية عصبية",
		clue = "جسم صغير وتفرّعات طويلة",
		build = function(m, c)
			local col = Color3.fromRGB(240, 190, 90)
			piece(m, BALL, Vector3.new(1.8, 1.8, 1.8), c * CFrame.new(-1, 0.4, 0), col)
			piece(m, BLOCK, Vector3.new(3.6, 0.3, 0.3), c * CFrame.new(1, -0.3, 0) * CFrame.Angles(0, 0, -0.35), col) -- axon
			for k = 0, 4 do -- dendrites
				local a = math.pi / 2 + (k - 2) * 0.55
				piece(
					m,
					BLOCK,
					Vector3.new(1.6, 0.2, 0.2),
					c * CFrame.new(-1 + math.cos(a) * 1.5, 0.4 + math.sin(a) * 1.5, 0) * CFrame.Angles(0, 0, a),
					col
				)
			end
			piece(m, BALL, Vector3.new(0.6, 0.6, 0.6), c * CFrame.new(-1, 0.4, 0.75), Color3.fromRGB(150, 90, 40))
		end,
	},
	{
		name = "خميرة",
		clue = "فطر يتكاثر بالتبرعم: خلية صغيرة طالعة منها",
		build = function(m, c)
			local col = Color3.fromRGB(235, 215, 170)
			piece(m, BALL, Vector3.new(2.8, 2.8, 2.8), c, col)
			piece(m, BALL, Vector3.new(1.3, 1.3, 1.3), c * CFrame.new(1.6, 1.1, 0), col)
			piece(m, BALL, Vector3.new(0.8, 0.8, 0.8), c * CFrame.new(-0.3, 0, 1.1), Color3.fromRGB(170, 140, 100))
		end,
	},
}

function Specimens.new(room, cfg, index)
	local self = setmetatable({ room = room, cfg = cfg, index = index, peds = {}, solved = false }, Specimens)
	self.board = room.folder:FindFirstChild("SpecimenClues")
	for i = 1, cfg.count do
		local part = room.folder:FindFirstChild("Pedestal|" .. i)
		local ped = { part = part, model = nil, pick = 0 }
		self.peds[i] = ped
		if part then
			local tag = Instance.new("BillboardGui")
			tag.Name = "NameTag"
			tag.Size = UDim2.fromScale(5.6, 1.3) -- in studs: shrinks with distance, so neighbours never overlap
			tag.StudsOffset = Vector3.new(0, 7, 0)
			tag.AlwaysOnTop = false
			tag.MaxDistance = 80
			local label = Instance.new("TextLabel")
			label.Size = UDim2.fromScale(1, 1)
			label.BackgroundColor3 = Color3.fromRGB(20, 26, 36)
			label.BackgroundTransparency = 0.15
			label.TextColor3 = Color3.new(1, 1, 1)
			label.TextScaled = true
			label.Font = Enum.Font.GothamBold
			label.Parent = tag
			tag.Parent = part
			ped.label = label
			room.makePrompt(part, "غيّر الاسم", "🏷️").Triggered:Connect(function(player)
				if self.solved or not room.isInside(player) then
					return
				end
				ped.pick = ped.pick % #self.names + 1
				self.dirty = true
				self:refreshTags()
				self:check()
			end)
		end
	end
	return self
end

function Specimens:buildCell(ped, cell)
	if ped.model then
		ped.model:Destroy()
	end
	local m = Instance.new("Model")
	m.Name = "Specimen"
	-- pedestals are rotated cylinders: measure their real height along world Y
	local up = ped.part.CFrame:VectorToObjectSpace(Vector3.yAxis)
	local height = math.abs(up.X) * ped.part.Size.X
		+ math.abs(up.Y) * ped.part.Size.Y
		+ math.abs(up.Z) * ped.part.Size.Z
	local top = ped.part.Position + Vector3.new(0, height / 2 + 2.4, 0)
	cell.build(m, CFrame.new(top))
	-- a soft light under the cell, like a microscope stage lamp
	local glow =
		piece(m, BALL, Vector3.new(0.2, 0.2, 0.2), CFrame.new(top - Vector3.new(0, 2, 0)), Color3.new(1, 1, 1), NEON, 1)
	local light = Instance.new("PointLight")
	light.Range, light.Brightness = 7, 1.2
	light.Parent = glow
	m.Parent = self.room.folder
	ped.model = m
end

function Specimens:reset()
	self.solved, self.dirty = false, false
	local pool = table.clone(CELLS)
	self.cells = {}
	self.names = {}
	for i = 1, 4 do
		self.cells[i] = table.remove(pool, math.random(1, #pool))
		self.names[i] = self.cells[i].name
	end
	-- the stages get the four cells in a shuffled order; truth[stage] = index into self.names
	local order = { 1, 2, 3, 4 }
	for i = 4, 2, -1 do
		local j = math.random(1, i)
		order[i], order[j] = order[j], order[i]
	end
	self.truth = {}
	local clues = { "🔬 دليل الخلايا" }
	for nameIdx = 1, 4 do
		local pedIdx = order[nameIdx]
		self.truth[pedIdx] = nameIdx
		local ped = self.peds[pedIdx]
		if ped and ped.part then
			self:buildCell(ped, self.cells[nameIdx])
		end
		table.insert(clues, ("%s: %s"):format(self.cells[nameIdx].name, self.cells[nameIdx].clue))
	end
	self.room.setScreen(self.board, table.concat(clues, "\n"))
	for _, ped in ipairs(self.peds) do
		ped.pick = 0
		if ped.label then
			ped.label.TextColor3 = Color3.new(1, 1, 1)
		end
	end
	self:refreshTags()
end

function Specimens:refreshTags()
	for _, ped in ipairs(self.peds) do
		if ped.label then
			ped.label.Text = ped.pick == 0 and "؟ اختار الاسم" or self.names[ped.pick]
		end
	end
end

function Specimens:check()
	for i, ped in ipairs(self.peds) do
		if ped.pick ~= self.truth[i] then
			return
		end
	end
	if not self.solved then
		self.solved = true
		for _, ped in ipairs(self.peds) do
			if ped.label then
				ped.label.TextColor3 = Color3.fromRGB(120, 255, 200)
			end
		end
		self.room.reveal(self.cfg.symbolSlot)
		self.room.tell(
			"🔬 عرفتوا كل الخلايا! طلع حرفين من شيفرة DNA على شاشة 🔬"
		)
		self.room.changed()
	end
end

function Specimens:hint(level)
	if level == 1 then
		return "قارن شكل كل خلية بالوصف على لوحة «دليل الخلايا» اللي على الجدار اليمين"
	elseif level == 2 then
		for i, ped in ipairs(self.peds) do
			if ped.pick ~= self.truth[i] then
				ped.pick = self.truth[i]
				self:refreshTags()
				self:check()
				return "حطيت لك اسم وحد صح، كمّل الباقي"
			end
		end
		return "كل الأسماء صح!"
	end
	local wrong = 0
	for i, ped in ipairs(self.peds) do
		if ped.label then
			local ok = ped.pick == self.truth[i]
			ped.label.TextColor3 = ok and Color3.fromRGB(120, 255, 200) or Color3.fromRGB(255, 110, 110)
			wrong += ok and 0 or 1
		end
	end
	return ("الأسماء الحمرا غلط (%d)، الخضرا صح"):format(wrong)
end

return Specimens
