-- v54 hands-on lab, client side: only small, temporary overlays. The work itself happens on the 3D benches
-- (Labs54.server). Shows: one-line lab feedback, what you are holding, the decolouriser timer, the microscope view
-- (Gram result), the gel reading choice and the thermocycler program.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer
local event = ReplicatedStorage:WaitForChild("Bench54", 60)
local fn = ReplicatedStorage:WaitForChild("Bench54Fn", 60)
if not (event and fn) then
	return
end

local function play(name)
	if _G.BSCPlay then
		_G.BSCPlay(name)
	end
end

local gui = Instance.new("ScreenGui")
gui.Name = "Bench54"
gui.ResetOnSpawn = false
gui.DisplayOrder = 26
gui.IgnoreGuiInset = true
gui.Parent = player:WaitForChild("PlayerGui")

local function corner(o, r)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(r or 0.25, 0)
	c.Parent = o
end

local function textLabel(parent, pos, size, color)
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.Position = pos
	t.Size = size
	t.TextColor3 = color or Color3.new(1, 1, 1)
	t.TextScaled = true
	t.TextWrapped = true
	t.Font = Enum.Font.GothamBold
	t.Parent = parent
	return t
end

local function button(parent, text, pos, size, color, onClick)
	local b = Instance.new("TextButton")
	b.Position = pos
	b.Size = size
	b.BackgroundColor3 = color
	b.TextColor3 = Color3.new(1, 1, 1)
	b.TextScaled = true
	b.TextWrapped = true
	b.Font = Enum.Font.GothamBold
	b.Text = text
	b.Parent = parent
	corner(b, 0.3)
	b.Activated:Connect(onClick)
	return b
end

-- ------------------------------------------------------------------ one-line feedback (replaces itself, fades out)
local TONES = {
	info = Color3.fromRGB(30, 34, 44),
	good = Color3.fromRGB(24, 80, 56),
	warn = Color3.fromRGB(120, 60, 24),
}
local line = Instance.new("TextLabel")
line.AnchorPoint = Vector2.new(0.5, 1)
line.Position = UDim2.fromScale(0.5, 0.86)
line.Size = UDim2.fromScale(0.5, 0.055)
line.BackgroundTransparency = 0.15
line.TextColor3 = Color3.new(1, 1, 1)
line.TextScaled = true
line.TextWrapped = true
line.Font = Enum.Font.GothamBold
line.Visible = false
line.Parent = gui
corner(line, 0.4)
local lineMin = Instance.new("UISizeConstraint")
lineMin.MinSize = Vector2.new(300, 34)
lineMin.Parent = line
local pad = Instance.new("UIPadding")
pad.PaddingLeft, pad.PaddingRight = UDim.new(0, 10), UDim.new(0, 10)
pad.Parent = line
local lineId = 0
local function say(text, tone)
	lineId += 1
	local my = lineId
	line.Text = text
	line.BackgroundColor3 = TONES[tone] or TONES.info
	line.Visible = true
	line.TextTransparency, line.BackgroundTransparency = 0, 0.15
	play(tone == "warn" and "wrong" or tone == "good" and "collect" or "click")
	task.delay(math.max(3.5, (utf8.len(text) or #text) / 16), function()
		if my == lineId then
			TweenService:Create(line, TweenInfo.new(0.5), { TextTransparency = 1, BackgroundTransparency = 1 }):Play()
			task.wait(0.5)
			if my == lineId then
				line.Visible = false
			end
		end
	end)
end

-- ------------------------------------------------------------------ holding chip
local holding = textLabel(gui, UDim2.fromScale(0.02, 0.8), UDim2.fromScale(0.16, 0.04))
holding.AnchorPoint = Vector2.new(0, 1)
holding.BackgroundColor3 = Color3.fromRGB(30, 34, 44)
holding.BackgroundTransparency = 0.25
holding.Visible = false
corner(holding, 0.4)
local function refreshHolding()
	local c = player:GetAttribute("Carrying")
	holding.Visible = c ~= nil
	holding.Text = c and ("🖐️ بيدك: " .. tostring(c)) or ""
end
player:GetAttributeChangedSignal("Carrying"):Connect(refreshHolding)

-- ------------------------------------------------------------------ decolouriser timer (a slim bar with the right window)
local timer = Instance.new("Frame")
timer.AnchorPoint = Vector2.new(0.5, 1)
timer.Position = UDim2.fromScale(0.5, 0.79)
timer.Size = UDim2.fromScale(0.34, 0.025)
timer.BackgroundColor3 = Color3.fromRGB(50, 54, 62)
timer.Visible = false
timer.Parent = gui
corner(timer, 1)
local band = Instance.new("Frame")
band.BackgroundColor3 = Color3.fromRGB(70, 190, 110)
band.BorderSizePixel = 0
band.Parent = timer
local needle = Instance.new("Frame")
needle.AnchorPoint = Vector2.new(0.5, 0.5)
needle.Size = UDim2.new(0, 4, 1.8, 0)
needle.BackgroundColor3 = Color3.new(1, 1, 1)
needle.Parent = timer
local timerId = 0

-- ------------------------------------------------------------------ small centred panel for choices
local panel = Instance.new("Frame")
panel.AnchorPoint = Vector2.new(0.5, 0.5)
panel.Position = UDim2.fromScale(0.5, 0.48)
panel.Size = UDim2.fromScale(0.38, 0.5)
panel.BackgroundColor3 = Color3.fromRGB(22, 26, 36)
panel.BackgroundTransparency = 0.08
panel.Visible = false
panel.Parent = gui
corner(panel, 0.06)
local panelMin = Instance.new("UISizeConstraint")
panelMin.MinSize = Vector2.new(300, 230)
panelMin.Parent = panel
local function clearPanel()
	panelMin.MinSize = Vector2.new(300, 230)
	panel.Position = UDim2.fromScale(0.5, 0.48)
	panel.Size = UDim2.fromScale(0.38, 0.5)
	for _, c in ipairs(panel:GetChildren()) do
		if not c:IsA("UICorner") and not c:IsA("UISizeConstraint") then
			c:Destroy()
		end
	end
end
local function closeButton()
	button(panel, "X", UDim2.fromScale(0.88, 0.02), UDim2.fromScale(0.1, 0.1), Color3.fromRGB(120, 50, 50), function()
		panel.Visible = false
	end).Name =
		"Close"
end

local VIOLET, PINK = Color3.fromRGB(110, 50, 180), Color3.fromRGB(226, 90, 140)

local function scope(data)
	clearPanel()
	closeButton()
	textLabel(panel, UDim2.fromScale(0.05, 0.02), UDim2.fromScale(0.8, 0.1)).Text = "🔬 عدسة الزيت ×100"
	local view = Instance.new("Frame")
	view.AnchorPoint = Vector2.new(0.5, 0)
	view.Position = UDim2.fromScale(0.5, 0.14)
	view.Size = UDim2.fromScale(0.6, 0.6)
	view.BackgroundColor3 = Color3.fromRGB(250, 246, 236)
	view.ClipsDescendants = true
	view.Parent = panel
	corner(view, 1)
	local ar = Instance.new("UIAspectRatioConstraint")
	ar.Parent = view
	local rnd = Random.new()
	local color = data.color == "violet" and VIOLET or PINK
	for _ = 1, data.cocci and 6 or 10 do
		local cx, cy = rnd:NextNumber(0.2, 0.8), rnd:NextNumber(0.2, 0.8)
		for _ = 1, data.cocci and 5 or 1 do
			local cell = Instance.new("Frame")
			cell.AnchorPoint = Vector2.new(0.5, 0.5)
			cell.BackgroundColor3 = color
			cell.BorderSizePixel = 0
			if data.cocci then
				cell.Size = UDim2.fromScale(0.06, 0.06)
				cell.Position = UDim2.fromScale(cx + rnd:NextNumber(-0.04, 0.04), cy + rnd:NextNumber(-0.04, 0.04))
			else
				cell.Size = UDim2.fromScale(0.15, 0.05)
				cell.Position = UDim2.fromScale(cx, cy)
				cell.Rotation = rnd:NextNumber(0, 180)
			end
			corner(cell, 1)
			cell.Parent = view
		end
	end
	local answered = false
	for i, k in ipairs({ "pos", "neg" }) do
		button(
			panel,
			k == "pos" and "🟣 موجبة الجرام" or "🌸 سالبة الجرام",
			UDim2.fromScale(0.05 + (i - 1) * 0.47, 0.8),
			UDim2.fromScale(0.43, 0.15),
			k == "pos" and VIOLET or PINK,
			function()
				if answered then
					return
				end
				answered = true
				local r = fn:InvokeServer("gram", k)
				panel.Visible = false
				if not r then
					return
				end
				if r.quality ~= "ok" then
					say(
						"🧪 النتيجة غير موثوقة: إزالة اللون ما كانت مضبوطة. أعد التجربة",
						"warn"
					)
				elseif r.ok then
					say(
						("✅ صح! %s %s • +%d 🧪"):format(
							r.name,
							r.truth == "pos" and "موجبة" or "سالبة",
							r.gained
						),
						"good"
					)
				else
					say(
						"❌ مو صح: شوف اللون بعد الصفرانين (بنفسجي = موجبة، وردي = سالبة)",
						"warn"
					)
				end
			end
		).Name = "Gram_"
			.. k
	end
	panel.Visible = true
end

local function gelRead(data)
	clearPanel()
	closeButton()
	textLabel(panel, UDim2.fromScale(0.05, 0.04), UDim2.fromScale(0.8, 0.3)).Text =
		"🔦 قارن شريط العيّنة (وردي) بشرائط الـ Ladder (أزرق): كم حجمها تقريباً؟"
	local answered = false
	for i, opt in ipairs(data.options) do
		button(
			panel,
			("%d bp"):format(opt),
			UDim2.fromScale(0.05 + (i - 1) * 0.31, 0.5),
			UDim2.fromScale(0.28, 0.3),
			Color3.fromRGB(60, 90, 170),
			function()
				if answered then
					return
				end
				answered = true
				local r = fn:InvokeServer("gel", i)
				panel.Visible = false
				if r then
					say(
						r.ok
								and ("✅ صح! %d bp • القطع الصغيرة تمشي أبعد • +%d 🧪"):format(
									r.truth,
									r.gained
								)
							or ("❌ الحجم الصح %d bp: قارن مكان الشريط بين شرائط الـ Ladder"):format(
								r.truth
							),
						r.ok and "good" or "warn"
					)
				end
			end
		).Name = "GelOption_"
			.. i
	end
	panel.Position = UDim2.fromScale(0.5, 0.17) -- a slim strip at the top: the gel itself stays visible
	panel.Size = UDim2.fromScale(0.4, 0.22)
	panelMin.MinSize = Vector2.new(300, 130)
	panel.Visible = true
end

local function pcrProgram()
	clearPanel()
	closeButton()
	panel.Position = UDim2.fromScale(0.5, 0.48)
	panel.Size = UDim2.fromScale(0.38, 0.5)
	textLabel(panel, UDim2.fromScale(0.05, 0.03), UDim2.fromScale(0.8, 0.09)).Text =
		"🌡️ برمج الجهاز (30 دورة)"
	local choice = {}
	local rows = {
		{ "فك الشريطين", { 55, 72, 95 } },
		{ "التصاق البادئات", { 95, 55, 72 } },
		{ "الاستطالة", { 55, 95, 72 } },
	}
	for r, row in ipairs(rows) do
		local y = 0.15 + (r - 1) * 0.22
		textLabel(panel, UDim2.fromScale(0.62, y), UDim2.fromScale(0.36, 0.16)).Text = row[1]
		local btns = {}
		for i, t in ipairs(row[2]) do
			local b
			b = button(
				panel,
				("%d°"):format(t),
				UDim2.fromScale(0.04 + (i - 1) * 0.19, y),
				UDim2.fromScale(0.17, 0.16),
				Color3.fromRGB(60, 70, 90),
				function()
					choice[r] = t
					for _, o in ipairs(btns) do
						o.BackgroundColor3 = Color3.fromRGB(60, 70, 90)
					end
					b.BackgroundColor3 = Color3.fromRGB(40, 150, 100)
				end
			)
			b.Name = ("Pcr%d_%d"):format(r, t)
			btns[i] = b
		end
	end
	button(
		panel,
		"▶ شغّل",
		UDim2.fromScale(0.3, 0.82),
		UDim2.fromScale(0.4, 0.14),
		Color3.fromRGB(40, 150, 100),
		function()
			if not (choice[1] and choice[2] and choice[3]) then
				return say("اختار حرارة لكل خطوة", "info")
			end
			local r = fn:InvokeServer("pcr", choice[1], choice[2], choice[3])
			if r and r.ok then
				panel.Visible = false
				say("🧬 الجهاز شغّال: راقب الشاشة", "info")
			elseif r then
				say(r.msg, "warn")
			end
		end
	).Name =
		"PcrStart"
	panel.Visible = true
end

event.OnClientEvent:Connect(function(data)
	if type(data) ~= "table" then
		return
	end
	if data.kind == "toast" then
		say(data.text, data.tone)
	elseif data.kind == "timer" then
		timerId += 1
		local my = timerId
		if data.stop then
			timer.Visible = false
			return
		end
		band.Position = UDim2.fromScale(data.min / data.bar, 0)
		band.Size = UDim2.fromScale((data.max - data.min) / data.bar, 1)
		timer.Visible = true
		local t0 = os.clock()
		task.spawn(function()
			while my == timerId and os.clock() - t0 < data.bar + 2 do
				needle.Position = UDim2.fromScale(math.clamp((os.clock() - t0) / data.bar, 0, 1), 0.5)
				task.wait()
			end
			if my == timerId then
				timer.Visible = false
			end
		end)
	elseif data.kind == "scope" then
		scope(data)
	elseif data.kind == "gelRead" then
		gelRead(data)
	elseif data.kind == "pcrProgram" then
		pcrProgram()
	end
end)
