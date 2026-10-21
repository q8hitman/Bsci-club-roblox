-- Micro Racers client (v60). The server decides movement, laps and results; this script only sends intents.
-- * Prediction: the local kart runs the same RacerMath step every 0.05 s with the player's input, so steering
--   answers at once; each server snapshot carries the authoritative state + the last input it applied, the client
--   replays the newer inputs on top of it and hides any small correction (decays in ~0.1 s, snaps past 6 studs).
-- * Other karts are drawn 0.12 s in the past, interpolated between snapshots.
-- * Karts are anchored part models moved with BulkMoveTo: wheels spin, front wheels and the steering wheel turn,
--   the body leans in turns and swings out in a drift; sparks show the drift tier, flames the turbo.
-- * Spring chase camera with look-ahead, speed FOV and small shakes; clean HUD; keyboard, gamepad and touch.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local Run = game:GetService("RunService")
local UIS = game:GetService("UserInputService")
local p = Players.LocalPlayer
local Shared = RS:WaitForChild("Shared")
local D = require(Shared:WaitForChild("RacerData"))
local M = require(Shared:WaitForChild("RacerMath"))
local request = RS:WaitForChild("RaceRequest")
local input = RS:WaitForChild("RaceInput")
local event = RS:WaitForChild("RaceState")
local world = workspace:WaitForChild("Map"):WaitForChild("Racers47")
local controls = require(p.PlayerScripts:WaitForChild("PlayerModule")):GetControls()

local TICK = 0.05
local INTERP = 0.12
local function sfx(name)
	if _G.BSCPlay then
		_G.BSCPlay(name)
	end
end

-- ================================================================== UI helpers
local gui = Instance.new("ScreenGui")
gui.Name = "MicroRacersUI"
gui.ResetOnSpawn = false
gui.DisplayOrder = 70
gui.ScreenInsets = Enum.ScreenInsets.CoreUISafeInsets
gui.Parent = p:WaitForChild("PlayerGui")
local INK = Color3.fromRGB(236, 245, 244)
local PANEL = Color3.fromRGB(20, 30, 44)
local ACCENT = Color3.fromRGB(83, 232, 196)
local function corner(obj, r)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(r or 0.2, 0)
	c.Parent = obj
end
local function label(parent, name, text, pos, size, max, color)
	local t = Instance.new("TextLabel")
	t.Name = name
	t.Text = text
	t.Position = pos
	t.Size = size
	t.TextWrapped = true
	t.TextScaled = true
	t.Font = Enum.Font.GothamBold
	t.TextColor3 = color or INK
	t.BackgroundTransparency = 1
	local b = Instance.new("UITextSizeConstraint")
	b.MinTextSize = 10
	b.MaxTextSize = max or 23
	b.Parent = t
	t.Parent = parent
	return t
end
local function button(parent, name, text, pos, size, fn, color)
	local b = Instance.new("TextButton")
	b.Name = name
	b.Text = text
	b.Position = pos
	b.Size = size
	b.TextScaled = true
	b.TextWrapped = true
	b.Font = Enum.Font.GothamBold
	b.TextColor3 = Color3.new(1, 1, 1)
	b.BackgroundColor3 = color or Color3.fromRGB(35, 105, 108)
	b.AutoButtonColor = true
	corner(b, 0.25)
	local bound = Instance.new("UITextSizeConstraint")
	bound.MinTextSize = 11
	bound.MaxTextSize = 24
	bound.Parent = b
	local touch = Instance.new("UISizeConstraint")
	touch.MinSize = Vector2.new(44, 40)
	touch.Parent = b
	b.Parent = parent
	if fn then
		b.Activated:Connect(fn)
	end
	return b
end
local function panel(name)
	local f = Instance.new("Frame")
	f.Name = name
	f.Size = UDim2.fromScale(0.92, 0.86)
	f.Position = UDim2.fromScale(0.5, 0.5)
	f.AnchorPoint = Vector2.new(0.5, 0.5)
	f.BackgroundColor3 = PANEL
	f.Visible = false
	f.Active = true
	f.Parent = gui
	corner(f, 0.05)
	local bound = Instance.new("UISizeConstraint")
	bound.MaxSize = Vector2.new(950, 500)
	bound.Parent = f
	return f
end

-- menu + results (same actions as before)
local menu = panel("RaceMenu")
label(
	menu,
	"Title",
	"🏁 سباق العالم المجهري",
	UDim2.fromScale(0.03, 0.02),
	UDim2.fromScale(0.94, 0.13),
	28
)
local menuMessage = label(menu, "Message", "", UDim2.fromScale(0.03, 0.61), UDim2.fromScale(0.94, 0.16), 19)
local result = panel("RaceResults")
label(result, "Title", "🏁 نتيجة السباق", UDim2.fromScale(0.03, 0.02), UDim2.fromScale(0.94, 0.12), 28)
local rows = Instance.new("ScrollingFrame")
rows.Name = "Rows"
rows.BackgroundTransparency = 1
rows.Position = UDim2.fromScale(0.04, 0.18)
rows.Size = UDim2.fromScale(0.92, 0.54)
rows.ScrollBarThickness = 5
rows.BorderSizePixel = 0
rows.Parent = result

-- race HUD: position + lap (top-left), progress strip (top-centre), compact leaderboard (right), big centre text,
-- a context hint at the bottom, touch controls only on touch devices
local hud = Instance.new("Frame")
hud.Name = "RaceHUD"
hud.BackgroundTransparency = 1
hud.Size = UDim2.fromScale(1, 1)
hud.Visible = false
hud.Parent = gui
local posCard = Instance.new("Frame")
posCard.Name = "PositionCard"
posCard.Position = UDim2.fromOffset(12, 12)
posCard.Size = UDim2.fromOffset(150, 92)
posCard.BackgroundColor3 = PANEL
posCard.BackgroundTransparency = 0.2
posCard.Parent = hud
corner(posCard, 0.18)
local posBig = label(posCard, "Position", "1", UDim2.fromOffset(8, 2), UDim2.fromOffset(62, 62), 58, ACCENT)
local posOf = label(posCard, "Of", "/4", UDim2.fromOffset(66, 22), UDim2.fromOffset(70, 36), 26)
local lapLabel = label(posCard, "Lap", "لفة 1/3", UDim2.fromOffset(8, 62), UDim2.fromOffset(134, 26), 20)
local strip = Instance.new("Frame")
strip.Name = "Progress"
strip.AnchorPoint = Vector2.new(0.5, 0)
strip.Position = UDim2.new(0.5, 0, 0, 16)
strip.Size = UDim2.new(0.38, 0, 0, 10)
strip.BackgroundColor3 = Color3.fromRGB(40, 52, 66)
strip.Parent = hud
corner(strip, 1)
local stripFill = Instance.new("Frame")
stripFill.Name = "Fill"
stripFill.Size = UDim2.fromScale(0, 1)
stripFill.BackgroundColor3 = ACCENT
stripFill.Parent = strip
corner(stripFill, 1)
local board = Instance.new("Frame")
board.Name = "Leaderboard"
board.AnchorPoint = Vector2.new(1, 0)
board.Position = UDim2.new(1, -12, 0, 60)
board.Size = UDim2.fromOffset(190, 4 * 26 + 8)
board.BackgroundColor3 = PANEL
board.BackgroundTransparency = 0.3
board.Parent = hud
corner(board, 0.12)
local boardRows = {}
for i = 1, 4 do
	boardRows[i] = label(board, "Row" .. i, "", UDim2.fromOffset(8, 4 + (i - 1) * 26), UDim2.new(1, -16, 0, 24), 17)
	boardRows[i].TextXAlignment = Enum.TextXAlignment.Right
end
local bigText = label(hud, "BigText", "", UDim2.fromScale(0.3, 0.3), UDim2.fromScale(0.4, 0.18), 90)
bigText.TextStrokeTransparency = 0.4
local banner =
	label(hud, "Banner", "", UDim2.fromScale(0.25, 0.48), UDim2.fromScale(0.5, 0.08), 34, Color3.fromRGB(255, 220, 110))
banner.TextStrokeTransparency = 0.4
local hint = label(hud, "Hint", "", UDim2.new(0.18, 0, 1, -40), UDim2.new(0.64, 0, 0, 28), 17)
hint.BackgroundColor3 = PANEL
hint.BackgroundTransparency = 0.35
corner(hint, 0.4)

-- ================================================================== input
local held = { throttle = {}, brake = {}, left = {}, right = {}, boost = {}, drift = {} }
local touches = {}
local padSteer = 0
local farCamera = false
local function clearInput()
	for _, v in pairs(held) do
		table.clear(v)
	end
	table.clear(touches)
	padSteer = 0
end
local function active(name)
	return next(held[name]) ~= nil
end
local touchMode = UIS.TouchEnabled and not UIS.KeyboardEnabled

local latest = nil
local function call(action, arg)
	local ok, res = pcall(request.InvokeServer, request, action, arg)
	if not ok or type(res) ~= "table" then
		res = { error = "تعذر الاتصال؛ أعد المحاولة" }
	end
	if res.error then
		menuMessage.Text = res.error
		hint.Text = res.error
	end
	return res
end
for i, t in ipairs(D.Tracks) do
	button(
		menu,
		"Track_" .. t.id,
		t.ar .. "\n" .. t.desc,
		UDim2.fromScale(i == 1 and 0.03 or 0.52, 0.20),
		UDim2.fromScale(0.45, 0.38),
		function()
			call("join", t.id)
		end
	)
end
button(menu, "Exit", "العودة للأركيد", UDim2.fromScale(0.63, 0.81), UDim2.fromScale(0.34, 0.14), function()
	call("leave")
end)
button(result, "Replay", "إعادة الحلبة", UDim2.fromScale(0.03, 0.81), UDim2.fromScale(0.29, 0.14), function()
	if latest then
		call("join", latest.track)
	end
end)
button(
	result,
	"Choose",
	"اختيار الحلبة",
	UDim2.fromScale(0.35, 0.81),
	UDim2.fromScale(0.29, 0.14),
	function()
		call("menu")
	end
)
button(
	result,
	"Exit",
	"العودة للأركيد",
	UDim2.fromScale(0.67, 0.81),
	UDim2.fromScale(0.30, 0.14),
	function()
		call("leave")
	end
)
-- small utility buttons (top-right, under the leaderboard)
button(hud, "Exit", "خروج", UDim2.new(1, -72, 0, 178), UDim2.fromOffset(60, 34), function()
	call("leave")
end, Color3.fromRGB(150, 60, 60))
button(hud, "Recover", "استعادة", UDim2.new(1, -150, 0, 178), UDim2.fromOffset(70, 34), function()
	call("recover")
end)
button(hud, "Camera", "كاميرا", UDim2.new(1, -228, 0, 178), UDim2.fromOffset(68, 34), function()
	farCamera = not farCamera
end)
-- touch: steer bottom-left, drift (largest) / brake / turbo bottom-right; the kart accelerates by itself on touch
local function holdButton(name, text, pos, size, action, color)
	local b = button(hud, name, text, pos, size, nil, color)
	b.BackgroundTransparency = 0.25
	b.InputBegan:Connect(function(v)
		if v.UserInputType == Enum.UserInputType.Touch or v.UserInputType == Enum.UserInputType.MouseButton1 then
			held[action][v] = true
			touches[v] = action
		end
	end)
	return b
end
local touchPad = Instance.new("Frame")
touchPad.Name = "TouchControls"
touchPad.BackgroundTransparency = 1
touchPad.Size = UDim2.fromScale(1, 1)
touchPad.Visible = touchMode
touchPad.Parent = hud
local function touchButton(...)
	local b = holdButton(...)
	b.Parent = touchPad
	return b
end
for _, b in ipairs({
	touchButton("SteerLeft", "◀", UDim2.new(0, 16, 1, -112), UDim2.fromOffset(96, 96), "left"),
	touchButton("SteerRight", "▶", UDim2.new(0, 124, 1, -112), UDim2.fromOffset(96, 96), "right"),
}) do
	b:FindFirstChildWhichIsA("UITextSizeConstraint").MaxTextSize = 56 -- big arrows for thumbs
end
touchButton(
	"Drift",
	"انجراف",
	UDim2.new(1, -124, 1, -124),
	UDim2.fromOffset(108, 108),
	"drift",
	Color3.fromRGB(150, 80, 200)
)
touchButton(
	"Brake",
	"فرامل",
	UDim2.new(1, -212, 1, -84),
	UDim2.fromOffset(76, 68),
	"brake",
	Color3.fromRGB(120, 60, 60)
)
local turboButton = touchButton(
	"Boost",
	"تيربو",
	UDim2.new(1, -212, 1, -164),
	UDim2.fromOffset(76, 68),
	"boost",
	Color3.fromRGB(40, 120, 170)
)

local keys = {
	[Enum.KeyCode.W] = "throttle",
	[Enum.KeyCode.Up] = "throttle",
	[Enum.KeyCode.ButtonR2] = "throttle",
	[Enum.KeyCode.S] = "brake",
	[Enum.KeyCode.Down] = "brake",
	[Enum.KeyCode.ButtonL2] = "brake",
	[Enum.KeyCode.A] = "left",
	[Enum.KeyCode.Left] = "left",
	[Enum.KeyCode.D] = "right",
	[Enum.KeyCode.Right] = "right",
	[Enum.KeyCode.Space] = "drift",
	[Enum.KeyCode.LeftShift] = "drift",
	[Enum.KeyCode.RightShift] = "drift",
	[Enum.KeyCode.ButtonR1] = "drift",
	[Enum.KeyCode.ButtonB] = "drift",
	[Enum.KeyCode.E] = "boost",
	[Enum.KeyCode.ButtonX] = "boost",
}
UIS.InputBegan:Connect(function(v, processed)
	if not hud.Visible or processed or UIS:GetFocusedTextBox() then
		return
	end
	if v.KeyCode == Enum.KeyCode.R or v.KeyCode == Enum.KeyCode.ButtonY then
		call("recover")
	elseif v.KeyCode == Enum.KeyCode.C then
		farCamera = not farCamera
	end
	local action = keys[v.KeyCode]
	if action then
		held[action][v.KeyCode] = true
	end
end)
UIS.InputChanged:Connect(function(v)
	if v.KeyCode == Enum.KeyCode.Thumbstick1 then
		padSteer = math.abs(v.Position.X) > 0.15 and v.Position.X or 0
	end
end)
UIS.InputEnded:Connect(function(v)
	local action = keys[v.KeyCode]
	if action then
		held[action][v.KeyCode] = nil
	end
	if v.KeyCode == Enum.KeyCode.Thumbstick1 then
		padSteer = 0
	end
	local touch = touches[v]
	if touch then
		held[touch][v] = nil
		touches[v] = nil
	end
end)
UIS.WindowFocusReleased:Connect(clearInput)
UIS.LastInputTypeChanged:Connect(function(t)
	touchMode = t == Enum.UserInputType.Touch
	touchPad.Visible = touchMode
end)

-- Studio-only QA driver (workspace attribute RacerAutopilot): closes the loop on the predicted state the way a
-- player would (look ahead, steer, drift long bends) so full races can be verified; never runs in a live server.
local autoTarget = 2
local autoDrift = false
local function autopilot(s, track)
	local pt = track.points[autoTarget]
	if math.sqrt((pt[1] - s.x) ^ 2 + (pt[2] - s.z) ^ 2) < 16 then
		autoTarget = autoTarget % #track.points + 1
		pt = track.points[autoTarget]
	end
	local delta = math.atan2(pt[1] - s.x, pt[2] - s.z) - s.heading
	delta = math.atan2(math.sin(delta), math.cos(delta))
	if not autoDrift and math.abs(delta) > 0.55 and s.speed > 25 then
		autoDrift = true
	elseif autoDrift and math.abs(delta) < 0.12 then
		autoDrift = false
	end
	return {
		throttle = 1,
		brake = 0,
		steer = math.abs(delta) > 0.06 and (delta > 0 and 1 or -1) or 0,
		boost = false,
		drift = autoDrift,
	}
end

-- a heading increase turns the kart to the LEFT of the chase camera, so "right" is steer -1
local function readInput()
	local steer = (active("left") and 1 or 0) - (active("right") and 1 or 0)
	if padSteer ~= 0 then
		steer = -padSteer
	end
	local throttle = active("throttle") and 1 or 0
	if touchMode and not active("brake") then
		throttle = 1
	end
	return {
		throttle = throttle,
		brake = active("brake") and 1 or 0,
		steer = math.clamp(steer, -1, 1),
		boost = active("boost"),
		drift = active("drift"),
	}
end

-- ================================================================== hiding the rest of the game UI during a race
local covered = {}
local interfaceActive = false
local background = {
	IslandHUD = true,
	Extras = true,
	WorldMenu = true,
	Welcome = true,
	ProfileMenu = true,
	LeaveCourse = true,
	StageHUD = true,
	Feedback = true,
	PhotoModeGui = true,
	Help = true,
	FirstDay = true,
	ArcadeVote = true,
	ArcadeWatch = true,
}
local function raceInterface(on)
	interfaceActive = on
	if on then
		for _, other in p.PlayerGui:GetChildren() do
			if other:IsA("ScreenGui") and background[other.Name] and covered[other] == nil then
				covered[other] = other.Enabled
				other.Enabled = false
			end
		end
	else
		for other, enabled in pairs(covered) do
			if other.Parent then
				other.Enabled = enabled
			end
		end
		table.clear(covered)
	end
end
p.PlayerGui.ChildAdded:Connect(function(other)
	if interfaceActive and other:IsA("ScreenGui") and background[other.Name] then
		covered[other] = other.Enabled
		other.Enabled = false
	end
end)

-- ================================================================== karts
local modelFolder = Instance.new("Folder")
modelFolder.Name = "LocalMicroRacers"
modelFolder.Parent = workspace
local PAINT = {
	{ Color3.fromRGB(70, 200, 170), Color3.fromRGB(255, 200, 80) }, -- mint / amber medium
	{ Color3.fromRGB(235, 110, 90), Color3.fromRGB(120, 220, 255) }, -- coral / blue medium
	{ Color3.fromRGB(150, 120, 230), Color3.fromRGB(140, 240, 140) }, -- lavender / green medium
	{ Color3.fromRGB(80, 150, 230), Color3.fromRGB(255, 130, 200) }, -- sky / pink medium
}
local SPARK = { Color3.fromRGB(90, 180, 255), Color3.fromRGB(255, 150, 40), Color3.fromRGB(200, 90, 255) }
local function emitter(parent, color)
	local e = Instance.new("ParticleEmitter")
	e.Color = ColorSequence.new(color)
	e.LightEmission = 0.8
	e.Size = NumberSequence.new(0.45, 0)
	e.Lifetime = NumberRange.new(0.2, 0.35)
	e.Speed = NumberRange.new(6, 10)
	e.SpreadAngle = Vector2.new(30, 30)
	e.Rate = 60
	e.Enabled = false
	e.Parent = parent
	return e
end
local localCars = {}
local function carModel(c, index)
	local model = world.VehicleTemplate:Clone()
	model.Name = "RaceCar_" .. c.id
	local parts, minY = {}, math.huge
	for _, v in model:GetDescendants() do
		if v:IsA("BasePart") then
			v.Anchored, v.CanCollide, v.CanTouch, v.CanQuery = true, false, false, false
			table.insert(parts, v)
			minY = math.min(minY, v.Position.Y - v.Size.Y / 2)
		end
	end
	local body = model:FindFirstChild("Body")
	local ground = CFrame.new(body.Position.X, minY, body.Position.Z)
	local paint = PAINT[(index - 1) % #PAINT + 1]
	local wheels = {}
	for _, v in ipairs(parts) do
		local tag = v.Name:match("^Wheel_(%u%u)")
		if tag and v.Name == "Wheel_" .. tag then
			wheels[tag] = { pivot = ground:ToObjectSpace(CFrame.new(v.Position)), radius = v.Size.Y / 2 }
		end
	end
	local rec = { model = model, parts = {}, cfs = {}, spin = { F = 0, R = 0 } }
	for _, v in ipairs(parts) do
		if v.Name == "Body" or v.Name:sub(1, 5) == "Paint" then
			v.Color = paint[1]
		elseif v.Name == "Liquid" then
			v.Color = paint[2]
		end
		local tag = v.Name:match("^Wheel_(%u%u)")
		local entry = { part = v, rel = ground:ToObjectSpace(v.CFrame) }
		if tag and wheels[tag] then
			entry.wheel = tag
			entry.inner = wheels[tag].pivot:ToObjectSpace(entry.rel)
		elseif v.Name == "SteeringWheel" then
			entry.steeringWheel = true
		end
		table.insert(rec.parts, entry)
	end
	rec.wheels = wheels
	-- effects ride on an invisible anchor that moves with the kart
	local fx = Instance.new("Part")
	fx.Name = "FX"
	fx.Size = Vector3.new(1, 1, 1)
	fx.Transparency = 1
	fx.Anchored, fx.CanCollide, fx.CanTouch, fx.CanQuery = true, false, false, false
	fx.Parent = model
	rec.fx = fx
	rec.sparks = {}
	for _, sx in ipairs({ -1, 1 }) do
		local a = Instance.new("Attachment")
		a.Position = Vector3.new(sx * 2.9, 0.3, -3.0)
		a.Parent = fx
		table.insert(rec.sparks, emitter(a, SPARK[1]))
	end
	rec.flames = {}
	for _, sx in ipairs({ -1, 1 }) do
		local a = Instance.new("Attachment")
		a.Position = Vector3.new(sx * 1.0, 1.4, -4.9)
		a.Orientation = Vector3.new(0, 180, 0)
		a.Parent = fx
		local f = emitter(a, Color3.fromRGB(255, 160, 60))
		f.Size = NumberSequence.new(0.8, 0.1)
		f.EmissionDirection = Enum.NormalId.Front
		f.Speed = NumberRange.new(10, 14)
		table.insert(rec.flames, f)
	end
	local glow = Instance.new("Highlight")
	glow.Name = "Shield"
	glow.FillColor = Color3.fromRGB(174, 148, 244)
	glow.FillTransparency = 0.65
	glow.OutlineTransparency = 0.2
	glow.Enabled = false
	glow.Parent = model
	rec.shield = glow
	if c.id ~= (latest and latest.you) then
		local bb = Instance.new("BillboardGui")
		bb.Name = "DriverName"
		bb.Size = UDim2.fromOffset(140, 22)
		bb.StudsOffset = Vector3.new(0, 6.5, 0)
		bb.MaxDistance = 60
		bb.Adornee = body
		bb.Parent = model
		label(bb, "Name", c.name, UDim2.new(), UDim2.fromScale(1, 1), 15)
	end
	model.Parent = modelFolder
	return rec
end

-- pose one kart: v = { x, z, heading, speed, drift, tier, steer, yaw, turbo, boost, shield }
local function pose(rec, track, v, dt)
	local driftVis = (v.drift or 0) * 0.38
	rec.driftVis = (rec.driftVis or 0) + (driftVis - (rec.driftVis or 0)) * math.min(1, dt * 10)
	local lean = math.clamp(-(v.yaw or 0) * 0.07, -0.16, 0.16)
	rec.lean = (rec.lean or 0) + (lean - (rec.lean or 0)) * math.min(1, dt * 8)
	local pitch = (v.turbo or v.boost) and -0.05 or 0
	local carCF = CFrame.new(track.origin[1] + v.x, track.origin[2], track.origin[3] + v.z)
		* CFrame.Angles(0, v.heading + rec.driftVis, 0)
		* CFrame.Angles(pitch, 0, rec.lean)
	local speed = v.speed or 0
	rec.spin.F += speed * dt / 1.0
	rec.spin.R += speed * dt / 1.3
	local steerAngle = math.clamp((v.steer or 0) * 0.42 - (v.drift or 0) * 0.3, -0.6, 0.6)
	local list, cfs = {}, {}
	for _, e in ipairs(rec.parts) do
		local cf
		if e.wheel then
			local front = e.wheel:sub(1, 1) == "F"
			local w = rec.wheels[e.wheel]
			cf = carCF
				* w.pivot
				* CFrame.Angles(0, front and steerAngle or 0, 0)
				* CFrame.Angles(front and rec.spin.F or rec.spin.R, 0, 0)
				* e.inner
		elseif e.steeringWheel then
			cf = carCF * e.rel * CFrame.Angles((v.steer or 0) * 1.4, 0, 0)
		else
			cf = carCF * e.rel
		end
		table.insert(list, e.part)
		table.insert(cfs, cf)
	end
	table.insert(list, rec.fx)
	table.insert(cfs, carCF)
	workspace:BulkMoveTo(list, cfs, Enum.BulkMoveMode.FireCFrameChanged)
	local tier = v.tier or 0
	for _, e in ipairs(rec.sparks) do
		e.Enabled = (v.drift or 0) ~= 0
		e.Color = ColorSequence.new(tier > 0 and SPARK[tier] or Color3.fromRGB(230, 230, 230))
		e.Rate = tier > 0 and 70 or 25
	end
	for _, f in ipairs(rec.flames) do
		f.Enabled = v.turbo == true or v.boost == true
		f.Color = ColorSequence.new(v.boost and Color3.fromRGB(90, 220, 255) or Color3.fromRGB(255, 160, 60))
	end
	rec.shield.Enabled = v.shield == true
	return carCF
end

-- ================================================================== prediction + interpolation state
local pred, prevPred, acc = nil, nil, 0
local pending, seq = {}, 0
local corr = Vector3.zero
local corrHeading = 0
local buffers = {} -- id -> { {t, car} ... }
local function copyState(s)
	local c = table.clone(s)
	c.pickups = table.clone(s.pickups or {})
	return c
end

local cameraOwned = false
local defaultFov = 70
local camPos, camFocus = nil, nil
local shake = 0
local lastWall, lastBoosting = false, false
local lastPhase, lastLap, lastFinished = nil, 0, false
local goUntil = 0

local function cleanup()
	raceInterface(false)
	for _, attribute in { "RaceTrack", "RacePhase", "RaceId", "RaceLap", "RaceGate" } do
		p:SetAttribute(attribute, nil)
	end
	clearInput()
	latest, pred, prevPred = nil, nil, nil
	table.clear(pending)
	table.clear(buffers)
	hud.Visible = false
	for _, c in pairs(localCars) do
		c.model:Destroy()
	end
	table.clear(localCars)
	controls:Enable()
	if cameraOwned then
		cameraOwned = false
		local cam = workspace.CurrentCamera
		cam.CameraType = Enum.CameraType.Custom
		cam.FieldOfView = defaultFov
		local hum = p.Character and p.Character:FindFirstChildOfClass("Humanoid")
		if hum then
			cam.CameraSubject = hum
		end
	end
	camPos, camFocus = nil, nil
	lastPhase, lastLap, lastFinished = nil, 0, false
end

local function standings(parent, cars)
	parent:ClearAllChildren()
	parent.CanvasSize = UDim2.fromOffset(0, #cars * 30)
	for i, c in ipairs(cars) do
		local text = ("%d. %s %s"):format(i, c.name, c.finished and ("%.1fث"):format(c.finishTime or 0) or "")
		label(parent, "Rank_" .. c.id, text, UDim2.fromOffset(0, (i - 1) * 30), UDim2.new(1, -8, 0, 28), 18)
	end
end

local KEY_HINT =
	"W تسارع • A / D توجيه • Space انجراف (لفّ للداخل يشحن أسرع) • E تيربو • R استعادة • C كاميرا"
local PAD_HINT = "R2 تسارع • العصا توجيه • R1 انجراف • X تيربو • Y استعادة"
local TOUCH_HINT =
	"الكارت يسرع بنفسه • ◀ ▶ توجيه • انجراف وأنت تلف = تيربو"

event.OnClientEvent:Connect(function(data)
	if type(data) ~= "table" then
		return
	end
	if data.kind == "error" then
		hint.Text = data.message
		return
	end
	if data.kind == "close" then
		cleanup()
		menu.Visible = false
		result.Visible = false
		return
	end
	if data.kind == "menu" then
		cleanup()
		raceInterface(true)
		menu.Visible = true
		result.Visible = false
		menuMessage.Text = "اختر حلبة • ضد منافسين آليين أو مع الأصدقاء • 3 لفات\n"
			.. (touchMode and TOUCH_HINT or KEY_HINT)
		return
	end
	local track = D.get(data.track)
	if not track or type(data.cars) ~= "table" then
		return
	end
	if not latest or latest.raceId ~= data.raceId then
		for _, c in pairs(localCars) do
			c.model:Destroy()
		end
		table.clear(localCars)
		table.clear(buffers)
		table.clear(pending)
		clearInput()
		pred, prevPred = nil, nil
		seq = 0
		autoTarget, autoDrift = 2, false
	end
	latest = data
	raceInterface(true)
	menu.Visible = false
	local now = os.clock()
	local own
	for i, c in ipairs(data.cars) do
		if c.id == data.you then
			own = c
		end
		if not localCars[c.id] then
			localCars[c.id] = carModel(c, i)
		end
		buffers[c.id] = buffers[c.id] or {}
		table.insert(buffers[c.id], { t = now, car = c })
		if #buffers[c.id] > 8 then
			table.remove(buffers[c.id], 1)
		end
	end
	local present = {}
	for _, c in ipairs(data.cars) do
		present[c.id] = true
	end
	for id, c in pairs(localCars) do
		if not present[id] then
			c.model:Destroy()
			localCars[id] = nil
			buffers[id] = nil
		end
	end
	-- reconcile the local prediction with the authoritative state
	if type(data.me) == "table" then
		local server = copyState(data.me)
		while pending[1] and pending[1].seq <= (data.ack or 0) do
			table.remove(pending, 1)
		end
		if data.phase == "running" and not server.done then
			for _, item in ipairs(pending) do
				M.step(server, item.input, TICK, track)
			end
		end
		if pred then
			local err = Vector3.new(pred.x - server.x, 0, pred.z - server.z)
			if err.Magnitude > 6 then
				corr, corrHeading = Vector3.zero, 0 -- far off (recover, teleport): snap
			else
				corr += err
				corrHeading += math.atan2(
					math.sin(pred.heading - server.heading),
					math.cos(pred.heading - server.heading)
				)
			end
		end
		pred = server
		prevPred = copyState(server)
	end
	hud.Visible = data.phase ~= "results"
	result.Visible = data.phase == "results"
	cameraOwned = true
	if data.phase == "results" then
		clearInput()
		controls:Enable()
		standings(rows, data.cars)
	else
		controls:Disable()
	end
	-- HUD
	local n = #data.cars
	if own then
		p:SetAttribute("RaceTrack", data.track)
		p:SetAttribute("RacePhase", data.phase)
		p:SetAttribute("RaceId", data.raceId)
		p:SetAttribute("RaceLap", own.lap)
		p:SetAttribute("RaceGate", own.gate)
		posBig.Text = tostring(own.rank)
		posOf.Text = "/" .. n
		lapLabel.Text = ("لفة %d/3"):format(math.min(own.lap, 3))
		local gates = #track.gates
		stripFill.Size = UDim2.fromScale(math.clamp(((own.lap - 1) * gates + own.gate - 1) / (3 * gates), 0, 1), 1)
		turboButton.Text = own.boostReady > 0 and tostring(math.ceil(own.boostReady)) or "تيربو"
		local folder = world:FindFirstChild("Track_" .. data.track)
		local function lights(count, color)
			for k = 1, 3 do
				local l = folder and folder:FindFirstChild("StartLight_" .. k)
				if l then
					l.Material = k <= count and Enum.Material.Neon or Enum.Material.SmoothPlastic
					l.Color = k <= count and color or Color3.fromRGB(50, 20, 20)
				end
			end
		end
		if data.phase == "queue" then
			local cd = math.ceil(data.countdown)
			lights(math.clamp(4 - cd, 0, 3), Color3.fromRGB(255, 60, 50)) -- v60 start gantry: red, red, red
			bigText.Text = cd <= 3 and tostring(cd) or "استعد"
			if cd ~= lastPhase and cd <= 3 then
				sfx("click")
			end
			lastPhase = cd
			hint.Visible = true
			hint.Text = touchMode and TOUCH_HINT or (UIS.GamepadEnabled and PAD_HINT or KEY_HINT)
		elseif data.phase == "running" then
			if lastPhase ~= "running" then
				lastPhase = "running"
				goUntil = now + 0.9
				sfx("whoosh")
			end
			bigText.Text = now < goUntil and "انطلق!" or ""
			lights(now < goUntil + 1.5 and 3 or 0, Color3.fromRGB(80, 255, 120))
			if own.lap ~= lastLap then
				if lastLap > 0 and own.lap <= 3 then
					sfx("checkpoint")
				end
				banner.Text = own.lap == 3 and "اللفة الأخيرة!" or ""
				lastLap = own.lap
				task.delay(2.2, function()
					if banner.Text == "اللفة الأخيرة!" then
						banner.Text = ""
					end
				end)
			end
			hint.Visible = now < goUntil + 4
			if own.finished and not lastFinished then
				lastFinished = true
				sfx("sting")
				banner.Text = ("أنهيت بالمركز %d • %.1f ث"):format(own.rank, own.finishTime or 0)
			end
		end
	end
	for i = 1, 4 do
		local c = data.cars[i]
		boardRows[i].Text = c and ("%s  %d"):format(c.name, i) or ""
		boardRows[i].TextColor3 = (c and c.id == data.you) and ACCENT or INK
	end
end)
p.CharacterAdded:Connect(function()
	cleanup()
	menu.Visible = false
	result.Visible = false
end)

-- interpolated view of a remote kart at (now - INTERP)
local function remoteView(buf, now)
	local t = now - INTERP
	for i = #buf, 2, -1 do
		local a, b = buf[i - 1], buf[i]
		if a.t <= t and t <= b.t then
			local k = (t - a.t) / math.max(1e-3, b.t - a.t)
			local ca, cb = a.car, b.car
			local dh = math.atan2(math.sin(cb.heading - ca.heading), math.cos(cb.heading - ca.heading))
			local v = table.clone(cb)
			v.x = ca.x + (cb.x - ca.x) * k
			v.z = ca.z + (cb.z - ca.z) * k
			v.heading = ca.heading + dh * k
			return v
		end
	end
	local last = buf[#buf]
	if not last then
		return nil
	end
	local v = table.clone(last.car)
	local ahead = math.clamp(t - last.t, 0, 0.1) -- short extrapolation when a packet is late
	v.x += math.sin(v.heading) * v.speed * ahead
	v.z += math.cos(v.heading) * v.speed * ahead
	return v
end

Run.RenderStepped:Connect(function(dt)
	if not latest or not cameraOwned then
		return
	end
	local track = D.get(latest.track)
	local running = latest.phase == "running"
	-- fixed-step local prediction for our kart
	if pred and running and not pred.done then
		acc = math.min(acc + dt, 0.25)
		while acc >= TICK do
			acc -= TICK
			local intent = (Run:IsStudio() and workspace:GetAttribute("RacerAutopilot")) and autopilot(pred, track)
				or readInput()
			seq += 1
			table.insert(pending, { seq = seq, input = intent })
			if #pending > 60 then
				table.remove(pending, 1)
			end
			prevPred = copyState(pred)
			M.step(pred, intent, TICK, track)
			if Run:IsStudio() then -- QA readout: drift side / tier / speed / wall of the predicted kart
				p:SetAttribute(
					"QA_Kart",
					("%d|%d|%.1f|%s|%.2f"):format(
						pred.drift or 0,
						pred.driftTier or 0,
						pred.speed,
						tostring(pred.wall),
						pred.steerV or 0
					)
				)
			end
			input:FireServer(latest.raceId, seq, intent)
		end
	else
		acc = 0
	end
	corr *= math.exp(-dt / 0.1)
	corrHeading *= math.exp(-dt / 0.1)
	local now = os.clock()
	local ownCF, ownView
	for _, c in ipairs(latest.cars) do
		local rec = localCars[c.id]
		if rec then
			local v
			if c.id == latest.you and pred then
				local a = prevPred or pred
				local k = running and acc / TICK or 1
				local dh = math.atan2(math.sin(pred.heading - a.heading), math.cos(pred.heading - a.heading))
				v = {
					x = a.x + (pred.x - a.x) * k + corr.X,
					z = a.z + (pred.z - a.z) * k + corr.Z,
					heading = a.heading + dh * k + corrHeading,
					speed = pred.speed,
					drift = pred.drift or 0,
					tier = pred.driftTier or 0,
					steer = pred.steerV or 0,
					yaw = pred.yawRate or 0,
					turbo = (pred.turboUntil or 0) > pred.time,
					boost = pred.boostUntil > pred.time,
					shield = pred.shieldUntil > pred.time,
					wall = pred.wall,
				}
				ownView = v
			else
				v = remoteView(buffers[c.id] or {}, now)
			end
			if v then
				local cf = pose(rec, track, v, dt)
				if c.id == latest.you then
					ownCF = cf
				end
			end
		end
	end
	-- chase camera
	if ownCF and ownView then
		local cam = workspace.CurrentCamera
		cam.CameraType = Enum.CameraType.Scriptable
		local pos = Vector3.new(track.origin[1] + ownView.x, track.origin[2], track.origin[3] + ownView.z)
		local fwd = Vector3.new(math.sin(ownView.heading), 0, math.cos(ownView.heading))
		local right = Vector3.new(-fwd.Z, 0, fwd.X)
		local back, up = farCamera and 22 or 14, farCamera and 11 or 6
		local desired = pos - fwd * back + Vector3.new(0, up, 0) + right * math.clamp(ownView.yaw * 1.2, -3, 3)
		local focus = pos + fwd * (6 + ownView.speed * 0.15) + Vector3.new(0, 2, 0)
		local params = RaycastParams.new()
		params.FilterType = Enum.RaycastFilterType.Exclude
		params.FilterDescendantsInstances = { modelFolder, p.Character, world.VehicleTemplate }
		params.RespectCanCollide = true
		local hit = workspace:Raycast(pos + Vector3.new(0, 3, 0), desired - (pos + Vector3.new(0, 3, 0)), params)
		if hit then
			desired = hit.Position + hit.Normal * 0.5
		end
		camPos = camPos and camPos:Lerp(desired, 1 - math.exp(-dt / 0.1)) or desired
		camFocus = camFocus and camFocus:Lerp(focus, 1 - math.exp(-dt / 0.07)) or focus
		local boosting = ownView.turbo or ownView.boost
		if ownView.wall and not lastWall then
			shake = 0.35
		end
		if boosting and not lastBoosting then
			shake = math.max(shake, 0.2)
			sfx("whoosh")
		end
		lastWall, lastBoosting = ownView.wall, boosting
		shake = math.max(0, shake - dt)
		local jitter = shake > 0
				and Vector3.new(math.random() - 0.5, math.random() - 0.5, math.random() - 0.5) * shake * 0.8
			or Vector3.zero
		cam.CFrame = CFrame.lookAt(camPos + jitter, camFocus)
		for id, rec in pairs(localCars) do
			if id ~= latest.you then
				local near = (rec.fx.Position - cam.CFrame.Position).Magnitude < 10
				if near ~= (rec.faded == true) then
					rec.faded = near
					for _, e in ipairs(rec.parts) do
						e.part.LocalTransparencyModifier = near and 0.75 or 0
					end
				end
			end
		end
		local fov = defaultFov + 10 * math.clamp(ownView.speed / 42, 0, 1) + (boosting and 6 or 0)
		cam.FieldOfView += (fov - cam.FieldOfView) * math.min(1, dt * 4)
	end
end)
