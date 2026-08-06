import json

sessionDatas = {}
players = []
xuid2players = {}
xuids = {}
TNTData = {}
isBackingUp = False
lastPlayerStamp = 0
lastBackupStamp = 0
consoleLoggerUrl = "https://discordapp.com/api/webhooks/1535020116012433511/pSrCE0-sgiHYwicUogMlY00vNOnnGGPJ8SR98fnffA--Q8Um962ZFLh0PoQiygDINa7K"
playerListUrl = "https://discordapp.com/api/webhooks/1535020116012433511/pSrCE0-sgiHYwicUogMlY00vNOnnGGPJ8SR98fnffA--Q8Um962ZFLh0PoQiygDINa7K"
statInfoUrl = "https://discordapp.com/api/webhooks/1535020116012433511/pSrCE0-sgiHYwicUogMlY00vNOnnGGPJ8SR98fnffA--Q8Um962ZFLh0PoQiygDINa7K"
logFile = "bedrock-server/server.log"
with open("data/verifyData.json", "r") as file:
    verifyData = json.load(file)
with open("bedrock-server/permissions.json", "r") as perms_file:
    permissions = json.load(perms_file)
with open("data/friends.json", "r") as friends_file:
    friends = json.load(friends_file)
with open("data/userSettings.json", "r") as settings_file:
    userSettings = json.load(settings_file)
with open("env.json", "r") as env_file:
    env = json.load(env_file)

playersWithoutBar = []    
    
excludeSubStrings = [
    "Running AutoCompaction...",
    "say §8§oSaving Paused",
    "save hold",
    "Saving...",
    "save resume",
    "say §8§oSaving Resumed",
    "Changes to the world are resumed.",
    "Player connected: ",
    " Player PartyIdUpdate:  ",
    "Player Spawned: ",
    "Player disconnected: ",
    "execute at @e[type=tnt] run summon armor_stand TNTFound ~ ~100000 ~",
    "execute at @e[name=TNTFound] run tp @e[name=TNTFound] ~ ~ ~",
    "execute at @e[type=tnt] run tag @p add nearestTNT",
    "tag @a remove nearestTNT",
    "kill @e[name=TNTFound]",
    "No targets matched selector",
    "Target does not have this tag",
    "§l§eWelcome to Name II!§r§e ",
    "Object successfully summoned",
    "Killed TNTFound",
    "Added tag 'nearestTNT' to ",
    "Removed tag 'nearestTNT' from ",
    "gamerule doDaylightCycle ",
]

def isDcidOnline(discord_id):
    xuid = verifyData.get(str(discord_id))
    if not xuid:
        return False
    name = xuid2players.get(xuid)
    return name in players
