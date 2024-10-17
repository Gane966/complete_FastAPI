from pydantic import BaseModel
from typing import Optional, List

class mongo_test_responcer(BaseModel):
    message: str
    databases: List[str]