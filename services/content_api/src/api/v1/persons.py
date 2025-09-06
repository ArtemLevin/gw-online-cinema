from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from ..v1.utils import get_services
from ...models.models import Person

router = APIRouter()

@router.get("/{person_uuid}", response_model=Person)
async def get_person(person_uuid: UUID, services=Depends(get_services)):
    person = await services["person"].get_by_uuid(person_uuid)
    if not person:
        raise HTTPException(status_code=404, detail="Персона не найдена")
    return person

@router.get("/", response_model=list[Person])
async def get_all_persons(services=Depends(get_services)):
    persons = await services["person"].get_all_persons()
    return persons
