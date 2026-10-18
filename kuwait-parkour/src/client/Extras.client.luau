-- Graduation photo frame (with shutter + confetti) and the Virus Tag banner.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer
local gui = Instance.new("ScreenGui")
gui.Name = "Extras"
gui.ResetOnSpawn = false
gui.IgnoreGuiInset = true
gui.DisplayOrder = 26
gui.Parent = player:WaitForChild("PlayerGui")

local function play(name)
	if _G.BSCPlay then
		_G.BSCPlay(name)
	end
end

-- ------------------------------------------------------------------ graduation photo
local frame = Instance.new("Frame")
frame.Size = UDim2.fromScale(1, 1)
frame.BackgroundTransparency = 1
frame.Visible = false
frame.Parent = gui
local border = Instance.new("UIStroke", frame)
border.Thickness = 18
border.Color = Color3.fromRGB(230, 190, 70)
local flash = Instance.new("Frame")
flash.Size = UDim2.fromScale(1, 1)
flash.BackgroundColor3 = Color3.new(1, 1, 1)
flash.BackgroundTransparency = 1
flash.Parent = gui
local caption = Instance.new("TextLabel")
caption.AnchorPoint = Vector2.new(0.5, 1)
caption.Position = UDim2.fromScale(0.5, 0.95)
caption.Size = UDim2.fromScale(0.6, 0.12)
caption.BackgroundColor3 = Color3.fromRGB(24, 80, 56)
caption.TextColor3 = Color3.new(1, 1, 1)
caption.TextScaled = true
caption.Font = Enum.Font.GothamBold
caption.Parent = frame
Instance.new("UICorner", caption).CornerRadius = UDim.new(0.2, 0)

local function confetti()
	local char = player.Character
	local root = char and char:FindFirstChild("HumanoidRootPart")
	if not root then
		return
	end
	local a = Instance.new("Attachment")
	a.Position = Vector3.new(0, 6, 0)
	a.Parent = root
	local e = Instance.new("ParticleEmitter")
	e.Color = ColorSequence.new({
		ColorSequenceKeypoint.new(0, Color3.fromRGB(250, 222, 170)),
		ColorSequenceKeypoint.new(0.5, Color3.fromRGB(220, 165, 238)),
		ColorSequenceKeypoint.new(1, Color3.fromRGB(160, 218, 236)),
	})
	e.Size = NumberSequence.new(0.35)
	e.Lifetime = NumberRange.new(2, 3)
	e.Speed = NumberRange.new(8, 16)
	e.SpreadAngle = Vector2.new(70, 70)
	e.Acceleration = Vector3.new(0, -14, 0)
	e.Rotation = NumberRange.new(0, 360)
	e.RotSpeed = NumberRange.new(-200, 200)
	e.Rate = 0
	e.Parent = a
	e:Emit(120)
	task.delay(4, function()
		a:Destroy()
	end)
end

local grad = ReplicatedStorage:WaitForChild("Graduate", 30)
if grad then
	grad.OnClientEvent:Connect(function()
		caption.Text = ("🎓 %s\nخريج كلية العلوم — جامعة الكويت • دفعة %s"):format(
			player.DisplayName,
			os.date("%Y")
		)
		frame.Visible = true
		flash.BackgroundTransparency = 0
		play("sting")
		TweenService:Create(flash, TweenInfo.new(0.6), { BackgroundTransparency = 1 }):Play()
		confetti()
		task.delay(6, function()
			frame.Visible = false
		end)
	end)
end

-- ------------------------------------------------------------------ Virus Tag banner
local banner = Instance.new("TextLabel")
banner.AnchorPoint = Vector2.new(0.5, 0)
banner.Position = UDim2.fromScale(0.5, 0.17)
banner.Size = UDim2.fromScale(0.42, 0.065)
banner.BackgroundColor3 = Color3.fromRGB(70, 24, 60)
banner.BackgroundTransparency = 0.1
banner.TextColor3 = Color3.new(1, 1, 1)
banner.TextScaled = true
banner.Font = Enum.Font.GothamBold
banner.Visible = false
banner.Parent = gui
Instance.new("UICorner", banner).CornerRadius = UDim.new(0.3, 0)

local function nearArena()
	local char = player.Character
	local root = char and char:FindFirstChild("HumanoidRootPart")
	return root and root.Position.Z < -12450 and root.Position.Z > -12750
end

RunService.Heartbeat:Connect(function()
	if not nearArena() then
		banner.Visible = false
		return
	end
	banner.Visible = true
	local phase = workspace:GetAttribute("VirusPhase")
	local left = math.max(0, math.ceil((workspace:GetAttribute("VirusEnds") or 0) - workspace:GetServerTimeNow()))
	local me = player:GetAttribute("Virus")
	if phase == "running" then
		if me == "infected" then
			banner.Text = ("🦠 أنت فيروس — المس الأصحاء! ⏱ %d"):format(left)
			banner.BackgroundColor3 = Color3.fromRGB(40, 110, 30)
		elseif me == "healthy" then
			banner.Text = ("🏃 اهرب وجمّع اللقاح 💉 ⏱ %d"):format(left)
			banner.BackgroundColor3 = Color3.fromRGB(30, 70, 120)
		else
			banner.Text = ("الجولة شغالة… انتظر الجولة الجاية ⏱ %d"):format(left)
			banner.BackgroundColor3 = Color3.fromRGB(70, 24, 60)
		end
	elseif phase == "countdown" then
		banner.Text = ("🦠 الجولة تبدأ بعد %d…"):format(left)
		banner.BackgroundColor3 = Color3.fromRGB(110, 40, 90)
	else
		banner.Text = ("🦠 لعبة الفيروس: تحتاج لاعبين أو أكثر (%d هنا) — جيب ربعك!"):format(
			workspace:GetAttribute("VirusCount") or 1
		)
		banner.BackgroundColor3 = Color3.fromRGB(70, 24, 60)
	end
end)
