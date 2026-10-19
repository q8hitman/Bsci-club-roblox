-- v41 Light Microscopy lab (opened from LabStation|lightmicro). An interactive, simplified simulation:
-- objectives 4x/10x/40x/100x oil on a nosepiece that turns one step at a time, coarse + fine focus, light, stage
-- movement, immersion oil, and a lab notebook graded by the server (Lab.server lmStart/lmSubmit).
-- The procedure is enforced the way a lab teaches it: find the sample at 4x, focus, centre, then go up; coarse focus is
-- blocked at 40x/100x; 100x needs oil; never swing back to 40x through oil. Every mistake is explained.
-- Drawings are representative (not photos); proportions between cells are kept, sizes are enlarged for readability.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local player = Players.LocalPlayer
local Micro = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("MicroscopyData"))
local openEvent = ReplicatedStorage:WaitForChild("LabOpen", 30)
local labFn = ReplicatedStorage:WaitForChild("Lab", 30)
if not (openEvent and labFn) then
	return
end

local OBJ = Micro.OBJECTIVES
local REGION = { blood = 360, elodea = 380, cheek = 360, staph = 260 }

-- ------------------------------------------------------------------ state
local st = {}
local function newSession(sample)
	st.sample = sample
	st.obj = 1
	st.z0 = 35 + math.random() * 30
	st.z = st.z0 + (math.random() < 0.5 and -1 or 1) * (18 + math.random() * 15)
	st.off = { 0, (math.random() - 0.5) * 3, (math.random() - 0.5) * 2.4, (math.random() - 0.5) * 1.2 }
	st.light = 2
	local a = math.random() * 2 * math.pi
	st.cx, st.cy = math.cos(a) * 640, math.sin(a) * 640 -- the sample starts off-centre: find it at 4x
	st.oil = false
	st.maxMag, st.sawOil = 0, false
	st.picks = {}
	st.steps = {}
	st.token = nil
	task.spawn(function()
		local r = labFn:InvokeServer("lmStart", sample.id)
		st.token = r and r.token
	end)
end

local function sharpness()
	local o = OBJ[st.obj]
	local s = math.clamp(1 - math.abs(st.z - (st.z0 + st.off[st.obj])) / o.dof, 0, 1)
	if o.oil and not st.oil then
		s = math.min(s, 0.3)
	end
	return s
end

local function lightState()
	local r = OBJ[st.obj].light
	if st.light < r[1] then
		return "dark", r[1] - st.light
	elseif st.light > r[2] then
		return "bright", st.light - r[2]
	end
	return "ok", 0
end

local function sampleInView(frac)
	return math.sqrt(st.cx ^ 2 + st.cy ^ 2) < (REGION[st.sample.id] or 300) * (frac or 0.85)
end

-- ------------------------------------------------------------------ UI helpers
local gui = Instance.new("ScreenGui")
gui.Name = "LightMicroscope"
gui.ResetOnSpawn = false
gui.Enabled = false
gui.DisplayOrder = 35
gui.Parent = player:WaitForChild("PlayerGui")

local function corner(o, r)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(r or 0.15, 0)
	c.Parent = o
end
local function label(parent, text, pos, size, color, font)
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.Position, t.Size = pos, size
	t.Text = text
	t.TextScaled = true
	t.TextWrapped = true
	t.TextColor3 = color or Color3.new(1, 1, 1)
	t.Font = font or Enum.Font.GothamBold
	t.Parent = parent
	return t
end
local function button(parent, text, pos, size, color, fn)
	local b = Instance.new("TextButton")
	b.Position, b.Size = pos, size
	b.BackgroundColor3 = color
	b.Text = text
	b.TextScaled = true
	b.TextWrapped = true
	b.TextColor3 = Color3.new(1, 1, 1)
	b.Font = Enum.Font.GothamBold
	b.AutoButtonColor = true
	b.Parent = parent
	corner(b, 0.2)
	b.Activated:Connect(fn)
	return b
end

local panel = Instance.new("Frame")
panel.AnchorPoint = Vector2.new(0.5, 0.5)
panel.Position = UDim2.fromScale(0.5, 0.5)
panel.Size = UDim2.fromScale(0.97, 0.94)
panel.BackgroundColor3 = Color3.fromRGB(20, 28, 34)
panel.Parent = gui
corner(panel, 0.02)

label(panel, "🔬 مختبر المجهر الضوئي", UDim2.fromScale(0.3, 0.01), UDim2.fromScale(0.4, 0.06))
label(
	panel,
	"محاكاة تعليمية مبسّطة، مو إجراء مخبري حقيقي",
	UDim2.fromScale(0.3, 0.065),
	UDim2.fromScale(0.4, 0.035),
	Color3.fromRGB(170, 200, 190),
	Enum.Font.Gotham
)
button(panel, "X", UDim2.fromScale(0.955, 0.012), UDim2.fromScale(0.035, 0.06), Color3.fromRGB(150, 50, 50), function()
	gui.Enabled = false
end)

local mode = "practice"
local modeBtns = {}
local tab = "lab"
local tabBtns = {}
local render -- forward

modeBtns.practice = button(
	panel,
	"🎓 تدريب",
	UDim2.fromScale(0.01, 0.015),
	UDim2.fromScale(0.09, 0.055),
	Color3.fromRGB(40, 120, 90),
	function()
		mode = "practice"
		render()
	end
)
modeBtns.eval = button(
	panel,
	"📝 تقييم",
	UDim2.fromScale(0.105, 0.015),
	UDim2.fromScale(0.09, 0.055),
	Color3.fromRGB(60, 70, 90),
	function()
		mode = "eval"
		render()
	end
)
tabBtns.lab = button(
	panel,
	"التجربة",
	UDim2.fromScale(0.75, 0.015),
	UDim2.fromScale(0.09, 0.055),
	Color3.fromRGB(40, 120, 90),
	function()
		tab = "lab"
		render()
	end
)
tabBtns.parts = button(
	panel,
	"أجزاء المجهر",
	UDim2.fromScale(0.845, 0.015),
	UDim2.fromScale(0.1, 0.055),
	Color3.fromRGB(60, 70, 90),
	function()
		tab = "parts"
		render()
	end
)

local labPage = Instance.new("Frame")
labPage.BackgroundTransparency = 1
labPage.Position, labPage.Size = UDim2.fromScale(0, 0.11), UDim2.fromScale(1, 0.89)
labPage.Parent = panel
local partsPage = Instance.new("ScrollingFrame")
partsPage.BackgroundTransparency = 1
partsPage.Position, partsPage.Size = UDim2.fromScale(0.05, 0.12), UDim2.fromScale(0.9, 0.85)
partsPage.CanvasSize = UDim2.fromScale(0, 1.6)
partsPage.ScrollBarThickness = 8
partsPage.Visible = false
partsPage.Parent = panel
for i, part in ipairs(Micro.PARTS) do
	local y = (i - 1) * 0.12
	local row = Instance.new("Frame")
	row.Position, row.Size = UDim2.fromScale(0, y), UDim2.fromScale(1, 0.11)
	row.BackgroundColor3 = Color3.fromRGB(30, 44, 52)
	row.Parent = partsPage
	corner(row, 0.1)
	label(row, part.ar, UDim2.fromScale(0.62, 0.05), UDim2.fromScale(0.36, 0.5))
	label(
		row,
		part.en,
		UDim2.fromScale(0.62, 0.55),
		UDim2.fromScale(0.36, 0.4),
		Color3.fromRGB(170, 200, 190),
		Enum.Font.Gotham
	)
	label(
		row,
		part.fn,
		UDim2.fromScale(0.02, 0.1),
		UDim2.fromScale(0.58, 0.8),
		Color3.fromRGB(230, 236, 240),
		Enum.Font.Gotham
	)
end

-- sample picker
local sampleBtns = {}
for i, sm in ipairs(Micro.SAMPLES) do
	sampleBtns[sm.id] = button(
		labPage,
		sm.ar,
		UDim2.fromScale(0.27 + (i - 1) * 0.115, 0),
		UDim2.fromScale(0.11, 0.065),
		Color3.fromRGB(60, 70, 90),
		function()
			newSession(sm)
			render()
		end
	)
end

-- the view: a circular field (CanvasGroup clips to its rounded corner)
local viewHolder = Instance.new("Frame")
viewHolder.BackgroundTransparency = 1
viewHolder.Position, viewHolder.Size = UDim2.fromScale(0.27, 0.08), UDim2.fromScale(0.45, 0.8)
viewHolder.Parent = labPage
local view = Instance.new("CanvasGroup")
view.AnchorPoint = Vector2.new(0.5, 0.5)
view.Position = UDim2.fromScale(0.5, 0.5)
view.Size = UDim2.fromScale(1, 1)
view.BackgroundColor3 = Color3.fromRGB(236, 232, 220)
view.ClipsDescendants = true
view.Parent = viewHolder
corner(view, 0.5)
local aspect = Instance.new("UIAspectRatioConstraint")
aspect.AspectRatio = 1
aspect.Parent = view
local ring = Instance.new("UIStroke")
ring.Thickness = 6
ring.Color = Color3.fromRGB(10, 10, 12)
ring.Parent = view
local layer = Instance.new("Frame")
layer.BackgroundTransparency = 1
layer.Size = UDim2.fromScale(1, 1)
layer.Parent = view
local shade = Instance.new("Frame") -- light too low (black) / too high (white)
shade.Size = UDim2.fromScale(1, 1)
shade.BorderSizePixel = 0
shade.ZIndex = 5
shade.Parent = view
local status =
	label(labPage, "", UDim2.fromScale(0.27, 0.885), UDim2.fromScale(0.45, 0.05), Color3.fromRGB(220, 230, 235))
local message =
	label(labPage, "", UDim2.fromScale(0.02, 0.94), UDim2.fromScale(0.96, 0.055), Color3.fromRGB(255, 220, 120))

local function say(text)
	message.Text = text
end

-- pooled frames for the cells
local pool, used = {}, 0
local function dot(x, y, d, color, transp, shape)
	used += 1
	local f = pool[used]
	if not f then
		f = Instance.new("Frame")
		f.AnchorPoint = Vector2.new(0.5, 0.5)
		f.BorderSizePixel = 0
		local c = Instance.new("UICorner")
		c.Name = "C"
		c.Parent = f
		f.Parent = layer
		pool[used] = f
	end
	local o = OBJ[st.obj]
	-- the eyepiece field is round: anything whose centre is outside it is not drawn (CanvasGroup clipping alone was
	-- not reliable; seen in a Studio capture)
	local w = type(d) == "table" and d[1] or d
	local h = type(d) == "table" and d[2] or d
	local rx, ry = (x - st.cx) / o.fov, (y - st.cy) / o.fov
	f.Visible = math.sqrt(rx * rx + ry * ry) < 0.5 + 0.3 * math.max(w, h) / o.fov -- big patches may straddle the edge
	f.Position = UDim2.fromScale(0.5 + (x - st.cx) / o.fov, 0.5 + (y - st.cy) / o.fov)
	f.Size = UDim2.fromScale(w / o.fov, h / o.fov)
	f.BackgroundColor3 = color
	f.BackgroundTransparency = transp
	f.C.CornerRadius = UDim.new(shape == "rect" and 0.18 or 0.5, 0)
	f.Rotation = 0
	return f
end

local function hash(i, j, k)
	local n = math.sin(i * 127.1 + j * 311.7 + (k or 0) * 74.7) * 43758.5453
	return n - math.floor(n)
end

local function drawSpecimen(s)
	local id = st.sample.id
	local o = OBJ[st.obj]
	local R = REGION[id] or 300
	local blur = 1 - s
	local inflate = 1 + blur * 0.7
	local tr = 0.15 + blur * 0.6
	local bg = view.BackgroundColor3
	local function col(c)
		return c:Lerp(bg, blur * 0.55)
	end
	if o.fov >= 800 then
		-- low power: the smear is a patch with a speckled texture
		local base = ({
			blood = Color3.fromRGB(220, 150, 160),
			elodea = Color3.fromRGB(140, 190, 110),
			cheek = Color3.fromRGB(170, 190, 225),
			staph = Color3.fromRGB(190, 160, 210),
		})[id]
		dot(0, 0, R * 2 * inflate, col(base), 0.35 + blur * 0.4)
		for k = 1, 90 do
			local a, r = hash(k, 1, 3) * 2 * math.pi, math.sqrt(hash(k, 2, 3)) * R
			dot(
				math.cos(a) * r,
				math.sin(a) * r,
				(o.fov / 120) * inflate,
				col(base:Lerp(Color3.new(0.2, 0.1, 0.25), 0.4)),
				tr
			)
		end
		return
	end
	local x0, x1 = st.cx - o.fov / 2, st.cx + o.fov / 2
	local y0, y1 = st.cy - o.fov / 2, st.cy + o.fov / 2
	if id == "blood" then
		local g = 9
		for i = math.floor(x0 / g), math.ceil(x1 / g) do
			for j = math.floor(y0 / g), math.ceil(y1 / g) do
				local x, y = i * g + (hash(i, j) - 0.5) * 4, j * g + (hash(j, i) - 0.5) * 4
				if x * x + y * y < R * R and used < 700 then
					local r = hash(i, j, 5)
					if r < 0.025 then -- white blood cell: bigger, purple lobed nucleus
						dot(x, y, 11 * inflate, col(Color3.fromRGB(226, 214, 232)), tr)
						for q = 0, 2 do
							dot(
								x - 2 + q * 2,
								y + (q % 2) * 1.6 - 0.8,
								3.4 * inflate,
								col(Color3.fromRGB(100, 50, 140)),
								tr
							)
						end
					elseif r < 0.1 then -- platelet
						dot(x, y, 2.2 * inflate, col(Color3.fromRGB(150, 90, 170)), tr)
					else -- red blood cell: biconcave disc, pale centre, NO nucleus
						dot(x, y, 6.5 * inflate, col(Color3.fromRGB(222, 112, 118)), tr)
						if st.obj >= 3 and s > 0.5 then
							dot(x, y, 2.6, col(Color3.fromRGB(240, 175, 175)), tr)
						end
					end
				end
			end
		end
	elseif id == "elodea" then
		local gx, gy = 72, 30
		for i = math.floor(x0 / gx), math.ceil(x1 / gx) do
			for j = math.floor(y0 / gy), math.ceil(y1 / gy) do
				local x, y = i * gx + (j % 2) * gx / 2, j * gy
				if x * x + y * y < R * R and used < 700 then
					local f = dot(x, y, { 68 * inflate, 26 * inflate }, col(Color3.fromRGB(176, 214, 150)), tr, "rect")
					f.BackgroundColor3 = col(Color3.fromRGB(176, 214, 150))
					if st.obj >= 3 then
						for q = 1, 8 do
							local px = x + (hash(i, j, q) - 0.5) * 58
							local py = y + (hash(j, i, q) - 0.5) * 18
							dot(px, py, 4.2 * inflate, col(Color3.fromRGB(46, 140, 60)), tr)
						end
					end
				end
			end
		end
		-- cell walls: thin dark lines between cells come from the gaps (the green fill stops short of the grid)
	elseif id == "cheek" then
		local g = 58
		for i = math.floor(x0 / g), math.ceil(x1 / g) do
			for j = math.floor(y0 / g), math.ceil(y1 / g) do
				if hash(i, j, 9) < 0.7 then
					local x, y = i * g + (hash(i, j) - 0.5) * 20, j * g + (hash(j, i) - 0.5) * 20
					if x * x + y * y < R * R and used < 700 then
						local w = 42 + hash(i, j, 2) * 14
						local f = dot(
							x,
							y,
							{ w * inflate, (w * 0.8) * inflate },
							col(Color3.fromRGB(196, 210, 236)),
							tr + 0.1,
							"rect"
						)
						f.Rotation = hash(i, j, 4) * 90
						dot(x + (hash(i, j, 6) - 0.5) * 8, y, 7.5 * inflate, col(Color3.fromRGB(56, 76, 170)), tr)
					end
				end
			end
		end
	elseif id == "staph" then
		local g = 11
		for i = math.floor(x0 / g), math.ceil(x1 / g) do
			for j = math.floor(y0 / g), math.ceil(y1 / g) do
				if hash(i, j, 1) < 0.55 then
					local x, y = i * g + (hash(i, j) - 0.5) * 6, j * g + (hash(j, i) - 0.5) * 6
					if x * x + y * y < R * R and used < 700 then
						if st.obj == 4 then -- grape-like clusters of tiny purple cocci
							for q = 1, 6 do
								local a = q * 1.05 + hash(i, j, q)
								dot(
									x + math.cos(a) * 1.6,
									y + math.sin(a) * 1.6,
									1.5 * inflate,
									col(Color3.fromRGB(104, 56, 160)),
									tr
								)
							end
						else
							dot(x, y, 2.4 * inflate, col(Color3.fromRGB(150, 110, 190)), tr + 0.2)
						end
					end
				end
			end
		end
	end
end

-- ------------------------------------------------------------------ controls
local ctrl = Instance.new("Frame")
ctrl.BackgroundTransparency = 1
ctrl.Position, ctrl.Size = UDim2.fromScale(0.01, 0.08), UDim2.fromScale(0.25, 0.85)
ctrl.Parent = labPage
local objBtns = {}

local function setObjective(k)
	local cur = st.obj
	if math.abs(k - cur) ~= 1 then
		say(
			"🔄 القرص الدوّار يلف خطوة خطوة: بدّل للعدسة اللي جنب الحالية"
		)
		return
	end
	if k > cur then
		if sharpness() < 0.6 or not sampleInView(0.85) then
			say(
				"🎯 قبل ما تكبّر: لازم العيّنة بالوسط والصورة واضحة بالتكبير الحالي"
			)
			return
		end
	elseif cur == 4 and st.oil then
		say(
			"❌ لا ترجع للـ40× والزيت على الشريحة، العدسة 40× بتتوسّخ بالزيت. نظّف الشريحة أول"
		)
		return
	end
	st.obj = k
	if OBJ[k].oil and not st.oil then
		say(
			"⚠️ العدسة 100× تحتاج نقطة زيت غمر، وبدونه الصورة تبقى مغبّشة"
		)
	else
		say(("التكبير الكلي الحين %d×"):format(Micro.OCULAR * OBJ[k].mag))
	end
	render()
end

label(ctrl, "العدسة الشيئية", UDim2.fromScale(0, 0), UDim2.fromScale(1, 0.06))
for k, o in ipairs(OBJ) do
	objBtns[k] = button(
		ctrl,
		o.oil and "100× زيت" or (o.mag .. "×"),
		UDim2.fromScale((k - 1) * 0.25, 0.065),
		UDim2.fromScale(0.235, 0.08),
		Color3.fromRGB(60, 70, 90),
		function()
			setObjective(k)
		end
	)
end

local function focus(delta, coarse)
	if coarse and st.obj >= 3 then
		say(
			"❌ لا تستخدم الضابط الكبير مع 40× أو 100×: العدسة قريبة من الشريحة وممكن تكسرها. استخدم الدقيق"
		)
		return
	end
	st.z += delta
	render()
end
label(ctrl, "الضابط الكبير", UDim2.fromScale(0, 0.17), UDim2.fromScale(0.48, 0.05))
button(ctrl, "▲", UDim2.fromScale(0, 0.225), UDim2.fromScale(0.23, 0.075), Color3.fromRGB(70, 90, 110), function()
	focus(4, true)
end)
button(ctrl, "▼", UDim2.fromScale(0.25, 0.225), UDim2.fromScale(0.23, 0.075), Color3.fromRGB(70, 90, 110), function()
	focus(-4, true)
end)
label(ctrl, "الضابط الدقيق", UDim2.fromScale(0.52, 0.17), UDim2.fromScale(0.48, 0.05))
button(ctrl, "▲", UDim2.fromScale(0.52, 0.225), UDim2.fromScale(0.23, 0.075), Color3.fromRGB(70, 110, 100), function()
	focus(0.4, false)
end)
button(ctrl, "▼", UDim2.fromScale(0.77, 0.225), UDim2.fromScale(0.23, 0.075), Color3.fromRGB(70, 110, 100), function()
	focus(-0.4, false)
end)

local lightLabel = label(ctrl, "", UDim2.fromScale(0, 0.32), UDim2.fromScale(1, 0.05))
button(
	ctrl,
	"− ضوء",
	UDim2.fromScale(0, 0.375),
	UDim2.fromScale(0.48, 0.075),
	Color3.fromRGB(90, 80, 50),
	function()
		st.light = math.max(0, st.light - 1)
		render()
	end
)
button(
	ctrl,
	"+ ضوء",
	UDim2.fromScale(0.52, 0.375),
	UDim2.fromScale(0.48, 0.075),
	Color3.fromRGB(130, 110, 50),
	function()
		st.light = math.min(10, st.light + 1)
		render()
	end
)

label(ctrl, "حرّك الشريحة", UDim2.fromScale(0, 0.47), UDim2.fromScale(1, 0.05))
local function move(dx, dy)
	local step = OBJ[st.obj].fov * 0.18
	st.cx, st.cy = st.cx + dx * step, st.cy + dy * step
	render()
end
button(ctrl, "▲", UDim2.fromScale(0.375, 0.525), UDim2.fromScale(0.25, 0.07), Color3.fromRGB(60, 70, 90), function()
	move(0, -1)
end)
button(ctrl, "◀", UDim2.fromScale(0.1, 0.6), UDim2.fromScale(0.25, 0.07), Color3.fromRGB(60, 70, 90), function()
	move(-1, 0)
end)
button(ctrl, "▶", UDim2.fromScale(0.65, 0.6), UDim2.fromScale(0.25, 0.07), Color3.fromRGB(60, 70, 90), function()
	move(1, 0)
end)
button(ctrl, "▼", UDim2.fromScale(0.375, 0.675), UDim2.fromScale(0.25, 0.07), Color3.fromRGB(60, 70, 90), function()
	move(0, 1)
end)

button(
	ctrl,
	"💧 نقطة زيت غمر",
	UDim2.fromScale(0, 0.78),
	UDim2.fromScale(0.6, 0.08),
	Color3.fromRGB(150, 120, 40),
	function()
		if st.obj < 4 then
			say("💧 الزيت بس مع العدسة 100×. كبّر لين 100× وبعدين حط الزيت")
			return
		end
		st.oil = true
		say("💧 حطيت زيت الغمر: الضوء ما يتشتت والصورة تصير أوضح بـ1000×")
		render()
	end
)
button(
	ctrl,
	"🧻 نظّف",
	UDim2.fromScale(0.64, 0.78),
	UDim2.fromScale(0.36, 0.08),
	Color3.fromRGB(90, 90, 100),
	function()
		if st.obj == 4 then
			say("رجّع العدسة لـ10× أو 4× قبل التنظيف")
			return
		end
		st.oil = false
		say("🧻 نظّفت الشريحة والعدسة")
		render()
	end
)

-- ------------------------------------------------------------------ notebook + guide (right)
local note = Instance.new("Frame")
note.BackgroundColor3 = Color3.fromRGB(240, 236, 222)
note.Position, note.Size = UDim2.fromScale(0.735, 0.08), UDim2.fromScale(0.255, 0.85)
note.Parent = labPage
corner(note, 0.04)
local noteTitle = label(
	note,
	"📒 دفتر المختبر",
	UDim2.fromScale(0.05, 0.01),
	UDim2.fromScale(0.9, 0.06),
	Color3.fromRGB(40, 40, 40)
)
local need = label(
	note,
	"",
	UDim2.fromScale(0.05, 0.07),
	UDim2.fromScale(0.9, 0.06),
	Color3.fromRGB(80, 60, 40),
	Enum.Font.Gotham
)
local list = Instance.new("Frame")
list.BackgroundTransparency = 1
list.Position, list.Size = UDim2.fromScale(0.04, 0.14), UDim2.fromScale(0.92, 0.42)
list.Parent = note
local guide = label(
	note,
	"",
	UDim2.fromScale(0.05, 0.57),
	UDim2.fromScale(0.9, 0.25),
	Color3.fromRGB(40, 70, 60),
	Enum.Font.Gotham
)
guide.TextXAlignment = Enum.TextXAlignment.Right
local result = label(
	note,
	"",
	UDim2.fromScale(0.05, 0.57),
	UDim2.fromScale(0.9, 0.25),
	Color3.fromRGB(40, 40, 40),
	Enum.Font.Gotham
)
result.Visible = false
local noteBtns = {}

local function buildNotes()
	for _, b in ipairs(noteBtns) do
		b:Destroy()
	end
	table.clear(noteBtns)
	result.Visible = false
	local n = #st.sample.notes
	for i, nt in ipairs(st.sample.notes) do
		local b = button(
			list,
			"⬜ " .. nt[1],
			UDim2.fromScale(0, (i - 1) / n),
			UDim2.fromScale(1, 0.9 / n),
			Color3.fromRGB(90, 96, 110),
			function()
				st.picks[i] = not st.picks[i] or nil
				render()
			end
		)
		noteBtns[i] = b
	end
end

button(
	note,
	"✍️ سجّل الملاحظات",
	UDim2.fromScale(0.1, 0.84),
	UDim2.fromScale(0.8, 0.09),
	Color3.fromRGB(24, 110, 76),
	function()
		if not st.token then
			say("لحظة… الجلسة تتجهز")
			return
		end
		local picks = {}
		for i in pairs(st.picks) do
			table.insert(picks, i)
		end
		local r = labFn:InvokeServer(
			"lmSubmit",
			st.token,
			{ picks = picks, maxMag = st.maxMag, oil = st.sawOil, eval = mode == "eval" }
		)
		if not r then
			return
		end
		local lines = {}
		if not r.sawIt then
			table.insert(
				lines,
				("👀 لازم تشوف العيّنة بوضوح بتكبير %d×%s"):format(
					Micro.OCULAR * st.sample.needMag,
					st.sample.needMag == 100 and " مع الزيت" or ""
				)
			)
		end
		for _, x in ipairs(r.results or {}) do
			if not x.right then
				table.insert(lines, "❌ " .. st.sample.notes[x.i][1] .. (x.why and (": " .. x.why) or ""))
			end
		end
		if r.ok then
			table.insert(
				lines,
				1,
				r.gained and r.gained > 0 and ("🎉 ممتاز! +%d 🧪"):format(r.gained)
					or "🎉 ممتاز! ملاحظاتك صحيحة"
			)
		end
		result.Text = table.concat(lines, "\n")
		result.Visible = true
		guide.Visible = false
		-- a new session token so the next try starts clean
		task.spawn(function()
			local s2 = labFn:InvokeServer("lmStart", st.sample.id)
			st.token = s2 and s2.token
		end)
	end
)

-- ------------------------------------------------------------------ render
render = function()
	partsPage.Visible = tab == "parts"
	labPage.Visible = tab == "lab"
	for k, b in pairs(modeBtns) do
		b.BackgroundColor3 = k == mode and Color3.fromRGB(40, 120, 90) or Color3.fromRGB(60, 70, 90)
	end
	for k, b in pairs(tabBtns) do
		b.BackgroundColor3 = k == tab and Color3.fromRGB(40, 120, 90) or Color3.fromRGB(60, 70, 90)
	end
	if not st.sample then
		return
	end
	for id, b in pairs(sampleBtns) do
		b.BackgroundColor3 = id == st.sample.id and Color3.fromRGB(40, 120, 90) or Color3.fromRGB(60, 70, 90)
	end
	for k, b in ipairs(objBtns) do
		b.BackgroundColor3 = k == st.obj and Color3.fromRGB(40, 120, 90) or Color3.fromRGB(60, 70, 90)
	end
	-- draw
	used = 0
	local s = sharpness()
	drawSpecimen(s)
	for i = used + 1, #pool do
		pool[i].Visible = false
	end
	local ls, amount = lightState()
	if ls == "dark" then
		shade.BackgroundColor3 = Color3.new(0, 0, 0)
		shade.BackgroundTransparency = math.max(0.05, 1 - amount * 0.22)
	elseif ls == "bright" then
		shade.BackgroundColor3 = Color3.new(1, 1, 1)
		shade.BackgroundTransparency = math.max(0.1, 1 - amount * 0.25)
	else
		shade.BackgroundTransparency = 1
	end
	lightLabel.Text = ("الضوء: %d / 10%s"):format(
		st.light,
		ls == "dark" and " (خافت)" or (ls == "bright" and " (قوي)" or " ✅")
	)
	local mag = Micro.OCULAR * OBJ[st.obj].mag
	status.Text = ("التكبير الكلي %d× • الوضوح %d%%%s"):format(
		mag,
		math.floor(s * 100),
		st.oil and " • 💧زيت" or ""
	)
	-- a good, centred, well-lit view at this power counts as "seen"
	if s >= 0.75 and ls == "ok" and sampleInView(0.7) then
		st.maxMag = math.max(st.maxMag, OBJ[st.obj].mag)
		if OBJ[st.obj].oil and st.oil then
			st.sawOil = true
		end
		st.steps.seen = true
	end
	if st.obj == 1 and s >= 0.75 and sampleInView(0.85) then
		st.steps.found = true
	end
	if ls == "ok" then
		st.steps.light = true
	end
	-- notebook
	need.Text = ("%s • المطلوب: %d×"):format(st.sample.ar, Micro.OCULAR * st.sample.needMag)
	for i, b in ipairs(noteBtns) do
		local on = st.picks[i] == true
		b.Text = (on and "✅ " or "⬜ ") .. st.sample.notes[i][1]
		b.BackgroundColor3 = on and Color3.fromRGB(40, 120, 90) or Color3.fromRGB(90, 96, 110)
	end
	if mode == "practice" and not result.Visible then
		guide.Visible = true
		local need100 = st.sample.needMag == 100
		local steps = {
			{
				st.steps.found,
				"١. ابدأ بـ4× وحرّك الشريحة لين تلقى العيّنة، وركّز بالضابط الكبير",
			},
			{ st.steps.light, "٢. ظبّط الضوء (كل ما كبّرت تحتاج ضوء أكثر)" },
			{ st.maxMag >= 40, "٣. كبّر 10× ثم 40× وركّز بالضابط الدقيق بس" },
		}
		if need100 then
			table.insert(
				steps,
				{ st.sawOil, "٤. كبّر للـ100×، حط زيت الغمر، وركّز بالدقيق" }
			)
		end
		table.insert(steps, { false, (need100 and "٥" or "٤") .. ". اختار ملاحظاتك وسجّلها" })
		local lines = {}
		for _, x in ipairs(steps) do
			table.insert(lines, (x[1] and "✅ " or "▫️ ") .. x[2])
		end
		guide.Text = table.concat(lines, "\n")
	else
		guide.Visible = false
	end
	noteTitle.Text = mode == "eval" and "📒 دفتر المختبر • تقييم"
		or "📒 دفتر المختبر • تدريب"
end

openEvent.OnClientEvent:Connect(function(kind)
	if kind ~= "lightmicro" then
		return
	end
	gui.Enabled = true
	if not st.sample then
		newSession(Micro.SAMPLES[1])
	end
	buildNotes()
	say("ابدأ بالعدسة 4×، وحرّك الشريحة لين تلقى العيّنة")
	render()
end)

-- rebuild the notebook when the sample changes
local lastSample = nil
task.spawn(function()
	while true do
		task.wait(0.3)
		if gui.Enabled and st.sample and st.sample ~= lastSample then
			lastSample = st.sample
			buildNotes()
			render()
		end
	end
end)
