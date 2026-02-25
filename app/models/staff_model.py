from pydantic import BaseModel
from typing import Optional

class staffModel(BaseModel):
    name: str
    position: str
    work_group: str
    job_desc: Optional[str] = None
    tel: Optional[str] = None

    