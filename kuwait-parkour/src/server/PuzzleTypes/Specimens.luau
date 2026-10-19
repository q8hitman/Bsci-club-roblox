-- Specimen Detective: four fantasy creatures on pedestals (Pedestal|1..4). The clue board describes each by TWO
-- features (colour + number of eyes); colours repeat in pairs and so do eye counts, so only the combination
-- identifies a creature: you have to look, not guess. Tap a pedestal to cycle its name tag; all four right = solved.
-- Every reset shuffles colours, eyes, spikes and which name belongs where.
local Specimens = {}
Specimens.__index = Specimens

local NAMES = { "غلوبق", "بلوبزي", "سبايكلت", "موسي", "زيبي", "نوفا" }
local COLORS = {
	{ "أحمر", Color3.fromRGB(230, 80, 80) },
	{ "أزرق", Color3.fromRGB(80, 140, 230) },
	{ "أخضر", Color3.fromRGB(90, 200, 110) },
	{ "بنفسجي", Color3.fromRGB(170, 110, 230) },
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
			tag.Size = UDim2.fromScale(5.2, 1.3) -- in studs: shrinks with distance, so neighbours never overlap
			tag.StudsOffset = Vector3.new(0, 6.6, 0)
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

function Specimens:buildCreature(ped, color, eyes, spikes)
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
	local top = ped.part.Position + Vector3.new(0, height / 2 + 1.8, 0)
	local body = Instance.new("Part")
	body.Shape = Enum.PartType.Ball
	body.Size = Vector3.new(3.4, 3.4, 3.4)
	body.Anchored, body.CanCollide = true, false
	body.Color, body.Material = color, Enum.Material.SmoothPlastic
	body.CFrame = CFrame.new(top)
	body.Parent = m
	for e = 1, eyes do
		local x = (e - (eyes + 1) / 2) * 0.95
		local eye = Instance.new("Part")
		eye.Shape = Enum.PartType.Ball
		eye.Size = Vector3.new(0.8, 0.8, 0.8)
		eye.Anchored, eye.CanCollide = true, false
		eye.Color = Color3.new(1, 1, 1)
		eye.CFrame = CFrame.new(top + Vector3.new(x, 0.6, 1.45))
		eye.Parent = m
		local pupil = eye:Clone()
		pupil.Size = Vector3.new(0.35, 0.35, 0.35)
		pupil.Color = Color3.new(0.05, 0.05, 0.05)
		pupil.CFrame = CFrame.new(top + Vector3.new(x, 0.6, 1.8))
		pupil.Parent = m
	end
	if spikes then
		for k = 0, 5 do
			local a = k * math.pi / 3
			local sp = Instance.new("Part")
			sp.Size = Vector3.new(0.4, 1.4, 0.4)
			sp.Anchored, sp.CanCollide = true, false
			sp.Color = color:Lerp(Color3.new(1, 1, 1), 0.4)
			sp.CFrame = CFrame.new(top + Vector3.new(math.cos(a) * 1.2, 1.6, math.sin(a) * 1.2))
				* CFrame.Angles(math.sin(a) * 0.5, 0, -math.cos(a) * 0.5)
			sp.Parent = m
		end
	end
	m.Parent = self.room.folder
	ped.model = m
end

function Specimens:reset()
	self.solved, self.dirty = false, false
	-- two colours x two eye counts = four unique combinations
	local pal = table.clone(COLORS)
	local c1 = table.remove(pal, math.random(1, #pal))
	local c2 = table.remove(pal, math.random(1, #pal))
	local e1 = math.random(1, 3)
	local e2 = e1 % 3 + 1
	local combos = { { c1, e1 }, { c1, e2 }, { c2, e1 }, { c2, e2 } }
	local namePool = table.clone(NAMES)
	self.names = {}
	for i = 1, 4 do
		self.names[i] = table.remove(namePool, math.random(1, #namePool))
	end
	-- creature i on pedestal i gets combo order shuffled; truth[i] = index into self.names
	local order = { 1, 2, 3, 4 }
	for i = 4, 2, -1 do
		local j = math.random(1, i)
		order[i], order[j] = order[j], order[i]
	end
	self.truth = {}
	local clues = { "🔍 ملف العيّنات" }
	for nameIdx = 1, 4 do
		local combo = combos[nameIdx]
		local pedIdx = order[nameIdx]
		self.truth[pedIdx] = nameIdx
		local ped = self.peds[pedIdx]
		if ped and ped.part then
			self:buildCreature(ped, combo[1][2], combo[2], math.random() < 0.5)
		end
		table.insert(
			clues,
			("%s: %s، %d %s"):format(
				self.names[nameIdx],
				combo[1][1],
				combo[2],
				combo[2] == 1 and "عين" or "عيون"
			)
		)
	end
	table.insert(clues, "(الأشواك ما لها دخل 😉)")
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
		self.room.tell("🔬 كل العيّنات صح! الرمز طلع على الشاشة")
		self.room.changed()
	end
end

function Specimens:hint(level)
	if level == 1 then
		return "كل وصف فيه صفتين: اللون وعدد العيون. لازم الثنتين يطابقون، لون وحده ما يكفي"
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
