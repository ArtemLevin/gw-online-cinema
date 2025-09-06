from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from ..v1.utils import get_services
from ...models.models import Genre

router = APIRouter()

@router.get("/{genre_uuid}", response_model=Genre)
async def get_genre(genre_uuid: UUID, services=Depends(get_services)):
    genre = await services["genre"].get_by_uuid(genre_uuid)
    if not genre:
        raise HTTPException(status_code=404, detail="Жанр не найден")
    return genre

@router.get("/", response_model=list[Genre])
async def get_all_genres(services=Depends(get_services)):
    genres = await services["genre"].get_all_genres()
    return genres
