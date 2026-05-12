# CHANGELOG

本檔案記錄 Taiwan Stock App 的重要版本變更。

---

## v0.4.1

### 主題
Dividend Search / Filter API 與前端股利頁強化

### Added
- 新增 `GET /api/v1/dividends/search`
- 支援依 `market / year / cash_min / stock_min / total_min` 篩選
- 支援依 `cash / stock / total / year / code` 排序
- 回傳 `industry_name`
- 回傳 `dividend_year_ad`
- 新增 `total_count`，支援真正分頁

### Frontend
- 新增 `/dividends` 頁
- 支援股利篩選 / 排行
- 支援分頁與每頁筆數切換
- 支援 URL query params 同步：
  - `market`
  - `year`
  - `cash_min`
  - `stock_min`
  - `total_min`
  - `sort_by`
  - `sort_dir`
  - `page`
  - `page_size`

---

## v0.4.0

### 主題
Stock Search API

### Added
- 新增 `GET /api/v1/stocks/search`
- 支援：
  - 股票代號 prefix 搜尋
  - 公司名稱搜尋
  - 公司簡稱搜尋
  - `market` 篩選
- 搜尋結果回傳摘要型股票資訊：
  - `stock_code`
  - `market`
  - `company_name`
  - `company_short_name`
  - `industry`
  - `industry_name`
  - `listing_date`

### Frontend
- 新增 `/stocks` 頁
- 支援股票搜尋
- 支援 `q / market` 同步到 URL query params
- 股票搜尋結果可導向個股股利頁

---

## v0.3.4

### 主題
Scheduler Control APIs

### Added
- 新增 `POST /api/v1/admin/scheduler/pause`
- 新增 `POST /api/v1/admin/scheduler/resume`
- 新增 `POST /api/v1/admin/scheduler/jobs/{job_id}/pause`
- 新增 `POST /api/v1/admin/scheduler/jobs/{job_id}/resume`
- 新增 `POST /api/v1/admin/scheduler/jobs/{job_id}/run-now`
- scheduler jobs API 新增 `paused` 狀態
- `run-now` 會寫入 `trigger_source = api_manual`

### Frontend
- 新增 `/admin/scheduler` 頁
- 可查看 scheduler 狀態與 jobs 清單
- 可執行 pause / resume / run-now

---

## v0.3.3

### 主題
Scheduler Foundation

### Added
- 建立 scheduler 啟動 / 關閉流程
- 註冊 scheduler jobs
- 新增 `GET /api/v1/admin/scheduler/status`
- 新增 `GET /api/v1/admin/scheduler/jobs`
- 支援 scheduler startup / shutdown

---

## v0.3.2

### 主題
Refresh Job Logs

### Added
- 新增 refresh job log table
- 記錄 refresh jobs 執行結果
- 新增 `GET /api/v1/admin/refresh/logs`
- 支援依 `job_name / market / status` 篩選

### Frontend
- 新增 `/admin/refresh-logs` 頁
- 顯示 refresh logs 表格
- 支援簡單分頁

---

## v0.3.1

### 主題
資料品質與 CI 基礎

### Added
- 新增 `industry_name`
- 新增 `dividend_year_ad`
- 新增 GitHub Actions 基本 CI 流程

---

## Frontend MVP Milestone

### 使用者頁
- `/stocks`
- `/dividends`
- `/stocks/:stockCode/dividends`

### 管理頁
- `/admin/refresh-logs`
- `/admin/scheduler`

### Frontend Capabilities
- React + Vite + TypeScript
- React Router
- 使用者頁 / 管理頁骨架完成
- URL query params 同步
- 股利分頁
- 個股股利導流

---

## Notes

- 前端資料來源為本地 API，不直接查外部資料源
- 第一次使用前，需先透過 refresh APIs 初始化本地 DB
