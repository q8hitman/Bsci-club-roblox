-- v53 Arcade results screen: after every round, a short ranked card (top 6 + your own rank), your rewards and
-- when the next round starts. Data comes from Arcade.server ("ArcadeResults"); nothing here changes rewards.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer
local event = ReplicatedStorage:WaitForChild("ArcadeResults", 60)
if not event then
	return
end

local gui = Instance.new("ScreenGui")
gui.Name = "ArcadeResults"
gui.ResetOnSpawn = false
gui.DisplayOrder = 30
gui.Enabled = false
gui.Parent = player:WaitForChild("PlayerGui")

local card = Instance.new("Frame")
card.AnchorPoint = Vector2.new(0.5, 0.5)
card.Position = UDim2.fromScale(0.5, 0.45)
card.Size = UDim2.fromScale(0.42, 0.56)
card.BackgroundColor3 = Color3.fromRGB(22, 26, 40)
card.BackgroundTransparency = 0.08
card.Parent = gui
Instance.new("UICorner", card).CornerRadius = UDim.new(0.05, 0)
local limits = Instance.new("UISizeConstraint")
limits.MinSize = Vector2.new(300, 240)
limits.Parent = card
local stroke = Instance.new("UIStroke")
stroke.Color = Color3.fromRGB(255, 210, 90)
stroke.Thickness = 2
stroke.Parent = card

local function label(pos, size, color, bold)
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.Position = pos
	t.Size = size
	t.TextColor3 = color or Color3.new(1, 1, 1)
	t.TextScaled = true
	t.Font = bold and Enum.Font.GothamBold or Enum.Font.Gotham
	t.Parent = card
	return t
end

local title = label(UDim2.fromScale(0.05, 0.03), UDim2.fromScale(0.9, 0.1), Color3.fromRGB(255, 220, 120), true)
local mine = label(UDim2.fromScale(0.05, 0.14), UDim2.fromScale(0.9, 0.09), Color3.new(1, 1, 1), true)
local rows = {}
for i = 1, 6 do
	rows[i] = label(UDim2.fromScale(0.08, 0.25 + (i - 1) * 0.09), UDim2.fromScale(0.84, 0.08), nil, false)
end
local reward = label(UDim2.fromScale(0.05, 0.81), UDim2.fromScale(0.9, 0.08), Color3.fromRGB(140, 240, 170), true)
local nextLine = label(UDim2.fromScale(0.05, 0.9), UDim2.fromScale(0.9, 0.07), Color3.fromRGB(190, 196, 210), false)

local MEDAL = { "🥇", "🥈", "🥉" }
local showId = 0
event.OnClientEvent:Connect(function(data)
	if type(data) ~= "table" or type(data.list) ~= "table" then
		return
	end
	showId += 1
	local my = showId
	title.Text = "🏁 " .. tostring(data.title or "")
	if data.mode == "coop" then
		mine.Text = data.teamDone and "🤝 الفريق نجح بالمهمة!"
			or "😅 الفريق ما لحق هالمرة"
	else
		local me = data.list[data.rank or 0]
		local anyWinner = data.list[1] and data.list[1].winner
		mine.Text = not anyWinner and "ما فاز أحد هالمرة 😅 جرّب مرة ثانية!"
			or ("ترتيبك: %s %d من %d"):format(me and me.winner and "👑" or "", data.rank or 0, #data.list)
	end
	for i, r in ipairs(rows) do
		local e = data.list[i]
		if e then
			local detail = data.mode == "survive" and (e.alive and "صمد للنهاية 💪" or "طاح")
				or ("%d نقطة"):format(e.score or 0)
			-- medals only for a real result (a winner exists); otherwise just the order
			local mark = data.list[1].winner and MEDAL[i] or (i .. ".")
			r.Text = ("%s %s • %s%s"):format(mark, e.name, detail, e.winner and " 👑" or "")
			r.TextColor3 = i == data.rank and Color3.fromRGB(255, 230, 140) or Color3.new(1, 1, 1)
		else
			r.Text = ""
		end
	end
	reward.Text = ("+%d 💰  +%d 🧪"):format(data.coins or 0, data.research or 0)
	gui.Enabled = true
	card.Size = UDim2.fromScale(0.3, 0.4)
	TweenService:Create(card, TweenInfo.new(0.35, Enum.EasingStyle.Back), { Size = UDim2.fromScale(0.42, 0.56) }):Play()
	if _G.BSCPlay then
		_G.BSCPlay(data.rank == 1 and "achievement" or "click")
	end
	-- count down to the next round, hide after the results phase
	task.spawn(function()
		local t0 = os.clock()
		while my == showId and os.clock() - t0 < 7 do
			nextLine.Text = ("الجولة الجاية بعد %d ثانية"):format(
				math.max(0, math.ceil((data.nextIn or 0) - (os.clock() - t0)))
			)
			task.wait(0.25)
		end
		if my == showId then
			gui.Enabled = false
		end
	end)
end)
