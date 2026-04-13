# Claude Code notification hook
# Shows a Windows toast notification when Claude is done or needs input

Add-Type -AssemblyName System.Windows.Forms

$balloon = New-Object System.Windows.Forms.NotifyIcon
$balloon.Icon = [System.Drawing.SystemIcons]::Information
$balloon.BalloonTipTitle = "Claude Code"
$balloon.BalloonTipText = "Klaar! Claude heeft je input nodig of is klaar met de taak."
$balloon.Visible = $True
$balloon.ShowBalloonTip(5000)

Start-Sleep -Seconds 6
$balloon.Dispose()

exit 0
