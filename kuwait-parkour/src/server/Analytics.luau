-- v57 analytics funnels (research: Roblox Creator Hub "funnel events"): where do players drop off?
--   onboarding: 1 joined, then one step per First Day task completed (in any order, so the step = tasks done + 1)
--   CartRide:   one step per valley reached, per ride
-- Every call is wrapped in pcall: in Studio or an unpublished place AnalyticsService may refuse, and the game must
-- never break because of analytics.
local AnalyticsService = game:GetService("AnalyticsService")
local HttpService = game:GetService("HttpService")

local Analytics = {}
local onboarded = {} -- [Player] = highest onboarding step logged this session

function Analytics.onboarding(player, step, name)
	if (onboarded[player] or 0) >= step then
		return
	end
	onboarded[player] = step
	pcall(function()
		AnalyticsService:LogOnboardingFunnelStepEvent(player, step, name)
	end)
end

function Analytics.newSession()
	return HttpService:GenerateGUID(false)
end

function Analytics.funnel(player, funnel, session, step, name)
	pcall(function()
		AnalyticsService:LogFunnelStepEvent(player, funnel, session, step, name)
	end)
end

function Analytics.forget(player)
	onboarded[player] = nil
end
game:GetService("Players").PlayerRemoving:Connect(Analytics.forget)

return Analytics
