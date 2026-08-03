import requests
import time
import json
from datetime import datetime, timezone
import threading
import subprocess

import _state
import parsers
import commun
import tnt
import bot as discordBot
import backup


def appendJSONL(event):
    now = datetime.now(timezone.utc)
    isoYear, isoWeek, _ = now.isocalendar()
    fileName = f"server_{isoYear}-W{isoWeek:02d}.jsonl"
    with open(f"joindb/{fileName}", "a") as dbFile:
        dbFile.write(event + "\n")


def dailyServerRestart():
    while True:
        time.sleep(60)
        if datetime.now(timezone.utc).hour == 11:
            if datetime.now(timezone.utc).minute == 15:
                while _state.players or _state.isBackingUp:
                    time.sleep(30)
                commun.sendTmuxCommand("mcserver", "stop")
                time.sleep(30)
                commun.sendTmuxCommand(
                    "mcserver",
                    "./bedrock_server 2>&1 | tee -a /home/logs/bedrock-server/server.log",
                )
                commun.sendWebhook("daily server restart", _state.consoleLoggerUrl)
                _state.players.clear()
                
def editHookMessage(webhook_url, message_id, content):
    requests.patch(f"{webhook_url}/messages/{message_id}", json={"content":f'{content}'})
                
def playerListHookUpdate():
    if _state.players:
        editHookMessage(_state.playerListUrl,"1527080499200262314",str(_state.players).replace("[","").replace("]","").replace("', ","\n").replace("'",""))
    else:
        editHookMessage(_state.playerListUrl,"1527080499200262314","There is no one online.")
        
def statWebhook():
    while True:
        result_cpu = subprocess.run(
            ["tmux", "capture-pane", "-t", "htop", "-p"],
            capture_output=True,
            text=True,
        )
        result_backup_usage =subprocess.run(
            ["du", "-sb", "/home/backups/nameiibackups"],
            capture_output=True,
            text=True,
        )
        editHookMessage(_state.statInfoUrl, "1527102878370627696", f'# CPU Usage\n```{result_cpu.stdout[:141]}```\n# Backup Info\nLast Backup was <t:{str(_state.lastBackupStamp)}:R>\nThere are currently {round(int((result_backup_usage.stdout).split()[0])/1073741824, 2)}GB of backups')
        time.sleep(1)



def watcher():  # main processer
    with open(_state.logFile, "r") as file:
        file.seek(0, 2)  # jump to end of file
        while True:
            line = file.readline()
            if line:
                type = parsers.determineType(line)
                if type == "join":
                    playerName, playerXuid, playerPfid, unix = parsers.parseJoin(line)
                    event = {
                        "joinTime": unix,
                        "exitTime": None,
                        "playerName": playerName,
                        "playerXuid": playerXuid,
                        "playerPfid": playerPfid,
                        "timestamp": unix,
                    }
                    if not _state.players:
                        commun.sendTmuxCommand(
                            "mcserver", "gamerule doDaylightCycle true"
                        )
                    _state.players.append(playerName)
                    _state.sessionDatas[playerXuid] = event
                    _state.xuids[playerName] = playerXuid
                    _state.xuid2players[playerXuid] = playerName
                    discordBot.on_player_join(playerName, playerXuid, playerPfid, unix)
                    print(_state.xuids)
                    if len(_state.players) == 1:
                        command = f'tellraw "{playerName}" {{"rawtext":[{{"text":"§l§eWelcome to Name II!§r§e\\nYou are alone."}}]}}'
                    else:
                        command = f'tellraw "{playerName}" {{"rawtext":[{{"text":"§l§eWelcome to Name II!§r§e Currently online players are\\n  - {"\\n  - ".join(_state.players).replace("[", "").replace("]", "")}"}}]}}'
                    commun.sendTmuxCommand("mcserver", command)
                    commun.sendWebhook(
                        f"→ {playerName} joined the server at <t:{unix}:F>",
                        _state.consoleLoggerUrl,
                    )  # form permissions.json
                    if playerXuid not in _state.verifyData:
                        commun.sendTmuxCommand(
                            "mcserver",
                            f'tellraw "{playerName}" {{"rawtext":[{{"text":"(i) You are not verified. Run /verify on the discord server to become a member."}}]}}',
                        )
                        if not any(p["xuid"] == playerXuid for p in _state.permissions):
                            _state.permissions.append(
                                {
                                    "permission": "visitor",
                                    "xuid": playerXuid,  # can use this directly, no need for the xuids lookup
                                }
                            )
                            with open(
                                "/home/bedrock-server/permissions.json", "w"
                            ) as permission_file:
                                json.dump(_state.permissions, permission_file, indent=2)
                            commun.sendTmuxCommand("mcserver", "permission reload")
                    if playerXuid in _state.verifyData:
                        discordBot.catchMissingSettingData(_state.verifyData[playerXuid])
                        _state.userSettings[_state.verifyData[playerXuid]].setdefault("locatorbar", True)
                        if not _state.userSettings[_state.verifyData[playerXuid]]["locatorbar"]:
                            _state.playersWithoutBar.append(playerXuid)
                            commun.sendTmuxCommand("mcserver", "gamerule playerwaypoints off")
                    playerListHookUpdate()
                        

                if type == "leave":
                    playerName, playerXuid, playerPfid, unix = parsers.parseLeave(line)
                    if playerXuid in _state.sessionDatas:
                        event = _state.sessionDatas[playerXuid]
                        event["exitTime"] = unix
                        jsonString = json.dumps(event, separators=(",", ":"))
                        appendJSONL(jsonString)
                        _state.sessionDatas.pop(playerXuid, None)
                    if playerName.rstrip() in _state.players:
                        _state.players.remove(playerName.rstrip())
                    if not _state.players:
                        commun.sendTmuxCommand(
                            "mcserver", "gamerule doDaylightCycle false"
                        )
                        _state.lastPlayerStamp = unix
                    commun.sendWebhook(
                        f"← {playerName} left the server at <t:{unix}:F>",
                        _state.consoleLoggerUrl,
                    )
                    if playerXuid in _state.verifyData:
                        discordBot.catchMissingSettingData(_state.verifyData[playerXuid])
                        _state.userSettings[_state.verifyData[playerXuid]].setdefault("locatorbar", True)
                        if not _state.userSettings[_state.verifyData[playerXuid]]["locatorbar"]:
                            _state.playersWithoutBar.remove(playerXuid)
                            if not _state.playersWithoutBar:
                                commun.sendTmuxCommand("mcserver", "gamerule playerwaypoints everyone")
                    playerListHookUpdate()

                if type == "tntpos":
                    # get tnt pos
                    _state.TNTData["tntPos"] = line.split(" Teleported TNTFound to ")[
                        1
                    ].rstrip()
                    if _state.TNTData.get("playerName") and _state.TNTData.get(
                        "tntPos"
                    ):
                        tnt.TNTMessage()

                if type == "tnttag":
                    # get player near tnt
                    # reacts like [2026-06-05 04:16:47:488 INFO] Added tag 'nearestTNT' to snowboyz0825
                    _state.TNTData["playerName"] = line.split(
                        " Added tag 'nearestTNT' to "
                    )[1].rstrip()
                    if _state.TNTData.get("playerName") and _state.TNTData.get(
                        "tntPos"
                    ):
                        tnt.TNTMessage()
                if not any(substring in line for substring in _state.excludeSubStrings):
                    requests.post(
                        _state.consoleLoggerUrl, json={"content": line.rstrip()}
                    )
                    
                if type == "stop":
                    _state.players = []
                    
            time.sleep(0.05)


with open(_state.logFile, "r") as file:
    file.seek(0, 2)
    commun.sendTmuxCommand("mcserver", "list")
    line = file.readline()
    while ("There are " in line and "players online:" in line) or line == "":
        if "There are 0/" in line:
            break
        line = file.readline()
        time.sleep(0.05)
    if "There are 0/" not in line:
        for playerName in line.split("INFO] ")[-1].strip().split(", "):
            _state.players.append(playerName.strip())


TNTWatchdogThread = threading.Thread(target=tnt.TNTWatchdog, daemon=True)
TNTWatchdogThread.start()

backupThread = threading.Thread(target=backup.backupWatcher, daemon=True)
backupThread.start()

serverRestartThread = threading.Thread(target=dailyServerRestart, daemon=True)
serverRestartThread.start()

statThread = threading.Thread(target=statWebhook, daemon=True)
statThread.start()

botThread = threading.Thread(target=discordBot.run_bot, daemon=True)
botThread.start()

watcher()
# tail(LOG_FILE)
