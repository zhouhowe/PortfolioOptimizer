from pydantic import BaseModel
from typing import Dict, Any, Optional

class StrategyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: Dict[str, Any]

class StrategyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    parameters: Dict[str, Any]
    created_at: str
