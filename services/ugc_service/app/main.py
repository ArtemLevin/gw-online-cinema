from fastapi import FastAPI, HTTPException
from .schemas import UserEvent
from . import clickhouse as ch

app = FastAPI(title="UGC Service", docs_url="/api/ugc/openapi", openapi_url="/api/ugc/openapi.json")

@app.on_event("startup")
async def startup():
    try:
        await ch.ensure_schema()
    except Exception as e:
        # Не падаем при первом старте, если ClickHouse ещё прогревается
        print("ensure_schema error:", e)

@app.get("/health")
async def health():
    return {"status": "OK"}

@app.post("/api/ugc/event")
async def post_event(event: UserEvent):
    try:
        await ch.insert_event(event.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"ok": True}

@app.get("/api/ugc/events")
async def list_events(limit: int = 50):
    try:
        records = await ch.recent_events(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"items": records, "limit": limit}
