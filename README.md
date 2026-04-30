# Taiwan Stock Dividend API

一個以 **FastAPI + SQLite** 為核心的台股股利 / 股票基本資料查詢專案。  
目前支援：

- **TWSE（上市）**
- **TPEX（上櫃）**

可提供：

- 股票基本資料查詢
- 歷年股利查詢
- 本地 SQLite 儲存
- 手動 refresh 官方資料
- pytest 測試
- Windows PowerShell 測試腳本

---

## 專案狀態

### 目前版本
**`v0.3.0`**

### 目前能力
- ✅ TWSE 股票基本資料
- ✅ TWSE 股利資料
- ✅ TPEX 股票基本資料
- ✅ TPEX 股利資料
- ✅ `market` 參數支援
- ✅ SQLite 本地資料庫
- ✅ FastAPI API
- ✅ pytest 測試
- ✅ PowerShell 測試腳本

### 目前測試基線
```text
23 passed, 2 skipped
```

### 備註
此版本為目前正式穩定版，代表：
- TWSE + TPEX 雙市場功能已完成
- 股票與股利 API 已整合
- pytest 測試已通過

---

## 專案目標

這個專案不是單純做「股利排行網站」，而是建立一套**可維護、可測試、可擴充的本地資料能力**，讓你可以：

- 建立自己的 SQLite 股利資料庫
- 提供自己的 API
- 自訂資料欄位與命名規則
- 不依賴單一第三方網站頁面
- 未來可接前端 / Excel / Power BI / 自動化工具 / 回測流程

---

## 核心功能

### 1. 股票基本資料查詢
可查詢：

- 股票代號
- 市場（TWSE / TPEX）
- 公司名稱
- 公司簡稱
- 產業別
- 每股面額
- 實收資本額
- 已發行普通股數
- 上市 / 上櫃日期

---

### 2. 歷年股利查詢
可查詢：

- 股利年度
- 期別
- 決議狀態
- 董事會決議日
- 股東會日期
- 現金股利（元/股）
- 股票股利（元/股）
- 總股利（元/股）
- 股票股利率（若可推算）

---

### 3. 官方資料手動 refresh
支援：

- `TWSE`
- `TPEX`

可個別刷新：

- 股票基本資料
- 股利資料

---

### 4. 雙市場查詢
API 支援：

- `market=TWSE`
- `market=TPEX`

若不指定 market：
- 會依系統邏輯做 fallback
- 若同代號跨市場同時存在且無法唯一判定，會回：
  - `409 MULTIPLE_MARKET_MATCH`

---

### 5. 本地 SQLite 儲存
目前預設資料庫：

```text
tw_dividend.db
```

這讓你可以：
- 本地保存資料
- 重複 refresh
- 保留自己的資料口徑
- 後續擴充到其他 DB（例如 PostgreSQL）

---

## 技術架構

### 後端
- FastAPI
- SQLAlchemy
- Pydantic
- requests

### 資料庫
- SQLite

### 測試
- pytest
- FastAPI TestClient

### 工具鏈
- PowerShell 測試腳本
- CHANGELOG
- README-TESTING

---

## 支援市場與資料範圍

| 市場 | 股票基本資料 | 股利資料 | 狀態 |
|------|--------------|----------|------|
| TWSE | ✅ | ✅ | 已完成 |
| TPEX | ✅ | ✅ | 已完成（beta 驗證中） |

---

## 專案結構

```text
tw_dividend_mvp/
├─ app/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ core/
│  │  ├─ __init__.py
│  │  ├─ config.py
│  │  └─ utils.py
│  ├─ db/
│  │  ├─ __init__.py
│  │  ├─ base.py
│  │  ├─ session.py
│  │  └─ init_db.py
│  ├─ models/
│  │  ├─ __init__.py
│  │  ├─ stock_basic.py
│  │  └─ dividend_history.py
│  ├─ schemas/
│  │  ├─ __init__.py
│  │  ├─ stock.py
│  │  └─ dividend.py
│  ├─ crawlers/
│  │  ├─ __init__.py
│  │  ├─ twse_client.py
│  │  └─ tpex_client.py
│  ├─ repositories/
│  │  ├─ __init__.py
│  │  ├─ stock_repository.py
│  │  └─ dividend_repository.py
│  ├─ services/
│  │  ├─ __init__.py
│  │  ├─ stock_service.py
│  │  └─ dividend_service.py
│  └─ api/
│     ├─ __init__.py
│     ├─ deps.py
│     └─ routes.py
├─ tests/
├─ scripts/
├─ requirements.txt
├─ .env.example
├─ README.md
├─ README-TESTING.md
└─ CHANGELOG.md
```

---

## 快速開始

### 1. 建立虛擬環境

```powershell
python -m venv .venv312
```

啟用（Windows PowerShell）：

```powershell
.\.venv312\Scripts\Activate.ps1
```

---

### 2. 安裝依賴

```powershell
pip install -r requirements.txt
```

---

### 3. 建立 `.env`

把 `.env.example` 複製成 `.env`

```powershell
Copy-Item .env.example .env
```

---

### 4. 啟動 API

```powershell
uvicorn app.main:app --reload
```

Swagger UI：

```text
http://127.0.0.1:8000/docs
```

---

## 建議第一次使用流程

### Step 1：刷新 TWSE 股票基本資料

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/admin/refresh/stocks?market=TWSE"
```

---

### Step 2：刷新 TPEX 股票基本資料

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/admin/refresh/stocks?market=TPEX"
```

---

### Step 3：刷新 TWSE 股利資料

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/admin/refresh/dividends?market=TWSE"
```

---

### Step 4：刷新 TPEX 股利資料

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/admin/refresh/dividends?market=TPEX"
```

---

## API 範例

### 健康檢查

```http
GET /healthz
```

PowerShell：

```powershell
(Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8000/healthz").Content
```

---

### 查詢 TWSE 股票基本資料

```http
GET /api/v1/stocks/2330?market=TWSE
```

PowerShell：

```powershell
(Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8000/api/v1/stocks/2330?market=TWSE").Content
```

---

### 查詢 TPEX 股票基本資料

```http
GET /api/v1/stocks/6488?market=TPEX
```

PowerShell：

```powershell
(Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8000/api/v1/stocks/6488?market=TPEX").Content
```

---

### 不指定 market（系統 fallback）

```http
GET /api/v1/stocks/6488
```

PowerShell：

```powershell
(Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8000/api/v1/stocks/6488").Content
```

---

### 查詢 TWSE 股利資料

```http
GET /api/v1/stocks/2330/dividends?market=TWSE
```

PowerShell：

```powershell
(Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8000/api/v1/stocks/2330/dividends?market=TWSE").Content
```

---

### 查詢 TPEX 股利資料

```http
GET /api/v1/stocks/6488/dividends?market=TPEX
```

PowerShell：

```powershell
(Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8000/api/v1/stocks/6488/dividends?market=TPEX").Content
```

---

### 依年份篩選股利資料

```http
GET /api/v1/stocks/2330/dividends?market=TWSE&year_from=113&year_to=114
```

---

## API 設計說明

### 股票基本資料
```http
GET /api/v1/stocks/{stock_code}
```

支援參數：
- `market=TWSE|TPEX`
- `fetch_remote=true|false`

---

### 股利資料
```http
GET /api/v1/stocks/{stock_code}/dividends
```

支援參數：
- `market=TWSE|TPEX`
- `year_from`
- `year_to`
- `fetch_remote=true|false`

---

### Refresh 股票基本資料
```http
POST /api/v1/admin/refresh/stocks?market=TWSE
POST /api/v1/admin/refresh/stocks?market=TPEX
```

---

### Refresh 股利資料
```http
POST /api/v1/admin/refresh/dividends?market=TWSE
POST /api/v1/admin/refresh/dividends?market=TPEX
```

---

## 錯誤碼設計

常見錯誤碼：

- `STOCK_NOT_FOUND`
- `INVALID_MARKET`
- `INVALID_YEAR_RANGE`
- `MULTIPLE_MARKET_MATCH`

### 例如：市場參數錯誤
```json
{
  "detail": {
    "code": "INVALID_MARKET",
    "message": "market must be TWSE or TPEX"
  }
}
```

### 例如：同代號跨市場歧義
```json
{
  "detail": {
    "code": "MULTIPLE_MARKET_MATCH",
    "message": "stock_code=xxxx exists in multiple markets, please specify ?market=TWSE or ?market=TPEX"
  }
}
```

---

## 測試

### 直接跑 pytest
```powershell
python -m pytest -q
```

### 詳細輸出
```powershell
python -m pytest -v
```

### 目前預期
```text
23 passed, 2 skipped
```

---

## PowerShell 測試腳本

專案內建：

```text
scripts/
├─ run_tests.ps1
├─ run_integration.ps1
├─ smoke_api.ps1
└─ run_all.ps1
```

### 跑單元測試
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_tests.ps1
```

### 跑 API smoke test
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_api.ps1
```

### 一鍵全跑
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_all.ps1
```

---

## 文件

### 測試文件
詳細測試方式請看：

```text
README-TESTING.md
```

### 版本紀錄
版本變更請看：

```text
CHANGELOG.md
```

---

## 目前限制

### 1. `dividend_year` 仍維持民國年
例如：

- `114`
- `113`

目前尚未統一轉成西元年。

---

### 2. `industry` 目前仍為來源代碼
例如：

- `"24"`

尚未做：
- 產業代碼 → 中文產業名稱映射

---

### 3. 目前仍以 SQLite 為主
這是 MVP 設計，未來可擴充到：

- PostgreSQL
- MySQL
- 其他正式 DB

---

### 4. 第三版已正式發布為 v0.3.0
雖然：
- stock / dividend 的雙市場 pytest 已通過
- API 路由已完成

但若要正式對外標成 `v0.3.0`，仍建議補最後一輪人工 smoke 驗證。

---

## 為什麼要自己做，而不是只看網站？

如果你只是要手動看股利排行，第三方網站很方便。  
但這個專案的目標不是單純「看網站」，而是建立你自己的：

- 資料主權
- SQLite 資料庫
- API
- refresh 流程
- 測試能力
- 版本控管
- 後續擴充基礎

也就是說，這個專案的定位不是複製一個網站頁面，而是建立**自己的資料與服務底層**。

---

## Roadmap

### 短期
- 補齊 TPEX 股利人工 smoke 驗證
- 將 `v0.3.0-beta.1` 升為 `v0.3.0`
- 更新 README / TESTING / CHANGELOG 封版內容

### 中期
- 產業代碼轉中文
- `dividend_year` 西元化
- coverage 報告
- CI（GitHub Actions / Azure DevOps）

### 長期
- PostgreSQL
- 排程 refresh
- 前端查詢頁
- 策略 / 選股 / 匯出功能

---

## 建議日常使用方式

### 平常開發
```powershell
python -m pytest -q
```

### 想快速檢查 API
先啟動：

```powershell
uvicorn app.main:app --reload
```

再跑：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_api.ps1
```

### 發版前
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_all.ps1
```

---

## License

目前尚未正式定義。  
若之後要公開 GitHub repo，建議補上：

- MIT
- Apache-2.0
- 或你自己的內部使用聲明

---

## Author / Maintenance

目前為內部開發 / 個人維護型專案。  
若未來公開，建議補：

- 維護者資訊
- 回報 issue 流程
- Release 節奏
