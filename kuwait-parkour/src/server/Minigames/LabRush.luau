-- مختبر الفوضى (Lab Rush): a co-op round in a fantasy lab. The order board always shows 3 orders; the team works the
-- four stations (ProximityPrompts, so it plays the same on phones) to fill them. Solo works too, a team is faster.
-- Everything here is playful fiction, not real lab procedure (said on the board and in the hint).
--   🧬 DNA Mixer      press the base bins in the board's order (progress is shared by the whole team)
--   🧪 Mutation       pick the two ingredients, then press Mix -> a silly creature pops out
--   🔬 Sample Sorter  send each sample to the bin that matches the rule (by shape or by colour; the rule changes)
--   ⚡ Lab Reactor    pull both levers together (7 s window solo, 2.5 s with friends)
-- The round ends when the team reaches its goal (all win) or time runs out (nobody loses anything).
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local M = {
	id = "LabRush",
	ar = "🧪 مختبر الفوضى (تعاوني)",
	hint = "خلّصوا طلبات اللوحة مع بعض! اضغط على الأجهزة 👆 (مختبر خيالي للعب، مو إجراءات حقيقية)",
	duration = 150,
	mode = "coop",
}

local LETTERS = { "A", "T", "G", "C" }
local INGREDIENTS = { "🧀 جبنة فضائية", "🌶️ فلفل مشع", "🧊 ثلج أزرق" }
local SHAPES = { Enum.PartType.Ball, Enum.PartType.Block, Enum.PartType.Cylinder }
local SHAPE_AR = { "دائري ●", "مكعب ■", "أسطواني ▮" }
local COLORS = { Color3.fromRGB(230, 80, 80), Color3.fromRGB(80, 140, 230), Color3.fromRGB(240, 200, 60) }
local COLOR_AR = { "أحمر", "أزرق", "أصفر" }
local KINDS = { "dna", "mutation", "sort", "reactor" }

local function notify(player, text)
	local ev = ReplicatedStorage:FindFirstChild("Notify")
	if ev and player.Parent then
		ev:FireClient(player, text)
	end
end

local function flash(part, color, t)
	if not part or not part.Parent then
		return
	end
	local old = part:GetAttribute("BaseColor") or part.Color
	part:SetAttribute("BaseColor", old)
	part.Color = color
	task.delay(t or 0.35, function()
		if part.Parent then
			part.Color = old
		end
	end)
end

function M.start(ctx)
	local arena = ctx.arena
	local tier = ctx.tier or 1
	local function find(name)
		return arena:FindFirstChild(name)
	end
	local board = find("OrderBoard")
	local boardText = board and board:FindFirstChildWhichIsA("TextLabel", true)

	local nPlayers = 0
	for _ in pairs(ctx.alive) do
		nPlayers += 1
	end
	local goal = math.clamp(4 + 2 * (nPlayers - 1) + (tier - 1), 4, 14)
	local done = 0
	ctx.prompts, ctx.temp = {}, {}
	local orders = {}

	local function temp(inst)
		table.insert(ctx.temp, inst)
		return inst
	end

	local function prompt(part, action, object)
		local p = Instance.new("ProximityPrompt")
		p.ActionText = action
		p.ObjectText = object or ""
		p.HoldDuration = 0
		p.MaxActivationDistance = 11
		p.RequiresLineOfSight = false
		p.Parent = part
		table.insert(ctx.prompts, p)
		return p
	end

	local function orderText(o)
		if o.kind == "dna" then
			local s = {}
			for i, L in ipairs(o.seq) do
				s[i] = i < o.idx and ("✅" .. L) or L
			end
			return "🧬 DNA: " .. table.concat(s, " ")
		elseif o.kind == "mutation" then
			return "🧪 طفرة: " .. INGREDIENTS[o.pair[1]] .. " + " .. INGREDIENTS[o.pair[2]]
		elseif o.kind == "sort" then
			return ("🔬 افرز حسب %s (%d/3)"):format(
				o.rule == "shape" and "الشكل" or "اللون",
				o.count
			)
		else
			return "⚡ المفاعل: اسحبوا الذراعين مع بعض"
		end
	end

	local function refresh()
		if not boardText then
			return
		end
		local lines = { ("✅ الفريق %d/%d"):format(done, goal) }
		if ctx.teamDone then
			table.insert(lines, "🎉 خلّصتوا كل الطلبات!")
		else
			for _, o in ipairs(orders) do
				table.insert(lines, orderText(o))
			end
		end
		table.insert(lines, "مختبر خيالي للعب")
		boardText.Text = table.concat(lines, "\n")
	end

	local spawnSample -- forward

	local function newOrder()
		local used = {}
		for _, o in ipairs(orders) do
			used[o.kind] = true
		end
		local free = {}
		for _, k in ipairs(KINDS) do
			if not used[k] then
				table.insert(free, k)
			end
		end
		local kind = free[math.random(1, #free)]
		local o = { kind = kind }
		if kind == "dna" then
			o.seq, o.idx = {}, 1
			for i = 1, 3 + math.min(tier, 2) do
				o.seq[i] = LETTERS[math.random(1, 4)]
			end
		elseif kind == "mutation" then
			local a = math.random(1, 3)
			local b = (a + math.random(0, 1)) % 3 + 1 -- always different from a
			o.pair = { a, b }
		elseif kind == "sort" then
			o.rule = math.random() < 0.5 and "shape" or "color"
			o.count = 0
		end
		table.insert(orders, o)
		if kind == "sort" then
			spawnSample()
		end
	end

	local function orderOf(kind)
		for _, o in ipairs(orders) do
			if o.kind == kind then
				return o
			end
		end
		return nil
	end

	local function complete(o, player)
		for i, x in ipairs(orders) do
			if x == o then
				table.remove(orders, i)
				break
			end
		end
		done += 1
		if player then
			ctx.addScore(player, 2)
		end
		for p in pairs(ctx.alive) do
			notify(p, ("✅ طلب خلص! الفريق %d/%d"):format(done, goal))
		end
		if done >= goal then
			ctx.teamDone = true
		else
			task.delay(1, function()
				if ctx.running and not ctx.teamDone then
					newOrder()
					refresh()
				end
			end)
		end
		refresh()
	end

	-- 🧬 DNA mixer
	local console = find("DNAConsole")
	for _, L in ipairs(LETTERS) do
		local bin = find("DNABin|" .. L)
		if bin then
			ctx.connect(prompt(bin, "حط " .. L, "DNA").Triggered:Connect(function(player)
				if not (ctx.running and ctx.alive[player]) then
					return
				end
				local o = orderOf("dna")
				if not o then
					notify(player, "ما في طلب DNA الحين")
					return
				end
				if o.seq[o.idx] == L then
					o.idx += 1
					flash(console, Color3.fromRGB(80, 220, 120))
					if o.idx > #o.seq then
						complete(o, player)
					else
						refresh()
					end
				else
					o.idx = 1
					flash(console, Color3.fromRGB(230, 70, 70))
					notify(player, "❌ الترتيب غلط، نبدأ من أول حرف")
					refresh()
				end
			end))
		end
	end

	-- 🧪 mutation machine
	local selected = {}
	local ingredientParts = {}
	for i = 1, 3 do
		local part = find("MutIngredient|" .. i)
		ingredientParts[i] = part
		if part then
			ctx.connect(prompt(part, "اختار", INGREDIENTS[i]).Triggered:Connect(function(player)
				if not (ctx.running and ctx.alive[player]) then
					return
				end
				if selected[i] then
					selected[i] = nil
					part.Material = Enum.Material.SmoothPlastic
					return
				end
				local n = 0
				for _ in pairs(selected) do
					n += 1
				end
				if n >= 2 then
					notify(player, "اخترتوا مكوّنين، اضغطوا «اخلط»")
					return
				end
				selected[i] = true
				part.Material = Enum.Material.Neon
			end))
		end
	end
	local machine = find("MutMachine")
	local output = find("MutOutput")
	local function creature(ok)
		if not output then
			return
		end
		local body = temp(Instance.new("Part"))
		body.Name = ok and "Creature" or "FailedMix"
		body.Shape = Enum.PartType.Ball
		body.Size = Vector3.new(4, 4, 4)
		body.Anchored = true
		body.CanCollide = false
		body.Material = ok and Enum.Material.SmoothPlastic or Enum.Material.Slate
		body.Color = ok and Color3.fromHSV(math.random(), 0.6, 1) or Color3.fromRGB(120, 120, 120)
		body.CFrame = CFrame.new(output.Position + Vector3.new(0, 2.2, 0))
		body.Parent = arena
		if ok then
			for s = -1, 1, 2 do
				local eye = Instance.new("Part")
				eye.Shape = Enum.PartType.Ball
				eye.Size = Vector3.new(1.1, 1.1, 1.1)
				eye.Anchored = true
				eye.CanCollide = false
				eye.Color = Color3.new(1, 1, 1)
				eye.CFrame = body.CFrame * CFrame.new(s * 0.8, 0.7, 1.7)
				eye.Parent = body
			end
			TweenService:Create(body, TweenInfo.new(0.4, Enum.EasingStyle.Sine, Enum.EasingDirection.Out, 5, true), {
				CFrame = body.CFrame + Vector3.new(0, 1.5, 0),
			}):Play()
		end
		task.delay(ok and 5 or 2, function()
			if body.Parent then
				body:Destroy()
			end
		end)
	end
	if machine then
		ctx.connect(prompt(machine, "اخلط", "آلة الطفرات").Triggered:Connect(function(player)
			if not (ctx.running and ctx.alive[player]) then
				return
			end
			local o = orderOf("mutation")
			local picked = {}
			for i in pairs(selected) do
				table.insert(picked, i)
			end
			local okMix = o
				and #picked == 2
				and (
					(picked[1] == o.pair[1] and picked[2] == o.pair[2])
					or (picked[1] == o.pair[2] and picked[2] == o.pair[1])
				)
			for i in pairs(selected) do
				if ingredientParts[i] then
					ingredientParts[i].Material = Enum.Material.SmoothPlastic
				end
			end
			table.clear(selected)
			creature(okMix)
			if okMix then
				complete(o, player)
			elseif not o then
				notify(player, "ما في طلب طفرة الحين")
			else
				notify(player, "💨 الخلطة غلط! شوف المكوّنين على اللوحة")
			end
		end))
	end

	-- 🔬 sample sorter
	local belt = find("SorterBelt")
	local sample = nil
	spawnSample = function()
		if sample and sample.part.Parent then
			sample.part:Destroy()
		end
		sample = nil
		if not (belt and ctx.running and orderOf("sort")) then
			return
		end
		local s, c = math.random(1, 3), math.random(1, 3)
		local part = temp(Instance.new("Part"))
		part.Name = "Sample"
		part.Shape = SHAPES[s]
		part.Size = s == 3 and Vector3.new(2.6, 2, 2) or Vector3.new(2.2, 2.2, 2.2)
		part.Anchored = true
		part.CanCollide = false
		part.Color = COLORS[c]
		part.Material = Enum.Material.SmoothPlastic
		part.CFrame = belt.CFrame + Vector3.new(0, 1.2, 0)
		part.Parent = arena
		TweenService
			:Create(part, TweenInfo.new(2.5, Enum.EasingStyle.Sine), { CFrame = belt.CFrame + Vector3.new(6, 1.2, 0) })
			:Play()
		sample = { part = part, shape = s, color = c }
	end
	for i = 1, 3 do
		local bin = find("SortBin|" .. i)
		if bin then
			ctx.connect(
				prompt(bin, "حط العيّنة هنا", SHAPE_AR[i] .. " • " .. COLOR_AR[i]).Triggered:Connect(
					function(player)
						if not (ctx.running and ctx.alive[player]) then
							return
						end
						local o = orderOf("sort")
						if not (o and sample) then
							notify(player, "ما في عيّنة للفرز الحين")
							return
						end
						local want = o.rule == "shape" and sample.shape or sample.color
						if want == i then
							o.count += 1
							flash(bin, Color3.fromRGB(80, 220, 120))
							if o.count >= 3 then
								complete(o, player)
								if sample and sample.part.Parent then
									sample.part:Destroy()
								end
								sample = nil
								return
							end
						else
							flash(bin, Color3.fromRGB(230, 70, 70))
							notify(
								player,
								o.rule == "shape" and "❌ القاعدة: حسب الشكل"
									or "❌ القاعدة: حسب اللون"
							)
						end
						refresh()
						task.delay(0.6, spawnSample)
					end
				)
			)
		end
	end

	-- ⚡ lab reactor
	local window = nPlayers <= 1 and 7 or 2.5
	local lastPull = {}
	local core = find("ReactorCore")
	for i = 1, 2 do
		local lever = find("ReactorLever|" .. i)
		if lever then
			ctx.connect(prompt(lever, "اسحب", "ذراع المفاعل " .. i).Triggered:Connect(function(player)
				if not (ctx.running and ctx.alive[player]) then
					return
				end
				local o = orderOf("reactor")
				if not o then
					notify(player, "ما في طلب مفاعل الحين")
					return
				end
				lastPull[i] = os.clock()
				flash(lever, Color3.fromRGB(120, 255, 200), 0.6)
				local other = lastPull[3 - i]
				if other and os.clock() - other <= window then
					table.clear(lastPull)
					if core then
						flash(core, Color3.fromRGB(255, 255, 160), 1.2)
					end
					complete(o, player)
				else
					notify(player, ("⚡ الحين الذراع الثاني خلال %d ثواني!"):format(window))
				end
			end))
		end
	end

	for _ = 1, 3 do
		newOrder()
	end
	refresh()
end

function M.stop(ctx)
	for _, p in ipairs(ctx.prompts or {}) do
		p:Destroy()
	end
	for _, t in ipairs(ctx.temp or {}) do
		if t.Parent then
			t:Destroy()
		end
	end
	for _, part in ipairs(ctx.arena:GetChildren()) do
		if part:IsA("BasePart") then
			local base = part:GetAttribute("BaseColor")
			if base then
				part.Color = base
			end
			if part.Name:match("^MutIngredient") then
				part.Material = Enum.Material.SmoothPlastic
			end
		end
	end
	local board = ctx.arena:FindFirstChild("OrderBoard")
	local label = board and board:FindFirstChildWhichIsA("TextLabel", true)
	if label then
		label.Text = "🧪 Lab Rush\nمختبر الفوضى"
	end
end

return M
