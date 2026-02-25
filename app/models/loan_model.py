from pydantic import BaseModel
from typing import Optional
from datetime import date

class LoanUpdateModel(BaseModel):
    batch_code: str  # 🔥 เปลี่ยนจาก training_batch_id เป็น batch_code
    contract_no: Optional[str] = None
    clearance_head: int = 0
    loan_date: Optional[date] = None
    clearance_date: Optional[date] = None
    clearance_head_day1: int = 0
    clearance_head_day2: int = 0