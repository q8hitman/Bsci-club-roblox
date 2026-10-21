-- v56 Arcade vote: during the break between rounds, three small buttons let the players in the lobby pick the next
-- game. State comes from workspace attributes set by Arcade.server (ArcadeVoteOptions, ArcadeVotes, ArcadePhase).
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local player = Players.LocalPlayer
local voteEvent = ReplicatedStorage:WaitForChild("ArcadeVote", 60)
if not voteEvent then
	return
end

local gui = Instance.new("ScreenGui")
gui.Name = "ArcadeVote"
gui.ResetOnSpawn = false
gui.DisplayOrder = 14
gui.Enabled = false
gui.Parent = player:WaitForChild("PlayerGui")

local bar = Instance.new("Frame")
bar.AnchorPoint = Vector2.new(0.5, 1)
bar.Position = UDim2.fromScale(0.5, 0.9)
bar.Size = UDim2.fromScale(0.56, 0.11)
bar.BackgroundTransparency = 1
bar.Parent = gui
local limits = Instance.new("UISizeConstraint")
limits.MinSize = Vector2.new(320, 54)
limits.Parent = bar

local title = Instance.new("TextLabel")
title.Size = UDim2.fromScale(1, 0.32)
title.BackgroundTransparency = 1
title.TextColor3 = Color3.fromRGB(255, 226, 120)
title.TextStrokeTransparency = 0.4
title.TextScaled = true
title.Font = Enum.Font.GothamBold
title.Text = "🗳️ صوّت للعبة الجاية"
title.Parent = bar

local buttons = {}
local mine = nil
for i = 1, 3 do
	local b = Instance.new("TextButton")
	b.Name = "Vote" .. i
	b.Position = UDim2.fromScale((i - 1) * 0.34, 0.38)
	b.Size = UDim2.fromScale(0.32, 0.62)
	b.BackgroundColor3 = Color3.fromRGB(40, 46, 66)
	b.TextColor3 = Color3.new(1, 1, 1)
	b.TextScaled = true
	b.TextWrapped = true
	b.Font = Enum.Font.GothamBold
	b.Parent = bar
	Instance.new("UICorner", b).CornerRadius = UDim.new(0.3, 0)
	b.Activated:Connect(function()
		mine = i
		voteEvent:FireServer(i)
		if _G.BSCPlay then
			_G.BSCPlay("click")
		end
	end)
	buttons[i] = b
end

local function nearArcade()
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
	return root and (Vector3.new(root.Position.X, 0, root.Position.Z) - Vector3.new(-6000, 0, -6000)).Magnitude < 420
end

local function refresh()
	local opts = workspace:GetAttribute("ArcadeVoteOptions") or ""
	local show = opts ~= "" and workspace:GetAttribute("ArcadePhase") == "intermission" and nearArcade()
	gui.Enabled = show and true or false
	if not show then
		mine = nil
		return
	end
	local counts = string.split(workspace:GetAttribute("ArcadeVotes") or "", ",")
	local list = string.split(opts, ";")
	for i, b in ipairs(buttons) do
		local entry = list[i]
		b.Visible = entry ~= nil and entry ~= ""
		if b.Visible then
			local name = string.split(entry, "|")[2] or "?"
			b.Text = ("%s  •  %s"):format(name, counts[i] or "0")
			b.BackgroundColor3 = mine == i and Color3.fromRGB(40, 150, 100) or Color3.fromRGB(40, 46, 66)
		end
	end
end

workspace:GetAttributeChangedSignal("ArcadeVoteOptions"):Connect(refresh)
workspace:GetAttributeChangedSignal("ArcadeVotes"):Connect(refresh)
workspace:GetAttributeChangedSignal("ArcadePhase"):Connect(refresh)
while true do
	refresh()
	task.wait(1)
end
