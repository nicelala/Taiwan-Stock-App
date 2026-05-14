from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.db.init_db import init_db
from app.scheduler import start_scheduler, shutdown_scheduler
from fastapi.middleware.cors import CORSMiddleware

class UTF8JSONResponse(JSONResponse):
    media_type = "application/json; charset=utf-8"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 啟動時初始化 DB
    init_db()

    # 啟動 scheduler（若 settings.enable_scheduler=False，會直接略過）
    scheduler = start_scheduler()
    app.state.scheduler = scheduler

    yield

    # 關閉 scheduler
    shutdown_scheduler(getattr(app.state, "scheduler", None))


app = FastAPI(
    title="TW Dividend MVP",
    version="0.2.0",
    description="台股配股/配息查詢最小可執行專案（第二版）",
    default_response_class=UTF8JSONResponse,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "https://taiwan-stock-app-delta.vercel.app",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def force_utf8_json_charset(request: Request, call_next):
    response = await call_next(request)

    content_type = response.headers.get("content-type", "")
    if content_type.startswith("application/json") and "charset=" not in content_type.lower():
        response.headers["content-type"] = "application/json; charset=utf-8"

    return response


app.include_router(router)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}