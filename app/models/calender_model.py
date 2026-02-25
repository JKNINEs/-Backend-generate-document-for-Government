from pydantic import BaseModel
from typing import Optional

class EventModel(BaseModel):
    title: str
    room_name : str
    start_datetime: str
    end_datetime: str
    status: str = "CONFIRMED"
    created_by: Optional[int] = None
    note: Optional[str] = None






















































