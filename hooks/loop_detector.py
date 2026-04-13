"""Loop Detector - PreToolUse hook for all tool events.
Detects repetitive edit loops and blocks them before they spiral.
Logs tool calls per session to a JSONL file in the OS temp directory.
Exit 0 = allow, Exit 2 = loop detected (blocks the tool call).
"""

import json
import os
import sys
import tempfile
import time

EDIT_TOOLS = {"Write", "Edit", "MultiEdit"}
MAX_SAME_FILE_EDITS = 10
MAX_CONSECUTIVE_REPEATS = 4
CLEANUP_AGE_SECONDS = 86400  # 24 hours


def get_log_path(session_id):
    return os.path.join(tempfile.gettempdir(), f"claude_loop_{session_id}.jsonl")


def cleanup_old_logs():
    try:
        tmp = tempfile.gettempdir()
        now = time.time()
        for f in os.listdir(tmp):
            if f.startswith("claude_loop_") and f.endswith(".jsonl"):
                path = os.path.join(tmp, f)
                if now - os.path.getmtime(path) > CLEANUP_AGE_SECONDS:
                    os.remove(path)
    except Exception:
        pass


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    session_id = data.get("session_id", "unknown")
    file_path = tool_input.get("file_path", "") if isinstance(tool_input, dict) else ""

    log_path = get_log_path(session_id)

    # Append current call to log
    entry = {
        "ts": time.time(),
        "tool": tool_name,
        "file": file_path,
    }
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        sys.exit(0)

    # Read full session log
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        history = [json.loads(line) for line in lines if line.strip()]
    except Exception:
        sys.exit(0)

    # Check 1: Same file edited more than MAX_SAME_FILE_EDITS times
    if tool_name in EDIT_TOOLS and file_path:
        edit_count = sum(
            1 for h in history
            if h.get("tool") in EDIT_TOOLS and h.get("file") == file_path
        )
        if edit_count > MAX_SAME_FILE_EDITS:
            print(
                f"Loop detected: {file_path} is al {edit_count}x bewerkt. "
                "Stop en vraag de gebruiker om input. "
                "Beschrijf wat je probeert te doen en waarom het niet lukt.",
                file=sys.stderr,
            )
            sys.exit(2)

    # Check 2: Same tool+file repeated MAX_CONSECUTIVE_REPEATS times in a row
    if len(history) >= MAX_CONSECUTIVE_REPEATS:
        tail = history[-MAX_CONSECUTIVE_REPEATS:]
        current_combo = (tool_name, file_path)
        if all(
            (h.get("tool"), h.get("file")) == current_combo
            for h in tail
        ):
            print(
                f"Loop detected: {tool_name} op {file_path or 'onbekend'} "
                f"is {MAX_CONSECUTIVE_REPEATS}x achter elkaar aangeroepen. "
                "Stop en vraag de gebruiker om input. "
                "Beschrijf wat je probeert te doen en waarom het niet lukt.",
                file=sys.stderr,
            )
            sys.exit(2)

    # Cleanup old session logs (non-blocking, best-effort)
    cleanup_old_logs()


if __name__ == "__main__":
    main()
