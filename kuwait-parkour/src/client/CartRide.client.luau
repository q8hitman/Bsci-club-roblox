-- BSC Science Express (v31): a classic sightseeing train through the eight specialty rooms. The server welds our own
-- train to us; we move it along the track waypoints ("CW|i|flags|label", RightVector = the track's right-hand side).
-- Controls: ▶ start once and the train runs on its own; ＋ / － change the cruise speed one step (it stays there);
-- ⏸ pauses smoothly, ▶ resumes. Sharp bends and the end of the line slow the train down by themselves, so no speed
-- can throw anyone off. At the end it stops gently and offers "back to the College of Science" or "ride again". No questions.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local player = Players.LocalPlayer
local mapFolder = workspace:WaitForChild("Map")
local remote = ReplicatedStorage:WaitForChild("CartRide")

local SPEEDS = { 15, 25, 35, 45, 60, 75, 90 } -- cruise steps (studs/s); motion is kinematic, so all are safe
local START_LEVEL = 3
local ACCEL, DECEL = 14, 20 -- gentle: no jolts when starting, pausing or arriving
local LATERAL = 70 -- comfort limit for v^2 / radius in bends
local SEAT_HEIGHT = 2.0
local CAR_GAP = 11

-- one short, checked fact per room (shown automatically, hides by itself)
local FACTS = {
	"🦠 بعض البكتيريا تتضاعف كل 20 دقيقة تقريباً بالظروف المثالية",
	"⚗️ الإنزيمات تسرّع التفاعلات بدون ما تُستهلك",
	"🐋 الحوت الأزرق أكبر حيوان عرفناه، وقلبه بحجم سيارة صغيرة",
	"🌿 البناء الضوئي يحوّل الضوء والماء وCO₂ إلى سكر وأكسجين",
	"🧬 الـ mRNA يحمل الشفرة من DNA إلى الريبوسوم ليبني البروتين",
	"🔎 البصمة تتكوّن قبل الولادة وما تتغير طول العمر",
	"💧 الري بالتنقيط يوصل الماء للجذور مباشرة ويقلل الهدر",
	"🧪 PCR يضاعف قطعة DNA ملايين المرات خلال ساعات",
}

-- ------------------------------------------------------------------ track
local pts = {}
for _, inst in ipairs(mapFolder:GetDescendants()) do
	if inst:IsA("BasePart") then
		local args = string.split(inst.Name, "|")
		if args[1] == "CW" and tonumber(args[2]) then
			local flags = {}
			for _, f in ipairs(string.split(args[3] or "", ",")) do
				if f ~= "" then
					local key, num = f:match("^(%a+)(%d*)$")
					if key then
						flags[key] = tonumber(num) or true
					end
				end
			end
			pts[tonumber(args[2])] =
				{ pos = inst.Position, right = inst.CFrame.RightVector, flags = flags, label = args[4] or "" }
		end
	end
end
if #pts < 2 then
	return
end
local dist = { 0 }
for i = 2, #pts do
	dist[i] = dist[i - 1] + (pts[i].pos - pts[i - 1].pos).Magnitude
end
local total = dist[#pts]

-- ------------------------------------------------------------------ UI (small, right-hand column + one status pill)
local gui = Instance.new("ScreenGui")
gui.Name = "CartRideGui"
gui.ResetOnSpawn = false
gui.IgnoreGuiInset = true
gui.DisplayOrder = 24
gui.Enabled = false
gui.Parent = player:WaitForChild("PlayerGui")

local function label(pos, size, color)
	local t = Instance.new("TextLabel")
	t.AnchorPoint = Vector2.new(0.5, 0.5)
	t.Position = pos
	t.Size = size
	t.BackgroundColor3 = color
	t.BackgroundTransparency = 0.2
	t.TextColor3 = Color3.new(1, 1, 1)
	t.TextScaled = true
	t.TextWrapped = true
	t.Font = Enum.Font.GothamBold
	t.Parent = gui
	Instance.new("UICorner", t).CornerRadius = UDim.new(0.3, 0)
	return t
end
local caption = label(UDim2.fromScale(0.5, 0.2), UDim2.fromScale(0.56, 0.07), Color3.fromRGB(30, 50, 90))
caption.Visible = false
local status = label(UDim2.fromScale(0.5, 0.92), UDim2.fromScale(0.38, 0.055), Color3.fromRGB(24, 28, 38))
local statusMin = Instance.new("UISizeConstraint", status)
statusMin.MinSize = Vector2.new(230, 30)

local function button(name, text, pos, color)
	local b = Instance.new("TextButton")
	b.Name = name
	b.AnchorPoint = Vector2.new(0.5, 0.5)
	b.Position = pos
	b.Size = UDim2.fromScale(0.075, 0.1)
	b.BackgroundColor3 = color
	b.TextColor3 = Color3.new(1, 1, 1)
	b.TextScaled = true
	b.Font = Enum.Font.GothamBold
	b.Text = text
	b.Parent = gui
	Instance.new("UICorner", b).CornerRadius = UDim.new(0.3, 0)
	Instance.new("UIAspectRatioConstraint", b)
	local m = Instance.new("UISizeConstraint", b)
	m.MinSize = Vector2.new(44, 44)
	return b
end
local exitBtn = button("ExitBtn", "خروج", UDim2.fromScale(0.91, 0.25), Color3.fromRGB(150, 50, 60))
local hornBtn = button("HornBtn", "🔔", UDim2.fromScale(0.91, 0.38), Color3.fromRGB(195, 140, 40))
local fasterBtn = button("FasterBtn", "＋", UDim2.fromScale(0.91, 0.51), Color3.fromRGB(60, 140, 200))
local slowerBtn = button("SlowerBtn", "－", UDim2.fromScale(0.91, 0.64), Color3.fromRGB(90, 100, 130))
local goBtn = button("GoBtn", "▶", UDim2.fromScale(0.91, 0.78), Color3.fromRGB(50, 170, 90))

-- end-of-line card
local endCard = Instance.new("Frame")
endCard.AnchorPoint = Vector2.new(0.5, 0.5)
endCard.Position = UDim2.fromScale(0.5, 0.45)
endCard.Size = UDim2.fromScale(0.42, 0.26)
endCard.BackgroundColor3 = Color3.fromRGB(24, 30, 44)
endCard.BackgroundTransparency = 0.1
endCard.Visible = false
endCard.Parent = gui
Instance.new("UICorner", endCard).CornerRadius = UDim.new(0.08, 0)
local endMin = Instance.new("UISizeConstraint", endCard)
endMin.MinSize = Vector2.new(300, 140)
local endTitle = Instance.new("TextLabel")
endTitle.Size = UDim2.fromScale(1, 0.45)
endTitle.BackgroundTransparency = 1
endTitle.TextColor3 = Color3.fromRGB(255, 230, 150)
endTitle.TextScaled = true
endTitle.Font = Enum.Font.GothamBold
endTitle.Text = "🎉 خلصت الرحلة!\nشفت التخصصات الثمانية"
endTitle.Parent = endCard
local function cardButton(name, text, x, color)
	local b = Instance.new("TextButton")
	b.Name = name
	b.Position = UDim2.fromScale(x, 0.55)
	b.Size = UDim2.fromScale(0.44, 0.36)
	b.BackgroundColor3 = color
	b.TextColor3 = Color3.new(1, 1, 1)
	b.TextScaled = true
	b.Font = Enum.Font.GothamBold
	b.Text = text
	b.Parent = endCard
	Instance.new("UICorner", b).CornerRadius = UDim.new(0.25, 0)
	return b
end
local hubBtn = cardButton("HubBtn", "🏛️ رجوع لكلية العلوم", 0.04, Color3.fromRGB(24, 110, 70))
local againBtn = cardButton("AgainBtn", "🔁 رحلة ثانية", 0.52, Color3.fromRGB(70, 90, 160))

local captionUntil = 0
local function say(text, seconds)
	caption.Text = text
	caption.Visible = true
	captionUntil = os.clock() + (seconds or 3)
end

local function play(name)
	if _G.BSCPlay then
		_G.BSCPlay(name)
	end
end

-- ------------------------------------------------------------------ track sampling
local function sample(d)
	local lo, hi = 1, #pts
	while hi - lo > 1 do
		local mid = (lo + hi) // 2
		if dist[mid] < d then
			lo = mid
		else
			hi = mid
		end
	end
	local a, b = pts[lo], pts[hi]
	local span = math.max(dist[hi] - dist[lo], 1e-3)
	local t = math.clamp((d - dist[lo]) / span, 0, 1)
	local dir = (b.pos - a.pos).Unit
	return a.pos:Lerp(b.pos, t), dir, a.right:Lerp(b.right, t).Unit, lo
end

local function frameAt(d)
	local pos, _, right = sample(d)
	-- tangent from a short window around d, so segment kinks never snap the train's orientation
	local ahead = sample(math.min(d + 3, total))
	local behind = sample(math.max(d - 3, 0))
	local dir = (ahead - behind).Magnitude > 1e-3 and (ahead - behind).Unit or select(2, sample(d))
	local up = dir:Cross(right)
	if up.Magnitude < 0.1 then
		up = Vector3.yAxis
	end
	up = up.Unit
	return CFrame.lookAt(pos + up * SEAT_HEIGHT, pos + up * SEAT_HEIGHT + dir, up), dir
end

-- comfortable speed through the bend ahead (looks 12..40 studs ahead so the train slows before the curve)
local function bendLimit(d)
	local limit = math.huge
	local _, d0 = frameAt(d)
	for _, ahead in ipairs({ 12, 24, 40 }) do
		local _, d1 = frameAt(math.min(d + ahead, total))
		local ang = math.acos(math.clamp(d0:Dot(d1), -1, 1))
		if ang > 0.05 then
			local radius = ahead / ang
			limit = math.min(limit, math.sqrt(LATERAL * radius))
		end
	end
	return math.max(limit, SPEEDS[1])
end

-- ------------------------------------------------------------------ cars behind the locomotive (local decoration)
local carTemplate = mapFolder:FindFirstChild("CartCarTemplate", true)
local function placeCars(r)
	for k, car in ipairs(r.cars or {}) do
		local dk = r.d - k * CAR_GAP
		local frame = frameAt(math.max(dk, 0))
		if dk < 0 then
			frame = frame * CFrame.new(0, 0, -dk) -- still in the station: line up behind the loco
		end
		car:PivotTo(frame * CFrame.new(0, -0.7, 0)) -- CarBody sits 0.7 below the seat line
	end
end
local function removeCars(r)
	for _, car in ipairs(r and r.cars or {}) do
		car:Destroy()
	end
	if r then
		r.cars = nil
	end
end

-- ------------------------------------------------------------------ ride state
local ride = nil -- { cart, seat, hum, d, v, idx, level, state, cars, lastRot, conns }

local STATE_TEXT = {
	ready = "⏹ واقف بالمحطة • اضغط ▶",
	running = "▶ ماشي",
	paused = "⏸ متوقف مؤقتاً • ▶ للاستئناف",
	finished = "🏁 وصلنا",
}

local function refreshUI(r)
	goBtn.Text = r.state == "running" and "⏸" or "▶"
	goBtn.BackgroundColor3 = r.state == "running" and Color3.fromRGB(200, 150, 40) or Color3.fromRGB(50, 170, 90)
	goBtn.Visible = r.state ~= "finished"
	fasterBtn.Visible, slowerBtn.Visible = r.state ~= "finished", r.state ~= "finished"
	endCard.Visible = r.state == "finished"
end

local function endRide(action)
	local r = ride
	if not r then
		return
	end
	ride = nil
	for _, c in ipairs(r.conns or {}) do
		c:Disconnect()
	end
	removeCars(r)
	gui.Enabled = false
	endCard.Visible = false
	caption.Visible = false
	-- the server removes the train and, for "station"/"hub", moves us with the safe teleport
	remote:FireServer(action or "stop")
end
_G.BSCEndCart = function()
	endRide("stop")
end

local function setState(r, s)
	r.state = s
	refreshUI(r)
end

local function toggleGo()
	local r = ride
	if not r or r.state == "finished" then
		return
	end
	if r.state == "running" then
		setState(r, "paused")
	else
		setState(r, "running")
		if r.d < 1 then
			say("🚆 انطلقنا! اترك الأزرار واستمتع بالمناظر", 3)
		end
	end
	play("click")
end

local function changeSpeed(step)
	local r = ride
	if not r or r.state == "finished" then
		return
	end
	r.level = math.clamp(r.level + step, 1, #SPEEDS)
	play("click")
end

goBtn.Activated:Connect(toggleGo)
hornBtn.Activated:Connect(function()
	play("sting")
	say("🚂 توت توت! قطار التخصصات البيولوجية ينطلق", 2.5)
end)
fasterBtn.Activated:Connect(function()
	changeSpeed(1)
end)
slowerBtn.Activated:Connect(function()
	changeSpeed(-1)
end)
exitBtn.Activated:Connect(function()
	endRide("station")
end)
hubBtn.Activated:Connect(function()
	endRide("hub")
end)
againBtn.Activated:Connect(function()
	endRide("again")
end)
UserInputService.InputBegan:Connect(function(input, processed)
	if processed or not ride then
		return
	end
	local k = input.KeyCode
	if k == Enum.KeyCode.W or k == Enum.KeyCode.Up then
		changeSpeed(1)
	elseif k == Enum.KeyCode.S or k == Enum.KeyCode.Down then
		changeSpeed(-1)
	elseif k == Enum.KeyCode.P or k == Enum.KeyCode.Return then
		toggleGo()
	end
end)

local function passFlags(r, fromIdx, toIdx)
	for i = fromIdx + 1, toIdx do
		local p = pts[i]
		local sec = p.flags.s
		if type(sec) == "number" and sec >= 1 and p.label ~= "" then
			r.section = sec
			say(p.label, 3)
			local fact = FACTS[sec]
			if fact then
				task.delay(3.2, function()
					if ride == r and r.section == sec then
						say(fact, 6)
					end
				end)
			end
		end
	end
end

RunService.RenderStepped:Connect(function(dt)
	local r = ride
	if not r then
		return
	end
	caption.Visible = os.clock() < captionUntil
	if not (r.seat.Parent and r.hum.Parent) or r.hum.Health <= 0 then
		endRide("stop")
		return
	end
	dt = math.min(dt, 1 / 20)
	-- cruise target -> bend comfort -> a smooth stop at the end of the line
	local target = r.state == "running" and SPEEDS[r.level] or 0
	target = math.min(target, bendLimit(r.d), math.sqrt(2 * DECEL * math.max(total - r.d, 0)))
	if r.v < target then
		r.v = math.min(target, r.v + ACCEL * dt)
	else
		r.v = math.max(target, r.v - DECEL * dt)
	end
	r.d = math.min(r.d + r.v * dt, total)
	if r.state == "running" and r.d >= total - 0.5 and r.v < 1 then
		r.v = 0
		setState(r, "finished")
		play("achievement")
		local milestone = ReplicatedStorage:FindFirstChild("Milestone")
		if milestone then
			milestone:FireServer("cartFinish")
		end
	end
	local frame, dir = frameAt(r.d)
	local _, _, _, idx = sample(r.d)
	passFlags(r, r.idx, idx)
	r.idx = math.max(r.idx, idx)
	-- ease the rotation (position stays exactly on the rail) so bends feel smooth, not jittery
	local ease = 1 - math.exp(-dt * 10)
	local rot = r.lastRot and r.lastRot:Lerp(frame.Rotation, ease) or frame.Rotation
	r.lastRot = rot
	r.seat.CFrame = CFrame.new(frame.Position) * rot
	r.seat.AssemblyLinearVelocity = dir * r.v
	r.seat.AssemblyAngularVelocity = Vector3.zero
	placeCars(r)
	local stateText = STATE_TEXT[r.state] or ""
	status.Text = r.state == "running"
			and ("%s • التخصص %d/8 • السرعة %d/%d"):format(stateText, r.section or 0, r.level, #SPEEDS)
		or stateText
end)

remote.OnClientEvent:Connect(function(action, cart)
	if action ~= "start" or not cart then
		return
	end
	local char = player.Character
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	local seat = cart:WaitForChild("Seat", 5)
	if not (hum and seat) then
		return
	end
	if ride then
		endRide("stop")
	end
	local r = {
		cart = cart,
		seat = seat,
		hum = hum,
		d = 0,
		v = 0,
		idx = 0,
		level = START_LEVEL,
		state = "ready",
		cars = {},
		conns = {},
	}
	ride = r
	if carTemplate then
		for k = 1, 3 do
			local car = carTemplate:Clone()
			car.Name = "LocalCartCar" .. k
			car.PrimaryPart = car:FindFirstChild("CarBody") -- pivot on the car floor (the template's own pivot is arbitrary)
			for _, p in ipairs(car:GetDescendants()) do
				if p:IsA("BasePart") then
					p.Anchored = true
					p.CanCollide = false
					p.CanQuery = false
					p.CanTouch = false
				end
			end
			car.Parent = workspace
			table.insert(r.cars, car)
		end
	end
	local frame = frameAt(0)
	r.seat.CFrame = frame
	r.lastRot = frame.Rotation
	placeCars(r)
	local milestone = ReplicatedStorage:FindFirstChild("Milestone")
	if milestone then
		milestone:FireServer("cartStart")
	end
	local cam = workspace.CurrentCamera
	cam.CameraType = Enum.CameraType.Custom
	cam.CameraSubject = hum
	gui.Enabled = true
	refreshUI(r)
	say(
		"🚆 أهلاً في قطار التخصصات! اضغط ▶ على لوحة العربة أو الشاشة",
		5
	)
	-- Wire 3D physical buttons mounted on the cart dashboard
	local function wireCartBtn(partName, fn)
		local p = cart:FindFirstChild(partName, true)
		local cd = p and p:FindFirstChildOfClass("ClickDetector")
		if cd then
			table.insert(
				r.conns,
				cd.MouseClick:Connect(function(clicker)
					if clicker == player and ride == r then
						fn()
					end
				end)
			)
		end
	end
	wireCartBtn("CartBtn_Go", toggleGo)
	wireCartBtn("CartBtn_Faster", function()
		changeSpeed(1)
	end)
	wireCartBtn("CartBtn_Slower", function()
		changeSpeed(-1)
	end)
	wireCartBtn("CartBtn_Horn", function()
		play("sting")
		say("🚂 توت توت! قطار التخصصات البيولوجية ينطلق", 2.5)
	end)
	-- jumping out of the seat ends the ride (back on the platform); dying ends it too
	table.insert(
		r.conns,
		hum:GetPropertyChangedSignal("Sit"):Connect(function()
			if not hum.Sit then
				task.wait(0.2)
				if ride == r and not hum.Sit then
					endRide("station")
				end
			end
		end)
	)
	table.insert(
		r.conns,
		hum.Died:Connect(function()
			if ride == r then
				endRide("stop")
			end
		end)
	)
end)
