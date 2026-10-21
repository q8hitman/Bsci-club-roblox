-- First minutes: a short optional welcome card (new players only; v37: start in the south building, world menu), a glowing guide beam from the player to the
-- parkour gate until they start, and light contextual hints. Also reports the HQ mini-obby summit.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer
local mapFolder = workspace:WaitForChild("Map")
local courseGates = {}
for _, d in ipairs(mapFolder:GetDescendants()) do
	if d.Name == "Portal|Course" and d:IsA("BasePart") then
		table.insert(courseGates, d)
	end
end
local continueGate = courseGates[1]
local obbyTop = mapFolder:FindFirstChild("ObbyTop", true)

task.wait(4) -- let the saved profile arrive
local isNew = (player:GetAttribute("Stage") or 0) == 0 and (player:GetAttribute("Achievements") or 0) == 0

-- ------------------------------------------------------------------ welcome card
if isNew then
	local gui = Instance.new("ScreenGui")
	gui.Name = "Welcome"
	gui.ResetOnSpawn = false
	gui.DisplayOrder = 40
	gui.Parent = player:WaitForChild("PlayerGui")
	local f = Instance.new("Frame")
	f.AnchorPoint = Vector2.new(0.5, 0.5)
	f.Position = UDim2.fromScale(0.5, 0.5)
	f.Size = UDim2.fromScale(0.5, 0.46)
	f.BackgroundColor3 = Color3.fromRGB(24, 80, 56)
	f.Parent = gui
	Instance.new("UICorner", f).CornerRadius = UDim.new(0.06, 0)
	local stroke = Instance.new("UIStroke", f)
	stroke.Color = Color3.fromRGB(120, 255, 200)
	stroke.Thickness = 3
	local lines = {
		{ "أهلاً فيك بكلية العلوم 🧬 نادي العلوم البيولوجية", 0.04, 0.18 },
		{ "إنت الحين في بهو المبنى الجنوبي", 0.26, 0.12 },
		{ "🌍 زر «العوالم» يسار الشاشة ياخذك لأي مكان", 0.4, 0.12 },
		{
			"🏃 باركور • 🚆 قطارات • 🎮 أركيد • 🔬 مختبرات • 🐱 قطاوة مخفية",
			0.54,
			0.12,
		},
	}
	for _, l in ipairs(lines) do
		local t = Instance.new("TextLabel")
		t.BackgroundTransparency = 1
		t.Position = UDim2.fromScale(0.05, l[2])
		t.Size = UDim2.fromScale(0.9, l[3])
		t.TextColor3 = Color3.new(1, 1, 1)
		t.TextScaled = true
		t.Font = Enum.Font.GothamBold
		t.Text = l[1]
		t.Parent = f
	end
	local go = Instance.new("TextButton")
	go.AnchorPoint = Vector2.new(0.5, 1)
	go.Position = UDim2.fromScale(0.5, 0.94)
	go.Size = UDim2.fromScale(0.4, 0.18)
	go.BackgroundColor3 = Color3.fromRGB(255, 220, 90)
	go.TextColor3 = Color3.fromRGB(30, 30, 30)
	go.TextScaled = true
	go.Font = Enum.Font.GothamBold
	go.Text = "🌍 اختر عالمك"
	go.Parent = f
	Instance.new("UICorner", go).CornerRadius = UDim.new(0.3, 0)
	f.Size = UDim2.fromScale(0.1, 0.1)
	TweenService:Create(f, TweenInfo.new(0.4, Enum.EasingStyle.Back), { Size = UDim2.fromScale(0.5, 0.46) }):Play()
	go.Activated:Connect(function()
		if _G.BSCPlay then
			_G.BSCPlay("click")
		end
		gui:Destroy()
		if _G.BSCOpenWorlds then
			_G.BSCOpenWorlds()
		end
	end)
	-- optional: stay and explore the college
	local stay = Instance.new("TextButton")
	stay.AnchorPoint = Vector2.new(1, 0)
	stay.Position = UDim2.fromScale(0.97, 0.03)
	stay.Size = UDim2.fromScale(0.08, 0.12)
	stay.BackgroundColor3 = Color3.fromRGB(150, 50, 50)
	stay.TextColor3 = Color3.new(1, 1, 1)
	stay.TextScaled = true
	stay.Font = Enum.Font.GothamBold
	stay.Text = "X"
	stay.Parent = f
	Instance.new("UICorner", stay).CornerRadius = UDim.new(0.3, 0)
	stay.Activated:Connect(function()
		gui:Destroy()
	end)
	task.delay(25, function()
		if gui.Parent then
			gui:Destroy()
		end
	end)
end

-- ------------------------------------------------------------------ guide beam to the parkour gate
local function attachBeam()
	if not continueGate or (player:GetAttribute("Stage") or 0) >= 3 then
		return
	end
	local char = player.Character or player.CharacterAdded:Wait()
	local root = char:WaitForChild("HumanoidRootPart", 5)
	if not root then
		return
	end
	local a0 = Instance.new("Attachment")
	a0.Name = "GuideA0"
	a0.Parent = root
	local a1 = Instance.new("Attachment")
	a1.Name = "GuideA1"
	a1.Parent = continueGate
	local beam = Instance.new("Beam")
	beam.Attachment0, beam.Attachment1 = a0, a1
	beam.Color = ColorSequence.new(Color3.fromRGB(120, 255, 200), Color3.fromRGB(255, 255, 255))
	beam.Width0, beam.Width1 = 0.6, 0.6
	beam.FaceCamera = true
	beam.LightEmission = 0.8
	beam.Transparency = NumberSequence.new(0.2, 0.7)
	beam.TextureSpeed = 1.5
	beam.Parent = root
	local function cleanup()
		beam:Destroy()
		a0:Destroy()
		a1:Destroy()
	end
	-- the beam only makes sense inside the HQ; drop it once the player starts the course
	task.spawn(function()
		while beam.Parent do
			if player:GetAttribute("InCourse") or (player:GetAttribute("Stage") or 0) >= 3 then
				cleanup()
				break
			end
			-- follow the nearest parkour gate (the HQ gate)
			local best, bestD = nil, 500
			for _, g in ipairs(courseGates) do
				local d = (g.Position - root.Position).Magnitude
				if d < bestD then
					best, bestD = g, d
				end
			end
			beam.Enabled = best ~= nil
			if best and a1.Parent ~= best then
				a1.Parent = best
			end
			task.wait(0.5)
		end
	end)
end
task.spawn(attachBeam)
player.CharacterAdded:Connect(function()
	task.wait(1)
	attachBeam()
end)

-- ------------------------------------------------------------------ light hints over time + summit report
task.spawn(function()
	local hints = {
		{
			45,
			"💡 اضغط 🎒 يسار الشاشة: إنجازاتك، قطاوتك، والأثر اللي تقدر تشتريه",
		},
		{
			140,
			"💡 كل منطقة باركور فيها عيّنة مخفية جنب المسار 🔬 تحتاج قفزة زيادة",
		},
		{
			300,
			"💡 قطار التخصصات: اضغط ▶ مرة وحدة ويمشي بروحه بين 8 عوالم",
		},
	}
	local t0 = os.clock()
	local summitSent = false
	local milestone = ReplicatedStorage:WaitForChild("Milestone", 20)
	while true do
		local elapsed = os.clock() - t0
		while #hints > 0 and elapsed >= hints[1][1] do
			local h = table.remove(hints, 1)
			if _G.BSCToast then
				_G.BSCToast(h[2], "info")
			end
		end
		local char = player.Character
		local root = char and char:FindFirstChild("HumanoidRootPart")
		if not summitSent and root and obbyTop and milestone and (root.Position - obbyTop.Position).Magnitude < 10 then
			summitSent = true
			milestone:FireServer("summit")
		end
		task.wait(1)
	end
end)
