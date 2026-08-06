import subprocess
import _state
import time
import commun
from datetime import datetime, timezone


def getSummaryLine(backupResult):
    for line in backupResult.stdout.splitlines():
        if '"message_type":"summary"' in line:
            return line
    return "No summary line found in restic output."


def createBackup():
    backupResult = subprocess.run(
        [
            "restic",
            "--json",
            "-r",
            "backups/",
            "--insecure-no-password",
            "backup",
            "bedrock-server/worlds/Bedrock level",
        ],
        capture_output=True,
        text=True,
    )
    commun.sendWebhook(getSummaryLine(backupResult), _state.consoleLoggerUrl)
    _state.lastBackupStamp = int(time.time())
    return backupResult


def backupScript():
    _state.isBackingUp = True
    commun.sendTmuxCommand("mcserver", "say §8§oSaving Paused [Creating Backup]")
    commun.sendTmuxCommand("mcserver", "save hold")
    time.sleep(10)
    backup_stdout = createBackup()
    commun.sendTmuxCommand("mcserver", "save resume")
    commun.sendTmuxCommand("mcserver", "say §8§oSaving Resumed [Backup Complete]")
    _state.isBackingUp = False
    return backup_stdout


def backupWatcher():
    while True:
        time.sleep(60)
        if (
            datetime.now(timezone.utc).minute == 0
            or datetime.now(timezone.utc).minute == 30
        ):
            if _state.players or _state.lastBackupStamp < _state.lastPlayerStamp:
                backupScript()
                time.sleep(60)
