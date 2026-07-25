# TaskHub API

Sample FastAPI project for learning API development.

## Setup

```bash
python3 -m venv .runvenv
.runvenv/bin/pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set `SECRET_KEY` to a long random string.

## Run

```bash
.runvenv/bin/uvicorn app.main:app --reload
```

Open:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Redis Cache

The app can cache `GET /api/v1/projects/{project_id}/tasks`.

If Redis is running, the app uses `REDIS_URL`.
If Redis is not running, the app still works with local memory cache.

```bash
redis-server
```

## Check Code

```bash
.runvenv/bin/python -m py_compile app/*.py
.runvenv/bin/ruff check app
.runvenv/bin/mypy app
```
