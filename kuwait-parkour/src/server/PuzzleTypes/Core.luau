-- Core Activation: two panels (CorePanel|1..2) each cycle through the symbols when tapped; the lever (CoreLever)
-- checks them against the symbols the earlier steps revealed. Nothing has to happen at the same time, so one player
-- can do it alone and a team can split the panels.
local Core = {}
Core.__index = Core

local SYMBOLS = { "🔺", "⭐", "🌙", "💧", "🍀", "🔷" } -- same list as PuzzleRooms.server

function Core.new(room, cfg, index)
	local self = setmetatable({ room = room, cfg = cfg, index = index, panels = {}, solved = false }, Core)
	for i = 1, #cfg.slots do
		local part = room.folder:FindFirstChild("CorePanel|" .. i)
		local panel = { part = part, pick = 0 }
		self.panels[i] = panel
		if part then
			local gui = Instance.new("SurfaceGui")
			gui.Face = Enum.NormalId.Back
			gui.CanvasSize = Vector2.new(200, 200)
			local label = Instance.new("TextLabel")
			label.Size = UDim2.fromScale(1, 1)
			label.BackgroundTransparency = 1
			label.TextScaled = true
			label.TextColor3 = Color3.new(1, 1, 1)
			label.Parent = gui
			gui.Parent = part
			panel.label = label
			room.makePrompt(part, "غيّر الرمز", "لوحة " .. i).Triggered:Connect(function(player)
				if self.solved or not room.isInside(player) then
					return
				end
				panel.pick = panel.pick % #SYMBOLS + 1
				self.dirty = true
				self:refresh()
			end)
		end
	end
	local lever = room.folder:FindFirstChild("CoreLever")
	if lever then
		room.makePrompt(lever, "شغّل النواة", "🧬").Triggered:Connect(function(player)
			if self.solved or not room.isInside(player) then
				return
			end
			self:activate()
		end)
	end
	return self
end

function Core:refresh()
	for _, panel in ipairs(self.panels) do
		if panel.label then
			panel.label.Text = panel.pick == 0 and "؟" or SYMBOLS[panel.pick]
		end
	end
end

function Core:reset()
	self.solved, self.dirty = false, false
	for _, panel in ipairs(self.panels) do
		panel.pick = 0
	end
	self:refresh()
end

function Core:activate()
	for _, need in ipairs(self.cfg.needs) do
		if not self.room.stepSolved(need) then
			self.room.tell(
				"🔒 النواة تحتاج رمزين: حلّوا الدائرة والعيّنات أول"
			)
			return
		end
	end
	for i, slot in ipairs(self.cfg.slots) do
		local panel = self.panels[i]
		if not panel or SYMBOLS[panel.pick] ~= self.room.symbols[slot] then
			self.room.tell("❌ الرموز ما تطابق الشاشات، جرّبوا مرة ثانية")
			return
		end
	end
	self.solved = true
	self.room.tell("🧬 النواة اشتغلت!")
	self.room.changed()
end

function Core:hint(level)
	if level == 1 then
		return "الرموز تطلع على الشاشتين فوق الدائرة والعيّنات لما تحلّونهم"
	elseif level == 2 then
		return "اللوحة ١ = رمز شاشة ⚡ الدائرة، واللوحة ٢ = رمز شاشة 🔬 العيّنات، وبعدين اسحب الذراع"
	end
	local slot = self.cfg.slots[1]
	if self.room.symbols[slot] and self.room.stepSolved(self.cfg.needs[1]) then
		self.panels[1].pick = table.find(SYMBOLS, self.room.symbols[slot]) or 0
		self:refresh()
		return "حطيت لك رمز اللوحة ١، حط رمز اللوحة ٢ واسحب الذراع"
	end
	return "حلّوا الدائرة أول عشان يطلع رمزها"
end

return Core
