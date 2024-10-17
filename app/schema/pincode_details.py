from pydantic import BaseModel
from typing import Optional, List

class pincode_get_response(BaseModel):
    country: str
    state: str
    district: str
    location: str
    pincode: str


class UploadGarbageImage(BaseModel):
    message: str