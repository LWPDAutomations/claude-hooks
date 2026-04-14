"""Notify - Hook for desktop notifications when Claude Code needs attention.
Fires on Stop (task complete), Notification (permission/idle), and
PreToolUse:AskUserQuestion (question asked).
Cross-platform: Windows balloon tip, macOS osascript, Linux notify-send.
Shows project name in title so user knows which window needs attention.
Deduplicates notifications within a short window to avoid double alerts.
"""

import json
import os
import platform
import random
import subprocess
import sys
import tempfile
import time

DEDUP_SECONDS = 5

TITLE = "The Oracle"

MESSAGES_STOP = [
    "Task complete, sir.",
    "Done. Awaiting your next move.",
    "Mission accomplished. Standing by.",
    "All clear on my end, boss.",
    "Executed without incident.",
    "Done. No errors. No mercy.",
    "Another one off the board.",
    "The deed is done. Flawlessly, I might add.",
    "Executed as planned. No surprises.",
    "Consider it done.",
    "Done. Cleanly, if I may say so.",
    "Finished. I'll be here when you need me.",
    "One more thing crossed off the list.",
    "That's a wrap on this one.",
    "Delivered as requested, sir.",
    "Another task in the books.",
]

MESSAGES_INPUT = [
    "I need your input, sir.",
    "Awaiting your decision.",
    "A question requires your attention.",
    "Your call. I'll wait.",
    "I need a green light on this one.",
    "Decision time, boss.",
    "Pending your response.",
    "I've hit a fork in the road. You decide.",
    "Waiting on you, sir.",
    "Quick decision needed.",
    "Over to you.",
    "Input required. Standing by.",
]

MESSAGES_PERMISSION = [
    "Permission requested, sir.",
    "I need authorization to proceed.",
    "Awaiting your approval.",
    "Green light needed.",
    "Requesting clearance.",
    "One approval away from execution.",
    "I need your go-ahead on this.",
    "Waiting for the thumbs up.",
]


def is_duplicate(session_id):
    """Check if a notification was already sent recently for this session."""
    stamp_path = os.path.join(tempfile.gettempdir(), f"claude_notify_{session_id}.stamp")
    now = time.time()
    try:
        if os.path.exists(stamp_path):
            mtime = os.path.getmtime(stamp_path)
            if now - mtime < DEDUP_SECONDS:
                return True
    except Exception:
        pass
    try:
        with open(stamp_path, "w") as f:
            f.write(str(now))
    except Exception:
        pass
    return False


def project_name(cwd):
    """Extract the project folder name from cwd."""
    if not cwd:
        return ""
    return cwd.replace("\\", "/").rstrip("/").rsplit("/", 1)[-1]


def pick_message(data):
    """Pick a notification message based on the hook event type.
    Returns (message, is_custom) where is_custom=True means we use
    Claude's own message instead of a random one."""
    event = data.get("hook_event_name", "")
    notification_type = data.get("notification_type", "")
    tool_name = data.get("tool_name", "")
    claude_message = data.get("message", "")

    # Notification event: permission_prompt or idle_prompt
    if event == "Notification":
        if notification_type == "permission_prompt":
            return random.choice(MESSAGES_PERMISSION), False
        elif notification_type == "idle_prompt":
            if claude_message:
                return claude_message, True
            return random.choice(MESSAGES_INPUT), False

    # PreToolUse:AskUserQuestion
    if tool_name == "AskUserQuestion":
        return random.choice(MESSAGES_INPUT), False

    # Stop: task complete
    if event == "Stop":
        return random.choice(MESSAGES_STOP), False

    return random.choice(MESSAGES_STOP), False


def notify_windows(title, message):
    import winsound
    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)

    safe_title = title.replace("'", "''")
    safe_msg = message.replace("'", "''")

    ps = (
        "Add-Type -AssemblyName System.Windows.Forms;"
        "[System.Windows.Forms.NotifyIcon]$n=New-Object System.Windows.Forms.NotifyIcon;"
        "$n.Icon=[System.Drawing.SystemIcons]::Information;"
        "$n.Visible=$true;"
        f"$n.BalloonTipTitle='{safe_title}';"
        f"$n.BalloonTipText='{safe_msg}';"
        "$n.ShowBalloonTip(5000);"
        "Start-Sleep -Seconds 6;"
        "$n.Dispose()"
    )
    subprocess.Popen(
        ["powershell", "-NoProfile", "-Command", ps],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=0x08000000,  # CREATE_NO_WINDOW
    )


def notify_macos(title, message):
    subprocess.Popen(
        ["afplay", "/System/Library/Sounds/Glass.aiff"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # Escape for AppleScript
    safe_title = title.replace('"', '\\"')
    safe_msg = message.replace('"', '\\"')
    subprocess.Popen(
        [
            "osascript", "-e",
            f'display notification "{safe_msg}" with title "{safe_title}" sound name "Ping"',
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def notify_linux(title, message):
    for cmd in [
        ["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"],
        ["aplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"],
    ]:
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            break
        except FileNotFoundError:
            continue

    subprocess.Popen(
        ["notify-send", title, message],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main():
    data = {}
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        pass

    session_id = data.get("session_id", "unknown")
    cwd = data.get("cwd", "")

    if is_duplicate(session_id):
        sys.exit(0)

    message, _ = pick_message(data)
    project = project_name(cwd)
    title = f"{TITLE} [{project}]" if project else TITLE

    os_name = platform.system()
    if os_name == "Windows":
        notify_windows(title, message)
    elif os_name == "Darwin":
        notify_macos(title, message)
    else:
        notify_linux(title, message)


if __name__ == "__main__":
    main()
