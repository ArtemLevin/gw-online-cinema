from .base_service import BaseService

class PersonService(BaseService):
    async def get_all_persons(self) -> list[dict]:
        return await self.get_all()
