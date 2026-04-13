"""Notify - Stop hook that shows a desktop notification when Claude is done.
Cross-platform: Windows toast, macOS osascript, Linux notify-send.
Exit always 0.
"""

import sys
import platform


def notify_windows(title, message):
    try:
        from ctypes import windll, c_int, c_wchar_p, Structure, POINTER, sizeof
        # Use simple MessageBeep + balloon via Windows Forms through PowerShell-free approach
        # Fall back to a simpler ctypes approach with WinToast
        import ctypes
        ctypes.windll.user32.MessageBeep(0x00000040)  # MB_ICONINFORMATION sound
    except Exception:
        pass

    # Try plyer first (richest notifications)
    try:
        from plyer import notification
        notification.notify(title=title, message=message, timeout=5)
        return
    except ImportError:
        pass

    # Fall back to Windows toast via PowerShell one-liner (no -File, avoids script issues)
    import subprocess
    ps_script = (
        "[System.Windows.Forms.NotifyIcon]$b=New-Object System.Windows.Forms.NotifyIcon;"
        "$b.Icon=[System.Drawing.SystemIcons]::Information;"
        f"$b.BalloonTipTitle='{title}';"
        f"$b.BalloonTipText='{message}';"
        "$b.Visible=$true;$b.ShowBalloonTip(5000);"
        "Start-Sleep -Seconds 6;$b.Dispose()"
    )
    try:
        subprocess.Popen(
            ["powershell", "-NoProfile", "-Command",
             "Add-Type -AssemblyName System.Windows.Forms;" + ps_script],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return
    except FileNotFoundError:
        pass

    print(f"{title}: {message}")


def notify_macos(title, message):
    import subprocess
    try:
        subprocess.run(
            ["osascript", "-e", f'display notification "{message}" with title "{title}"'],
            timeout=5
        )
        return
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    print(f"{title}: {message}")


def notify_linux(title, message):
    import subprocess
    try:
        subprocess.run(["notify-send", title, message], timeout=5)
        return
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    print(f"{title}: {message}")


def main():
    title = "Claude Code"
    message = "Klaar! Claude heeft je input nodig of is klaar met de taak."

    os_name = platform.system()
    if os_name == "Windows":
        notify_windows(title, message)
    elif os_name == "Darwin":
        notify_macos(title, message)
    else:
        notify_linux(title, message)


if __name__ == "__main__":
    main()
