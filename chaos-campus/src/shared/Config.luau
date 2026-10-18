-- Chaos Campus tuning. Minigames live in ServerScriptService.Server.Minigames (one module each);
-- adding a minigame = adding a module + an arena folder named Arena_<id> in the map.
local RunService = game:GetService("RunService")

return {
	MinPlayers = RunService:IsStudio() and 1 or 2, -- solo rounds only for testing in Studio
	Intermission = 15,
	ResultsTime = 6,
	WinPoints = 5,
	PlayPoints = 1,

	-- each round rolls one mutation on top of the minigame (the "chaos")
	Mutations = {
		{ id = "none", ar = "بدون طفرة", weight = 2 },
		{ id = "moon", ar = "🌙 جاذبية القمر", weight = 3 },
		{ id = "speed", ar = "⚡ سرعة الميتوكوندريا", weight = 3 },
		{ id = "giant", ar = "🦖 عمالقة", weight = 2 },
		{ id = "tiny", ar = "🐜 بكتيريا صغيرة", weight = 2 },
		{ id = "night", ar = "🌑 مختبر مظلم", weight = 2 },
	},
}
