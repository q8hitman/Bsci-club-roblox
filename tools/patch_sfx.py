"""Puzzle sound cues: Obstacles.server fires ReplicatedStorage.Sfx(kind); Feedback.client plays it."""
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kuwait-parkour", "src")
T = "\t"


def patch(rel, pairs):
    p = os.path.join(ROOT, rel)
    s = open(p, encoding="utf-8").read()
    for a, b in pairs:
        assert a in s, (rel, a[:60])
        s = s.replace(a, b, 1)
    open(p, "w", encoding="utf-8").write(s)


patch("server/Obstacles.server.luau", [
    ('local mapFolder = workspace:WaitForChild("Map")\n',
     'local mapFolder = workspace:WaitForChild("Map")\n\n'
     '-- tiny sound cues for puzzle feedback (played by Feedback.client)\n'
     'local sfx = Instance.new("RemoteEvent")\n'
     'sfx.Name = "Sfx"\n'
     'sfx.Parent = game:GetService("ReplicatedStorage")\n'),
    (T * 2 + "flash(part, Color3.fromRGB(90, 255, 140))\n" + T * 2 + "if idx == #key then\n" + T * 3 + "seqProgress[id][player] = 0\n"
     + T * 3 + "openGhosts(id, 16)\n" + T * 2 + "else\n",
     T * 2 + "flash(part, Color3.fromRGB(90, 255, 140))\n" + T * 2 + "if idx == #key then\n" + T * 3 + "seqProgress[id][player] = 0\n"
     + T * 3 + "openGhosts(id, 16)\n" + T * 3 + 'sfx:FireClient(player, "sting")\n' + T * 2 + "else\n" + T * 3
     + 'sfx:FireClient(player, "click")\n'),
    (T * 2 + "flash(part, Color3.fromRGB(255, 70, 70))\n" + T * 2 + "seqProgress[id][player] = 0\n",
     T * 2 + "flash(part, Color3.fromRGB(255, 70, 70))\n" + T * 2 + "seqProgress[id][player] = 0\n" + T * 2
     + 'sfx:FireClient(player, "wrong")\n'),
    (T * 2 + "if humanoidFrom(hit) then\n" + T * 3 + "openGhosts(args[2], tonumber(args[3]) or 14)\n",
     T * 2 + "local _, model = humanoidFrom(hit)\n" + T * 2 + "if model then\n"
     + T * 3 + "local plr = not open[args[2]] and Players:GetPlayerFromCharacter(model)\n"
     + T * 3 + "if plr then\n" + T * 4 + 'sfx:FireClient(plr, "sting")\n' + T * 3 + "end\n"
     + T * 3 + "openGhosts(args[2], tonumber(args[3]) or 14)\n"),
])

patch("client/Feedback.client.luau", [
    ('task.spawn(function()\n\tlocal shop = ReplicatedStorage:WaitForChild("Shop", 20)',
     'task.spawn(function()\n\tlocal remote = ReplicatedStorage:WaitForChild("Sfx", 20)\n\tif remote then\n'
     '\t\tremote.OnClientEvent:Connect(play)\n\tend\nend)\n\n'
     'task.spawn(function()\n\tlocal shop = ReplicatedStorage:WaitForChild("Shop", 20)'),
])
print("sfx patched")
