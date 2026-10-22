-- Exercise the production claim/reset code with independent player identities.
local fs = require('@lune/fs')
local source = fs.readFile('kuwait-parkour/src/server/Labs54.server.luau')
local first = assert(source:find('local resetBench', 1, true))
local last = assert(source:find('for _, model in ipairs(mapFolder:GetDescendants()) do', first, true))
local env = {
    benches = {}, carrying = {}, EXP = {}, os = os, pairs = pairs,
    toast = function() end, dropCarried = function() end, returnHome = function() end,
    event = { FireClient = function() end },
}
env.EXP.test = { reset = function(b) b.st = {} end }
local chunk = assert(loadstring(source:sub(first, last-1)..'\nreturn claim, resetBench'))
setfenv(chunk, env)
local claim, reset = chunk()
local a = { kind='test', items={} }
local b = { kind='test', items={} }
env.benches = {a, b}
local players = {}
for i=1,24 do
    players[i] = {Parent=true, DisplayName=tostring(i), GetAttribute=function() return true end}
end
assert(claim(players[1], a))
local state = a.st
for i=2,24 do assert(not claim(players[i], a), 'occupied table stolen') end
assert(a.st == state, 'rejected claims changed experiment')
assert(claim(players[2], b))
assert(not claim(players[1], b))
assert(a.owner == players[1], 'busy destination released previous table')
reset(b)
assert(claim(players[1], b))
assert(a.owner == nil and b.owner == players[1], 'one player hoarded two stations')
assert(a.st ~= state, 'old async session still valid')
assert(claim(players[2], a), 'released table unavailable')
reset(a)
assert(a.owner == nil)
print('PASS: 24 identities, exclusive ownership, busy destination, switching, state invalidation, reuse')
