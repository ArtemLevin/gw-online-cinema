from .base_service import BaseService

class GenreService(BaseService):
    async def get_all_genres(self) -> list[dict]:
        return await self.get_all()
