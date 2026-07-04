from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .routers import compare, courses, majors

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="培养方案数据库系统",
    description="基于 PostgreSQL 与 FastAPI 的培养方案查询和跨校对比系统",
    version="0.3.0",
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

templates = Jinja2Templates(directory=BASE_DIR / "templates")
app.include_router(majors.router)
app.include_router(courses.router)
app.include_router(compare.router)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
    )


@app.get("/health")
def health():
    return {"ok": True}
