-- "Back to the hub" button, shown only while the player is inside the parkour course.
-- Progress is kept; the server just moves the player back to the College of Science (and clears InCourse).
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local player = Players.LocalPlayer
local leave = ReplicatedStorage:WaitForChild("LeaveCourse", 30)
if not leave then
	return
end

local gui = Instance.new("ScreenGui")
gui.Name = "LeaveCourse"
gui.ResetOnSpawn = false
gui.DisplayOrder = 20
gui.Parent = player:WaitForChild("PlayerGui")

local button = Instance.new("TextButton")
button.AnchorPoint = Vector2.new(0, 0.5)
button.Position = UDim2.fromScale(0.01, 0.56)
button.Size = UDim2.fromScale(0.11, 0.07)
button.BackgroundColor3 = Color3.fromRGB(24, 80, 56)
button.TextColor3 = Color3.new(1, 1, 1)
button.TextScaled = true
button.Font = Enum.Font.GothamBold
button.Text = "🏛️ رجوع لكلية العلوم"
button.Visible = false
button.Parent = gui
local corner = Instance.new("UICorner")
corner.CornerRadius = UDim.new(0.3, 0)
corner.Parent = button
local minSize = Instance.new("UISizeConstraint")
minSize.MinSize = Vector2.new(120, 44)
minSize.Parent = button

local function refresh()
	button.Visible = player:GetAttribute("InCourse") == true
end
player:GetAttributeChangedSignal("InCourse"):Connect(refresh)
refresh()

local last = 0
button.Activated:Connect(function()
	if os.clock() - last < 2 then
		return
	end
	last = os.clock()
	if _G.BSCPlay then
		_G.BSCPlay("click")
	end
	leave:FireServer()
end)
