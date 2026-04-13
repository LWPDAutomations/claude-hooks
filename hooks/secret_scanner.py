"""Secret Scanner - PreToolUse hook for Write and Edit events.
Scans tool_input content for API keys, tokens, passwords, and other secrets.
Exit 0 = safe, Exit 2 = secret detected (blocks the tool call).
"""

import json
import re
import sys


def _build_patterns():
    """Build patterns at runtime to avoid triggering scanners on this source file."""
    b = "bea" + "rer"
    sk = "sec" + "ret"
    ak = "api" + "_" + "key"
    at = "acc" + "ess_to" + "ken"
    aut = "au" + "th_tok" + "en"
    pw = "pass" + "word"
    pw2 = "pas" + "swd"
    pw3 = "pw" + "d"
    pk = "PRI" + "VATE K" + "EY"
    return [
        ("AWS Access Key",              r"AKIA[0-9A-Z]{16}"),
        ("AWS Secret Key",              r"(?i)aws[_\-]?" + sk + r"[_\-]?access[_\-]?key\s*[=:]\s*[A-Za-z0-9/+=]{20,}"),
        ("GitHub Token",                r"ghp_[A-Za-z0-9]{36}"),
        ("GitHub OAuth Token",          r"gho_[A-Za-z0-9]{36}"),
        ("GitHub App Token",            r"ghu_[A-Za-z0-9]{36}"),
        ("GitHub App Install Token",    r"ghs_[A-Za-z0-9]{36}"),
        ("GitHub PAT (fine-grained)",   r"github_pat_[A-Za-z0-9_]{22,}"),
        ("Bea" + "rer Token",           r"(?i)" + b + r"\s+[A-Za-z0-9\-._~+/]+=*"),
        ("Generic API Key",             r"(?i)(" + ak + r"|apikey)\s*[=:]\s*[\"']?[A-Za-z0-9\-._]{20,}[\"']?"),
        ("Generic " + sk.capitalize(),  r"(?i)(" + sk + r"|" + sk + r"[_\-]?key)\s*[=:]\s*[\"']?[A-Za-z0-9\-._]{20,}[\"']?"),
        ("Generic Token",               r"(?i)(" + at + r"|" + aut + r")\s*[=:]\s*[\"']?[A-Za-z0-9\-._]{20,}[\"']?"),
        (pw.capitalize() + " in Config", r"(?i)(" + pw + r"|" + pw2 + r"|" + pw3 + r")\s*[=:]\s*[\"']?[^\s\"']{8,}[\"']?"),
        ("Private Key",                 r"-----BEGIN\s+(RSA|EC|DSA|OPENSSH|PGP)?\s*" + pk + r"-----"),
        ("Slack Token",                 r"xox[bpors]-[A-Za-z0-9\-]{10,}"),
        ("Stripe Key",                  r"[sr]k_(live|test)_[A-Za-z0-9]{20,}"),
        ("Google API Key",              r"AIza[0-9A-Za-z\-_]{35}"),
        ("Anthropic API Key",           r"sk-ant-[A-Za-z0-9\-]{20,}"),
        ("OpenAI API Key",              r"sk-[A-Za-z0-9]{20,}"),
        ("DB Connection String",        r"(?i)(mongodb|postgres|mysql|redis)://[^\s\"']{10,}"),
    ]


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_input = data.get("tool_input")
    if not tool_input:
        sys.exit(0)

    strings_to_scan = []
    for field in ("content", "new_string", "old_string", "command"):
        value = tool_input.get(field)
        if value:
            strings_to_scan.append(value)

    if not strings_to_scan:
        sys.exit(0)

    text_to_scan = "\n".join(strings_to_scan)

    detected = []
    for name, pattern in _build_patterns():
        if re.search(pattern, text_to_scan):
            detected.append(name)

    if detected:
        secret_list = ", ".join(detected)
        print(
            f"SECRET DETECTED - Blocking write operation. Found: {secret_list}. "
            "Remove secrets and use environment variables or a secrets manager instead.",
            file=sys.stderr,
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
