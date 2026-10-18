"""Adds v9 obstacle kinds (Gate, SimonLamp, Swing, Orbit, timed Button) to Obstacles.server.luau."""
p = "kuwait-parkour/src/server/Obstacles.server.luau"
s = open(p, encoding="utf-8").read()
T = "\t"


def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)


rep("--   Ghost|id   Button|id  SeqKey|id|LETTERS   SeqBtn|id|LETTER\n",
    "--   Ghost|id   Button|id|seconds   SeqKey|id|LETTERS   SeqBtn|id|LETTER\n"
    "--   Gate|id               (solid wall that opens with its Button / solved puzzle)\n"
    "--   SimonLamp|id|LETTER   (lamps that keep flashing the SeqKey pattern of their puzzle)\n"
    "--   Swing|dx,dy,dz|deg|period|phase[|safe]   (pendulum around the path axis, pivot = position + d)\n"
    "--   Orbit|dx,dy,dz|speed  (kill ball circling the point position + d)\n")
rep('local Players = game:GetService("Players")\n',
    'local Players = game:GetService("Players")\nlocal RunService = game:GetService("RunService")\n')
rep("local ghosts = {}\nlocal open = {}", "local ghosts = {}\nlocal gates = {}\nlocal open = {}")
rep(T + "for _, g in ipairs(ghosts[id] or {}) do\n" + T * 2 + "g.CanCollide = true\n" + T * 2 + "g.Transparency = 0.1\n" + T + "end\n",
    T + "for _, g in ipairs(ghosts[id] or {}) do\n" + T * 2 + "g.CanCollide = true\n" + T * 2 + "g.Transparency = 0.1\n" + T + "end\n"
    + T + "for _, g in ipairs(gates[id] or {}) do\n" + T * 2 + "g.CanCollide = false\n" + T * 2 + "g.Transparency = 0.85\n" + T + "end\n")
rep(T * 2 + "open[id] = nil\n",
    T * 2 + "for _, g in ipairs(gates[id] or {}) do\n" + T * 3 + "g.CanCollide = true\n" + T * 3 + "g.Transparency = 0.2\n"
    + T * 2 + "end\n" + T * 2 + "open[id] = nil\n")
rep("openGhosts(args[2], 14)", "openGhosts(args[2], tonumber(args[3]) or 14)")

HELPERS = '''-- memory puzzle: the lamps replay the stored pattern forever
local simonLamps = {} -- [id][LETTER] = part

local function runSimon(id)
	local lamps = simonLamps[id]
	local key = seqKeys[id]
	if not (lamps and key) then
		return
	end
	local dim = {}
	for letter, lamp in pairs(lamps) do
		dim[letter] = lamp.Color
	end
	task.spawn(function()
		while true do
			for i = 1, #key do
				local letter = key:sub(i, i)
				local lamp = lamps[letter]
				if lamp then
					local c = dim[letter]
					lamp.Color = Color3.new(math.min(c.R * 4, 1), math.min(c.G * 4, 1), math.min(c.B * 4, 1))
					task.wait(0.55)
					lamp.Color = c
					task.wait(0.25)
				end
			end
			task.wait(2.2)
		end
	end)
end

-- anchored parts animated every frame (pendulums, orbiting electrons)
local animated = {}

local function addAnimated(part, args, kind)
	local d = nums(args[2])
	local pivot = CFrame.new(part.Position + Vector3.new(d[1] or 0, d[2] or 0, d[3] or 0))
	local a = { part = part, pivot = pivot, rel = pivot:Inverse() * part.CFrame, kind = kind }
	if kind == "swing" then
		a.amp = math.rad(tonumber(args[3]) or 50)
		a.period = tonumber(args[4]) or 2.5
		a.phase = tonumber(args[5]) or 0
	else
		a.speed = tonumber(args[3]) or 2
	end
	table.insert(animated, a)
	if args[6] ~= "safe" then
		makeKill(part)
	end
end

RunService.Heartbeat:Connect(function()
	local now = workspace:GetServerTimeNow()
	for _, a in ipairs(animated) do
		if a.kind == "swing" then
			local angle = a.amp * math.sin((now + a.phase) * 2 * math.pi / a.period)
			a.part.CFrame = a.pivot * CFrame.Angles(0, 0, angle) * a.rel
		else
			a.part.CFrame = a.pivot * CFrame.Angles(0, now * a.speed, 0) * a.rel
		end
	end
end)

local rotoGroups, wheelGroups = {}, {}'''
rep("local rotoGroups, wheelGroups = {}, {}", HELPERS)
rep(T * 2 + 'elseif kind == "Button" then\n',
    T * 2 + 'elseif kind == "Gate" then\n'
    + T * 3 + "gates[args[2]] = gates[args[2]] or {}\n" + T * 3 + "table.insert(gates[args[2]], inst)\n"
    + T * 2 + 'elseif kind == "SimonLamp" then\n'
    + T * 3 + "simonLamps[args[2]] = simonLamps[args[2]] or {}\n" + T * 3 + "simonLamps[args[2]][args[3]] = inst\n"
    + T * 2 + 'elseif kind == "Swing" then\n' + T * 3 + 'addAnimated(inst, args, "swing")\n'
    + T * 2 + 'elseif kind == "Orbit" then\n' + T * 3 + 'addAnimated(inst, args, "orbit")\n'
    + T * 2 + 'elseif kind == "Button" then\n')
rep("for _, g in pairs(rotoGroups) do", "for id in pairs(simonLamps) do\n" + T + "runSimon(id)\nend\n\nfor _, g in pairs(rotoGroups) do")
open(p, "w", encoding="utf-8").write(s)
print("obstacles patched")
