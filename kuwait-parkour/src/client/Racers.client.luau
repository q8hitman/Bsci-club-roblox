-- Intent-only keyboard/touch driving, local interpolation and chase camera. Server decides movement and results.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local Run = game:GetService("RunService")
local UIS = game:GetService("UserInputService")
local p = Players.LocalPlayer
local D = require(RS:WaitForChild("Shared"):WaitForChild("RacerData"))
local request = RS:WaitForChild("RaceRequest")
local input = RS:WaitForChild("RaceInput")
local event = RS:WaitForChild("RaceState")
local world = workspace:WaitForChild("Map"):WaitForChild("Racers47")
local controls = require(p.PlayerScripts:WaitForChild("PlayerModule")):GetControls()
local gui = Instance.new("ScreenGui")
gui.Name = "MicroRacersUI"
gui.ResetOnSpawn = false
gui.DisplayOrder = 70
gui.Parent = p:WaitForChild("PlayerGui")
local function label(parent, name, text, pos, size, max)
	local t = Instance.new("TextLabel")
	t.Name = name
	t.Text = text
	t.Position = pos
	t.Size = size
	t.TextWrapped = true
	t.TextScaled = true
	t.Font = Enum.Font.GothamBold
	t.TextColor3 = Color3.fromRGB(236, 245, 244)
	t.BackgroundTransparency = 1
	local b = Instance.new("UITextSizeConstraint")
	b.MinTextSize = 12
	b.MaxTextSize = max or 23
	b.Parent = t
	t.Parent = parent
	return t
end
local function button(parent, name, text, pos, size, fn)
	local b = Instance.new("TextButton")
	b.Name = name
	b.Text = text
	b.Position = pos
	b.Size = size
	b.TextScaled = true
	b.TextWrapped = true
	b.Font = Enum.Font.GothamBold
	b.TextColor3 = Color3.new(1, 1, 1)
	b.BackgroundColor3 = Color3.fromRGB(35, 105, 108)
	local bound = Instance.new("UITextSizeConstraint")
	bound.MinTextSize = 12
	bound.MaxTextSize = 24
	bound.Parent = b
	local touch = Instance.new("UISizeConstraint")
	touch.MinSize = Vector2.new(48, 44)
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
	f.BackgroundColor3 = Color3.fromRGB(20, 34, 48)
	f.Visible = false
	f.Active = true
	f.Parent = gui
	local bound = Instance.new("UISizeConstraint")
	bound.MaxSize = Vector2.new(950, 500)
	bound.Parent = f
	return f
end
local menu = panel("RaceMenu")
label(
	menu,
	"Title",
	"🏁 سباق العالم المجهري",
	UDim2.fromScale(0.03, 0.02),
	UDim2.fromScale(0.94, 0.13),
	28
)
local menuMessage = label(
	menu,
	"Message",
	"اختر حلبة • Solo مع منافسين آليين أو سباق مع الأصدقاء\n3 لفات • القيادة يدوية: توجيه وتسارع وفرامل",
	UDim2.fromScale(0.03, 0.61),
	UDim2.fromScale(0.94, 0.16),
	19
)
local hud = Instance.new("Frame")
hud.Name = "RaceHUD"
hud.BackgroundTransparency = 1
hud.Size = UDim2.fromScale(1, 1)
hud.Visible = false
hud.Parent = gui
local status = label(hud, "Status", "", UDim2.new(0.23, 0, 0, 46), UDim2.new(0.54, 0, 0, 72), 22)
status.BackgroundColor3 = Color3.fromRGB(20, 34, 48)
status.BackgroundTransparency = 0.15
local score = Instance.new("ScrollingFrame")
score.Name = "Standings"
score.Position = UDim2.new(0.02, 0, 0, 120)
score.Size = UDim2.new(0.24, 0, 0, 112)
score.BackgroundColor3 = Color3.fromRGB(20, 34, 48)
score.BackgroundTransparency = 0.2
score.ScrollBarThickness = 4
score.BorderSizePixel = 0
score.Parent = hud
local result = panel("RaceResults")
label(result, "Title", "نتيجة السباق 🏁", UDim2.fromScale(0.03, 0.02), UDim2.fromScale(0.94, 0.12), 28)
local rows = Instance.new("ScrollingFrame")
rows.Name = "Rows"
rows.BackgroundTransparency = 1
rows.Position = UDim2.fromScale(0.04, 0.18)
rows.Size = UDim2.fromScale(0.92, 0.54)
rows.ScrollBarThickness = 5
rows.BorderSizePixel = 0
rows.Parent = result
local notice = label(hud, "Notice", "", UDim2.new(0.3, 0, 1, -125), UDim2.new(0.46, 0, 0, 34), 18)
notice.BackgroundTransparency = 0.25
notice.BackgroundColor3 = Color3.fromRGB(20, 34, 48)
local latest, localCars, cameraOwned = nil, {}, false
local modelFolder = Instance.new("Folder")
modelFolder.Name = "LocalMicroRacers"
modelFolder.Parent = workspace
local held = { throttle = {}, brake = {}, left = {}, right = {}, boost = {} }
local touches, seq, packetTime = {}, 0, 0
local highCamera = false
local function clearInput()
	for _, v in pairs(held) do
		table.clear(v)
	end
	table.clear(touches)
end
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
}
local function raceInterface(active)
	interfaceActive = active
	if active then
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
local function cleanup()
	raceInterface(false)
	for _, attribute in { "RaceTrack", "RacePhase", "RaceId", "RaceLap", "RaceGate" } do
		p:SetAttribute(attribute, nil)
	end
	clearInput()
	latest = nil
	hud.Visible = false
	for _, c in pairs(localCars) do
		c.model:Destroy()
	end
	table.clear(localCars)
	controls:Enable()
	if cameraOwned then
		cameraOwned = false
		workspace.CurrentCamera.CameraType = Enum.CameraType.Custom
		local hum = p.Character and p.Character:FindFirstChildOfClass("Humanoid")
		if hum then
			local camera = workspace.CurrentCamera
			camera.CameraSubject = hum
		end
	end
end
local function call(action, arg)
	local ok, res = pcall(request.InvokeServer, request, action, arg)
	if not ok or type(res) ~= "table" then
		res = { error = "تعذر الاتصال؛ أعد المحاولة" }
	end
	if res.error then
		menuMessage.Text = res.error
		notice.Text = res.error
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
local function actionButton(name, text, x, action)
	local b = button(hud, name, text, UDim2.new(x, 0, 1, -78), UDim2.new(0.10, 0, 0, 62))
	b.InputBegan:Connect(function(v)
		if v.UserInputType == Enum.UserInputType.Touch or v.UserInputType == Enum.UserInputType.MouseButton1 then
			held[action][v] = true
			touches[v] = action
		end
	end)
	return b
end
actionButton("SteerLeft", "←", 0.02, "left")
actionButton("SteerRight", "→", 0.13, "right")
actionButton("Throttle", "تسارع ↑", 0.76, "throttle")
actionButton("Brake", "فرامل ↓", 0.87, "brake")
actionButton("Boost", "سرعة ⚡", 0.32, "boost")
button(hud, "Recover", "استعادة", UDim2.new(0.44, 0, 1, -78), UDim2.new(0.10, 0, 0, 62), function()
	call("recover")
end)
button(hud, "Exit", "خروج", UDim2.new(0.56, 0, 1, -78), UDim2.new(0.10, 0, 0, 62), function()
	call("leave")
end)
button(hud, "Camera", "الكاميرا", UDim2.new(0.02, 0, 1, -146), UDim2.new(0.14, 0, 0, 44), function()
	highCamera = not highCamera
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
local keys = {
	[Enum.KeyCode.W] = "throttle",
	[Enum.KeyCode.Up] = "throttle",
	[Enum.KeyCode.S] = "brake",
	[Enum.KeyCode.Down] = "brake",
	[Enum.KeyCode.A] = "left",
	[Enum.KeyCode.Left] = "left",
	[Enum.KeyCode.D] = "right",
	[Enum.KeyCode.Right] = "right",
	[Enum.KeyCode.Space] = "boost",
}
UIS.InputBegan:Connect(function(v, processed)
	if not hud.Visible or processed or UIS:GetFocusedTextBox() then
		return
	end
	local action = keys[v.KeyCode]
	if action then
		held[action][v.KeyCode] = true
	end
end)
UIS.InputEnded:Connect(function(v)
	local action = keys[v.KeyCode]
	if action then
		held[action][v.KeyCode] = nil
	end
	local touch = touches[v]
	if touch then
		held[touch][v] = nil
		touches[v] = nil
	end
end)
UIS.WindowFocusReleased:Connect(clearInput)
local function active(name)
	return next(held[name]) ~= nil
end
local palette = {
	Color3.fromRGB(87, 231, 195),
	Color3.fromRGB(245, 167, 110),
	Color3.fromRGB(166, 151, 247),
	Color3.fromRGB(111, 189, 245),
}
local function carModel(c)
	local model = world.VehicleTemplate:Clone()
	model.Name = "RaceCar_" .. c.id
	model.PrimaryPart = model.Body
	model.Parent = modelFolder
	for _, v in model:GetDescendants() do
		if v:IsA("BasePart") then
			v.CanCollide = false
			v.CanTouch = false
			v.CanQuery = false
		end
	end
	model.Body.Color = palette[(tonumber(c.id) or #c.id) % #palette + 1]
	local glow = Instance.new("Highlight")
	glow.Name = "Shield"
	glow.FillColor = Color3.fromRGB(174, 148, 244)
	glow.FillTransparency = 0.6
	glow.OutlineTransparency = 0.2
	glow.Parent = model
	local bb = Instance.new("BillboardGui")
	bb.Name = "DriverName"
	bb.Size = UDim2.fromOffset(160, 26)
	bb.StudsOffset = Vector3.new(0, 5, 0)
	bb.MaxDistance = 100
	bb.Adornee = model.Body
	bb.Parent = model
	label(bb, "Name", c.name .. (c.bot and " • آلي" or ""), UDim2.new(), UDim2.fromScale(1, 1), 16)
	local tail = Instance.new("Part")
	tail.Name = "BoostFlame"
	tail.Size = Vector3.new(2, 1, 3)
	tail.Anchored = true
	tail.CanCollide = false
	tail.CanQuery = false
	tail.CanTouch = false
	tail.Material = Enum.Material.Neon
	tail.Color = Color3.fromRGB(95, 213, 255)
	tail.Parent = model
	return { model = model, frame = nil, flame = tail, shield = glow }
end
local function standings(parent, cars)
	parent:ClearAllChildren()
	parent.CanvasSize = UDim2.fromOffset(0, #cars * 30)
	for i, c in ipairs(cars) do
		local text = ("%d. %s %s"):format(i, c.name, c.finished and ("%.1fث"):format(c.finishTime or 0) or "")
		label(parent, "Rank_" .. c.id, text, UDim2.fromOffset(0, (i - 1) * 30), UDim2.new(1, -8, 0, 28), 18)
	end
end
event.OnClientEvent:Connect(function(data)
	if type(data) ~= "table" then
		return
	end
	if data.kind == "error" then
		notice.Text = data.message
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
		menuMessage.Text =
			"اختر حلبة • Solo مع منافسين آليين أو سباق مع الأصدقاء\n3 لفات • W/A/S/D أو الأسهم • Space للتعزيز"
		return
	end
	if not D.get(data.track) or type(data.cars) ~= "table" then
		return
	end
	if not latest or latest.raceId ~= data.raceId then
		for _, c in pairs(localCars) do
			c.model:Destroy()
		end
		table.clear(localCars)
		clearInput()
		seq = 0
	end
	latest = data
	raceInterface(true)
	menu.Visible = false
	local own
	for _, c in ipairs(data.cars) do
		if c.id == data.you then
			own = c
		end
		if not localCars[c.id] then
			localCars[c.id] = carModel(c)
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
		end
	end
	hud.Visible = data.phase ~= "results"
	result.Visible = data.phase == "results"
	cameraOwned = true
	if data.phase == "results" then
		clearInput()
		controls:Enable()
	else
		controls:Disable()
	end
	if own then
		p:SetAttribute("RaceX", own.x)
		p:SetAttribute("RaceZ", own.z)
		p:SetAttribute("RaceHeading", own.heading)
		p:SetAttribute("RaceTrack", data.track)
		p:SetAttribute("RacePhase", data.phase)
		p:SetAttribute("RaceId", data.raceId)
		p:SetAttribute("RaceLap", own.lap)
		p:SetAttribute("RaceGate", own.gate)
		if data.phase == "queue" then
			status.Text = ("%s\nالبداية خلال %d • استعد للتوجيه والتسارع"):format(
				D.get(data.track).ar,
				math.ceil(data.countdown)
			)
		elseif own.finished then
			status.Text = ("أنهيت السباق بالمركز %d\nالزمن %.1f ثانية • انتظار بقية المتسابقين"):format(
				own.rank,
				own.finishTime or 0
			)
		else
			status.Text = ("لفة %d من 3 • المركز %d\nسرعة %d • باقي %dث • البوابة %d"):format(
				own.lap,
				own.rank,
				math.floor(own.speed),
				math.ceil(data.remaining),
				own.gate
			)
		end
		hud.Boost.Text = own.boostReady > 0 and ("سرعة\n%ds"):format(math.ceil(own.boostReady)) or "سرعة ⚡"
		notice.Text = own.shield and "◇ الدرع جاهز لصد عائق واحد"
			or "توجيه + تسارع • استعادة عند التعطل"
	end
	standings(score, data.cars)
	if data.phase == "results" then
		standings(rows, data.cars)
	end
end)
p.CharacterAdded:Connect(function()
	cleanup()
	menu.Visible = false
	result.Visible = false
end)
Run.RenderStepped:Connect(function(dt)
	if not latest or not cameraOwned then
		return
	end
	local track = D.get(latest.track)
	local ownFrame
	for _, c in ipairs(latest.cars) do
		local rendered = localCars[c.id]
		if rendered then
			local target = CFrame.new(track.origin[1] + c.x, track.origin[2] + 1.3, track.origin[3] + c.z)
				* CFrame.Angles(0, c.heading, 0)
			rendered.frame = rendered.frame and rendered.frame:Lerp(target, math.min(1, dt * 14)) or target
			rendered.model:PivotTo(rendered.frame)
			rendered.flame.CFrame = rendered.frame * CFrame.new(0, 0, -5)
			rendered.flame.Transparency = c.boost and 0.15 or 1
			rendered.shield.Enabled = c.shield
			if c.id == latest.you then
				ownFrame = rendered.frame
			end
		end
	end
	if ownFrame then
		local forward = ownFrame.LookVector * -1
		local focus = ownFrame.Position + forward * 6
		local desired = ownFrame.Position
			- forward * (highCamera and 16 or 23)
			+ Vector3.new(0, highCamera and 32 or 14, 0)
		local params = RaycastParams.new()
		params.FilterType = Enum.RaycastFilterType.Exclude
		params.FilterDescendantsInstances = { modelFolder, p.Character, world.VehicleTemplate }
		params.RespectCanCollide = true
		local hit = workspace:Raycast(focus, desired - focus, params)
		if hit then
			desired = hit.Position + hit.Normal * 2
		end
		local cam = workspace.CurrentCamera
		cam.CameraType = Enum.CameraType.Scriptable
		local cf = CFrame.lookAt(desired, focus)
		cam.CFrame = cam.CFrame:Lerp(cf, math.min(1, dt * 10))
	end
	packetTime += dt
	if packetTime > 0.08 and latest.phase == "running" then
		packetTime = 0
		seq += 1
		input:FireServer(latest.raceId, seq, {
			throttle = active("throttle") and 1 or 0,
			brake = active("brake") and 1 or 0,
			-- v59: a heading increase turns the car to the LEFT of the chase camera, so right = -1 (was reversed)
			steer = (active("left") and 1 or 0) - (active("right") and 1 or 0),
			boost = active("boost"),
		})
	end
end)
