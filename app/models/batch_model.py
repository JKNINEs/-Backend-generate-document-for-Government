from pydantic import BaseModel, field_validator
from datetime import date
from typing import Optional

class BatchCreateModel(BaseModel):
    batch_code: str
    request_doc_no: Optional[str] = None
    request_date: Optional[date] = None
    system_code: Optional[str] = None
    activity_id: Optional[int] = None
    course_id: Optional[int] = None
    location_id: Optional[int] = None
    instructor_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    training_dates_text: Optional[str] = None
    borrow_date: Optional[date] = None
    training_time: Optional[str] = None
    duration_days: Optional[int] = None
    target_group: Optional[str] = None
    budget_speaker: float = 0.0
    budget_material: float = 0.0
    budget_food: float = 0.0
    budget_snack: float = 0.0
    controller_id: Optional[int] = None
    coordinator_1_id: Optional[int] = None
    coordinator_2_id: Optional[int] = None
    coordinator_3_id: Optional[int] = None
    borrow_staff_id: Optional[int] = None
    cert_announce_date: Optional[date] = None
    number_of_snacks: int = 0

    # ✅ เพิ่มแค่นี้ — แปลง 0 → None อัตโนมัติ
    @field_validator('activity_id', 'course_id', 'location_id', 'instructor_id',
                     'controller_id', 'coordinator_1_id', 'coordinator_2_id',
                     'coordinator_3_id', 'borrow_staff_id', mode='before')
    @classmethod
    def zero_to_none(cls, v):
        if v == 0:
            return None
        return v