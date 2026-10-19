local D = if script then require(script.Parent.MuseumData) else require("./MuseumData")
local R = {}
function R.start(id)
	if not D.get(id) then
		return nil
	end
	return { id = id, step = 1, done = false }
end
function R.act(s, choice)
	if type(s) ~= "table" or s.done or type(choice) ~= "string" then
		return false
	end
	local d = D.get(s.id)
	local step = d and d.steps[s.step]
	if not step or choice ~= step.correct then
		return false
	end
	s.step += 1
	s.done = s.step > #d.steps
	return true
end
return R
