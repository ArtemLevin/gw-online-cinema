from .base_service import BaseService

class FilmService(BaseService):
    async def get_all_films(self) -> list[dict]:
        return await self.get_all()
