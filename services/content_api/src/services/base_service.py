from typing import Any, Optional
from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch

class BaseService:
    def __init__(self, es: AsyncElasticsearch, redis: Redis, index_name: str):
        self.es = es
        self.redis = redis
        self.index_name = index_name

    async def get_by_uuid(self, uuid: Any) -> Optional[dict]:
        # try cache
        key = f"{self.index_name}:{uuid}"
        cached = await self.redis.get(key)
        if cached:
            import orjson
            return orjson.loads(cached)
        # fetch from ES
        try:
            doc = await self.es.get(index=self.index_name, id=str(uuid))
            source = doc["_source"]
            await self.redis.set(key, __import__("orjson").dumps(source))
            return source
        except Exception:
            return None

    async def get_all(self, size: int = 50) -> list[dict]:
        try:
            res = await self.es.search(index=self.index_name, query={"match_all": {}}, size=size)
            return [hit["_source"] for hit in res["hits"]["hits"]]
        except Exception:
            return []
