-- Individual interactive displays; all accepted actions/progression are decided by Museum.server.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local Visuals = require(script.Parent.MuseumVisuals)
local player = Players.LocalPlayer
local D = require(RS:WaitForChild("Shared"):WaitForChild("MuseumData"))
local remote = RS:WaitForChild("Museum")
local open = RS:WaitForChild("MuseumOpen")
local gui = Instance.new("ScreenGui")
gui.Name = "MuseumUI"
gui.DisplayOrder = 60
gui.ResetOnSpawn = false
gui.Parent = player:WaitForChild("PlayerGui")
local panel = Instance.new("Frame")
panel.Name = "MuseumPanel"
panel.Size = UDim2.fromScale(0.94, 0.88)
panel.Position = UDim2.fromScale(0.5, 0.5)
panel.AnchorPoint = Vector2.new(0.5, 0.5)
panel.BackgroundColor3 = Color3.fromRGB(20, 37, 46)
panel.Visible = false
panel.Active = true
panel.Parent = gui
local constraint = Instance.new("UISizeConstraint")
constraint.MaxSize = Vector2.new(1050, 650)
constraint.Parent = panel
local function label(parent, name, text, pos, size, max)
	local l = Instance.new("TextLabel")
	l.Name = name
	l.Position = pos
	l.Size = size
	l.BackgroundTransparency = 1
	l.TextColor3 = Color3.fromRGB(238, 244, 238)
	l.Font = Enum.Font.GothamBold
	l.TextWrapped = true
	l.TextScaled = true
	l.Text = text
	local bound = Instance.new("UITextSizeConstraint")
	bound.MinTextSize = 12
	bound.MaxTextSize = max or 22
	bound.Parent = l
	l.Parent = parent
	return l
end
local title = label(panel, "Title", "", UDim2.new(0.02, 0, 0, 4), UDim2.new(0.96, 0, 0, 42), 25)
local view = Instance.new("ViewportFrame")
view.Name = "InteractiveModel"
view.Position = UDim2.new(0.02, 0, 0, 54)
view.Size = UDim2.new(0.36, 0, 1, -118)
view.BackgroundColor3 = Color3.fromRGB(35, 61, 67)
view.Ambient = Color3.fromRGB(190, 190, 190)
view.LightColor = Color3.new(1, 1, 1)
view.Parent = panel
local diagram = label(view, "Assembly", "", UDim2.fromScale(0.02, 0.78), UDim2.fromScale(0.96, 0.21), 20)
local modelStatus = label(view, "ModelStatus", "", UDim2.fromScale(0.02, 0.01), UDim2.fromScale(0.96, 0.16), 18)
diagram.BackgroundTransparency = 0.2
diagram.BackgroundColor3 = Color3.fromRGB(15, 34, 40)
local scroll = Instance.new("ScrollingFrame")
scroll.Name = "Interaction"
scroll.Position = UDim2.new(0.40, 0, 0, 54)
scroll.Size = UDim2.new(0.58, 0, 1, -118)
scroll.BackgroundTransparency = 1
scroll.BorderSizePixel = 0
scroll.ScrollBarThickness = 6
scroll.CanvasSize = UDim2.fromOffset(0, 420)
scroll.Parent = panel
local instruction = label(scroll, "Instruction", "", UDim2.new(), UDim2.new(1, -12, 0, 62), 21)
local choices = Instance.new("Frame")
choices.Name = "Choices"
choices.BackgroundTransparency = 1
choices.Position = UDim2.fromOffset(0, 72)
choices.Size = UDim2.new(1, -12, 0, 112)
choices.Parent = scroll
local feedback = label(scroll, "Feedback", "", UDim2.fromOffset(0, 194), UDim2.new(1, -12, 0, 110), 20)
local caveat = label(
	scroll,
	"ModelNote",
	"محاكاة تعليمية مبسطة\nإضافة خيالية للنادي، وليست موقعًا جامعيًا موثقًا",
	UDim2.fromOffset(0, 316),
	UDim2.new(1, -12, 0, 70),
	16
)
caveat.TextColor3 = Color3.fromRGB(181, 199, 202)
local function button(parent, name, text, pos, size, fn)
	local b = Instance.new("TextButton")
	b.Name = name
	b.Text = text
	b.Position = pos
	b.Size = size
	b.TextWrapped = true
	b.TextScaled = true
	b.Font = Enum.Font.GothamBold
	b.TextColor3 = Color3.new(1, 1, 1)
	b.BackgroundColor3 = Color3.fromRGB(33, 91, 91)
	local bound = Instance.new("UITextSizeConstraint")
	bound.MinTextSize = 12
	bound.MaxTextSize = 20
	bound.Parent = b
	b.Parent = parent
	b.Activated:Connect(fn)
	return b
end
local state, busy, revision = nil, false, 0
local render, begin
local function call(...)
	local ok, res = pcall(remote.InvokeServer, remote, ...)
	return if ok and type(res) == "table" then res else { error = "تعذر الاتصال؛ أعد المحاولة" }
end
local function close()
	local old = state
	state = nil
	panel.Visible = false
	revision += 1
	busy = false
	if old then
		task.spawn(function()
			call("close", old.id, old.token)
		end)
	end
end
button(panel, "Close", "إغلاق ×", UDim2.new(0.73, 0, 1, -54), UDim2.new(0.25, 0, 0, 44), close)
button(panel, "Replay", "إعادة التجربة", UDim2.new(0.40, 0, 1, -54), UDim2.new(0.30, 0, 0, 44), function()
	if state and not busy then
		begin(state.id)
	end
end)
label(panel, "Progress", "", UDim2.new(0.02, 0, 1, -54), UDim2.new(0.36, 0, 0, 44), 20)
local function drawModel(d)
	Visuals.draw(view, d, state)
end
render = function()
	if not state then
		return
	end
	local d = D.get(state.id)
	title.Text = d.ar .. "\n" .. d.en
	panel.Progress.Text = ("المتحف: %d من 8"):format(state.passport and state.passport.museum or 0)
	feedback.Text = state.note ~= "" and state.note or d.intro
	feedback.TextColor3 = state.ok and Color3.fromRGB(168, 242, 199) or Color3.fromRGB(255, 203, 149)
	modelStatus.Text = state.done and "اكتملت التجربة ✓"
		or (
			state.ok and (state.step > 1 and "تمت الخطوة ✓" or "جرّب التركيب")
			or "اختيار غير مناسب؛ جرّب ثانية"
		)
	modelStatus.TextColor3 = feedback.TextColor3
	choices:ClearAllChildren()
	if state.done then
		instruction.Text = "اكتملت التجربة ✓ — 10 XP لأول إكمال فقط"
		feedback.Text = d.result .. "\nتقدر تعيدها للتجربة دون تكرار المكافأة."
		feedback.Size = UDim2.new(1, -12, 0, 145)
		caveat.Position = UDim2.fromOffset(0, 350)
		if scroll.AbsoluteSize.Y < 350 then
			scroll.CanvasPosition = Vector2.new(0, 170)
		end
	else
		local step = D.get(state.id).steps[state.step]
		instruction.Text = ("خطوة %d من %d\n%s"):format(state.step, #d.steps, step.ar)
		feedback.Size = UDim2.new(1, -12, 0, 110)
		caveat.Position = UDim2.fromOffset(0, 316)
		for i, opt in ipairs(step.options) do
			button(
				choices,
				"Choice_" .. opt.id,
				opt.ar,
				UDim2.new(((i - 1) % 2) * 0.51, 0, 0, math.floor((i - 1) / 2) * 56),
				UDim2.new(0.48, 0, 0, 48),
				function()
					if busy or not state then
						return
					end
					busy = true
					local rev = revision
					local res = call("act", state.id, state.token, state.step, opt.id)
					if revision ~= rev then
						return
					end
					busy = false
					if res.error then
						feedback.Text = res.error
						if not res.retry then
							close()
						end
						return
					end
					state = res
					render()
				end
			)
		end
	end
	drawModel(d)
end
begin = function(id)
	if busy or not D.get(id) then
		return
	end
	busy = true
	revision += 1
	local rev = revision
	local res = call("start", id)
	if revision ~= rev then
		return
	end
	busy = false
	if res.error then
		return
	end
	state = res
	panel.Visible = true
	scroll.CanvasPosition = Vector2.zero
	render()
end
open.OnClientEvent:Connect(begin)
task.spawn(function()
	while gui.Parent do
		task.wait(0.5)
		if state then
			local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
			local hum = player.Character and player.Character:FindFirstChildOfClass("Humanoid")
			local station = workspace.Map.Campus.Museum46:FindFirstChild("Exhibit_" .. state.id)
			if
				not root
				or not hum
				or hum.Health <= 0
				or not station
				or (root.Position - station.Console.Position).Magnitude > 28
			then
				close()
			end
		end
	end
end)
