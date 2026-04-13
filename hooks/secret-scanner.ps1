# Secret Scanner - PreToolUse hook for Write and Edit events
# Scans tool_input content for API keys, tokens, passwords, and other secrets.
# Exit 0 = safe, Exit 2 = secret detected (blocks the tool call).

$ErrorActionPreference = "Stop"

$hookData = $null
try {
    $raw = [Console]::In.ReadToEnd()
    $hookData = $raw | ConvertFrom-Json
} catch {
    # Cannot parse input, allow through
    exit 0
}

$toolInput = $hookData.tool_input
if (-not $toolInput) {
    exit 0
}

# Collect all string values from tool_input to scan
$stringsToScan = @()

if ($toolInput.content) {
    $stringsToScan += $toolInput.content
}
if ($toolInput.new_string) {
    $stringsToScan += $toolInput.new_string
}
if ($toolInput.old_string) {
    $stringsToScan += $toolInput.old_string
}
if ($toolInput.command) {
    $stringsToScan += $toolInput.command
}

if ($stringsToScan.Count -eq 0) {
    exit 0
}

$textToScan = $stringsToScan -join "`n"

# Secret detection patterns
$patterns = @(
    @{ Name = "AWS Access Key";         Regex = "AKIA[0-9A-Z]{16}" }
    @{ Name = "AWS Secret Key";         Regex = "(?i)aws[_\-]?secret[_\-]?access[_\-]?key\s*[=:]\s*[A-Za-z0-9/+=]{20,}" }
    @{ Name = "GitHub Token";           Regex = "ghp_[A-Za-z0-9]{36}" }
    @{ Name = "GitHub OAuth Token";     Regex = "gho_[A-Za-z0-9]{36}" }
    @{ Name = "GitHub App Token";       Regex = "ghu_[A-Za-z0-9]{36}" }
    @{ Name = "GitHub App Install Token"; Regex = "ghs_[A-Za-z0-9]{36}" }
    @{ Name = "GitHub PAT (fine-grained)"; Regex = "github_pat_[A-Za-z0-9_]{22,}" }
    @{ Name = "Bearer Token";           Regex = "(?i)bearer\s+[A-Za-z0-9\-._~+/]+=*" }
    @{ Name = "Generic API Key";        Regex = "(?i)(api[_\-]?key|apikey)\s*[=:]\s*[""']?[A-Za-z0-9\-._]{20,}[""']?" }
    @{ Name = "Generic Secret";         Regex = "(?i)(secret|secret[_\-]?key)\s*[=:]\s*[""']?[A-Za-z0-9\-._]{20,}[""']?" }
    @{ Name = "Generic Token";          Regex = "(?i)(access[_\-]?token|auth[_\-]?token)\s*[=:]\s*[""']?[A-Za-z0-9\-._]{20,}[""']?" }
    @{ Name = "Password in Config";     Regex = "(?i)(password|passwd|pwd)\s*[=:]\s*[""']?[^\s""']{8,}[""']?" }
    @{ Name = "Private Key";            Regex = "-----BEGIN\s+(RSA|EC|DSA|OPENSSH|PGP)?\s*PRIVATE KEY-----" }
    @{ Name = "Slack Token";            Regex = "xox[bpors]-[A-Za-z0-9\-]{10,}" }
    @{ Name = "Stripe Key";             Regex = "[sr]k_(live|test)_[A-Za-z0-9]{20,}" }
    @{ Name = "Google API Key";         Regex = "AIza[0-9A-Za-z\-_]{35}" }
    @{ Name = "Anthropic API Key";      Regex = "sk-ant-[A-Za-z0-9\-]{20,}" }
    @{ Name = "OpenAI API Key";         Regex = "sk-[A-Za-z0-9]{20,}" }
    @{ Name = "Database Connection String"; Regex = "(?i)(mongodb|postgres|mysql|redis)://[^\s""']{10,}" }
)

$detectedSecrets = @()

foreach ($pattern in $patterns) {
    if ($textToScan -match $pattern.Regex) {
        $detectedSecrets += $pattern.Name
    }
}

if ($detectedSecrets.Count -gt 0) {
    $secretList = $detectedSecrets -join ", "
    [Console]::Error.WriteLine("SECRET DETECTED - Blocking write operation. Found: $secretList. Remove secrets and use environment variables or a secrets manager instead.")
    exit 2
}

exit 0
