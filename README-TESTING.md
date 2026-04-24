# README-TESTING

本文件說明本專案的測試方式、PowerShell 腳本用法，以及 Windows / PowerShell 常見問題排查方式。

---

## 目錄

1. [測試目標](#1-測試目標)
2. [測試範圍與目前版本狀態](#2-測試範圍與目前版本狀態)
3. [測試目錄結構](#3-測試目錄結構)
4. [前置條件](#4-前置條件)
5. [單元測試 / API 測試](#5-單元測試--api-測試)
6. [整合測試（可選）](#6-整合測試可選)
7. [Smoke API 測試](#7-smoke-api-測試)
8. [一鍵執行所有常用測試](#8-一鍵執行所有常用測試)
9. [雙市場（TWSE / TPEX）測試方式](#9-雙市場twse--tpex測試方式)
10. [Windows / PowerShell 常見問題](#10-windowspowershell-常見問題)
11. [測試通過的預期結果](#11-測試通過的預期結果)
12. [建議日常開發流程](#12-建議日常開發流程)
13. [後續可擴充方向](#13-後續可擴充方向)
14. [維護建議](#14-維護建議)

---

## 1. 測試目標

本專案目前提供以下測試類型：

### 1.1 單元測試 / API 測試
使用 `pytest`，主要驗證：

- `/healthz`
- 股票基本資料 API
- 股利查詢 API
- `utils.py` 內的解析與編碼修正函式
- repository 的 `upsert` 行為
- 測試資料庫初始化與清理流程
- 雙市場（`TWSE` / `TPEX`）查詢與 refresh 行為

### 1.2 整合測試（可選）
可直接打外部資料源（例如 TWSE / TPEX 開放資料），用於確認：

- 外部資料源是否仍可用
- 回傳結構是否仍符合預期
- crawler 是否仍能正常抓取資料

> 整合測試會依賴網路與外部服務，因此**不建議每次開發都跑**。

### 1.3 Smoke API 測試
驗證本機 API 是否正常啟動，並快速檢查：

- `/healthz`
- `/api/v1/stocks/2330`
- `/api/v1/stocks/2330/dividends`
- `/api/v1/stocks/6488?market=TPEX`
- `/api/v1/stocks/6488/dividends?market=TPEX`

同時驗證：

- HTTP Status Code
- `Content-Type`
- JSON 原始內容
- UTF-8 / 中文輸出是否正常

---

## 2. 測試範圍與目前版本狀態

### 2.1 目前版本狀態
目前專案測試狀態可視為：

- **第二版穩定基線**：`v0.2.0`
- **第三版開發驗證版**：`v0.3.0-beta.1`

### 2.2 目前已驗證能力
目前測試已覆蓋：

- `TWSE` 股票基本資料
- `TWSE` 股利資料
- `TPEX` 股票基本資料
- `TPEX` 股利資料
- `market` query param
- refresh API 的 `market` 支援
- stock / dividend 的 fallback 與多市場歧義處理

### 2.3 目前 pytest 基線
目前預期測試結果：

```text
23 passed, 2 skipped

---

## 2. 測試目錄結構

```text
tests/
├─ conftest.py
├─ test_api_healthz.py
├─ test_api_stocks.py
├─ test_utils.py
├─ test_repository_upsert.py
└─ integration/
   └─ test_twse_live.py

scripts/
├─ run_tests.ps1
├─ run_integration.ps1
├─ smoke_api.ps1
└─ run_all.ps

單元測試 / API 測試
python -m pytest -q
看詳細輸出：
python -m pytest -v
只跑某一支：
python -m pytest tests/test_api_stocks.py -v

4.2 使用 PowerShell 腳本
powershell -ExecutionPolicy Bypass -File .\scripts\run_tests.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\run_tests.ps1 -VerboseMode
保留測試 DB（除錯用）：
powershell -ExecutionPolicy Bypass -File .\scripts\run_tests.ps1 -KeepTestDb

Smoke API 測試
請先在另一個 PowerShell 視窗啟動 FastAPI：
uvicorn app.main:app --reload
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_api.ps1

一鍵執行所有常用測試
powershell -ExecutionPolicy Bypass -File .\scripts\run_all.ps1