# voice/speak.ps1 — Lila's one-shot voice line.
# Usage:
#   pwsh -File voice/speak.ps1 "Hi Travis, can you hear me?"
#   pwsh -File voice/speak.ps1 -Voice af_sky -Speed 1.0 "..."
# Requires the Lila-voice (Kokoro-FastAPI) container at http://localhost:8880.

param(
    [Parameter(Mandatory = $true, Position = 0, ValueFromRemainingArguments = $true)]
    [string[]]$Text,

    [string]$Voice = "af_sky",
    [double]$Speed = 1.0,
    [string]$Endpoint = "http://localhost:8880/v1/audio/speech",
    [switch]$NoPlay
)

$ErrorActionPreference = "Stop"

$message = ($Text -join ' ').Trim()
if (-not $message) {
    Write-Error "speak.ps1: no text provided"
    exit 2
}

$tempFile = Join-Path $env:TEMP ("lila_speak_{0}.mp3" -f ([guid]::NewGuid().ToString("N").Substring(0, 8)))

$body = @{
    model           = "kokoro"
    voice           = $Voice
    input           = $message
    response_format = "mp3"
    speed           = $Speed
} | ConvertTo-Json -Compress

try {
    Invoke-RestMethod -Uri $Endpoint -Method Post -ContentType "application/json" -Body $body -OutFile $tempFile -TimeoutSec 30
}
catch {
    Write-Error ("speak.ps1: TTS request failed - " + $_.Exception.Message + ". Is the Lila-voice container running? (docker ps)")
    exit 1
}

if ($NoPlay) {
    Write-Output $tempFile
    exit 0
}

Add-Type -AssemblyName presentationCore
$player = New-Object System.Windows.Media.MediaPlayer
$player.Open([Uri]::new($tempFile, [UriKind]::Absolute))
$player.Play()

$waited = 0
while (-not $player.NaturalDuration.HasTimeSpan -and $waited -lt 2000) {
    Start-Sleep -Milliseconds 50
    $waited += 50
}

if ($player.NaturalDuration.HasTimeSpan) {
    $ms = [int]$player.NaturalDuration.TimeSpan.TotalMilliseconds + 250
    Start-Sleep -Milliseconds $ms
}
else {
    Start-Sleep -Seconds 8
}

$player.Stop()
$player.Close()
Remove-Item $tempFile -ErrorAction SilentlyContinue
