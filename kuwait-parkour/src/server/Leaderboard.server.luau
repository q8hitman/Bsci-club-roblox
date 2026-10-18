-- Live "top players" board in the club HQ: the players in this server sorted by parkour stage.
local Players = game:GetService("Players")

local board = workspace:WaitForChild("Map"):FindFirstChild("Leaderboard", true)
local label = board and board:FindFirstChild("Label") and board.Label:FindFirstChild("T")
if not label then
	return
end

local MEDALS = { "🥇", "🥈", "🥉" }

while true do
	local rows = {}
	for _, p in ipairs(Players:GetPlayers()) do
		table.insert(rows, { name = p.DisplayName, stage = p:GetAttribute("Stage") or 0 })
	end
	table.sort(rows, function(a, b)
		return a.stage > b.stage
	end)
	local lines = { "🏆 الأبطال الحين | Top Players" }
	for i = 1, math.min(#rows, 8) do
		table.insert(lines, ("%s %s — %d/100"):format(MEDALS[i] or (i .. "."), rows[i].name, rows[i].stage))
	end
	if #rows == 0 then
		table.insert(lines, "—")
	end
	label.Text = table.concat(lines, "\n")
	task.wait(5)
end
