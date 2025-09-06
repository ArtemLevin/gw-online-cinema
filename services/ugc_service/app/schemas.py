from pydantic import BaseModel, Field
from datetime import datetime

class UserEvent(BaseModel):
    user_id: str
    movie_id: str
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: dict | None = None
