import requests
import subprocess


def sendWebhook(content, url):
    requests.post(url, json={"content": content})
    print(f"Sent webhook: {content}")


def sendTmuxCommand(session_name, command):
    try:
        subprocess.run(
            ["tmux", "send-keys", "-t", session_name, command, "ENTER"], check=True
        )
    except subprocess.CalledProcessError:
        print(
            f"Error: Could not send command to tmux session '{session_name}'. Is it running?"
        )
