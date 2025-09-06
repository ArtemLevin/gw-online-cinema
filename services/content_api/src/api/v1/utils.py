from fastapi import Depends
from ...db.elastic import get_elastic
from ...db.redis_client import get_redis
from ...services.film_service import FilmService
from ...services.genre_service import GenreService
from ...services.person_service import PersonService

async def get_services(es=Depends(get_elastic), redis=Depends(get_redis)):
    return {
        "film": FilmService(es, redis, "films"),
        "genre": GenreService(es, redis, "genres"),
        "person": PersonService(es, redis, "persons"),
    }
