param(
    [switch]$VerboseMode,
    [switch]$KeepTestDb
)

$ErrorActionPreference = "Stop"

# -----------------------------
# Resolve project root
# -----------------------------
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $ProjectRoot

Write-Host "==> ProjectRoot: $ProjectRoot"

# -----------------------------
# Resolve Python executable (Strategy C)
# 1) Prefer local .venv312
# 2) Fallback to current shell python
# -----------------------------
$LocalPython = Join-Path $ProjectRoot ".venv312\Scripts\python.exe"

if (Test-Path $LocalPython) {
    $PythonExe = $LocalPython
    Write-Host "==> Using local venv python: $PythonExe"
}
else {
    try {
        $PythonExe = (Get-Command python -ErrorAction Stop).Source
        Write-Host "==> Using shell python: $PythonExe"
    }
    catch {
        Write-Error "Python executable not found. Activate a virtualenv or create .venv312 first."
        exit 1
    }
}

# -----------------------------
# UTF-8 console safety
# -----------------------------
chcp 65001 > $null
$utf8 = [System.Text.UTF8Encoding]::new()
[Console]::InputEncoding  = $utf8
[Console]::OutputEncoding = $utf8
$OutputEncoding = $utf8

# -----------------------------
# Test DB cleanup
# -----------------------------
$TestDb = Join-Path $ProjectRoot "test_tw_dividend.db"

if ((Test-Path $TestDb) -and (-not $KeepTestDb)) {
    Write-Host "==> Removing leftover test DB: $TestDb"
}