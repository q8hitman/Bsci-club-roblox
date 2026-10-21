-- Nucleus lock (v61, was "match two random emoji"): every earlier step reveals two bases of a DNA strand on its screen;
-- the nucleus opens with the complementary strand (A-T, G-C) set on the base panels (CorePanel|1..4, two per slot, in
-- screen order). Tap a panel to cycle A/T/G/C, then pull the lever (CoreLever). Nothing has to happen at the same
-- time, so one player can do it alone and a team can split the panels.
local Core = {}
Core.__index = Core

local BASES = { "A", "T", "G", "C" }
local PAIR = { A = "T", T = "A", G = "C", C = "G" }
local COLOR = {
	A = Color3.fromRGB(220, 70, 70),
	T = Color3.fromRGB(235, 190, 50),
	G = Color3.fromRGB(70, 180, 90),
	C = Color3.fromRGB(70, 130, 230),
}
local BLANK = Color3.fromRGB(40, 50, 70)

function Core.new(room, cfg, index)
	local self = setmetatable({ room = room, cfg = cfg, index = index, panels = {}, solved = false }, Core)
	for i = 1, #cfg.slots * 2 do
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
			label.Font = Enum.Font.GothamBlack
			label.TextColor3 = Color3.new(1, 1, 1)
			label.Parent = gui
			gui.Parent = part
			panel.label = label
			room.makePrompt(part, "غيّر القاعدة", "قاعدة " .. i).Triggered:Connect(function(player)
				if self.solved or not room.isInside(player) then
					return
				end
				panel.pick = panel.pick % #BASES + 1
				self.dirty = true
				self:refresh()
			end)
		end
	end
	local lever = room.folder:FindFirstChild("CoreLever")
	if lever then
		room.makePrompt(lever, "افتح النواة", "🧬").Triggered:Connect(function(player)
			if self.solved or not room.isInside(player) then
				return
			end
			self:activate()
		end)
	end
	return self
end

-- the base panel i needs: the pair of base ((i-1) % 2 + 1) on slot cfg.slots[ceil(i/2)]
function Core:need(i)
	local strand = self.room.symbols[self.cfg.slots[math.ceil(i / 2)]]
	return strand and PAIR[strand[(i - 1) % 2 + 1]]
end

function Core:refresh()
	for _, panel in ipairs(self.panels) do
		local b = BASES[panel.pick]
		if panel.label then
			panel.label.Text = b or "؟"
		end
		if panel.part then
			panel.part.Color = b and COLOR[b] or BLANK
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
				"🔒 الشيفرة ناقصة: شغّلوا الطاقة ⚡ وتعرّفوا على الخلايا 🔬 أول"
			)
			return
		end
	end
	for i, panel in ipairs(self.panels) do
		if BASES[panel.pick] ~= self:need(i) then
			self.room.tell("❌ الشريط ما يكمّل الشيفرة. تذكّروا: A مع T، و G مع C")
			return
		end
	end
	self.solved = true
	self.room.tell("🧬 الشريط المكمّل صح! النواة اشتغلت")
	self.room.changed()
end

function Core:hint(level)
	if level == 1 then
		return "كل قاعدة لها شريك: A مع T، و G مع C. حطّوا الشريك تحت كل حرف من الشاشتين"
	elseif level == 2 then
		return "القاعدة ١ و٢ = شركاء حرفي شاشة ⚡، والقاعدة ٣ و٤ = شركاء حرفي شاشة 🔬، وبعدين اسحبوا الذراع"
	end
	if self.room.stepSolved(self.cfg.needs[1]) then
		self.panels[1].pick = table.find(BASES, self:need(1)) or 0
		self:refresh()
		return "حطيت لك القاعدة الأولى، كمّلوا الباقي واسحبوا الذراع"
	end
	return "شغّلوا الطاقة أول عشان تطلع أول حروف الشيفرة"
end

return Core
