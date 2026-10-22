-- Cell Train: board at the station, ride a real train model through the giant purple cell, return to the station.
-- Map provides: "TrainStart" pad, the parked "TrainTemplate" model (cloned locally for the ride; v62: one child Model
-- per car, each with a "Base" part), an invisible track of parts named "WP|<index>|<stop id>" and name anchors
-- "CellName|<stop id>". v62 teaching: the map only names the structures (billboards here); what each one does is
-- explained on screen (Shared/CellStops) while the train waits at its stop. Everything here is local to the rider.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer
local mapFolder = workspace:WaitForChild("Map")
local CellStops = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("CellStops"))

local CRUISE, SLOW = 16, 6 -- studs/s; slows down near each stop
local DWELL = 12 -- reading time; the rider can pause for longer (fast mode: no wait)
local LIFT = 0.9 -- car pivot above the track centre line (wheels sit on the rails)

local points, labels, anchors = {}, {}, {}
local startPad, template
local startPads = {}
for _, inst in ipairs(mapFolder:GetDescendants()) do
	if inst:IsA("BasePart") then
		local args = string.split(inst.Name, "|")
		if args[1] == "WP" and tonumber(args[2]) then
			local i = tonumber(args[2])
			points[i] = inst.Position
			if args[3] and args[3] ~= "" then
				labels[i] = args[3]
			end
		elseif args[1] == "CellName" and args[2] then
			anchors[args[2]] = inst
		elseif inst.Name == "TrainStart" then
			startPad = startPad or inst
			table.insert(startPads, inst)
		end
	elseif inst:IsA("Model") and inst.Name == "TrainTemplate" then
		template = inst
	end
end
if not (startPad and template) or #points < 2 then
	warn("CellTrain: station, train or track missing")
	return
end

local dist = { 0 }
for i = 2, #points do
	dist[i] = dist[i - 1] + (points[i] - points[i - 1]).Magnitude
end
local total = dist[#points]
local stops = {}
for i, id in pairs(labels) do
	if CellStops[id] then
		table.insert(stops, { at = dist[i], id = id, info = CellStops[id] })
	end
end
table.sort(stops, function(a, b)
	return a.at < b.at
end)

local function sample(d)
	d = math.clamp(d, 0, total)
	for i = 2, #points do
		if dist[i] >= d then
			local a = (d - dist[i - 1]) / math.max(dist[i] - dist[i - 1], 1e-3)
			return points[i - 1]:Lerp(points[i], a)
		end
	end
	return points[#points]
end

-- a car spans from its rear axle to its front axle; aiming it along that chord keeps it on curved rails
local function carFrame(dc, half)
	local front, rear = sample(dc + half), sample(dc - half)
	local mid = (front + rear) / 2
	local fwd = front - rear
	if fwd.Magnitude < 1e-3 then
		fwd = Vector3.new(0, 0, -1)
	end
	return CFrame.lookAt(mid, mid + fwd.Unit) * CFrame.new(0, LIFT, 0)
end

-- the latest stop whose window we are in (the nucleus stops are close together, the newest one wins)
local function nearStop(d)
	local found = nil
	for _, stop in ipairs(stops) do
		if d > stop.at - 12 and d < stop.at + 50 then -- 12: the closest two stops are 15 apart
			found = stop
		end
	end
	return found
end

-- name tags: only the structure's name in the world ------------------------
local tags = {}
for id, part in pairs(anchors) do
	local info = CellStops[id]
	if info then
		local bb = Instance.new("BillboardGui")
		bb.Name = "CellNameTag"
		bb.Size = UDim2.fromScale(26, 6) -- studs: stays in proportion with the organelles
		bb.LightInfluence = 0
		bb.MaxDistance = 320
		bb.AlwaysOnTop = false
		local frame = Instance.new("Frame")
		frame.Size = UDim2.fromScale(1, 1)
		frame.BackgroundColor3 = Color3.fromRGB(40, 16, 70)
		frame.BackgroundTransparency = 0.25
		frame.Parent = bb
		Instance.new("UICorner", frame).CornerRadius = UDim.new(0.3, 0)
		local stroke = Instance.new("UIStroke")
		stroke.Parent = frame
		stroke.Color = Color3.fromRGB(255, 170, 235)
		stroke.Thickness = 2
		stroke.Transparency = 0.4
		local ar = Instance.new("TextLabel")
		ar.BackgroundTransparency = 1
		ar.Size = UDim2.fromScale(0.92, 0.6)
		ar.Position = UDim2.fromScale(0.04, 0.04)
		ar.Font = Enum.Font.GothamBold
		ar.TextScaled = true
		ar.TextColor3 = Color3.new(1, 1, 1)
		ar.Text = info.ar
		ar.Parent = frame
		local en = ar:Clone()
		en.Size = UDim2.fromScale(0.92, 0.32)
		en.Position = UDim2.fromScale(0.04, 0.64)
		en.Font = Enum.Font.Gotham
		en.TextColor3 = Color3.fromRGB(255, 200, 240)
		en.Text = info.en
		en.Parent = frame
		bb.Adornee = part
		bb.Parent = part
		tags[id] = { frame = frame, stroke = stroke }
	end
end
local function highlightTag(id)
	for key, t in pairs(tags) do
		local on = key == id
		t.frame.BackgroundColor3 = on and Color3.fromRGB(150, 50, 140) or Color3.fromRGB(40, 16, 70)
		t.stroke.Transparency = on and 0 or 0.4
	end
end

-- UI ---------------------------------------------------------------
local gui = Instance.new("ScreenGui")
gui.Name = "CellTrainGui"
gui.ResetOnSpawn = false
gui.IgnoreGuiInset = true
gui.DisplayOrder = 25
gui.Parent = player:WaitForChild("PlayerGui")

local fade = Instance.new("Frame")
fade.Size = UDim2.fromScale(1, 1)
fade.BackgroundColor3 = Color3.new(0, 0, 0)
fade.BackgroundTransparency = 1
fade.ZIndex = 10
fade.Parent = gui

-- the lesson card: name, what it does, one fact; fades in and out
local card = Instance.new("CanvasGroup")
card.Name = "LessonCard"
card.AnchorPoint = Vector2.new(0.5, 1)
card.Position = UDim2.fromScale(0.5, 0.97)
card.Size = UDim2.fromScale(0.62, 0.3)
card.BackgroundColor3 = Color3.fromRGB(30, 12, 54)
card.BackgroundTransparency = 0.12
card.GroupTransparency = 1
card.Visible = false
card.Parent = gui
Instance.new("UICorner", card).CornerRadius = UDim.new(0.08, 0)
local cardStroke = Instance.new("UIStroke")
cardStroke.Parent = card
cardStroke.Color = Color3.fromRGB(255, 160, 230)
cardStroke.Thickness = 2
local sizeLimit = Instance.new("UISizeConstraint")
sizeLimit.Parent = card
sizeLimit.MaxSize = Vector2.new(820, 260)

local function cardLabel(name, pos, size, font, color, align)
	local l = Instance.new("TextLabel")
	l.Name = name
	l.BackgroundTransparency = 1
	l.Position = pos
	l.Size = size
	l.Font = font
	l.TextScaled = true
	l.TextWrapped = true
	l.TextColor3 = color
	l.TextXAlignment = align or Enum.TextXAlignment.Right
	l.Parent = card
	return l
end
local cardTitle = cardLabel(
	"Title",
	UDim2.fromScale(0.3, 0.05),
	UDim2.fromScale(0.66, 0.22),
	Enum.Font.GothamBlack,
	Color3.new(1, 1, 1)
)
local cardEn = cardLabel(
	"English",
	UDim2.fromScale(0.04, 0.07),
	UDim2.fromScale(0.3, 0.16),
	Enum.Font.GothamMedium,
	Color3.fromRGB(255, 190, 235),
	Enum.TextXAlignment.Left
)
local cardBody = cardLabel(
	"Body",
	UDim2.fromScale(0.04, 0.3),
	UDim2.fromScale(0.92, 0.42),
	Enum.Font.GothamMedium,
	Color3.fromRGB(240, 235, 250)
)
local cardFact = cardLabel(
	"Fact",
	UDim2.fromScale(0.04, 0.75),
	UDim2.fromScale(0.92, 0.2),
	Enum.Font.Gotham,
	Color3.fromRGB(255, 220, 130)
)
local cardShown = nil
local function showCard(stop)
	local id = stop and stop.id
	if id == cardShown then
		return
	end
	cardShown = id
	highlightTag(id)
	if stop then
		cardTitle.Text = stop.info.ar
		cardEn.Text = stop.info.en
		cardBody.Text = stop.info.body
		cardFact.Text = "💡 " .. stop.info.fact
		card.Visible = true
		TweenService:Create(card, TweenInfo.new(0.45, Enum.EasingStyle.Quad), { GroupTransparency = 0 }):Play()
	else
		local tw = TweenService:Create(card, TweenInfo.new(0.45, Enum.EasingStyle.Quad), { GroupTransparency = 1 })
		tw:Play()
		tw.Completed:Connect(function()
			if cardShown == nil then
				card.Visible = false
			end
		end)
	end
end

local function button(name, y, color, text)
	local b = Instance.new("TextButton")
	b.Name = name
	b.AnchorPoint = Vector2.new(1, 0)
	b.Position = UDim2.fromScale(0.98, y)
	b.Size = UDim2.fromScale(0.14, 0.065)
	b.BackgroundColor3 = color
	b.TextColor3 = Color3.new(1, 1, 1)
	b.TextScaled = true
	b.Font = Enum.Font.GothamBold
	b.Text = text
	b.Visible = false
	b.Parent = gui
	Instance.new("UICorner", b).CornerRadius = UDim.new(0.25, 0)
	return b
end
-- v30: top-right under the Discord/code buttons (top-left drew over the coins panel)
local exitBtn = button("ExitBtn", 0.24, Color3.fromRGB(150, 50, 60), "خروج")
local camBtn = button("CamToggleBtn", 0.325, Color3.fromRGB(70, 50, 130), "🎥 كاميرا: سينمائية")
local speedBtn = button("SpeedToggleBtn", 0.405, Color3.fromRGB(45, 110, 145), "⚡ السرعة: عادية")
local pauseBtn = button("PauseReadingBtn", 0.485, Color3.fromRGB(48, 100, 92), "توقف للقراءة")

local stopBadge = Instance.new("TextLabel")
stopBadge.Name = "StopProgressBadge"
stopBadge.AnchorPoint = Vector2.new(0.5, 0)
stopBadge.Position = UDim2.fromScale(0.5, 0.12)
stopBadge.Size = UDim2.fromScale(0.26, 0.055)
stopBadge.BackgroundColor3 = Color3.fromRGB(55, 25, 95)
stopBadge.BackgroundTransparency = 0.15
stopBadge.TextColor3 = Color3.fromRGB(235, 220, 255)
stopBadge.TextScaled = true
stopBadge.Font = Enum.Font.GothamBold
stopBadge.Visible = false
stopBadge.Parent = gui
Instance.new("UICorner", stopBadge).CornerRadius = UDim.new(0.3, 0)

local freeCam = false
local fastMode = false
local paused = false
local hum -- the rider's Humanoid during a ride

local function applyCam()
	camBtn.Text = freeCam and "🔄 كاميرا: حرة" or "🎥 كاميرا: سينمائية"
	local cam = workspace.CurrentCamera
	cam.CameraType = freeCam and Enum.CameraType.Custom or Enum.CameraType.Scriptable
	if freeCam and hum then
		cam.CameraSubject = hum
	end
end
camBtn.Activated:Connect(function()
	freeCam = not freeCam
	applyCam()
end)
speedBtn.Activated:Connect(function()
	fastMode = not fastMode
	speedBtn.Text = fastMode and "⚡ السرعة: سريعة" or "⚡ السرعة: عادية"
end)
pauseBtn.Activated:Connect(function()
	paused = not paused
	pauseBtn.Text = paused and "كمّل الرحلة" or "توقف للقراءة"
end)

local function fadeTo(alpha)
	local tw = TweenService:Create(fade, TweenInfo.new(0.6), { BackgroundTransparency = alpha })
	tw:Play()
	tw.Completed:Wait()
end

-- ride -------------------------------------------------------------
local riding, stopRequested = false, false
local skipReturn = false -- a server teleport ended the ride: do not walk the player back to the boarding pad
_G.BSCStopCellTrain = function()
	if riding then
		stopRequested, skipReturn = true, true
	end
end
local TURN = CFrame.Angles(0, math.rad(90), 0) -- the cars are built along +X; travel frames look along -Z

local function ride()
	if riding then
		return
	end
	local char = player.Character
	hum = char and char:FindFirstChildOfClass("Humanoid")
	local root = char and char:FindFirstChild("HumanoidRootPart")
	if not (hum and root) then
		return
	end
	riding, stopRequested, skipReturn = true, false, false
	local milestone = ReplicatedStorage:FindFirstChild("Milestone")
	if milestone then
		milestone:FireServer("trainStart")
	end
	local oldSpeed, oldJump = hum.WalkSpeed, hum.JumpPower
	hum.WalkSpeed, hum.JumpPower = 0, 0

	fadeTo(0)
	local train = template:Clone()
	train.Name = "LocalCellTrain"
	train.Parent = workspace
	-- each car keeps its distance behind the locomotive's centre (from the parked layout)
	local cars = {}
	local loco = train:FindFirstChild("Loco")
	local locoBase = loco and loco:FindFirstChild("Base")
	for _, m in ipairs(train:GetChildren()) do
		local base = m:IsA("Model") and m:FindFirstChild("Base")
		if base and locoBase then
			m.PrimaryPart = base
			table.insert(cars, {
				model = m,
				back = (locoBase.Position - base.Position).Magnitude,
				half = base.Size.X / 2 - 1,
			})
		end
	end
	local rideCar = train:FindFirstChild("Car1")
	local seat = rideCar and rideCar:FindFirstChild("Seat1")
	local rideBack = 0
	for _, c in ipairs(cars) do
		if c.model == rideCar then
			rideBack = c.back
		end
	end
	root.Anchored = true
	local cam = workspace.CurrentCamera
	freeCam, fastMode, paused = false, false, false
	speedBtn.Text = "⚡ السرعة: عادية"
	pauseBtn.Text = "توقف للقراءة"
	pauseBtn.Visible = true
	applyCam()
	exitBtn.Visible, camBtn.Visible, speedBtn.Visible, stopBadge.Visible = true, true, true, true

	-- start with the whole train on the rails (the rear cars sit behind the locomotive)
	local d = 0
	for _, c in ipairs(cars) do
		d = math.max(d, c.back + c.half + 1)
	end
	local camCF = nil
	local waitUntil, waitedFor = 0, {}
	local function place(dt)
		for _, c in ipairs(cars) do
			c.model:PivotTo(carFrame(d - c.back, c.half) * TURN)
		end
		local seatFrame = carFrame(d - rideBack, 4)
		if seat then
			local sp = seat.Position + Vector3.new(0, 2.4, 0)
			root.CFrame = CFrame.lookAt(sp, sp + seatFrame.LookVector)
		end
		local stop = nearStop(d)
		if not freeCam then
			-- behind and above the rider; near a stop the camera turns to the structure being explained
			local want = seatFrame * CFrame.new(-10, 12, 22)
			local look = seatFrame * Vector3.new(0, 2, -40)
			local anchor = stop and anchors[stop.id]
			if anchor then
				look = look:Lerp(anchor.Position, 0.75)
			end
			local target = CFrame.lookAt(want.Position, look)
			camCF = camCF and camCF:Lerp(target, math.clamp(dt * 2.5, 0, 1)) or target
			cam.CFrame = camCF
		end
		local passed = 0
		for _, st in ipairs(stops) do
			if d >= st.at - 30 then
				passed += 1
			end
		end
		stopBadge.Text = ("📍 المحطة %d/%d"):format(passed, #stops)
		showCard(stop)
	end
	place(1)
	task.wait(0.1)
	fadeTo(1)

	local finished = false
	-- dying or resetting mid-ride must not leave the camera locked or the ride flag stuck
	local diedConn = hum.Died:Connect(function()
		stopRequested = true
	end)
	local conn
	conn = RunService.RenderStepped:Connect(function(dt)
		if finished then
			return
		end
		-- the train waits at every stop so the card can be read (fast mode rolls through)
		if (paused or (os.clock() < waitUntil and not fastMode)) and not stopRequested then
			place(dt)
			return
		end
		local mult = fastMode and 1.8 or 1.0
		local nd = d + (nearStop(d) and SLOW or CRUISE) * mult * dt
		for _, st in ipairs(stops) do
			if d < st.at and nd >= st.at and not waitedFor[st.id] then
				waitedFor[st.id] = true
				waitUntil = os.clock() + DWELL
				if not fastMode then
					nd = st.at -- a slow frame must not skip the stop and its lesson card
					break
				end
			end
		end
		d = nd
		if d >= total or stopRequested then
			finished = true
			if d >= total and milestone then
				milestone:FireServer("trainFinish")
			end
			conn:Disconnect()
			diedConn:Disconnect()
			task.spawn(function()
				fadeTo(0)
				train:Destroy()
				showCard(nil)
				pauseBtn.Visible = false
				paused = false
				highlightTag(nil)
				exitBtn.Visible, camBtn.Visible, speedBtn.Visible, stopBadge.Visible = false, false, false, false
				cam.CameraType = Enum.CameraType.Custom
				cam.CameraSubject = hum
				root.Anchored = false
				hum.WalkSpeed, hum.JumpPower = oldSpeed, oldJump
				if hum.Health > 0 and char.Parent and not skipReturn then
					char:PivotTo(startPad.CFrame * CFrame.new(-8, 4, -4))
				end
				fadeTo(1)
				riding = false
			end)
			return
		end
		place(dt)
	end)
end

exitBtn.Activated:Connect(function()
	stopRequested = true
end)

for _, pad in ipairs(startPads) do
	pad.Touched:Connect(function(hit)
		if not riding and player.Character and hit:IsDescendantOf(player.Character) then
			startPad = pad -- come back to the pad you boarded from
			ride()
		end
	end)
end
