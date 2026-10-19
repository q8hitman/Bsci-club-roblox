local R = {}
function R.phase(t, room)
	local v = t % room.cycle
	if v < room.safe then
		return "safe"
	elseif v < room.safe + room.warning then
		return "warning"
	end
	return "danger"
end
function R.platform(t)
	return math.sin(t * 0.5) * 14
end
function R.grid(t)
	return math.sin(t * 0.6) * 6, math.sin(t * 0.7) * 13
end
function R.start(room, now)
	return { room = room, zone = 0, started = now, key = false }
end
function R.visit(s, z, now, key)
	if s.done then
		return false
	end
	if s.zone == 0 and z >= 7 and z <= 14 then
		s.zone = 1
	end
	if s.zone == 1 and z >= -14 and z <= -7 then
		s.zone = 2
	end
	if key then
		s.key = true
	end
	if z < -29 and s.zone == 2 and now - s.started >= 3.8 and ((s.room ~= 3 and s.room ~= 5) or s.key) then
		s.done = true
		return true
	end
	return false
end
function R.motion(dx, dz, dt, speed, carry)
	if dx ~= dx or dz ~= dz or dt <= 0 or dt > 1 then
		return false
	end
	local distance = math.sqrt(dx * dx + dz * dz)
	return distance <= (math.max(20, speed + 5) * dt + 1.5) + (carry or 0)
end
function R.contact(i, x, y, z, t)
	if y < 0 or y > 12 then
		return false
	end
	if i == 2 then
		local gx, gz = R.grid(t)
		return math.abs(x - gx) < 12 and math.abs(z - gz) < 2
	end
	if i == 3 then
		return x > 6 and x < 24 and math.abs(z) < 2
	end
	if i == 5 then
		return (math.abs(z - 1) < 2 and x < 10) or (math.abs(z + 18) < 2 and x > -10)
	end
	return math.abs(z) < 2
end
return R
