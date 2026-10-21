-- v59 Game Show tie QA (2 clients): both contestants answer the same pod at the same instant every question, so the
-- Red and Blue team scores stay equal and the show must end with the tie screen (both teams rewarded).
-- Run from Edit: StudioTestService:ExecuteMultiplayerTestAsync(2, "GameShow59")
local test = game:GetService("StudioTestService")
if test:GetTestArgs() ~= "GameShow59" then
	return
end
local Players = game:GetService("Players")
local ended = false
local function finish(v)
	if not ended then
		ended = true
		test:EndTest(v)
	end
end
task.delay(280, function()
	finish({ passed = false, error = "timeout" })
end)
while #Players:GetPlayers() < 2 do
	task.wait(0.1)
end
local spawn = workspace.Map:FindFirstChild("GameShowSpawn", true)
for i, p in ipairs(Players:GetPlayers()) do
	while not p.Character or not p.Character:FindFirstChild("HumanoidRootPart") do
		task.wait(0.1)
	end
	p.Character:PivotTo(spawn.CFrame + Vector3.new(i * 4 - 6, 4, 0))
end
task.wait(2)
local qa = game:GetService("ServerStorage"):WaitForChild("GameShowQA")
local label = workspace.Map:FindFirstChild("MainScreen", true):FindFirstChildWhichIsA("TextLabel", true)
local seen = {}
label:GetPropertyChangedSignal("Text"):Connect(function()
	table.insert(seen, label.Text)
end)
qa:Invoke("start", Players:GetPlayers()[1])
local answered, last, questions = false, nil, 0
while true do
	local st = qa:Invoke("state")
	if st then
		last = st
		if st.asking and not answered then
			task.wait(1)
			if qa:Invoke("answerAll", 1) then
				questions += 1
			end
			answered = true
		elseif not st.asking then
			answered = false
		end
	elseif last then
		break
	end
	task.wait(0.2)
end
local text = ""
for _, t in ipairs(seen) do
	if t:find("تعادل") or t:find("فاز") then
		text = t
	end
end
finish({
	passed = last.teams == true and last.red == last.blue and text:find("تعادل") ~= nil,
	teams = last.teams,
	red = last.red,
	blue = last.blue,
	questions = questions,
	screen = text,
})
