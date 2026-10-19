-- Separate per-player sessions. Client choices never directly grant completion or XP.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local Http = game:GetService("HttpService")
local D = require(RS.Shared.MuseumData)
local R = require(RS.Shared.MuseumRules)
local Profiles = require(script.Parent.Profiles)
local Passport = require(script.Parent.PassportService)
local museum = workspace:WaitForChild("Map"):WaitForChild("Campus"):WaitForChild("Museum46")
local remote = Instance.new("RemoteFunction")
remote.Name = "Museum"
remote.Parent = RS
local open = Instance.new("RemoteEvent")
open.Name = "MuseumOpen"
open.Parent = RS
local sessions, last = {}, {}
local function near(p, id)
	local root = p.Character and p.Character:FindFirstChild("HumanoidRootPart")
	local hum = p.Character and p.Character:FindFirstChildOfClass("Humanoid")
	local station = museum:FindFirstChild("Exhibit_" .. id)
	local anchor = station and station:FindFirstChild("Console")
	return root and hum and hum.Health > 0 and anchor and (root.Position - anchor.Position).Magnitude < 24
end
local function snapshot(p, s, ok, note)
	return {
		id = s.id,
		token = s.token,
		step = s.step,
		done = s.done,
		ok = ok,
		note = note,
		passport = Passport.refresh(p),
	}
end
for _, d in ipairs(D.Exhibits) do
	local console = museum:WaitForChild("Exhibit_" .. d.id):WaitForChild("Console")
	local prompt = Instance.new("ProximityPrompt")
	prompt.Name = "MuseumPrompt"
	prompt.ActionText = "جرّب المعروضة"
	prompt.ObjectText = d.ar
	prompt.MaxActivationDistance = 12
	prompt.RequiresLineOfSight = false
	prompt.Parent = console
	prompt.Triggered:Connect(function(p)
		if near(p, d.id) then
			open:FireClient(p, d.id)
		end
	end)
end
remote.OnServerInvoke = function(p, action, id, token, step, choice)
	if type(action) ~= "string" or type(id) ~= "string" or not D.get(id) or not Profiles.state[p] then
		return { error = "طلب غير صالح" }
	end
	if action == "close" then
		local s = sessions[p]
		if s and s.token == token then
			sessions[p] = nil
		end
		return { closed = true }
	end
	if not near(p, id) then
		sessions[p] = nil
		return { error = "اقترب من المعروضة وافتحها من جديد" }
	end
	local now = os.clock()
	if last[p] and now - last[p] < 0.12 then
		return { error = "تمهّل ثم أعد المحاولة", retry = true }
	end
	last[p] = now
	if action == "start" then
		local s = R.start(id)
		s.token = Http:GenerateGUID(false)
		s.at = now
		s.character = p.Character
		s.travelRevision = p:GetAttribute("TeleportRevision")
		sessions[p] = s
		return snapshot(p, s, true, "")
	end
	local s = sessions[p]
	if
		action ~= "act"
		or not s
		or s.id ~= id
		or s.token ~= token
		or s.step ~= step
		or s.done
		or now - s.at > 300
		or s.character ~= p.Character
		or s.travelRevision ~= p:GetAttribute("TeleportRevision")
	then
		return { error = "انتهت الجلسة؛ افتح المعروضة من جديد" }
	end
	local current = D.get(id).steps[s.step]
	local ok = R.act(s, choice)
	if s.done then
		Passport.record(p, "museum", id)
	end
	return snapshot(p, s, ok, (ok and "✓ " or "جرّب مرة ثانية: ") .. current.note)
end
Players.PlayerRemoving:Connect(function(p)
	sessions[p], last[p] = nil, nil
end)
task.spawn(function()
	while museum.Parent do
		task.wait(0.2)
		for p, s in pairs(sessions) do
			if
				s.character ~= p.Character
				or s.travelRevision ~= p:GetAttribute("TeleportRevision")
				or not near(p, s.id)
			then
				sessions[p] = nil
			end
		end
	end
end)
