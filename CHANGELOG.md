# CHANGELOG

All notable changes to this project will be documented in this file.

> 版本規則（本專案採用）
>
> - `v0.1.x`：早期規劃與原型
> - `v0.2.0`：第二版穩定基線（FastAPI + SQLite + TWSE only）
> - `v0.3.0-beta.x`：第三版開發驗證階段（TPEx 支援已導入、待最終人工驗證）
> - `v0.3.0`：第三版正式版（TWSE + TPEX 雙市場完成）
> - `v0.3.x`：第三版後續修正與增量版本

---

## Current Status

### Latest Stable Baseline
**`v0.3.0`**

代表：
- 第三版 TPEx 上櫃支援主線已完成到：
  - Batch 2-1：StockService
  - Batch 2-2：DividendService
- pytest 結果：
  - `23 passed, 2 skipped`
- 雙市場（`TWSE` / `TPEX`）的股票與股利 API 已完成程式層與測試層整合
- 尚待最終人工驗證：
  - `POST /api/v1/admin/refresh/dividends?market=TPEX`
  - `GET /api/v1/stocks/{stock_code}/dividends?market=TPEX`

### Latest Stable Baseline
**`v0.2.0`**

代表：
- 第二版穩定基線
- TWSE only
- SQLite + FastAPI + pytest + PowerShell 測試腳本已可用

---

## [v0.3.0] - 2026-04-22

### Added
- TWSE + TPEX 雙市場支援
- 股票基本資料與股利資料皆支援 `market`
- refresh API 支援 `market=TWSE|TPEX`

### Changed
- StockService 與 DividendService 升級為雙市場架構
- repositories 以 `stock_code + market` 做資料解析
- dividend response 納入 `market`

### Validation
- pytest: 23 passed, 2 skipped
- TWSE / TPEX 股票與股利流程已完成第三版主線整合

### Notes
- 此版本為第三版正式版
- `dividend_year` 目前仍維持民國年
- `industry` 目前仍維持來源代碼
---
## [Unreleased]

### Planned after v0.3.0
- industry 代碼轉中文
- dividend_year 西元化
- CI / GitHub Actions
- scheduler / refresh log

---
## [v0.3.0] - 2026-04-22

### Added
- TWSE + TPEX 雙市場支援
- 股票基本資料與股利資料皆支援 `market`
- refresh API 支援 `market=TWSE|TPEX`

### Changed
- StockService 與 DividendService 升級為雙市場架構
- repositories 以 `stock_code + market` 做資料解析
- dividend response 納入 `market`

### Validation
- pytest: 23 passed, 2 skipped
- TWSE / TPEX 股票與股利流程已完成第三版主線整合

### Notes
- 此版本為第三版正式版
- `dividend_year` 目前仍維持民國年
- `industry` 目前仍維持來源代碼

---

## [v0.3.0-beta.1] - 2026-04-22

### Added
- 新增 **TPEx 上櫃股票基本資料** 支援
- 新增 **TPEx 上櫃股利資料** 支援
- 新增 `TPExClient`
- 新增雙市場（`TWSE` / `TPEX`）股票查詢能力
- 新增雙市場（`TWSE` / `TPEX`）股利查詢能力
- 新增 `market` query param 支援：
  - `GET /api/v1/stocks/{stock_code}?market=TWSE|TPEX`
  - `GET /api/v1/stocks/{stock_code}/dividends?market=TWSE|TPEX`
  - `POST /api/v1/admin/refresh/stocks?market=TWSE|TPEX`
  - `POST /api/v1/admin/refresh/dividends?market=TWSE|TPEX`
- 新增 TPEX 測試案例：
  - stock API
  - dividend API
  - repository 雙市場支援
- 新增可選整合測試：
  - `tests/integration/test_tpex_live.py`

### Changed
- `StockService` 從單一市場升級為雙市場路由邏輯
- `DividendService` 從單一市場升級為雙市場路由邏輯
- `StockRepository.get_by_code()` 改為顯式接受 `market`
- `StockRepository` 新增 `list_by_code()`，供跨市場查詢 / fallback / 衝突判定
- `DividendRepository.list_by_stock_code()` 改為顯式接受 `market`
- `DividendListResponse` 新增 `market` 欄位
- stock / dividend API route 與 refresh route 全面支援 `market`

### Fixed
- 修正 repository 原本硬綁 `TWSE` 導致 `TPEX` 無法查詢的限制
- 修正 stock query 在雙市場下的 fallback / ambiguous match 行為
- 修正 dividend query 在雙市場下的 market resolution 行為
- 修正同股票代號跨市場共存時的 API 歧義問題，加入：
  - `409 MULTIPLE_MARKET_MATCH`
- 修正 TPEX crawler / service 串接流程，使其與既有 TWSE 分層一致

### Validation
- pytest 結果：
  - `23 passed, 2 skipped`
- 已驗證：
  - `refresh/stocks?market=TWSE`
  - `refresh/stocks?market=TPEX`
  - `GET /stocks/{stock_code}?market=TPEX`
  - `GET /stocks/{stock_code}` fallback 到 TPEX
- 待人工驗證：
  - `refresh/dividends?market=TPEX`
  - `GET /stocks/{stock_code}/dividends?market=TPEX`

### Notes
- 第三版資料來源策略：
  - TWSE：官方 OpenAPI / 開放資料
  - TPEX：官方開放資料 / CSV 為主
- `dividend_year` 目前仍維持 **民國年**
- `industry` 目前仍維持來源代碼（例如 `"24"`）
- 第三版的重點是：
  - 在不推翻第二版架構下，擴充為雙市場共用系統
  - 保持 SQLite MVP / FastAPI / pytest / PowerShell 工具鏈可持續使用

---

## [v0.2.0] - 2026-04-22

### Added
- 建立 **FastAPI + SQLite** 的單機 MVP 專案骨架
- 建立 `stock_basic`、`dividend_history` 等核心資料表
- 建立 `TWSEClient`，可抓取：
  - 上市公司基本資料
  - 上市公司股利分派資料
- 建立 `StockService` / `DividendService`
- 建立股票基本資料 API
- 建立股利查詢 API
- 建立手動 refresh API
- 建立 pytest 測試骨架
- 建立 PowerShell 測試腳本：
  - `run_tests.ps1`
  - `run_integration.ps1`
  - `smoke_api.ps1`
  - `run_all.ps1`
- 建立 `README-TESTING.md`

### Changed
- API 回應改為明確使用 UTF-8 JSON response
- 增加 `Content-Type: application/json; charset=utf-8`
- 將 `FastAPI startup on_event` 改為 `lifespan`
- 將 `datetime.utcnow()` 替換為較新寫法，避免 Python 3.12 deprecation warning
- `run_tests.ps1` 改為：
  - 優先使用專案內 `.venv312`
  - 若不存在，fallback 到目前 shell 的 `python`

### Fixed
- 修正 `dividend_service.py` 字串未結束造成的 `SyntaxError`
- 修正 PowerShell 下 `curl -X POST ...` 不適用問題，改以 `Invoke-RestMethod` / `curl.exe` 測試
- 修正 API 中文亂碼問題：
  - 後端 response header 明確指定 UTF-8
  - PowerShell 使用 `.Content` 驗證原始 JSON
- 修正 SQLite 測試 DB 在 Windows 下 teardown 時的 `WinError 32` 檔案鎖定問題：
  - 增加 `close_all_sessions()`
  - `engine.dispose()`
  - `gc.collect()`
  - retry 刪檔機制
- 修正 `run_tests.ps1` 可能因虛擬環境路徑不一致導致無法執行 pytest 的問題

### Notes
- 此版本以 **TWSE only** 為主
- `dividend_year` 維持民國年
- `industry` 維持來源代碼
- 此版重點在於：
  - 先把 **資料抓取、SQLite、API、測試、PowerShell 工具鏈** 打通
  - 尚未正式進入 TPEx 雙市場功能實作

---

## [v0.1.x] - Historical / Pre-baseline

### Notes
- 早期規劃階段與原型階段
- 主要完成：
  - 名詞定義
  - SQLite MVP 架構設計
  - 資料來源評估
  - API / DB / 專案結構規格草案
- 未作為穩定可執行基線版本

---

# Tag / Branch 建議

## 建議目前 Git tag
若你要先標記第三版測試完成但尚未完成人工 smoke 驗證的狀態，建議：

```bash
git add .
git commit -m "feat: complete v0.3.0-beta.1 dual-market stock and dividend support"
git tag v0.3.0-beta.1
