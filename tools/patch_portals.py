p = "kuwait-parkour/src/server/Main.server.luau"
s = open(p, encoding="utf-8").read()

# 1) portals + in-course flag, inserted right after placeAtCheckpoint is defined
anchor = '''-- Server-authoritative state.'''
assert anchor in s, "anchor missing"
portal_code = '''-- Portals: "Portal|Course" resumes the obby at the saved checkpoint, "Portal|Campus" returns.
local campusSpawn = mapFolder:FindFirstChild("CampusSpawn", true)
local portalCooldown = {} -- [Player] = os.clock()

local function teleportPlayer(player, toCourse)
	local char = player.Character
	if not (char and char.Parent) then
		return
	end
	local now = os.clock()
	if portalCooldown[player] and now - portalCooldown[player] < 2 then
		return
	end
	portalCooldown[player] = now
	player:SetAttribute("InCourse", toCourse)
	if toCourse then
		local stage = player:GetAttribute("Stage") or 0
		local cp = checkpoints[stage]
		if cp then
			char:PivotTo(cp.CFrame + Vector3.new(0, 4, 0))
		end
	elseif campusSpawn then
		char:PivotTo(campusSpawn.CFrame + Vector3.new(0, 4, 0))
	end
end

for _, inst in ipairs(mapFolder:GetDescendants()) do
	if inst:IsA("BasePart") then
		local kind = inst.Name:match("^Portal|(%w+)$")
		if kind then
			inst.Touched:Connect(function(hit)
				local plr = game:GetService("Players"):GetPlayerFromCharacter(hit.Parent)
				if plr then
					teleportPlayer(plr, kind == "Course")
				end
			end)
		end
	end
end

'''
s = s.replace(anchor, portal_code + anchor, 1)

# 2) only place at the checkpoint on spawn when the player is in the course
old = '''		local cur = state[player]
		if cur and cur.stage > 0 then
			placeAtCheckpoint(char, cur.stage)
		end'''
new = '''		local cur = state[player]
		if cur and player:GetAttribute("InCourse") then
			placeAtCheckpoint(char, cur.stage)
		end'''
assert old in s
s = s.replace(old, new, 1)

# 3) fall-off respawn only applies in the course
old2 = "			if root and cp and root.Position.Y < cp.Position.Y - 45 then"
new2 = '''			if root and cp and player:GetAttribute("InCourse") and root.Position.Y < cp.Position.Y - 45 then'''
assert old2 in s
s = s.replace(old2, new2, 1)

# 4) the course-start checkpoint must exist, but campus spawn is not required to be a checkpoint
open(p, "w", encoding="utf-8").write(s)
print("patched")
