from pydantic import BaseModel
from typing import List, Optional

class ApplicantBaseModel(BaseModel):
    name: str
    gender: str
    result: Optional[str] = None

class BulkApplicantCreateModel(BaseModel):
    batch_code: str  # 🔥 เปลี่ยนจาก training_batch_id เป็น batch_code
    applicants: List[ApplicantBaseModel]

class BulkUpdateResultModel(BaseModel):
    ids: List[int]
    result: str