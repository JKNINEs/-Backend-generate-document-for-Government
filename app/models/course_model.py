from pydantic import BaseModel
from typing import Optional

class CourseModel(BaseModel):
    code: str
    name: str
    hours: int
    course_type: str
    sub_type: Optional[str] = None
