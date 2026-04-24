param(
    [switch]$VerboseMode,
    [switch]$IncludeIntegration,
    [string]$BaseUrl = "http://127.0.0.1:8000"
)

$ErrorActionPreference = "Stop"

# -----------------------------
# Resolve paths
# -----------------------------
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ScriptsDir  = Join-Path $ProjectRoot "scripts"

$RunTestsScript       = Join-Path $ScriptsDir "run_tests.ps1"
$SmokeApiScript       = Join-Path $ScriptsDir "smoke_api.ps1"
$RunIntegrationScript = Join-Path $ScriptsDir "run_integration.ps1"

Write-Host "==> ProjectRoot: $ProjectRoot"
Set-Location $ProjectRoot

# -----------------------------
# UTF-8 console safety
# -----------------------------
chcp 65001 > $null
$utf8 = [System.Text.UTF8Encoding]::new()
[Console]::InputEncoding  = $utf8
[Console]::OutputEncoding = $utf8
$OutputEncoding = $utf8

# -----------------------------
# Validate required scripts
# -----------------------------
if (-not (Test-Path $RunTestsScript)) {
    Write-Error "Missing script: $RunTestsScript"
    exit 1
}

if (-not (Test-Path $SmokeApiScript)) {
    Write-Error "Missing script: $SmokeApiScript"
    exit 1
}

if ($IncludeIntegration -and (-not (Test-Path $RunIntegrationScript))) {
    Write-Error "Missing script: $RunIntegrationScript"
    exit 1
}

# -----------------------------
# Resolve shell executable
# Prefer pwsh if available, otherwise use powershell
# -----------------------------
$ShellExe = $null
if (Get-Command pwsh -ErrorAction SilentlyContinue) {
    $ShellExe = (Get-Command pwsh).Source
}
elseif (Get-Command powershell -ErrorAction SilentlyContinue) {
    $ShellExe = (Get-Command powershell).Source
}
else {
    Write-Error "Neither pwsh nor powershell is available in PATH."
    exit 1
}

Write-Host "==> ShellExe: $ShellExe"

# -----------------------------
# Helper: run child script and fail fast
# -----------------------------
function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [string]$ScriptPath,

        [string[]]$Arguments = @()
    )

    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "STEP: $Name" -ForegroundColor Cyan
    Write-Host "SCRIPT: $ScriptPath" -ForegroundColor Cyan
    if ($Arguments.Count -gt 0) {
        Write-Host "ARGS: $($Arguments -join ' ')" -ForegroundColor Cyan
    }
    Write-Host "==================================================" -ForegroundColor Cyan

    & $ShellExe -ExecutionPolicy Bypass -File $ScriptPath @Arguments
    $ExitCode = $LASTEXITCODE

    if ($ExitCode -ne 0) {
        Write-Host ""
        Write-Host "❌ Step failed: $Name (exit code: $ExitCode)" -ForegroundColor Red
        exit $ExitCode
    }

    Write-Host "✅ Step passed: $Name" -ForegroundColor Green
}

# -----------------------------
# Helper: verify API is up before smoke test
# -----------------------------
function Test-ApiHealth {
    param(
        [Parameter(Mandatory = $true)]
        [string]$BaseUrl
    )

    $HealthUrl = "$BaseUrl/healthz"
    Write-Host ""
    Write-Host "==> Checking API health: $HealthUrl"

    try {
        $resp = Invoke-WebRequest -UseBasicParsing -Uri $HealthUrl -TimeoutSec 5
        if ($resp.StatusCode -eq 200) {
            Write-Host "✅ API health check passed"
            return $true
        }

        Write-Host "❌ API health check returned non-200: $($resp.StatusCode)" -ForegroundColor Red
        return $false
    }
    catch {
        Write-Host "❌ API health check failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# -----------------------------
# 1) Run tests
# -----------------------------
$RunTestsArgs = @()
if ($VerboseMode) {
    $RunTestsArgs += "-VerboseMode"
}

Invoke-Step -Name "Unit/API Tests" -ScriptPath $RunTestsScript -Arguments $RunTestsArgs

# -----------------------------
# 2) Check API before smoke test
# -----------------------------
if (-not (Test-ApiHealth -BaseUrl $BaseUrl)) {
    Write-Host ""
    Write-Host "API is not running. Please start it first:" -ForegroundColor Yellow
    Write-Host "    uvicorn app.main:app --reload" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Then rerun:" -ForegroundColor Yellow
    Write-Host "    powershell -ExecutionPolicy Bypass -File .\scripts\run_all.ps1" -ForegroundColor Yellow
    exit 1
}

# -----------------------------
# 3) Run smoke API test
# -----------------------------
$SmokeArgs = @("-BaseUrl", $BaseUrl)
Invoke-Step -Name "Smoke API Test" -ScriptPath $SmokeApiScript -Arguments $SmokeArgs

# -----------------------------
# 4) Optional integration tests
# -----------------------------
if ($IncludeIntegration) {
    $IntegrationArgs = @()
    if ($VerboseMode) {
        $IntegrationArgs += "-VerboseMode"
    }

    Invoke-Step -Name "Integration Tests" -ScriptPath $RunIntegrationScript -Arguments $IntegrationArgs
}

Write-Host ""
Write-Host "🎉 All selected steps completed successfully." -ForegroundColor Green
exit 0