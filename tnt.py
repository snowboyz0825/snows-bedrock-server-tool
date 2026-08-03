import time
import commun
import _state


def TNTWatchdog():
    while True:
        if _state.players:
            _state.TNTData.clear()
            commun.sendTmuxCommand(
                "mcserver",
                "execute at @e[type=tnt] run summon armor_stand TNTFound ~ ~100000 ~",
            )
            commun.sendTmuxCommand(
                "mcserver",
                "execute at @e[name=TNTFound] run tp @e[name=TNTFound] ~ ~ ~",
            )
            commun.sendTmuxCommand("mcserver", "kill @e[name=TNTFound]")
            commun.sendTmuxCommand(
                "mcserver", "execute at @e[type=tnt] run tag @p add nearestTNT"
            )
            commun.sendTmuxCommand("mcserver", "tag @a remove nearestTNT")
        time.sleep(3.5)


def TNTMessage():
    commun.sendWebhook(
        f"<@&1457323549986521088>, <@&1240133433045286974> - Primed TNT found near {_state.TNTData['playerName']} at {_state.TNTData['tntPos']}",
        _state.consoleLoggerUrl,
    )
    _state.TNTData.clear()
