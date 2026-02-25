from pydantic import BaseModel
from typing import Optional

class ActivityModel(BaseModel):
    activity_name: str
    fiscal_year: str
    kind_of_fiscal: str
    activity: str
    expenses: str
    sub_activity_name: Optional[str] = None
    plan_id: int
    project_id: int
    target_goal: int = 0

class MasterData(BaseModel):
    name: str