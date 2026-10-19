-- v49 Photo Mode (وضع التصوير الإعلامي): lets players and the BSC Media Committee hide all HUD elements,
-- cycle club frames/cinema bars, adjust lighting filters, trigger celebratory confetti/shutter effects,
-- and temporarily hide the control bar for 100% clean screenshots and video capture.
local Lighting = game:GetService("Lighting")
local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")
local UserInputService = game:GetService("UserInputService")

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

local gui = Instance.new("ScreenGui")
gui.Name = "PhotoModeGui"
gui.ResetOnSpawn = false
gui.IgnoreGuiInset = true
gui.DisplayOrder = 90
gui.Parent = playerGui

local function corner(parent, r)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(r or 0.25, 0)
	c.Parent = parent
end

local function playSfx(name)
	if _G.BSCPlay then
		_G.BSCPlay(name)
	end
end

-- Top-right toggle button (sits cleanly between StageHUD at 0.35..0.65 and Discord at 0.84..0.98)
local toggleBtn = Instance.new("TextButton")
toggleBtn.Name = "PhotoModeToggle"
toggleBtn.AnchorPoint = Vector2.new(1, 0)
toggleBtn.Position = UDim2.fromScale(0.83, 0.05)
toggleBtn.Size = UDim2.fromScale(0.12, 0.055)
toggleBtn.BackgroundColor3 = Color3.fromRGB(24, 80, 56)
toggleBtn.TextColor3 = Color3.new(1, 1, 1)
toggleBtn.TextScaled = true
toggleBtn.Font = Enum.Font.GothamBold
toggleBtn.Text = "📸 تصوير"
toggleBtn.Parent = gui
corner(toggleBtn, 0.25)
local toggleStroke = Instance.new("UIStroke")
toggleStroke.Color = Color3.fromRGB(120, 255, 200)
toggleStroke.Thickness = 1.5
toggleStroke.Parent = toggleBtn
local toggleMin = Instance.new("UISizeConstraint")
toggleMin.MinSize = Vector2.new(68, 32)
toggleMin.Parent = toggleBtn

-- Overlay container for frames/letterbox
local overlay = Instance.new("Frame")
overlay.Name = "Overlay"
overlay.Size = UDim2.fromScale(1, 1)
overlay.BackgroundTransparency = 1
overlay.Visible = false
overlay.Parent = gui

local borderStroke = Instance.new("UIStroke")
borderStroke.Thickness = 14
borderStroke.Color = Color3.fromRGB(230, 190, 70)
borderStroke.Enabled = false
borderStroke.Parent = overlay

local badge = Instance.new("TextLabel")
badge.Name = "ClubBadge"
badge.AnchorPoint = Vector2.new(0, 0)
badge.Position = UDim2.fromScale(0.03, 0.05)
badge.Size = UDim2.fromScale(0.38, 0.07)
badge.BackgroundColor3 = Color3.fromRGB(20, 56, 40)
badge.BackgroundTransparency = 0.15
badge.TextColor3 = Color3.fromRGB(255, 240, 190)
badge.TextScaled = true
badge.Font = Enum.Font.GothamBold
badge.Text = "🧬 نادي العلوم البيولوجية • كلية العلوم • جامعة الكويت"
badge.Visible = false
badge.Parent = overlay
corner(badge, 0.25)

local postcard = Instance.new("TextLabel")
postcard.Name = "PostcardCaption"
postcard.AnchorPoint = Vector2.new(0.5, 1)
postcard.Position = UDim2.fromScale(0.5, 0.86)
postcard.Size = UDim2.fromScale(0.56, 0.08)
postcard.BackgroundColor3 = Color3.fromRGB(24, 80, 56)
postcard.BackgroundTransparency = 0.12
postcard.TextColor3 = Color3.new(1, 1, 1)
postcard.TextScaled = true
postcard.Font = Enum.Font.GothamBold
postcard.Text = "🏛️ كلية العلوم — جامعة الكويت • BSC Island"
postcard.Visible = false
postcard.Parent = overlay
corner(postcard, 0.22)

local topBar = Instance.new("Frame")
topBar.Name = "CinemaTop"
topBar.Size = UDim2.fromScale(1, 0.11)
topBar.Position = UDim2.fromScale(0, 0)
topBar.BackgroundColor3 = Color3.new(0, 0, 0)
topBar.BorderSizePixel = 0
topBar.Visible = false
topBar.Parent = overlay

local bottomBar = Instance.new("Frame")
bottomBar.Name = "CinemaBottom"
bottomBar.AnchorPoint = Vector2.new(0, 1)
bottomBar.Size = UDim2.fromScale(1, 0.11)
bottomBar.Position = UDim2.fromScale(0, 1)
bottomBar.BackgroundColor3 = Color3.new(0, 0, 0)
bottomBar.BorderSizePixel = 0
bottomBar.Visible = false
bottomBar.Parent = overlay

local flash = Instance.new("Frame")
flash.Name = "ShutterFlash"
flash.Size = UDim2.fromScale(1, 1)
flash.BackgroundColor3 = Color3.new(1, 1, 1)
flash.BackgroundTransparency = 1
flash.Visible = false
flash.Parent = gui

-- Control Dock at bottom center
local dock = Instance.new("Frame")
dock.Name = "ControlDock"
dock.AnchorPoint = Vector2.new(0.5, 1)
dock.Position = UDim2.fromScale(0.5, 0.97)
dock.Size = UDim2.fromScale(0.84, 0.085)
dock.BackgroundColor3 = Color3.fromRGB(16, 26, 22)
dock.BackgroundTransparency = 0.12
dock.Visible = false
dock.Parent = gui
corner(dock, 0.25)
local dockConstraint = Instance.new("UISizeConstraint")
dockConstraint.MaxSize = Vector2.new(780, 58)
dockConstraint.MinSize = Vector2.new(360, 38)
dockConstraint.Parent = dock

local dockLayout = Instance.new("UIListLayout")
dockLayout.FillDirection = Enum.FillDirection.Horizontal
dockLayout.HorizontalAlignment = Enum.HorizontalAlignment.Center
dockLayout.VerticalAlignment = Enum.VerticalAlignment.Center
dockLayout.Padding = UDim.new(0.012, 0)
dockLayout.SortOrder = Enum.SortOrder.LayoutOrder
dockLayout.Parent = dock

local function makeDockBtn(order, text, bg, widthScale)
	local b = Instance.new("TextButton")
	b.LayoutOrder = order
	b.Size = UDim2.fromScale(widthScale or 0.18, 0.8)
	b.BackgroundColor3 = bg
	b.TextColor3 = Color3.new(1, 1, 1)
	b.TextScaled = true
	b.Font = Enum.Font.GothamBold
	b.Text = text
	b.Parent = dock
	corner(b, 0.25)
	return b
end

local frameBtn = makeDockBtn(1, "🖼️ الإطار: بدون", Color3.fromRGB(38, 92, 68), 0.21)
local filterBtn = makeDockBtn(2, "✨ الفلتر: طبيعي", Color3.fromRGB(48, 82, 120), 0.21)
local snapBtn = makeDockBtn(3, "📸 لقطة + احتفال", Color3.fromRGB(185, 130, 35), 0.21)
local hideBarBtn = makeDockBtn(4, "👁️ إخفاء الأزرار", Color3.fromRGB(70, 76, 88), 0.18)
local exitBtn = makeDockBtn(5, "✖ خروج", Color3.fromRGB(150, 50, 55), 0.13)

-- Invisible full-screen button to restore dock when hidden
local restoreCatcher = Instance.new("TextButton")
restoreCatcher.Name = "RestoreDock"
restoreCatcher.Size = UDim2.fromScale(1, 1)
restoreCatcher.BackgroundTransparency = 1
restoreCatcher.Text = ""
restoreCatcher.Visible = false
restoreCatcher.Parent = gui

local FRAMES = {
	{ name = "بدون", border = false, badge = false, postcard = false, cinema = false },
	{ name = "نادي العلوم", border = true, badge = true, postcard = false, cinema = false },
	{ name = "بطاقة الكلية", border = true, badge = false, postcard = true, cinema = false },
	{ name = "سينمائي", border = false, badge = false, postcard = false, cinema = true },
}

local FILTERS = {
	{ name = "طبيعي", brightness = 0, contrast = 0, saturation = 0, tint = Color3.fromRGB(255, 255, 255) },
	{
		name = "ذهبي دافئ",
		brightness = 0.03,
		contrast = 0.12,
		saturation = 0.15,
		tint = Color3.fromRGB(255, 242, 218),
	},
	{
		name = "إعلامي واضح",
		brightness = 0.02,
		contrast = 0.18,
		saturation = 0.22,
		tint = Color3.fromRGB(248, 252, 255),
	},
}

local active = false
local frameIdx = 1
local filterIdx = 1
local savedGuis = {}
local ccEffect = nil

local function applyFrame()
	local f = FRAMES[frameIdx]
	frameBtn.Text = "🖼️ الإطار: " .. f.name
	borderStroke.Enabled = f.border
	badge.Visible = f.badge
	postcard.Visible = f.postcard
	topBar.Visible = f.cinema
	bottomBar.Visible = f.cinema
end

local function applyFilter()
	local flt = FILTERS[filterIdx]
	filterBtn.Text = "✨ الفلتر: " .. flt.name
	if not active then
		if ccEffect then
			ccEffect:Destroy()
			ccEffect = nil
		end
		return
	end
	if not ccEffect then
		ccEffect = Instance.new("ColorCorrectionEffect")
		ccEffect.Name = "BSCPhotoModeCC"
		ccEffect.Parent = Lighting
	end
	ccEffect.Brightness = flt.brightness
	ccEffect.Contrast = flt.contrast
	ccEffect.Saturation = flt.saturation
	ccEffect.TintColor = flt.tint
end

local function emitCelebration()
	playSfx("sting")
	flash.Visible = true
	flash.BackgroundTransparency = 0.15
	local tw = TweenService:Create(flash, TweenInfo.new(0.45), { BackgroundTransparency = 1 })
	tw:Play()
	task.delay(0.5, function()
		flash.Visible = false
	end)
	local char = player.Character
	local root = char and char:FindFirstChild("HumanoidRootPart")
	if not root then
		return
	end
	local att = Instance.new("Attachment")
	att.Position = Vector3.new(0, 5.5, 0)
	att.Parent = root
	local p = Instance.new("ParticleEmitter")
	p.Color = ColorSequence.new({
		ColorSequenceKeypoint.new(0, Color3.fromRGB(120, 255, 200)),
		ColorSequenceKeypoint.new(0.5, Color3.fromRGB(255, 220, 90)),
		ColorSequenceKeypoint.new(1, Color3.fromRGB(160, 218, 236)),
	})
	p.Size = NumberSequence.new(0.32)
	p.Lifetime = NumberRange.new(1.8, 2.8)
	p.Speed = NumberRange.new(9, 16)
	p.SpreadAngle = Vector2.new(65, 65)
	p.Acceleration = Vector3.new(0, -14, 0)
	p.Rate = 0
	p.Parent = att
	p:Emit(80)
	task.delay(3.2, function()
		att:Destroy()
	end)
end

local function setPhotoMode(on)
	if active == on then
		return
	end
	active = on
	playSfx("click")
	if active then
		savedGuis = {}
		for _, child in ipairs(playerGui:GetChildren()) do
			if child:IsA("ScreenGui") and child ~= gui and child.Enabled then
				savedGuis[child] = true
				child.Enabled = false
			end
		end
		toggleBtn.Visible = false
		overlay.Visible = true
		dock.Visible = true
		restoreCatcher.Visible = false
		frameIdx = 2 -- default to official BSC frame on open
		applyFrame()
		applyFilter()
	else
		for g in pairs(savedGuis) do
			if g and g.Parent then
				g.Enabled = true
			end
		end
		savedGuis = {}
		overlay.Visible = false
		dock.Visible = false
		restoreCatcher.Visible = false
		toggleBtn.Visible = true
		applyFilter()
	end
end

toggleBtn.Activated:Connect(function()
	setPhotoMode(true)
end)

exitBtn.Activated:Connect(function()
	setPhotoMode(false)
end)

frameBtn.Activated:Connect(function()
	playSfx("click")
	frameIdx = (frameIdx % #FRAMES) + 1
	applyFrame()
end)

filterBtn.Activated:Connect(function()
	playSfx("click")
	filterIdx = (filterIdx % #FILTERS) + 1
	applyFilter()
end)

snapBtn.Activated:Connect(function()
	emitCelebration()
end)

hideBarBtn.Activated:Connect(function()
	playSfx("click")
	dock.Visible = false
	restoreCatcher.Visible = true
end)

restoreCatcher.Activated:Connect(function()
	if active then
		dock.Visible = true
		restoreCatcher.Visible = false
	end
end)

UserInputService.InputBegan:Connect(function(input, processed)
	if processed then
		return
	end
	if input.KeyCode == Enum.KeyCode.P then
		setPhotoMode(not active)
	elseif active and input.KeyCode == Enum.KeyCode.H then
		dock.Visible = not dock.Visible
		restoreCatcher.Visible = not dock.Visible
	end
end)
