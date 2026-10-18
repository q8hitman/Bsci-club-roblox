p = "kuwait-parkour/src/server/Obstacles.server.luau"
s = open(p, encoding="utf-8").read()

new_funcs = '''local function makeBlink(part, args, deadly)
	local on = tonumber(args[2]) or 2.5
	local off = tonumber(args[3]) or 1.5
	local phase = tonumber(args[4]) or 0
	local solidTransparency = part.Transparency
	local period = on + off
	task.spawn(function()
		task.wait(phase % period)
		while part.Parent do
			part.Transparency = solidTransparency
			part.CanCollide = not deadly
			part.CanTouch = true
			task.wait(on)
			-- warning flicker before it vanishes
			for _ = 1, 3 do
				part.Transparency = 0.6
				task.wait(0.08)
				part.Transparency = solidTransparency
				task.wait(0.08)
			end
			part.Transparency = deadly and 1 or 0.85
			part.CanCollide = false
			part.CanTouch = false
			task.wait(math.max(off - 0.48, 0.1))
		end
	end)
end

local rotoGroups = {} -- id -> { speed, parts }

local function makeRoto(part, args)
	local id = args[3] or args[2]
	local g = rotoGroups[id]
	if not g then
		g = { speed = tonumber(args[2]) or 0.5, parts = {} }
		rotoGroups[id] = g
	end
	table.insert(g.parts, part)
end

local function finishRoto()
	for _, g in pairs(rotoGroups) do
		local first = g.parts[1]
		local axle = Instance.new("Part")
		axle.Name = "RotoAxle"
		axle.Anchored = true
		axle.CanCollide = false
		axle.CanQuery = false
		axle.Transparency = 1
		axle.Size = Vector3.new(0.5, 0.5, 0.5)
		axle.CFrame = first.CFrame
		axle.Parent = first.Parent
		for i = 2, #g.parts do
			local w = Instance.new("WeldConstraint")
			w.Part0 = first
			w.Part1 = g.parts[i]
			w.Parent = first
		end
		for _, p in ipairs(g.parts) do
			p.Anchored = false
		end
		local a0 = Instance.new("Attachment")
		a0.CFrame = CFrame.Angles(0, 0, math.rad(90))
		a0.Parent = axle
		local a1 = Instance.new("Attachment")
		a1.CFrame = CFrame.Angles(0, 0, math.rad(90))
		a1.Parent = first
		local hinge = Instance.new("HingeConstraint")
		hinge.Attachment0 = a0
		hinge.Attachment1 = a1
		hinge.ActuatorType = Enum.ActuatorType.Motor
		hinge.MotorMaxTorque = 1e10
		hinge.MotorMaxAcceleration = 1e5
		hinge.AngularVelocity = g.speed
		hinge.Parent = first
		first:SetNetworkOwner(nil)
	end
end

'''
marker = "local ghosts = {}"
assert marker in s
s = s.replace(marker, new_funcs + marker, 1)

old = '''		elseif kind == "Kill" then
			makeKill(inst)'''
new = '''		elseif kind == "Kill" then
			makeKill(inst)
		elseif kind == "KillBlink" then
			makeKill(inst)
			makeBlink(inst, args, true)
		elseif kind == "Blink" then
			makeBlink(inst, args, false)
		elseif kind == "Roto" then
			makeRoto(inst, args)'''
assert old in s
s = s.replace(old, new, 1)

s = s.rstrip() + "\n\nfinishRoto()\n"
open(p, "w", encoding="utf-8").write(s)
print("obstacles patched")
