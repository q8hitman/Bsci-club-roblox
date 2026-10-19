-- Local assembly models; no shared world geometry is changed.
local Tween = game:GetService("TweenService")
local V = {}
local C = Color3.fromRGB(76, 231, 193)
local function part(parent, name, size, pos, color, shape)
	local p = Instance.new("Part")
	p.Name = name
	p.Size = size
	p.CFrame = CFrame.new(pos)
	p.Color = color
	p.Anchored = true
	p.CanCollide = false
	if shape then
		p.Shape = shape
	end
	p.Parent = parent
	return p
end
local function move(p, goal)
	Tween:Create(p, TweenInfo.new(0.65), goal):Play()
end
function V.draw(view, d, state)
	for _, v in view:GetChildren() do
		if v:IsA("WorldModel") or v:IsA("Camera") then
			v:Destroy()
		end
	end
	local source = workspace.Map.Campus.Museum46:FindFirstChild("Exhibit_" .. d.id)
	if not source then
		return
	end
	local world = Instance.new("WorldModel")
	world.Parent = view
	local model = source.Display:Clone()
	model.Parent = world
	local originalPivot = model:GetPivot()
	model:PivotTo(originalPivot - originalPivot.Position)
	local n = math.min(state.step - 1, #d.steps)
	local objects = model:GetDescendants()
	if d.id == "micro" then
		for i = 1, 3 do
			part(
				model,
				"ClassificationTray_" .. i,
				Vector3.new(5, 0.25, 5),
				Vector3.new((i - 2) * 6, -2, 8),
				Color3.fromRGB(45, 90, 101)
			)
		end
		for _, p in ipairs(objects) do
			if p:IsA("BasePart") then
				local group = ({ Bacillus = 1, Yeast = 2, Bud = 2, Nucleus = 2, Paramecium = 3, Cilium = 3 })[p.Name]
				if group and n >= group then
					move(p, { Position = p.Position + Vector3.new(0, 0, 8), Color = C })
				end
			end
		end
	elseif d.id == "enzyme" then
		local k = 0
		for _, p in ipairs(objects) do
			if p:IsA("BasePart") and p.Name == "Substrate" then
				k += 1
				if n == 1 then
					move(p, { Position = p.Position - Vector3.new(0, 2.5, 0) })
				elseif n == 2 then
					move(p, {
						Position = Vector3.new(k == 1 and -5 or 5, 1, 7),
						Color = k == 1 and C or Color3.fromRGB(255, 205, 100),
					})
				end
			end
		end
		if n == 2 then
			part(model, "ProductsTray", Vector3.new(15, 0.3, 5), Vector3.new(0, -1, 7), Color3.fromRGB(42, 80, 90))
		end
	elseif d.id == "animal" then
		for _, p in ipairs(objects) do
			if p:IsA("BasePart") and p.Name == "Ear" and p.Position.X < 0 then
				local size = p.Size
				p.Size = Vector3.new(size.X, 0.35, size.Z)
				if n >= 1 then
					move(p, { Size = size, Color = C })
				end
			end
		end
		if n >= 2 then
			local coat = part(
				model,
				"FurAndFatInsulation",
				Vector3.new(4.6, 4.6, 4.6),
				Vector3.new(5, -0.2, 0),
				Color3.fromRGB(222, 232, 233),
				Enum.PartType.Ball
			)
			coat.Transparency = 0.25
		end
	elseif d.id == "plant" then
		for i, pos in ipairs({ Vector3.new(-7, -1, 4), Vector3.new(7, -1, 4) }) do
			local inlet =
				part(model, "Inlet_" .. i, Vector3.new(2, 2, 2), pos, Color3.fromRGB(97, 174, 238), Enum.PartType.Ball)
			if n >= 1 then
				move(inlet, { Position = Vector3.new(i == 1 and -2 or 2, 1, 0), Color = C })
			end
		end
		if n >= 2 then
			part(
				model,
				"SunlightEnergy",
				Vector3.new(4, 4, 4),
				Vector3.new(0, 6, 0),
				Color3.fromRGB(255, 224, 96),
				Enum.PartType.Ball
			).Material =
				Enum.Material.Neon
		end
		if n >= 3 then
			part(model, "SugarProduct", Vector3.new(2, 2, 2), Vector3.new(-5, 2, 7), Color3.fromRGB(255, 194, 120))
			part(model, "OxygenProduct", Vector3.new(2, 2, 2), Vector3.new(5, 2, 7), C, Enum.PartType.Ball)
		end
	elseif d.id == "dna" then
		for _, p in ipairs(objects) do
			if p:IsA("BasePart") and p.Name == "BasePair" then
				p.Transparency = 1
			end
		end
		for i = 1, 4 do
			local rung = part(
				model,
				"ComplementSlot_" .. i,
				Vector3.new(8, 0.5, 0.7),
				Vector3.new(0, -4 + i * 2, 5),
				Color3.fromRGB(74, 87, 106)
			)
			if i <= n then
				move(rung, {
					Color = ({
						C,
						Color3.fromRGB(255, 185, 92),
						Color3.fromRGB(170, 150, 240),
						Color3.fromRGB(110, 191, 245),
					})[i],
				})
			end
		end
	elseif d.id == "evidence" then
		for _, p in ipairs(objects) do
			if p:IsA("BasePart") and p.Position.X > -4 and p.Position.X < 0 and n >= 1 then
				if p.Name == "Lane" then
					p.Color = Color3.fromRGB(38, 112, 98)
				elseif p.Name == "Band" then
					p.Color = C
				end
			end
		end
		if n >= 1 then
			part(model, "PatternMatch", Vector3.new(8, 0.5, 1), Vector3.new(-5, -4, 1), C)
		end
	elseif d.id == "farm" then
		for _, p in ipairs(objects) do
			if p:IsA("BasePart") then
				if p.Name == "WaterTank" and n >= 1 then
					p.Color = Color3.fromRGB(63, 180, 235)
				end
				if p.Name == "GrowLamp" then
					p.Material = n >= 2 and Enum.Material.Neon or Enum.Material.SmoothPlastic
				end
				if p.Name == "Stem" and n >= 2 then
					move(p, { Size = p.Size + Vector3.new(0, 3, 0), Position = p.Position + Vector3.new(0, 1.5, 0) })
				end
				if p.Name == "Leaf" and n >= 2 then
					move(p, { Size = p.Size * 1.4, Color = C, Position = p.Position + Vector3.new(0, 3, 0) })
				end
			end
		end
	elseif d.id == "biotech" then
		for _, p in ipairs(objects) do
			if p:IsA("BasePart") then
				if p.Name == "YeastCell" then
					p.Transparency = n >= 2 and 0 or 1
					if n >= 3 then
						Tween:Create(
							p,
							TweenInfo.new(1, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, 2, true),
							{ Position = p.Position + Vector3.new(0, 1, 0) }
						):Play()
					end
				elseif p.Name == "Culture" then
					p.Transparency = n >= 3 and 0.35 or 1
				elseif p.Name == "Pipe" and n >= 3 then
					p.Color = C
				end
			end
		end
		if n >= 1 then
			for i = 1, 4 do
				part(model, "GeneticInstruction_" .. i, Vector3.new(1, 0.4, 2), Vector3.new(-15, -3 + i, 3), C)
			end
		end
		if n >= 4 then
			for i = 1, 5 do
				part(
					model,
					"PurifiedEnzyme_" .. i,
					Vector3.new(1.1, 1.1, 1.1),
					Vector3.new(13 + (i % 2) * 2, -4 + i, 4),
					Color3.fromRGB(255, 204, 113),
					Enum.PartType.Ball
				)
			end
		end
	end
	local cf, size = model:GetBoundingBox()
	local camera = Instance.new("Camera")
	camera.FieldOfView = 40
	local aspect = math.max(0.5, view.AbsoluteSize.X / math.max(1, view.AbsoluteSize.Y))
	local dist = math.max(size.Y, size.X / aspect, size.Z) * 1.7 + 5
	camera.CFrame = CFrame.lookAt(cf.Position + Vector3.new(dist * 0.25, dist * 0.25, dist), cf.Position)
	camera.Parent = view
	view.CurrentCamera = camera
	local diagram = view.Assembly
	if d.id == "dna" then
		local seq = {}
		for i = 1, n do
			table.insert(seq, d.steps[i].correct)
		end
		diagram.Text = "5′ ATGC 3′\n3′ " .. table.concat(seq) .. string.rep("?", 4 - n) .. " 5′"
	elseif d.id == "micro" then
		diagram.Text = ({
			"صنّف الخلايا في الصواني",
			"البكتيريا ✓",
			"البكتيريا ✓ • الفطر ✓",
			"بكتيريا • فطر • طلائعي ✓",
		})[n + 1]
	elseif d.id == "animal" then
		diagram.Text = ({ "ركّب التكيفات", "أذنا الفنك ✓", "العزل القطبي ✓" })[n + 1]
	elseif d.id == "enzyme" then
		diagram.Text = ({
			"الركيزة → موقع الإنزيم",
			"ارتباط اللاكتوز ✓",
			"جلوكوز + جالاكتوز ✓",
		})[n + 1]
	elseif d.id == "plant" then
		diagram.Text = ({
			"املأ منافذ الورقة",
			"الماء + CO₂ ✓",
			"طاقة ضوئية ✓",
			"سكريات + أكسجين ✓",
		})[n + 1]
	elseif d.id == "evidence" then
		diagram.Text = ({
			"الدليل | A | B | C",
			"النمط A مطابق ✓",
			"تطابق في النموذج فقط ✓",
		})[n + 1]
	elseif d.id == "biotech" then
		diagram.Text = ({
			"صمّم خط الإنتاج",
			"تعليمات وراثية ✓",
			"خلية مناسبة ✓",
			"إنتاج مضبوط ✓",
			"تنقية وتحقق ✓",
		})[n + 1]
	else
		diagram.Text = ({ "ماء + ضوء → نمو", "الماء ملائم ✓", "النبات ينمو ✓" })[n + 1]
	end
end
return V
