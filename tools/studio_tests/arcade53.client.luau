-- v53 arcade QA, client side (see arcade53.server.luau)
local test = game:GetService("StudioTestService")
if test:GetTestArgs() ~= "Arcade53" then
	return
end
local rs = game.ReplicatedStorage
local done = rs:WaitForChild("Arcade53QADone")
rs:WaitForChild("ArcadeResults").OnClientEvent:Connect(function(data)
	done:FireServer({ n = #data.list, rank = data.rank, mode = data.mode, title = data.title, coins = data.coins })
end)
