import os
import httpx

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse")
CLICKHOUSE_HTTP_PORT = int(os.getenv("CLICKHOUSE_HTTP_PORT", "8123"))
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "")

def _base_url() -> str:
    return f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_HTTP_PORT}"

async def ensure_schema():
    # Create simple table (no partitions, for demo robustness)
    create_sql = '''
    CREATE TABLE IF NOT EXISTS default.user_events
    (
        user_id String,
        movie_id String,
        event_type String,
        timestamp DateTime,
        payload String
    )
    ENGINE = MergeTree
    ORDER BY (timestamp, user_id)
    '''
    async with httpx.AsyncClient() as client:
        r = await client.post(_base_url(), params={"query": create_sql}, auth=(CLICKHOUSE_USER, CLICKHOUSE_PASSWORD))
        r.raise_for_status()

async def insert_event(e: dict):
    payload = e.get("payload")
    payload_str = "" if payload is None else __import__("json").dumps(payload, ensure_ascii=False)
    values = f"('{e['user_id']}', '{e['movie_id']}', '{e['event_type']}', toDateTime('{e['timestamp'].replace(microsecond=0).isoformat()}'), '{payload_str.replace("'", "''")}')"
    sql = f"INSERT INTO default.user_events (user_id, movie_id, event_type, timestamp, payload) VALUES {values}"
    async with httpx.AsyncClient() as client:
        r = await client.post(_base_url(), params={"query": sql}, auth=(CLICKHOUSE_USER, CLICKHOUSE_PASSWORD))
        r.raise_for_status()

async def recent_events(limit: int = 50) -> list[dict]:
    sql = f"SELECT user_id, movie_id, event_type, toString(timestamp) as timestamp, payload FROM default.user_events ORDER BY timestamp DESC LIMIT {limit}"
    async with httpx.AsyncClient() as client:
        r = await client.post(_base_url(), params={"query": sql, "default_format": "JSON"}, auth=(CLICKHOUSE_USER, CLICKHOUSE_PASSWORD))
        r.raise_for_status()
        data = r.json()
        # ClickHouse JSON format: {"meta":[...], "data":[{...}], ...}
        return data.get("data", [])
