"""Syntax Checker - PostToolUse hook for Write, Edit, and MultiEdit events.
Checks syntax of written/edited files and reports errors to Claude.
Exit always 0 (PostToolUse cannot block).
"""

import json
import sys
import os
import py_compile
import subprocess
import tempfile


def check_python(file_path):
    try:
        py_compile.compile(file_path, doraise=True)
    except py_compile.PyCompileError as e:
        print(f"SYNTAX ERROR in {file_path}: {e}")


def check_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            json.loads(f.read())
    except json.JSONDecodeError as e:
        print(f"SYNTAX ERROR in {file_path}: {e}")


def check_js(file_path):
    try:
        result = subprocess.run(
            ["node", "--check", file_path],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            err = result.stderr.strip()
            print(f"SYNTAX ERROR in {file_path}: {err}")
    except FileNotFoundError:
        pass  # node not available
    except subprocess.TimeoutExpired:
        pass


def check_yaml(file_path):
    try:
        import yaml
    except ImportError:
        return
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            yaml.safe_load(f.read())
    except yaml.YAMLError as e:
        print(f"SYNTAX ERROR in {file_path}: {e}")


CHECKERS = {
    ".py": check_python,
    ".json": check_json,
    ".js": check_js,
    ".jsx": check_js,
    ".yaml": check_yaml,
    ".yml": check_yaml,
}


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return

    tool_input = data.get("tool_input")
    if not tool_input:
        return

    file_path = tool_input.get("file_path")
    if not file_path:
        return

    if not os.path.isfile(file_path):
        return

    ext = os.path.splitext(file_path)[1].lower()
    checker = CHECKERS.get(ext)
    if checker:
        checker(file_path)


if __name__ == "__main__":
    main()
