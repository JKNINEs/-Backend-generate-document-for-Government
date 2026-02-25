from pydantic import BaseModel
from typing import Optional

class instructorsModel(BaseModel):
    name:          str
    skill:         Optional[str] = None
    in_card:       Optional[str] = None
    tel:           Optional[str] = None
    address_no:    Optional[str] = None
    moo:           Optional[str] = None
    road:          Optional[str] = None
    sub_distruict: Optional[str] = None  # ⚠️ ชื่อนี้ typo แต่ต้องคงไว้ให้ตรงกับ routes.py
    district:      Optional[str] = None
    province:      Optional[str] = None
    zipcode:       Optional[str] = None