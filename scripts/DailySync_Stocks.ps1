# scripts\DailySync_Stocks.ps1
$ErrorActionPreference = "Stop"

# ===== 基本路徑設定 =====
$ProjectRoot = "D:\Py_code\Taiwan Stock App"
$Python      = "D:\Py_code\Dash_Board\.venv312\Scripts\python.exe"

# ===== 雲端設定（從環境變數讀）=====
$CloudBase = $env:CLOUD_API_BASE
$Token     = $env:CLOUD_ADMIN_TOKEN

# ===== 日誌設定（一定要在 Log() 前完成）=====
$LogDir = Join-Path $ProjectRoot "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Stamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
$LogFile = Join-Path $LogDir "daily_sync_$Stamp.log"

function Log([string]$msg) {
  $line = "[{0}] {1}" -f (Get-Date).ToString("yyyy-MM-dd HH:mm:ss"), $msg
  $line | Tee-Object -FilePath $LogFile -Append
}

# ===== 早期檢查（避免後面才爆）=====
Log "Python path=$Python"
if (-not (Test-Path $Python)) { throw "Python not found: $Python" }

if ([string]::IsNullOrWhiteSpace($CloudBase)) { throw "CLOUD_API_BASE not set" }
if ([string]::IsNullOrWhiteSpace($Token))     { throw "CLOUD_ADMIN_TOKEN not set" }

Log "CloudBase=$CloudBase"

# 日誌
$LogDir = Join-Path $ProjectRoot "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Stamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
$LogFile = Join-Path $LogDir "daily_sync_$Stamp.log"

function Log($msg) {
  $line = "[{0}] {1}" -f (Get-Date).ToString("yyyy-MM-dd HH:mm:ss"), $msg
  $line | Tee-Object -FilePath $LogFile -Append
}

function Invoke-RetryCurlUpload($url, $csvPath) {
  # Render Free 可能冷啟動，做重試
  $max = 5
  for ($i=1; $i -le $max; $i++) {
    Log "UPLOAD try $i/$max -> $url (file=$csvPath)"
    $resp = & curl.exe -s -S -f -X POST $url `
      -H "X-ADMIN-TOKEN: $Token" `
      -F "file=@$csvPath"
    if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($resp)) {
      Log "UPLOAD OK response=$resp"
      return $resp
    }
    Log "UPLOAD failed (exit=$LASTEXITCODE). Sleep 10s..."
    Start-Sleep -Seconds 10
  }
  throw "UPLOAD failed after $max retries: $url"
}

function Invoke-RetryCurlPost($url) {
  $max = 5
  for ($i=1; $i -le $max; $i++) {
    Log "POST try $i/$max -> $url"
    $resp = & curl.exe -s -S -f -X POST $url -H "accept: application/json"
    if ($LASTEXITCODE -eq 0) {
      Log "POST OK response=$resp"
      return $resp
    }
    Log "POST failed (exit=$LASTEXITCODE). Sleep 5s..."
    Start-Sleep -Seconds 5
  }
  throw "POST failed after $max retries: $url"
}

# ===== (A) 啟動本機後端（如你要每天先 refresh 本機 DB）=====
# 你本機 refresh TWSE 成功，所以這段是「每天更新本機 DB」的關鍵。
# 若你本機已經有其他方式更新 DB，可把此段改成你自己的 refresh 流程。
$LocalHost = "127.0.0.1"
$LocalPort = 8000
$LocalBase = "http://{0}:{1}" -f $LocalHost, $LocalPort

Log "LocalBase=$LocalBase"
# ===== (A) 啟動本機後端（uvicorn）=====
Log "Start local backend (uvicorn) ..."

$UvicornOut = Join-Path $LogDir "uvicorn_$Stamp.out"
$UvicornErr = Join-Path $LogDir "uvicorn_$Stamp.err"

# 用 --app-dir 明確指定 app 的搜尋根目錄，避免找不到 app 套件
# Uvicorn 支援 --app-dir：把指定目錄加入 PYTHONPATH 來載入 <module>:<attribute> [3](https://uvicorn.dev/settings/)
$proc = Start-Process -FilePath $Python -WorkingDirectory $ProjectRoot -ArgumentList @(
  "-m","uvicorn","app.main:app",
  "--host",$LocalHost,
  "--port",$LocalPort,
  "--app-dir", ('"' + $ProjectRoot + '"')
) -PassThru -WindowStyle Hidden -RedirectStandardOutput $UvicornOut -RedirectStandardError $UvicornErr

Start-Sleep -Seconds 1
if ($proc.HasExited) {
  Log "Uvicorn exited immediately. ExitCode=$($proc.ExitCode)"
  Log "---- uvicorn stderr (tail) ----"
  if (Test-Path $UvicornErr) { Get-Content $UvicornErr -Tail 200 | Tee-Object -FilePath $LogFile -Append }
  Log "---- uvicorn stdout (tail) ----"
  if (Test-Path $UvicornOut) { Get-Content $UvicornOut -Tail 200 | Tee-Object -FilePath $LogFile -Append }
  throw "Uvicorn failed to start"
}

# 等待健康檢查
$ready = $false
for ($t=1; $t -le 30; $t++) {
  try {
    $HealthUrl = "$LocalBase/healthz"
    Log "HealthUrl=$HealthUrl"
    & curl.exe -s -S $HealthUrl | Out-Null
    if ($LASTEXITCODE -eq 0) { $ready = $true; break }
  } catch {}
  Start-Sleep -Seconds 1
}
if (-not $ready) {
  try { Stop-Process -Id $proc.Id -Force } catch {}
  throw "Local backend did not become ready: $LocalBase/healthz"
}
Log "Local backend ready."

# ===== (B) 本機 refresh（TWSE/TPEX stocks）=====
# 這是用你現有的 admin refresh API；若你的本機路由不同，改這兩行 URL 即可。
Invoke-RetryCurlPost "$LocalBase/api/v1/admin/refresh/stocks?market=TWSE"
Invoke-RetryCurlPost "$LocalBase/api/v1/admin/refresh/stocks?market=TPEX"

Invoke-RetryCurlPost "$LocalBase/api/v1/admin/refresh/dividends?market=TWSE"
Invoke-RetryCurlPost "$LocalBase/api/v1/admin/refresh/dividends?market=TPEX"


# ===== (C) 匯出兩份 CSV（你已處理好 export_stocks_for_import.py）=====
Log "Export CSV for cloud import ..."
Set-Location $ProjectRoot
& $Python -m scripts.export_stocks_for_import | Tee-Object -FilePath $LogFile -Append
if ($LASTEXITCODE -ne 0) { throw "Export script failed with exit code $LASTEXITCODE" }

try {
  & $Python -m scripts.export_dividends_for_import
} catch {
  Log "Dividend export failed:"
  Log $_
  throw
}
if ($LASTEXITCODE -ne 0) { throw "Dividend export script failed with exit code $LASTEXITCODE" }

$TwseCsv = Join-Path $ProjectRoot "stocks_TWSE_import.csv"
$TpexCsv = Join-Path $ProjectRoot "stocks_TPEX_import.csv"

if (-not (Test-Path $TwseCsv)) { throw "Missing $TwseCsv" }
if (-not (Test-Path $TpexCsv)) { throw "Missing $TpexCsv" }

# ===== (D) 上傳到雲端匯入 API =====
Invoke-RetryCurlUpload "$CloudBase/api/v1/admin/import/stocks?market=TWSE" $TwseCsv
Invoke-RetryCurlUpload "$CloudBase/api/v1/admin/import/stocks?market=TPEX" $TpexCsv

Invoke-RetryCurlUpload "$CloudBase/api/v1/admin/import/dividends" (Join-Path $ProjectRoot "dividends_TWSE_import.tsv")
Invoke-RetryCurlUpload "$CloudBase/api/v1/admin/import/dividends" (Join-Path $ProjectRoot "dividends_TPEX_import.tsv")


# ===== (E) 收尾：關閉本機 uvicorn =====
Log "Stop local backend ..."
try { Stop-Process -Id $proc.Id -Force } catch {}
Log "DONE"
