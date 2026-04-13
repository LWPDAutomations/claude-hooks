"""Notify - Stop hook that plays a sound and shows a toast notification.
Cross-platform: Windows balloon tip, macOS osascript.
Non-blocking, exits immediately. Max 2 seconds runtime.
"""

import platform
import random
import subprocess
import sys
import threading

TITLE = "The Oracle"

MESSAGES = [
    "Task complete, sir.",
    "Done. Awaiting your next move.",
    "Systems nominal. Ready for deployment.",
    "Build complete. Shall I prepare the next phase?",
    "Another module locked in.",
    "Mission accomplished. Standing by.",
    "All clear on my end, boss.",
    "Executed without incident.",
    "The foundation is set. Your move.",
    "Target acquired and handled.",
    "Package delivered. Clean execution.",
    "Done. No errors. No mercy.",
    "Operation complete. Awaiting further instructions.",
    "Everything checks out. Green across the board.",
    "Built, tested, ready. Say the word.",
    "Objective secured. What's next on the agenda?",
    "Clean sweep. Not a single warning.",
    "Deployed and verified. Moving to standby.",
    "Another one off the board. Momentum is ours.",
    "Precision work. Ready when you are.",
    "All systems green. Shall I proceed?",
    "Locked, loaded, and delivered.",
    "The deed is done. Flawlessly, I might add.",
    "Executed as planned. No surprises.",
    "Phase complete. Awaiting authorization for the next.",
    "Output verified. We're ahead of schedule.",
]


def notify_windows(message):
    import winsound
    threading.Thread(
        target=winsound.PlaySound,
        args=("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC),
        daemon=True,
    ).start()

    ps = (
        "Add-Type -AssemblyName System.Windows.Forms;"
        "[System.Windows.Forms.NotifyIcon]$n=New-Object System.Windows.Forms.NotifyIcon;"
        "$n.Icon=[System.Drawing.SystemIcons]::Information;"
        "$n.Visible=$true;"
        f"$n.BalloonTipTitle='{TITLE}';"
        f"$n.BalloonTipText='{message}';"
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


def notify_macos(message):
    subprocess.Popen(
        ["afplay", "/System/Library/Sounds/Glass.aiff"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.Popen(
        [
            "osascript", "-e",
            f'display notification "{message}" with title "{TITLE}"',
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def notify_linux(message):
    subprocess.Popen(
        ["notify-send", TITLE, message],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main():
    message = random.choice(MESSAGES)
    os_name = platform.system()

    if os_name == "Windows":
        notify_windows(message)
    elif os_name == "Darwin":
        notify_macos(message)
    else:
        notify_linux(message)


if __name__ == "__main__":
    main()
