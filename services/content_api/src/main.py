import logging
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis
from .api.v1 import films, genres, persons
from .core import config
from .db import elastic, redis_client

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url='/api/content/openapi',
    openapi_url='/api/content/openapi.json',
    default_response_class=ORJSONResponse,
)

@app.on_event('startup')
async def startup():
    redis_client.redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    elastic.es = AsyncElasticsearch(hosts=[f'http://{config.ELASTIC_HOST}:{config.ELASTIC_PORT}'])
    try:
        await redis_client.redis.ping()
    except Exception as e:
        logger.warning(f"Redis ping failed: {e}")
    try:
        await elastic.es.ping()
    except Exception as e:
        logger.warning(f"Elasticsearch ping failed: {e}")

@app.on_event('shutdown')
async def shutdown():
    if redis_client.redis:
        await redis_client.redis.close()
    if elastic.es:
        await elastic.es.close()

@app.get("/health")
async def health():
    return {"status": "OK"}

app.include_router(films.router, prefix="/api/content/films", tags=["films"])
app.include_router(genres.router, prefix="/api/content/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/content/persons", tags=["persons"])
