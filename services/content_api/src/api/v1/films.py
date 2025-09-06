from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from ..v1.utils import get_services
from ...models.models import Film

router = APIRouter()

@router.get("/{film_uuid}", response_model=Film)
async def get_film(film_uuid: UUID, services=Depends(get_services)):
    film = await services["film"].get_by_uuid(film_uuid)
    if not film:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    return film

@router.get("/", response_model=list[Film])
async def get_all_films(services=Depends(get_services)):
    films = await services["film"].get_all_films()
    return films
