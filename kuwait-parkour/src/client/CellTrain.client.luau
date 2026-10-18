-- Cell Train: board at the station, ride a real train model through the giant purple cell, return to the station.
-- Map provides: "TrainStart" pad, the parked "TrainTemplate" model (cloned locally for the ride) and an
-- invisible track of parts named "WP|<index>|<label>". Everything here is local to the rider.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer
local mapFolder = workspace:WaitForChild("Map")

local CRUISE, SLOW = 16, 7 -- studs/s; slows down near each labelled stop

local points, labels = {}, {}
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
for i, text in pairs(labels) do
	table.insert(stops, { at = dist[i], text = text })
end

local function sample(d)
	for i = 2, #points do
		if dist[i] >= d then
			local a = (d - dist[i - 1]) / math.max(dist[i] - dist[i - 1], 1e-3)
			return points[i - 1]:Lerp(points[i], a), (points[i] - points[i - 1]).Unit, i
		end
	end
	return points[#points], (points[#points] - points[#points - 1]).Unit, #points
end

-- the stop the train is currently slowing for, if any
local function nearStop(d)
	for _, stop in ipairs(stops) do
		if d > stop.at - 25 and d < stop.at + 35 then
			return stop
		end
	end
	return nil
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

local caption = Instance.new("TextLabel")
caption.AnchorPoint = Vector2.new(0.5, 1)
caption.Position = UDim2.fromScale(0.5, 0.93)
caption.Size = UDim2.fromScale(0.72, 0.11)
caption.BackgroundColor3 = Color3.fromRGB(40, 16, 70)
caption.BackgroundTransparency = 0.15
caption.TextColor3 = Color3.new(1, 1, 1)
caption.TextScaled = true
caption.Font = Enum.Font.GothamBold
caption.Visible = false
caption.Parent = gui
Instance.new("UICorner", caption).CornerRadius = UDim.new(0.2, 0)

local exitBtn = Instance.new("TextButton")
-- v30: top-right under the Discord/code buttons (top-left drew over the coins panel)
exitBtn.AnchorPoint = Vector2.new(1, 0)
exitBtn.Position = UDim2.fromScale(0.98, 0.24)
exitBtn.Size = UDim2.fromScale(0.12, 0.07)
exitBtn.BackgroundColor3 = Color3.fromRGB(150, 50, 60)
exitBtn.TextColor3 = Color3.new(1, 1, 1)
exitBtn.TextScaled = true
exitBtn.Font = Enum.Font.GothamBold
exitBtn.Text = "خروج"
exitBtn.Visible = false
exitBtn.Parent = gui
Instance.new("UICorner", exitBtn).CornerRadius = UDim.new(0.25, 0)

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
local TURN = CFrame.Angles(0, math.rad(90), 0) -- the model is built along +X; travel frames look along -Z

local function ride()
	if riding then
		return
	end
	local char = player.Character
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	local root = char and char:FindFirstChild("HumanoidRootPart")
	if not (hum and root) then
		return
	end
	riding, stopRequested, skipReturn = true, false, false
	local milestone = game:GetService("ReplicatedStorage"):FindFirstChild("Milestone")
	if milestone then
		milestone:FireServer("trainStart")
	end
	local oldSpeed, oldJump = hum.WalkSpeed, hum.JumpPower
	hum.WalkSpeed, hum.JumpPower = 0, 0

	fadeTo(0)
	local train = template:Clone()
	train.Name = "LocalCellTrain"
	train.PrimaryPart = train:FindFirstChild("Base")
	train.Parent = workspace
	local seat = train:FindFirstChild("Seat1")
	root.Anchored = true
	local cam = workspace.CurrentCamera
	cam.CameraType = Enum.CameraType.Scriptable
	caption.Text =
		"🚋 أهلاً فيك في قطار الخلية! جولة داخل الخلية الحيوانية"
	caption.Visible, exitBtn.Visible = true, true

	local d, shownUntil = 0, os.clock() + 5
	local function place()
		local pos, dir = sample(d)
		local frame = CFrame.lookAt(pos, pos + dir)
		train:PivotTo(frame * TURN)
		if seat then
			local sp = seat.Position + Vector3.new(0, 2.4, 0)
			root.CFrame = CFrame.lookAt(sp, sp + dir)
		end
		-- organelles sit inside the loop, on the train's right: look slightly right, past the rider
		cam.CFrame = frame
			* CFrame.new(-16, 16, 28)
			* CFrame.Angles(0, math.rad(-36), 0)
			* CFrame.Angles(math.rad(-14), 0, 0)
		local stop = nearStop(d)
		if stop then
			caption.Text = stop.text
		end
	end
	place()
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
		d += (nearStop(d) and SLOW or CRUISE) * dt
		if d >= total or stopRequested then
			finished = true
			if d >= total then
				local finishEvent = game:GetService("ReplicatedStorage"):FindFirstChild("Milestone")
				if finishEvent then
					finishEvent:FireServer("trainFinish")
				end
			end
			conn:Disconnect()
			diedConn:Disconnect()
			task.spawn(function()
				fadeTo(0)
				train:Destroy()
				caption.Visible, exitBtn.Visible = false, false
				cam.CameraType = Enum.CameraType.Custom
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
		place()
		caption.Visible = nearStop(d) ~= nil or os.clock() <= shownUntil
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
