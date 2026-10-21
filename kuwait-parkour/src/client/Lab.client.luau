-- Research Lab UI: microscope, PCR (timing), gel electrophoresis, the projects computer, the batch picker,
-- and the "field microscope" upgrade that outlines nearby hidden collectibles. Server checks everything (Lab.server).
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer
local LabData = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("LabData"))
local openEvent = ReplicatedStorage:WaitForChild("LabOpen", 30)
local labFn = ReplicatedStorage:WaitForChild("Lab", 30)
if not (openEvent and labFn) then
	return
end

local GREEN = Color3.fromRGB(24, 80, 56)
local PAPER = Color3.fromRGB(246, 248, 246)
local INK = Color3.fromRGB(30, 40, 36)

local function play(name)
	if _G.BSCPlay then
		_G.BSCPlay(name)
	end
end

-- ------------------------------------------------------------------ panel
local gui = Instance.new("ScreenGui")
gui.Name = "LabPanel"
gui.ResetOnSpawn = false
gui.DisplayOrder = 45
gui.Enabled = false
gui.Parent = player:WaitForChild("PlayerGui")

local panel = Instance.new("Frame")
panel.AnchorPoint = Vector2.new(0.5, 0.5)
panel.Position = UDim2.fromScale(0.5, 0.52)
panel.Size = UDim2.fromScale(0.56, 0.66)
panel.BackgroundColor3 = PAPER
panel.Parent = gui
local function corner(o, r)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(r or 0.04, 0)
	c.Parent = o
end
corner(panel)
local size = Instance.new("UISizeConstraint")
size.MinSize = Vector2.new(330, 280)
size.Parent = panel

local header = Instance.new("TextLabel")
header.Size = UDim2.fromScale(1, 0.13)
header.BackgroundColor3 = GREEN
header.TextColor3 = Color3.new(1, 1, 1)
header.TextScaled = true
header.Font = Enum.Font.GothamBold
header.Parent = panel
corner(header, 0.25)

local rpLabel = Instance.new("TextLabel")
rpLabel.AnchorPoint = Vector2.new(1, 0)
rpLabel.Position = UDim2.fromScale(0.98, 0.15)
rpLabel.Size = UDim2.fromScale(0.36, 0.07)
rpLabel.BackgroundTransparency = 1
rpLabel.TextColor3 = GREEN
rpLabel.TextScaled = true
rpLabel.Font = Enum.Font.GothamBold
rpLabel.TextXAlignment = Enum.TextXAlignment.Right
rpLabel.Parent = panel

local body = Instance.new("Frame")
body.Position = UDim2.fromScale(0.04, 0.23)
body.Size = UDim2.fromScale(0.92, 0.66)
body.BackgroundTransparency = 1
body.Parent = panel

local closeBtn = Instance.new("TextButton")
closeBtn.AnchorPoint = Vector2.new(0.5, 1)
closeBtn.Position = UDim2.fromScale(0.5, 0.98)
closeBtn.Size = UDim2.fromScale(0.3, 0.08)
closeBtn.BackgroundColor3 = Color3.fromRGB(150, 50, 60)
closeBtn.TextColor3 = Color3.new(1, 1, 1)
closeBtn.TextScaled = true
closeBtn.Font = Enum.Font.GothamBold
closeBtn.Text = "إغلاق"
closeBtn.Parent = panel
corner(closeBtn, 0.3)

local session = 0
local function clear()
	session += 1
	for _, c in ipairs(body:GetChildren()) do
		c:Destroy()
	end
end
local function close()
	clear()
	gui.Enabled = false
end
closeBtn.Activated:Connect(close)

local function setRP(n)
	rpLabel.Text = ("🧪 نقاط البحث: %d"):format(n or player:GetAttribute("Research") or 0)
end

local function text(parent, str, pos, sz, color, bold)
	local t = Instance.new("TextLabel")
	t.Position = pos
	t.Size = sz
	t.BackgroundTransparency = 1
	t.TextColor3 = color or INK
	t.TextScaled = true
	t.TextWrapped = true
	t.Font = bold and Enum.Font.GothamBold or Enum.Font.Gotham
	t.Text = str
	t.Parent = parent
	return t
end

local function button(parent, str, pos, sz, color, fn)
	local b = Instance.new("TextButton")
	b.Position = pos
	b.Size = sz
	b.BackgroundColor3 = color
	b.TextColor3 = Color3.new(1, 1, 1)
	b.TextScaled = true
	b.TextWrapped = true
	b.Font = Enum.Font.GothamBold
	b.Text = str
	b.Parent = parent
	corner(b, 0.2)
	b.Activated:Connect(function()
		play("click")
		fn(b)
	end)
	return b
end

local function feedback(result, rightText)
	if result and result.ok then
		play("collect")
		return ("✅ صح! +%d نقطة بحث"):format(result.gained or 0)
			.. ((result.gained or 0) == 0 and " (استنى ثواني بين التجارب)" or "")
	end
	play("wrong")
	return "❌ مو صح" .. (rightText and ("، الجواب: " .. rightText) or "")
end

-- ------------------------------------------------------------------ microscope
local function microscope()
	clear()
	local my = session
	header.Text = "🔬 تحديد الخلايا | Cell Identification (محاكاة)"
	local data = labFn:InvokeServer("slide")
	if my ~= session or not data then
		return
	end
	setRP(data.research)
	text(body, "🔎 " .. data.text, UDim2.fromScale(0, 0), UDim2.fromScale(1, 0.26), INK, true)
	local result = text(body, "", UDim2.fromScale(0, 0.82), UDim2.fromScale(1, 0.16), GREEN, true)
	local kinds = { "plant", "animal", "bacteria", "fungus" }
	local cols = {
		Color3.fromRGB(60, 140, 80),
		Color3.fromRGB(190, 110, 70),
		Color3.fromRGB(80, 110, 190),
		Color3.fromRGB(140, 90, 170),
	}
	local answered = false
	for i, k in ipairs(kinds) do
		local col, row = (i - 1) % 2, (i - 1) // 2
		button(
			body,
			LabData.KINDS[k],
			UDim2.fromScale(col * 0.51, 0.32 + row * 0.24),
			UDim2.fromScale(0.49, 0.2),
			cols[i],
			function()
				if answered then
					return
				end
				answered = true
				local r = labFn:InvokeServer("answer", data.token, k)
				if my ~= session then
					return
				end
				result.Text = feedback(r, r and r.answer and LabData.KINDS[r.answer])
				setRP(r and r.research)
				task.delay(1.6, function()
					if my == session then
						microscope()
					end
				end)
			end
		)
	end
end

-- ------------------------------------------------------------------ gel electrophoresis
local function gel()
	clear()
	local my = session
	header.Text = "🧪 الفصل الكهربائي | Gel Electrophoresis (محاكاة)"
	local data = labFn:InvokeServer("gel")
	if my ~= session or not data then
		return
	end
	setRP(data.research)
	text(
		body,
		"الـ DNA سالب الشحنة فيمشي باتجاه القطب الموجب (+). اختار القطعة اللي بتقطع أطول مسافة:",
		UDim2.fromScale(0, 0),
		UDim2.fromScale(1, 0.18),
		INK
	)
	-- the gel: wells at the top, bands start there and only move after you answer
	local gelBox = Instance.new("Frame")
	gelBox.Position = UDim2.fromScale(0.05, 0.2)
	gelBox.Size = UDim2.fromScale(0.9, 0.42)
	gelBox.BackgroundColor3 = Color3.fromRGB(150, 200, 230)
	gelBox.Parent = body
	corner(gelBox, 0.05)
	text(gelBox, "− (الآبار)", UDim2.fromScale(0, 0), UDim2.fromScale(0.3, 0.12), INK)
	text(gelBox, "+", UDim2.fromScale(0.9, 0.86), UDim2.fromScale(0.1, 0.14), INK, true)
	local bands = {}
	for i = 1, #data.bands do
		local band = Instance.new("Frame")
		band.Position = UDim2.fromScale(0.08 + (i - 1) * 0.31, 0.14)
		band.Size = UDim2.fromScale(0.22, 0.06)
		band.BackgroundColor3 = Color3.fromRGB(40, 60, 160)
		band.Parent = gelBox
		bands[i] = band
	end
	local result = text(body, "", UDim2.fromScale(0, 0.88), UDim2.fromScale(1, 0.12), GREEN, true)
	local answered = false
	for i, label in ipairs(data.bands) do
		button(
			body,
			label,
			UDim2.fromScale(0.05 + (i - 1) * 0.31, 0.66),
			UDim2.fromScale(0.27, 0.18),
			Color3.fromRGB(60, 90, 170),
			function()
				if answered then
					return
				end
				answered = true
				local r = labFn:InvokeServer("answer", data.token, i)
				if my ~= session then
					return
				end
				result.Text = feedback(r, r and r.answer and data.bands[r.answer])
				setRP(r and r.research)
				-- run the gel: distance ~ inverse to log(size)
				for j, lb in ipairs(data.bands) do
					local bp = tonumber(lb:match("%d+"))
					local y = 0.14 + math.clamp(1 - (math.log10(bp) - 2) / 1.7, 0.05, 1) * 0.7
					TweenService:Create(
						bands[j],
						TweenInfo.new(1.4, Enum.EasingStyle.Quad),
						{ Position = UDim2.fromScale(0.08 + (j - 1) * 0.31, y) }
					):Play()
				end
				task.delay(2.6, function()
					if my == session then
						gel()
					end
				end)
			end
		)
	end
end

-- ------------------------------------------------------------------ PCR (timing game)
local function pcr()
	clear()
	local my = session
	header.Text = "🧬 تفاعل البوليميراز | PCR Thermocycler (محاكاة)"
	local data = labFn:InvokeServer("pcr")
	if my ~= session or not data then
		return
	end
	setRP(data.research)
	local stepLabel = text(body, "", UDim2.fromScale(0, 0), UDim2.fromScale(1, 0.16), INK, true)
	local bar = Instance.new("Frame")
	bar.Position = UDim2.fromScale(0.04, 0.2)
	bar.Size = UDim2.fromScale(0.92, 0.16)
	bar.BackgroundColor3 = Color3.fromRGB(225, 230, 235)
	bar.Parent = body
	corner(bar, 0.2)
	local zone = Instance.new("Frame")
	zone.BackgroundColor3 = Color3.fromRGB(90, 200, 120)
	zone.BackgroundTransparency = 0.2
	zone.Parent = bar
	local needle = Instance.new("Frame")
	needle.Size = UDim2.fromScale(0.012, 1.3)
	needle.AnchorPoint = Vector2.new(0.5, 0.5)
	needle.BackgroundColor3 = Color3.fromRGB(200, 40, 40)
	needle.Parent = bar
	local tempLabel =
		text(body, "", UDim2.fromScale(0, 0.38), UDim2.fromScale(1, 0.12), Color3.fromRGB(200, 40, 40), true)
	local result = text(body, "", UDim2.fromScale(0, 0.86), UDim2.fromScale(1, 0.12), GREEN, true)
	local LO, HI = 40, 100
	local stepIndex, cycle, temp, t0 = 1, 1, 40, os.clock()
	local function showStep()
		local st = LabData.PCR_STEPS[stepIndex]
		stepLabel.Text = ("الدورة %d/%d • %s (%d–%d °م)"):format(
			cycle,
			LabData.PCR_CYCLES,
			st.name,
			st.lo,
			st.hi
		)
		zone.Position = UDim2.fromScale((st.lo - LO) / (HI - LO), 0)
		zone.Size = UDim2.fromScale((st.hi - st.lo) / (HI - LO), 1)
	end
	showStep()
	local conn = RunService.RenderStepped:Connect(function()
		if my ~= session then
			return
		end
		-- the block heats and cools continuously (about 3.4 s per sweep)
		temp = LO + (HI - LO) * (0.5 - 0.5 * math.cos((os.clock() - t0) * 1.85))
		needle.Position = UDim2.fromScale((temp - LO) / (HI - LO), 0.5)
		tempLabel.Text = ("🌡️ %d °م"):format(math.floor(temp + 0.5))
	end)
	local done = false
	button(
		body,
		"اضغط الحين! ⏺",
		UDim2.fromScale(0.25, 0.54),
		UDim2.fromScale(0.5, 0.24),
		Color3.fromRGB(46, 140, 90),
		function()
			if done or my ~= session then
				return
			end
			local st = LabData.PCR_STEPS[stepIndex]
			if temp >= st.lo and temp <= st.hi then
				play("click")
				stepIndex += 1
				if stepIndex > #LabData.PCR_STEPS then
					stepIndex = 1
					cycle += 1
				end
				if cycle > LabData.PCR_CYCLES then
					done = true
					conn:Disconnect()
					local r = labFn:InvokeServer("answer", data.token, true)
					if my == session then
						result.Text = r
								and r.ok
								and ("✅ تضاعف الـ DNA 8 مرات (2³)! +%d نقطة"):format(r.gained or 0)
							or "⏳ أسرع من اللازم، جرّب مرة ثانية"
						setRP(r and r.research)
						play(r and r.ok and "collect" or "wrong")
					end
					return
				end
				result.Text = "👍"
				showStep()
			else
				play("wrong")
				result.Text = "مو الحين! راقب المدى الأخضر"
			end
		end
	)
	-- stop the sweep when the panel changes
	task.spawn(function()
		while my == session do
			task.wait(0.5)
		end
		conn:Disconnect()
	end)
end

-- ------------------------------------------------------------------ computer: projects
local function computer()
	clear()
	local my = session
	header.Text = "💻 مشاريع المختبر"
	local data = labFn:InvokeServer("projects")
	if my ~= session or not data then
		return
	end
	setRP(data.research)
	for i, u in ipairs(data.list) do
		local y = (i - 1) * 0.25
		text(body, u.ar .. "\n" .. u.desc, UDim2.fromScale(0, y), UDim2.fromScale(0.62, 0.22), INK, true)
		if u.owned then
			text(body, "✅ مفعّل", UDim2.fromScale(0.66, y + 0.03), UDim2.fromScale(0.34, 0.16), GREEN, true)
		else
			button(
				body,
				("طوّر (%d 🧪)"):format(u.cost),
				UDim2.fromScale(0.66, y + 0.02),
				UDim2.fromScale(0.34, 0.18),
				Color3.fromRGB(60, 110, 190),
				function()
					local r = labFn:InvokeServer("buy", u.id)
					if r and r.ok then
						play("purchase")
					else
						play("wrong")
					end
					if my == session then
						computer()
					end
				end
			)
		end
	end
end

-- ------------------------------------------------------------------ batch picker
local function batch()
	clear()
	local my = session
	header.Text = "🎓 اختار دفعتك"
	local data = labFn:InvokeServer("batches")
	if my ~= session or not data then
		return
	end
	setRP()
	local n = #data.list + 1
	for i, b in ipairs(data.list) do
		local mark = data.current == b.id and "✅ " or ""
		button(
			body,
			mark .. b.ar,
			UDim2.fromScale(0.1, (i - 1) / n),
			UDim2.fromScale(0.8, 0.8 / n),
			Color3.fromRGB(b.color[1], b.color[2], b.color[3]),
			function()
				labFn:InvokeServer("setBatch", b.id)
				if my == session then
					batch()
				end
			end
		)
	end
	button(
		body,
		(data.current == nil and "✅ " or "") .. "بدون دفعة",
		UDim2.fromScale(0.1, (n - 1) / n),
		UDim2.fromScale(0.8, 0.8 / n),
		Color3.fromRGB(110, 110, 120),
		function()
			labFn:InvokeServer("setBatch", nil)
			if my == session then
				batch()
			end
		end
	)
end

-- ------------------------------------------------------------------ v53: Gram Staining as a real procedure
-- Pick each reagent from the rack yourself (a wrong pick explains why and lets you try again), time the decolouriser
-- (the step that decides the result), add the counterstain, then read the slide under the microscope and identify it.
-- The server decides what the slide looks like from the cell wall AND your timing (gramView), and grades the answer.
local VIOLET, PINKC = Color3.fromRGB(110, 50, 180), Color3.fromRGB(226, 90, 140)
local REAGENT_COLOR = {
	cv = Color3.fromRGB(120, 50, 190),
	iodine = Color3.fromRGB(150, 90, 30),
	alcohol = Color3.fromRGB(90, 140, 200),
	safranin = Color3.fromRGB(210, 60, 90),
}

local function drawCells(view, cocci, color)
	for _, c in ipairs(view:GetChildren()) do
		if c:IsA("Frame") then
			c:Destroy()
		end
	end
	local rnd = Random.new(7)
	for _ = 1, cocci and 5 or 9 do
		local cx, cy = rnd:NextNumber(0.18, 0.82), rnd:NextNumber(0.18, 0.82)
		for _ = 1, cocci and 5 or 1 do
			local cell = Instance.new("Frame")
			cell.AnchorPoint = Vector2.new(0.5, 0.5)
			cell.BackgroundColor3 = color
			cell.BorderSizePixel = 0
			if cocci then -- grape-like clusters of round cells
				cell.Size = UDim2.fromScale(0.07, 0.07)
				cell.Position = UDim2.fromScale(cx + rnd:NextNumber(-0.05, 0.05), cy + rnd:NextNumber(-0.05, 0.05))
				corner(cell, 1)
			else -- short rods
				cell.Size = UDim2.fromScale(0.16, 0.055)
				cell.Position = UDim2.fromScale(cx, cy)
				cell.Rotation = rnd:NextNumber(0, 180)
				corner(cell, 1)
			end
			cell.Parent = view
		end
	end
end

local function gram()
	clear()
	local my = session
	header.Text = "🧪 صبغة جرام | Gram Staining"
	local data = labFn:InvokeServer("gram")
	if my ~= session or not data then
		return
	end
	setRP(data.research)
	text(
		body,
		("العيّنة: %s\n%s"):format(data.name, data.shape),
		UDim2.fromScale(0, 0),
		UDim2.fromScale(0.62, 0.16),
		INK,
		true
	)
	-- the slide (left) and the microscope view (right)
	local slide = Instance.new("Frame")
	slide.Position = UDim2.fromScale(0, 0.18)
	slide.Size = UDim2.fromScale(0.6, 0.2)
	slide.BackgroundColor3 = Color3.fromRGB(232, 236, 240)
	slide.Parent = body
	corner(slide, 0.15)
	local note = text(
		slide,
		"🔬 لطخة بكتيريا مثبتة بالحرارة على الشريحة. اختار الكاشف الأول من الرف 👇",
		UDim2.fromScale(0.03, 0.06),
		UDim2.fromScale(0.94, 0.88),
		INK,
		true
	)
	local view = Instance.new("Frame")
	view.Position = UDim2.fromScale(0.66, 0.0)
	view.Size = UDim2.fromScale(0.3, 0.38)
	view.BackgroundColor3 = Color3.fromRGB(250, 246, 236)
	view.Parent = body
	corner(view, 1)
	local viewAspect = Instance.new("UIAspectRatioConstraint")
	viewAspect.Parent = view
	local viewNote = text(view, "🔬", UDim2.fromScale(0.3, 0.3), UDim2.fromScale(0.4, 0.4), INK, true)

	local result = text(body, "", UDim2.fromScale(0, 0.86), UDim2.fromScale(1, 0.14), GREEN, true)
	local rack = Instance.new("Frame")
	rack.Position = UDim2.fromScale(0, 0.42)
	rack.Size = UDim2.fromScale(1, 0.2)
	rack.BackgroundTransparency = 1
	rack.Parent = body
	local stage = Instance.new("Frame") -- decolouriser timer / identification buttons live here
	stage.Position = UDim2.fromScale(0, 0.64)
	stage.Size = UDim2.fromScale(1, 0.2)
	stage.BackgroundTransparency = 1
	stage.Parent = body

	local order = table.clone(LabData.GRAM_STEPS)
	local shuffled = table.clone(order)
	for i = #shuffled, 2, -1 do
		local j = math.random(1, i)
		shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
	end
	local stepIdx = 1
	local busy = false
	local SLIDE_AFTER = { cv = VIOLET, iodine = Color3.fromRGB(80, 30, 140) }

	local function identify()
		for _, c in ipairs(stage:GetChildren()) do
			c:Destroy()
		end
		local answered = false
		for i, k in ipairs({ "pos", "neg" }) do
			local idBtn = button(
				stage,
				LabData.GRAM_ANSWERS[k],
				UDim2.fromScale((i - 1) * 0.52, 0.05),
				UDim2.fromScale(0.48, 0.9),
				k == "pos" and VIOLET or PINKC,
				function()
					if answered or my ~= session then
						return
					end
					answered = true
					local r = labFn:InvokeServer("answer", data.token, k)
					if my ~= session then
						return
					end
					local msg
					if r and r.quality and r.quality ~= "ok" then
						-- the identification may even be right, but a badly decolourised slide proves nothing
						play("wrong")
						msg = "🧪 النتيجة غير موثوقة\n"
							.. LabData.GRAM_QUALITY[r.quality]
							.. " • أعد التجربة واضبط وقت الكحول"
					else
						msg = feedback(r, r and r.answer and LabData.GRAM_ANSWERS[r.answer])
					end
					result.Text = msg
					setRP(r and r.research)
					task.delay(3.5, function()
						if my == session then
							gram()
						end
					end)
				end
			)
			idBtn.Name = "Answer_" .. k
		end
	end

	local function decolourise()
		-- a timer bar: the green band is the right time to rinse with water
		busy = true
		local D = LabData.GRAM_DECOLOR
		local track = Instance.new("Frame")
		track.Position = UDim2.fromScale(0, 0.05)
		track.Size = UDim2.fromScale(0.62, 0.4)
		track.BackgroundColor3 = Color3.fromRGB(60, 64, 72)
		track.Parent = stage
		corner(track, 0.4)
		local window = Instance.new("Frame")
		window.Position = UDim2.fromScale(D.min / D.bar, 0)
		window.Size = UDim2.fromScale((D.max - D.min) / D.bar, 1)
		window.BackgroundColor3 = Color3.fromRGB(70, 190, 110)
		window.BorderSizePixel = 0
		window.Parent = track
		local needle = Instance.new("Frame")
		needle.Size = UDim2.new(0, 4, 1.3, 0)
		needle.AnchorPoint = Vector2.new(0.5, 0.5)
		needle.Position = UDim2.fromScale(0, 0.5)
		needle.BackgroundColor3 = Color3.new(1, 1, 1)
		needle.Parent = track
		text(
			stage,
			"💧 الكحول ينزل على الشريحة… اغسل بالماء لما المؤشر يكون بالأخضر",
			UDim2.fromScale(0, 0.5),
			UDim2.fromScale(0.62, 0.45),
			INK,
			true
		)
		local t0 = os.clock()
		local stopped = false
		local function rinse()
			if stopped or my ~= session then
				return
			end
			stopped = true
			local secs = os.clock() - t0
			play("click")
			for _, c in ipairs(stage:GetChildren()) do
				c:Destroy()
			end
			local v = labFn:InvokeServer("gramView", data.token, secs)
			if my ~= session or not v then
				return
			end
			data.view = v
			note.Text = ("🚿 غسلت بعد %.1f ثانية. باقي الخطوة الأخيرة: الصبغة المقابلة"):format(
				secs
			)
			busy = false
		end
		button(
			stage,
			"🚿 اغسل بالماء الحين!",
			UDim2.fromScale(0.66, 0.05),
			UDim2.fromScale(0.34, 0.9),
			Color3.fromRGB(40, 120, 190),
			rinse
		).Name =
			"RinseBtn"
		task.spawn(function()
			while not stopped and my == session do
				local secs = os.clock() - t0
				needle.Position = UDim2.fromScale(math.clamp(secs / D.bar, 0, 1), 0.5)
				-- run-off: the purple slowly washes out of the smear
				slide.BackgroundColor3 = Color3.fromRGB(80, 30, 140)
					:Lerp(Color3.fromRGB(190, 170, 220), math.clamp(secs / D.bar, 0, 1))
				if secs >= D.bar then
					rinse()
					break
				end
				task.wait()
			end
		end)
	end

	local function pick(st)
		if busy or my ~= session or stepIdx > #order then
			return
		end
		local want = order[stepIdx]
		if st.id ~= want.id then
			play("wrong")
			result.TextColor3 = Color3.fromRGB(170, 60, 40)
			result.Text = ("❌ مو هذا الحين. %s\n(هذا الكاشف: %s)"):format(
				stepIdx == 1 and "أول شي الصبغة الأساسية اللي تلوّن كل الخلايا"
					or "فكّر شنو لازم يصير قبل",
				st.note
			)
			return
		end
		play("click")
		result.TextColor3 = GREEN
		result.Text = ""
		stepIdx += 1
		note.Text = st.note
		if st.id == "alcohol" then
			decolourise()
		elseif st.id == "safranin" then
			-- the counterstain: then the microscope shows what the timing really produced
			local v = data.view
			if not v then
				return
			end
			TweenService
				:Create(slide, TweenInfo.new(0.4), { BackgroundColor3 = v.color == "violet" and VIOLET or PINKC })
				:Play()
			note.Text = st.note .. "\n🔬 شوف الخلايا بالمجهر وحدد نوعها"
			viewNote.Visible = false
			drawCells(view, data.cocci, v.color == "violet" and VIOLET or PINKC)
			rack.Visible = false
			identify()
		else
			TweenService:Create(slide, TweenInfo.new(0.4), { BackgroundColor3 = SLIDE_AFTER[st.id] }):Play()
			note.TextColor3 = Color3.new(1, 1, 1)
		end
	end

	for i, st in ipairs(shuffled) do
		-- the rack shows the name only (no step number), Arabic and English on separate lines (mixed text reorders)
		local name = st.ar:gsub("^%S+%s", "")
		local ar, en = name:match("^(.-)%s*%((.+)%)$")
		local b = button(
			rack,
			ar and (ar .. "\n" .. en) or name,
			UDim2.fromScale((i - 1) * 0.25 + 0.005, 0),
			UDim2.fromScale(0.24, 1),
			REAGENT_COLOR[st.id] or INK,
			function()
				pick(st)
			end
		)
		b.Name = "Reagent_" .. st.id
		b.TextWrapped = true
	end
end

local MODES = { microscope = microscope, gel = gel, pcr = pcr, gram = gram, computer = computer, batch = batch }
openEvent.OnClientEvent:Connect(function(kind)
	local fn = MODES[kind]
	if fn then
		gui.Enabled = true
		fn()
	end
end)

-- ------------------------------------------------------------------ "field microscope" upgrade: mark nearby unfound collectibles
-- (the Collect| boxes are invisible, so a small always-on-top marker is used instead of an outline)
local found = {}
task.spawn(function()
	local shop = ReplicatedStorage:WaitForChild("Shop", 30)
	task.wait(4)
	local snap = shop and shop:InvokeServer("get")
	for id in pairs(snap and snap.found or {}) do
		found[id] = true
	end
end)
local notify = ReplicatedStorage:WaitForChild("Notify", 30)
if notify then
	notify.OnClientEvent:Connect(function(_, kind, id)
		if kind == "collect" and id then
			found[id] = true
		end
	end)
end

local markers = {}
task.spawn(function()
	local mapFolder = workspace:WaitForChild("Map")
	local collectibles = {}
	for _, d in ipairs(mapFolder:GetDescendants()) do
		local id = d:IsA("BasePart") and d.Name:match("^Collect|%a+|(.+)$")
		if id then
			table.insert(collectibles, { part = d, id = id })
		end
	end
	while true do
		task.wait(1)
		local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
		local on = player:GetAttribute("Upg_scope") == true and root ~= nil
		for _, c in ipairs(collectibles) do
			local near = on and not found[c.id] and (c.part.Position - root.Position).Magnitude < 45
			if near and not markers[c.part] then
				local bb = Instance.new("BillboardGui")
				bb.Size = UDim2.fromOffset(44, 44)
				bb.AlwaysOnTop = true
				bb.LightInfluence = 0
				local t = Instance.new("TextLabel")
				t.Size = UDim2.fromScale(1, 1)
				t.BackgroundTransparency = 1
				t.TextScaled = true
				t.Text = "✨"
				t.Parent = bb
				bb.Adornee = c.part
				bb.Parent = player.PlayerGui
				markers[c.part] = bb
			elseif not near and markers[c.part] then
				markers[c.part]:Destroy()
				markers[c.part] = nil
			end
		end
	end
end)
