param(
    [string]$BaseUrl = "http://127.0.0.1:8000"
)

$ErrorActionPreference = "Stop"

chcp 65001 > $null
[Console]::InputEncoding  = [System.Text.UTF8Encoding]::new()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [Console]::OutputEncoding

function Invoke-JsonGet {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Url
    )

    Write-Host ""
    Write-Host "==> GET $Url" -ForegroundColor Cyan

    $resp = Invoke-WebRequest -UseBasicParsing -Uri $Url

    Write-Host "-- StatusCode --"
    Write-Host $resp.StatusCode

    Write-Host "-- Content-Type --"
    Write-Host $resp.Headers["Content-Type"]

    Write-Host "-- Content --"
    Write-Host $resp.Content

    return $resp
}

try {
    Invoke-JsonGet -Url "$BaseUrl/healthz" | Out-Null
    Invoke-JsonGet -Url "$BaseUrl/api/v1/stocks/2330" | Out-Null
    Invoke-JsonGet -Url "$BaseUrl/api/v1/stocks/2330/dividends" | Out-Null

    Write-Host ""
    Write-Host "✅ API smoke test 完成" -ForegroundColor Green
    exit 0
}
catch {
    Write-Host ""
    Write-Host "❌ API smoke test 失敗" -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}