# README-TESTING

本文件整理 Taiwan Stock App 的前後端測試方式、初始化流程、頁面驗證清單，以及常見錯誤排除方式。

---

## 1. 測試前準備

在開始驗證前，請先確認：

### Backend

- 已啟用 Python 虛擬環境
- 已安裝依賴
- FastAPI 可正常啟動
- `/healthz` 可正常回應

建議流程：

```powershell
.\.venv312\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

健康檢查：

```powershell
(Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8000/healthz").Content
```

預期：

```json
{"status":"ok"}
```

### Frontend

- 已進入 `taiwan-stock-frontend`
- 已安裝前端依賴
- `.env` 已設定正確 API base URL
- Vite 可正常啟動

```powershell
cd "D:\Py_code\Taiwan Stock App\taiwan-stock-frontend"
npm install
npm run dev
```

`.env`：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

---

## 2. 後端自動測試

執行 pytest：

```powershell
python -m pytest -q
```

建議在每次修改後端 API、service、repository、scheduler 邏輯後都執行一次。

> 測試基線請以你當下專案最新結果為準，建議在每次穩定後同步更新到文件。

---

## 3. 初始化資料驗證

本專案前端查詢的是 **本地 DB**，因此第一次使用前，必須先將資料 refresh 進本地資料庫。

### 建議初始化順序

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/admin/refresh/stocks?market=TWSE"
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/admin/refresh/stocks?market=TPEX"
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/admin/refresh/dividends?market=TWSE"
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/admin/refresh/dividends?market=TPEX"
```

### 驗證方式

#### 驗證股票搜尋 API

```powershell
(Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8000/api/v1/stocks/search?q=2330").Content
```

#### 驗證股利搜尋 API

```powershell
(Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8000/api/v1/dividends/search?year=114&limit=20").Content
```

#### 驗證個股股利 API

```powershell
(Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8000/api/v1/stocks/2330/dividends?market=TWSE").Content
```

---

## 4. 使用者頁驗證清單

### A. 股票搜尋頁 `/stocks`

建議驗證項目：

#### 驗證 1：代號搜尋

```text
/stocks?q=2330
```

預期：
- 自動帶入 `2330`
- 自動查詢
- 顯示 `2330 台積電`

#### 驗證 2：名稱搜尋

```text
/stocks?q=台積
```

預期：
- 顯示台積電結果

#### 驗證 3：市場搜尋

```text
/stocks?q=環球晶&market=TPEX
```

預期：
- 顯示 `6488 環球晶`
- 市場為 `TPEX`

#### 驗證 4：查看股利導流

在股票卡片上點 `查看股利`。

預期導向：

```text
/stocks/2330/dividends?market=TWSE
```

#### 驗證 5：URL query params 還原

直接貼：

```text
/stocks?q=2330
```

重新整理後應保留查詢條件與結果。

---

### B. 股利篩選頁 `/dividends`

建議驗證項目：

#### 驗證 1：年度篩選

```text
/dividends?year=114&page=1&page_size=20&sort_by=total&sort_dir=desc
```

預期：
- 自動還原年度條件
- 自動查詢
- 顯示 114 年股利資料

#### 驗證 2：市場篩選

```text
/dividends?market=TPEX&page=1&page_size=20&sort_by=total&sort_dir=desc
```

預期：
- 顯示 TPEX 資料

#### 驗證 3：現金股利篩選

```text
/dividends?year=114&cash_min=5&page=1&page_size=20&sort_by=total&sort_dir=desc
```

預期：
- 僅顯示現金股利 >= 5 的資料

#### 驗證 4：分頁

在 `/dividends` 頁按 `下一頁`。

預期：
- URL 的 `page` 會同步變更
- 頁面結果改變

#### 驗證 5：每頁筆數

切換 `20 / 50 / 100`。

預期：
- `page_size` 會同步到 URL
- `page` 重設為 1

#### 驗證 6：URL query params 還原

直接貼：

```text
/dividends?market=TWSE&year=114&cash_min=5&sort_by=total&sort_dir=desc&page=2&page_size=50
```

重新整理後應保留：
- 篩選條件
- 排序條件
- page
- page_size

---

### C. 個股股利頁 `/stocks/:stockCode/dividends`

#### 驗證 1：自動載入

打開：

```text
/stocks/2330/dividends?market=TWSE
```

預期：
- 自動查出台積電股利資料

#### 驗證 2：年份篩選

在頁面輸入：
- `year_from`
- `year_to`

按 `套用條件`。

預期：
- 重新查詢並顯示篩選後結果

#### 驗證 3：返回按鈕

點 `返回股票搜尋`。

預期：
- 回到 `/stocks`

---

## 5. 管理頁驗證清單

### A. Refresh Logs 頁 `/admin/refresh-logs`

#### 驗證 1：初始載入

預期：
- 進頁面自動載入第一頁 logs

#### 驗證 2：依 job_name 篩選

選：
- `refresh_stocks`
- `refresh_dividends`

預期：
- 表格結果符合條件

#### 驗證 3：依 market 篩選

選：
- `TWSE`
- `TPEX`

預期：
- 表格結果符合條件

#### 驗證 4：依 status 篩選

選：
- `success`
- `failed`
- `running`

預期：
- 表格結果符合條件

#### 驗證 5：簡單分頁

按：
- `上一頁`
- `下一頁`

預期：
- offset 對應改變
- logs 列表更新

---

### B. Scheduler 頁 `/admin/scheduler`

#### 驗證 1：狀態卡片

預期頁面可看到：
- Enabled
- Running
- Job Count

#### 驗證 2：jobs 列表

預期：
- 顯示 scheduler jobs 卡片
- 可看到：
  - job id
  - name
  - args
  - trigger
  - next run time
  - paused / running

#### 驗證 3：整體 pause / resume

按：
- `Pause Scheduler`
- `Resume Scheduler`

預期：
- 狀態卡片同步更新
- 顯示 success / error banner

#### 驗證 4：job pause / resume

在單一 job 卡片上按：
- `Pause`
- `Resume`

預期：
- card 狀態更新
- 顯示 success / error banner

#### 驗證 5：run-now

在單一 job 卡片上按：
- `Run Now`

預期：
- 顯示成功訊息
- scheduler data 重新刷新

---

## 6. Query Params 還原驗證

這一章專門驗證 URL state 是否可正確同步與還原。

### `/stocks`

驗證：

```text
/stocks?q=2330&market=TWSE
```

檢查：
- 搜尋框是否自動還原
- 市場是否自動還原
- 是否自動查詢

### `/dividends`

驗證：

```text
/dividends?market=TWSE&year=114&cash_min=5&sort_by=total&sort_dir=desc&page=2&page_size=50
```

檢查：
- 表單條件是否還原
- 是否自動查詢
- page / page_size 是否還原
- 重新整理後是否仍一致

---

## 7. 常見錯誤與排除

### 1. Node / npm 找不到

現象：

```text
node : 無法辨識 'node'
npm : 無法辨識 'npm'
```

處理：
- 安裝 Node.js LTS
- 重新開 PowerShell
- 確認 `node -v` / `npm -v`

---

### 2. npm SSL / issuer certificate 問題

現象：

```text
UNABLE_TO_GET_ISSUER_CERT_LOCALLY
```

常見於公司網路 / VPN / Proxy 環境。

處理：
- 向 IT 取得公司 CA 憑證並設定 `cafile`
- 或暫時用 `strict-ssl=false` 進行安裝（僅作短暫 workaround）

---

### 3. `npm run dev` 在錯誤資料夾執行

現象：

```text
Could not read package.json
```

處理：
- 進入前端資料夾：

```powershell
cd "D:\Py_code\Taiwan Stock App\taiwan-stock-frontend"
```

---

### 4. CORS 問題

現象：

```text
has been blocked by CORS policy
```

處理：
- FastAPI 加入 `CORSMiddleware`
- 最小允許：
  - `http://localhost:5173`

---

### 5. Vite parse error / import 黏壞

現象：
- `Expected from`
- `Expected }`
- `Identifier already declared`

通常原因：
- 貼檔時 import 被黏在一起
- 檔案內容覆蓋到別的檔案

處理：
- 不要局部 patch
- 直接整份覆蓋成乾淨版本

---

### 6. `App.tsx` 或 page 檔不存在

現象：

```text
Failed to resolve import "./App"
```

處理：
- 檢查 `src/App.tsx` 是否存在
- 檢查 page / component / service 是否放對資料夾

---

### 7. DB 未 refresh 導致查無資料

現象：
- 前端頁可正常 render
- 但查不到完整股票 / 股利

處理：
- 先跑 4 次初始化 refresh

---

## 8. 前後端同步驗證順序（建議）

建議每次大改完後，照下面順序走一遍：

### Step 1：啟動後端

```powershell
uvicorn app.main:app --reload
```

### Step 2：啟動前端

```powershell
cd "D:\Py_code\Taiwan Stock App\taiwan-stock-frontend"
npm run dev
```

### Step 3：初始化資料

- TWSE stocks
- TPEX stocks
- TWSE dividends
- TPEX dividends

### Step 4：驗證 `/stocks`

### Step 5：驗證 `/dividends`

### Step 6：驗證 `/stocks/:stockCode/dividends`

### Step 7：驗證 `/admin/refresh-logs`

### Step 8：驗證 `/admin/scheduler`

---

## 9. 建議維護方式

- 每次新增頁面後，補上對應手動驗證項目
- 每次後端新增 API 或改 response schema，更新本文件
- 每次重大功能穩定後，同步更新 `README.md` 與 `CHANGELOG.md`
