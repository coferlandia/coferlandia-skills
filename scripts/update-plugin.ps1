# update-plugin.ps1
# Actualiza el repo desde origin y reempaqueta coferlandia-skills.plugin
# Uso: .\scripts\update-plugin.ps1
# Opcional: .\scripts\update-plugin.ps1 -Output "C:\ruta\destino"

param(
    [string]$Output = "$PSScriptRoot\..\coferlandia-skills.plugin"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path "$PSScriptRoot\.."

Write-Host "=== coferlandia-skills: update-plugin ===" -ForegroundColor Cyan
Write-Host "Repo: $RepoRoot"

# 1. Pull
Write-Host "`n[1/3] git pull..." -ForegroundColor Yellow
Set-Location $RepoRoot
git pull origin main
if ($LASTEXITCODE -ne 0) { Write-Error "git pull falló"; exit 1 }

# 2. Leer versión del plugin.json
$pluginJson = Get-Content "$RepoRoot\.claude-plugin\plugin.json" | ConvertFrom-Json
$version = $pluginJson.version
Write-Host "`n[2/3] Empaquetando v$version..." -ForegroundColor Yellow

# 3. Empaquetar (incluir solo lo necesario para el plugin)
$TmpDir = [System.IO.Path]::GetTempPath() + "coferlandia-skills-plugin-" + [System.Guid]::NewGuid().ToString("N").Substring(0,8)
New-Item -ItemType Directory -Path $TmpDir | Out-Null

$include = @(".claude-plugin", "skills", "README.md", "AGENTS.md", "LICENSE", "_protocol")
foreach ($item in $include) {
    $src = Join-Path $RepoRoot $item
    if (Test-Path $src) {
        Copy-Item -Recurse -Force $src (Join-Path $TmpDir $item)
    }
}

# Zip
$OutputResolved = [System.IO.Path]::GetFullPath($Output)
if (Test-Path $OutputResolved) { Remove-Item $OutputResolved -Force }
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($TmpDir, $OutputResolved)
Remove-Item -Recurse -Force $TmpDir

$size = [math]::Round((Get-Item $OutputResolved).Length / 1KB)
Write-Host "`n[3/3] Plugin generado: $OutputResolved ($size KB)" -ForegroundColor Green
Write-Host "Instalar en Claude: Settings > Capabilities > Plugins > Install from file" -ForegroundColor Cyan
