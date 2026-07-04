# 培养方案数据库项目

把本科培养方案数据整理后存进 PostgreSQL，用 FastAPI 做课程、专业、培养方案的查询和两校对比。目前覆盖西南财经大学和上海财经大学的部分专业。

## 目录结构

- `src/app/`：FastAPI 应用源码，路由、查询逻辑、数据模型和自然语言解析。
- `sql/`：数据库建表、暂存表、数据导入和典型查询 SQL。
- `scripts/load_sample_data.py`：样例 CSV 数据导入脚本。
- `data/samples/`：整理后、可直接导入的 CSV 数据。
- `docs/`：Schema 设计、演示用例、ER 图和验收截图。

## 环境准备

需要先安装：

- Python 3.10 或以上版本
- uv
- PostgreSQL

同步 Python 依赖：

```bash
uv sync
```

## 数据库配置

项目通过 `DATABASE_URL` 环境变量读取 PostgreSQL 连接信息。请根据本地数据库用户名、密码和数据库名自行设置。

Git Bash：

```bash
export DATABASE_URL="postgresql://用户名:密码@localhost:5432/curriculum"
```

Windows PowerShell：

```powershell
$env:DATABASE_URL="postgresql://用户名:密码@localhost:5432/curriculum"
```

如果本地还没有数据库，可以先创建数据库：

```bash
createdb curriculum
```

或者使用 psql：

```bash
psql -U postgres -c "CREATE DATABASE curriculum;"
```

## 数据导入

CSV 字段统一为：

```csv
school,college,major,entry_year,course_name,course_type,credits,hours,semester,total_credits
```

空数据库首次导入，执行建表、暂存和加载脚本：

```bash
uv run python scripts/load_sample_data.py --init-schema --reset-data --reset-staging
```

表已存在、只需重新导入 `data/samples/` 下的 CSV：

```bash
uv run python scripts/load_sample_data.py --reset-data --reset-staging
```

也可以直接用 psql 按顺序执行 SQL：

```bash
psql "$DATABASE_URL" -f sql/01_schema.sql
psql "$DATABASE_URL" -f sql/02_staging.sql
# 用 psql \copy 将 data/samples/*.csv 导入 staging_courses
psql "$DATABASE_URL" -f sql/03_load_from_staging.sql
```

## 启动服务

```bash
uv run uvicorn app.main:app --reload --app-dir src
```

启动后可访问：

- `http://127.0.0.1:8000/`：Web 查询页面。
- `http://127.0.0.1:8000/docs`：接口文档页面，可直接在浏览器中调用各接口。
- `GET /health`：健康检查。

## 子模块 A：单校培养方案查询

- `GET /majors/{major_name}/courses`：专业课程列表。
- `GET /majors/{major_name}/required-courses`：专业必修课。
- `GET /majors/{major_name}/summary`：专业总学分等概览。
- `GET /courses/search?keyword=数学`：课程名关键词模糊搜索。
- `GET /courses/{course_name}`：课程学分学时详情。
- `GET /courses/{course_name}/majors`：课程开设专业。
- `GET /colleges/{college_name}/summary`：学院概览。

常用可选参数：`school_name`、`college_name`、`entry_year`、`limit`、`offset`。

## 子模块 B：跨校对比查询

默认对比西南财经大学与上海财经大学：

- `GET /compare/majors/{major_name}/summary`：同专业总览对比。
- `GET /compare/majors/{major_name}/common-courses`：两校共同课程。
- `GET /compare/majors/{major_name}/school-only-courses`：某校独有课程。
- `GET /compare/courses/{course_name}`：课程跨校开设情况。
- `POST /compare/nl-query`：中文自然语言查询。

自然语言查询将问题映射到白名单 SQL 模板，不执行用户输入的任意 SQL。请求示例：

```json
{"question": "对比两校计算机科学与技术总学分"}
```
