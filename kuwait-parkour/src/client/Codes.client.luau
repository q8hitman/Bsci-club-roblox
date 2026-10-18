local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local player = Players.LocalPlayer
local gui = player:WaitForChild("PlayerGui"):WaitForChild("StageHUD")
local redeem = ReplicatedStorage:WaitForChild("RedeemCode")

local MESSAGES = {
	ok = "تم! حصلت على %d عملة",
	used = "استخدمت هذا الكود من قبل",
	invalid = "الكود غير صحيح",
	expired = "انتهت صلاحية الكود",
	slow = "انتظر ثانيتين وحاول مرة ثانية",
	unavailable = "تعذّر الحفظ الآن، حاول لاحقاً",
}

local button = Instance.new("TextButton")
button.AnchorPoint = Vector2.new(1, 0)
button.Position = UDim2.fromScale(0.83, 0.02)
button.Size = UDim2.fromScale(0.12, 0.07)
button.BackgroundColor3 = Color3.fromRGB(46, 160, 90)
button.TextColor3 = Color3.new(1, 1, 1)
button.TextScaled = true
button.Font = Enum.Font.GothamBold
button.Text = "كود"
button.Parent = gui
Instance.new("UICorner", button).CornerRadius = UDim.new(0.25, 0)

local panel = Instance.new("Frame")
panel.AnchorPoint = Vector2.new(0.5, 0.5)
panel.Position = UDim2.fromScale(0.5, 0.5)
panel.Size = UDim2.fromScale(0.45, 0.3)
panel.BackgroundColor3 = Color3.fromRGB(20, 40, 30)
panel.Visible = false
panel.Parent = gui
Instance.new("UICorner", panel).CornerRadius = UDim.new(0.06, 0)

local input = Instance.new("TextBox")
input.Size = UDim2.fromScale(0.9, 0.28)
input.Position = UDim2.fromScale(0.05, 0.12)
input.BackgroundColor3 = Color3.fromRGB(10, 22, 16)
input.TextColor3 = Color3.new(1, 1, 1)
input.PlaceholderText = "اكتب الكود هنا"
input.TextScaled = true
input.Font = Enum.Font.Code
input.Text = ""
input.ClearTextOnFocus = false
input.Parent = panel
Instance.new("UICorner", input).CornerRadius = UDim.new(0.2, 0)

local go = Instance.new("TextButton")
go.Size = UDim2.fromScale(0.6, 0.25)
go.Position = UDim2.fromScale(0.2, 0.48)
go.BackgroundColor3 = Color3.fromRGB(46, 160, 90)
go.TextColor3 = Color3.new(1, 1, 1)
go.TextScaled = true
go.Font = Enum.Font.GothamBold
go.Text = "استلام"
go.Parent = panel
Instance.new("UICorner", go).CornerRadius = UDim.new(0.2, 0)

local result = Instance.new("TextLabel")
result.Size = UDim2.fromScale(0.9, 0.18)
result.Position = UDim2.fromScale(0.05, 0.78)
result.BackgroundTransparency = 1
result.TextColor3 = Color3.fromRGB(220, 220, 220)
result.TextScaled = true
result.Font = Enum.Font.Gotham
result.Text = ""
result.Parent = panel

local busy = false
go.Activated:Connect(function()
	if busy or input.Text == "" then
		return
	end
	busy = true
	local status, amount = redeem:InvokeServer(input.Text)
	local template = MESSAGES[status] or MESSAGES.invalid
	result.Text = status == "ok" and template:format(amount or 0) or template
	if status == "ok" then
		input.Text = ""
	end
	busy = false
end)

button.Activated:Connect(function()
	panel.Visible = not panel.Visible
end)
