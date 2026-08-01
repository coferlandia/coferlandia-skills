# update-plugin.ps1
# Package the current reviewed checkout without pulling or changing Git state.
# Usage: .\scripts\update-plugin.ps1
# Optional: .\scripts\update-plugin.ps1 -Output "C:\path\coferlandia-skills.plugin"

param(
    [string]$Output = "$PSScriptRoot\..\coferlandia-skills.plugin"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path "$PSScriptRoot\..").Path
$Cli = Join-Path $RepoRoot ".agents\skills\coferlandia-release-maintainer\scripts\coferlandia-release-maintainer-cli.py"
$OutputResolved = [System.IO.Path]::GetFullPath($Output)

if (-not (Test-Path $Cli)) {
    Write-Error "Release-maintainer CLI not found: $Cli"
    exit 1
}

Write-Host "=== coferlandia-skills: verified package ===" -ForegroundColor Cyan
Write-Host "Repository: $RepoRoot"
Write-Host "Output: $OutputResolved"
Write-Host "Packaging the current checkout exactly as reviewed; no git pull is performed." -ForegroundColor Yellow

python $Cli --repo $RepoRoot package --output $OutputResolved --verify
if ($LASTEXITCODE -ne 0) {
    Write-Error "Plugin packaging or verification failed."
    exit $LASTEXITCODE
}

Write-Host "Plugin package created and verified: $OutputResolved" -ForegroundColor Green
