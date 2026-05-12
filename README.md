# Taiwan Stock App

台股資料查詢與管理工具，支援 **TWSE / TPEX** 雙市場，提供：

- 股票搜尋
- 股利篩選 / 排行
- 個股股利查詢
- Refresh Logs 管理頁
- Scheduler 管理頁

目前架構採用：

- **Backend**：FastAPI + SQLAlchemy + pytest
- **Frontend**：React + Vite + TypeScript + React Router
- **Data Flow**：透過 refresh / scheduler 將資料同步到本地 DB，前端僅查本地 API，不直接向外部資料來源查詢

---

## 功能總覽

### 使用者功能

- **股票搜尋頁**：`/stocks`
  - 依股票代號、公司名稱、公司簡稱搜尋
  - 支援 `TWSE / TPEX` 市場篩選
  - 查詢條件同步到 URL query params

- **股利篩選 / 排行頁**：`/dividends`
  - 支援依市場、年度、現金股利 / 股票股利 / 總股利條件篩選
  - 支援排序、分頁、每頁筆數切換
  - 查詢條件與分頁狀態同步到 URL query params

- **個股股利頁**：`/stocks/:stockCode/dividends`
  - 由股票搜尋頁直接導流
  - 依個股查詢股利資料
  - 支援 `year_from / year_to` 篩選

### 管理功能

- **Refresh Logs 頁**：`/admin/refresh-logs`
  - 查看股票 / 股利 refresh 歷史紀錄
  - 支援依 `job_name / market / status` 篩選
  - 支援簡單分頁

- **Scheduler 頁**：`/admin/scheduler`
  - 查看 scheduler 狀態
  - 查看 scheduler jobs
  - 支援：
    - Pause / Resume 整體 scheduler
    - Pause / Resume 單一 job
    - Run Now 單一 job

---

## 技術架構

### Backend

- FastAPI
- SQLAlchemy
- pytest
- APScheduler（scheduler / jobs / run-now / pause / resume）
- 本地 DB 儲存 stocks / dividends / refresh logs

### Frontend

- React
- Vite
- TypeScript
- React Router
- 以本地 API 為唯一資料來源

### Data Flow

1. 後端透過 refresh API 或 scheduler 同步 TWSE / TPEX 資料到本地 DB
2. 前端查詢 `/api/v1/...` 本地 API
3. 管理頁面查看 refresh logs 與 scheduler 狀態

---

## 後端 API 概覽

### Stock APIs

- `GET /api/v1/stocks/search`
- `GET /api/v1/stocks/{stock_code}`

### Dividend APIs

- `GET /api/v1/dividends/search`
- `GET /api/v1/stocks/{stock_code}/dividends`

### Admin Refresh APIs

- `POST /api/v1/admin/refresh/stocks`
- `POST /api/v1/admin/refresh/dividends`
- `GET /api/v1/admin/refresh/logs`

### Scheduler APIs

- `GET /api/v1/admin/scheduler/status`
- `GET /api/v1/admin/scheduler/jobs`
- `POST /api/v1/admin/scheduler/pause`
- `POST /api/v1/admin/scheduler/resume`
- `POST /api/v1/admin/scheduler/jobs/{job_id}/pause`
- `POST /api/v1/admin/scheduler/jobs/{job_id}/resume`
- `POST /api/v1/admin/scheduler/jobs/{job_id}/run-now`

---

## 前端頁面概覽

### 使用者頁

- `/stocks`
- `/dividends`
- `/stocks/:stockCode/dividends`

### 管理頁

- `/admin/refresh-logs`
- `/admin/scheduler`

---

## 如何啟動後端

### 1. 啟用 Python 虛擬環境

```powershell
.\.venv312\Scripts\Activate.ps1
```

### 2. 安裝依賴（若尚未安裝）

```powershell
pip install -r requirements.txt
```

### 3. 啟動 FastAPI

```powershell
uvicorn app.main:app --reload
```

### 4. 驗證後端

```powershell
(Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8000/healthz").Content
```

預期：

```json
{"status":"ok"}
```

---

## 如何啟動前端

### 1. 進入前端專案資料夾

```powershell
cd "D:\Py_code\Taiwan Stock App\taiwan-stock-frontend"
```

### 2. 安裝依賴

```powershell
npm install
```

### 3. 設定 `.env`

建立 `taiwan-stock-frontend/.env`：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### 4. 啟動前端

```powershell
npm run dev
```

預設網址：

```text
http://localhost:5173/
```

---

## 初始化資料（重要）

前端查詢的是 **本地 DB**，因此第一次使用前，建議先完成初始化 refresh。

### 建議初始化順序

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/admin/refresh/stocks?market=TWSE"
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/admin/refresh/stocks?market=TPEX"
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/admin/refresh/dividends?market=TWSE"
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/admin/refresh/dividends?market=TPEX"
```

### 為什麼要先做？

如果本地 DB 尚未初始化：

- `/stocks` 可能查不到完整股票資料
- `/dividends` 可能查不到完整股利資料
- `/stocks/:stockCode/dividends` 可能只顯示空狀態

---

## 已完成的產品能力

### 資料能力

- TWSE / TPEX 雙市場
- 股票搜尋 API
- 股利篩選 / 排行 API
- 個股股利 API
- `industry_name`
- `dividend_year_ad`

### 維運能力

- 手動 refresh
- refresh logs
- scheduler 狀態 / jobs 查詢
- scheduler control（pause / resume / run-now）

### 前端能力

- React Router
- 使用者頁 + 管理頁
- URL query params 同步
- 股利分頁
- Scheduler 管理頁

---

## 專案結構（摘要）

```text
Taiwan Stock App/
├─ app/                        # FastAPI backend
├─ tests/                      # backend tests
├─ taiwan-stock-frontend/      # React frontend
│  ├─ src/
│  │  ├─ pages/
│  │  ├─ components/
│  │  ├─ services/
│  │  └─ types/
│  └─ .env
└─ README.md
```

---

## 未來規劃

- 股票搜尋頁分頁
- 匯出 CSV / Excel
- Admin 導覽整理
- UI / Layout 美化
- 文件與 release 收斂
