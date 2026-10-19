-- Default Roblox movement/camera stay active. A compact status strip and two actions only.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local p = Players.LocalPlayer
local D = require(RS:WaitForChild("Shared"):WaitForChild("LaserData"))
local request = RS:WaitForChild("LaserRequest")
local event = RS:WaitForChild("LaserState")
local gui = Instance.new("ScreenGui")
gui.Name = "LaserEscapeUI"
gui.DisplayOrder = 65
gui.ResetOnSpawn = false
gui.Parent = p:WaitForChild("PlayerGui")
local function text(parent, name, caption, pos, size)
	local t = Instance.new("TextLabel")
	t.Name = name
	t.Text = caption
	t.Position = pos
	t.Size = size
	t.TextWrapped = true
	t.TextScaled = true
	t.Font = Enum.Font.GothamBold
	t.TextColor3 = Color3.fromRGB(239, 247, 250)
	t.BackgroundColor3 = Color3.fromRGB(29, 49, 65)
	t.BackgroundTransparency = 0.12
	local c = Instance.new("UITextSizeConstraint")
	c.MinTextSize = 12
	c.MaxTextSize = 20
	c.Parent = t
	t.Parent = parent
	return t
end
local hud = Instance.new("Frame")
hud.Name = "StatusHUD"
hud.Size = UDim2.fromScale(1, 1)
hud.BackgroundTransparency = 1
hud.Visible = false
hud.Parent = gui
local status = text(hud, "Status", "", UDim2.new(0.23, 0, 0, 58), UDim2.new(0.54, 0, 0, 80))
local toast = text(gui, "Notice", "", UDim2.fromScale(0.25, 0.6), UDim2.new(0.5, 0, 0, 46))
toast.Visible = false
local covered, active = {}, false
local protected = { Welcome = true, Extras = true, ProfileMenu = true }
local function hide(other)
	if other:IsA("ScreenGui") and protected[other.Name] and covered[other] == nil then
		covered[other] = other.Enabled
		other.Enabled = false
	end
end
local function interface(on)
	active = on
	if on then
		for _, other in p.PlayerGui:GetChildren() do
			hide(other)
		end
	else
		for other, enabled in covered do
			if other.Parent then
				other.Enabled = enabled
			end
		end
		table.clear(covered)
	end
end
p.PlayerGui.ChildAdded:Connect(function(other)
	if active then
		hide(other)
	end
end)
local messageId = 0
local function notice(message)
	messageId += 1
	local id = messageId
	toast.Text = message
	toast.Visible = true
	task.delay(3, function()
		if id == messageId then
			toast.Visible = false
		end
	end)
end
local function call(action)
	local ok, res = pcall(request.InvokeServer, request, action)
	if not ok or type(res) ~= "table" then
		notice("تعذر الاتصال؛ أعد المحاولة")
	elseif res.error then
		notice(res.error)
	end
end
local function button(name, caption, x, fn)
	local b = Instance.new("TextButton")
	b.Name = name
	b.Text = caption
	b.TextScaled = true
	b.TextWrapped = true
	b.Font = Enum.Font.GothamBold
	b.TextColor3 = Color3.new(1, 1, 1)
	b.BackgroundColor3 = Color3.fromRGB(35, 105, 108)
	b.Position = UDim2.new(x, 0, 0, 148)
	b.Size = UDim2.new(0.13, 0, 0, 44)
	local c = Instance.new("UITextSizeConstraint")
	c.MinTextSize = 12
	c.MaxTextSize = 20
	c.Parent = b
	local min = Instance.new("UISizeConstraint")
	min.MinSize = Vector2.new(70, 44)
	min.Parent = b
	b.Parent = hud
	b.Activated:Connect(fn)
	return b
end
local retry = button("Retry", "نقطة الحفظ", 0.65, function()
	call("retry")
end)
local replay = button("Replay", "إعادة الهروب", 0.65, function()
	call("replay")
end)
replay.Visible = false
button("Exit", "الأركيد", 0.80, function()
	call("leave")
end)
local failures = 0
local function cleanup()
	interface(false)
	hud.Visible = false
	toast.Visible = false
	failures = 0
end
event.OnClientEvent:Connect(function(data)
	if data.kind == "close" then
		cleanup()
		return
	end
	if data.kind == "error" then
		notice(data.message)
		return
	end
	if data.kind ~= "state" then
		return
	end
	interface(true)
	hud.Visible = true
	retry.Visible = not data.finished
	replay.Visible = data.finished
	if data.failures > failures then
		notice("إلى آخر نقطة حفظ • جرّب مرة ثانية")
	end
	failures = data.failures
	local room = D.Rooms[data.room]
	if data.finished then
		status.Text = ("✓ أكملت الغرف الخمس • %.1fث\nمكافأة الجواز مرة واحدة • أعد اللعب أو ارجع للأركيد"):format(
			data.elapsed
		)
	else
		local phase = data.phase == "danger" and "أحمر: خطر"
			or data.phase == "warning" and "كهرماني: استعد"
			or "أزرق: عبور"
		status.Text = ("%d / 5 • %s • %s\nمحاولات غير محدودة • إعادة: %d %s"):format(
			data.room,
			room.ar,
			phase,
			data.failures,
			data.key and "• المفتاح جاهز" or ""
		)
	end
end)
p.CharacterAdded:Connect(cleanup)
