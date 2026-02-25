from pydantic import BaseModel
from typing import Optional

class locationsModel(BaseModel):
    name: str
    address_no:   Optional[str] = None
    sub_district: Optional[str] = None
    district:     Optional[str] = None
    province:     Optional[str] = None
    zipcode:      Optional[str] = None
    
