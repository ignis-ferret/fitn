# app/models.py
from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field, validator

# --- Rewards/Pick Model Tree ---
class Variation(BaseModel):
    code: str
    example: str

class Level3Item(BaseModel):
    code: str
    title: str
    variations: List[Variation]

class Level2Category(BaseModel):
    code: str
    title: str
    items: List[Level3Item] = []

class Level1Group(BaseModel):
    code: str
    title: str
    categories: List[Level2Category] = []

class RewardTree(BaseModel):
    groups: List[Level1Group] = []

class SelectionPayload(BaseModel):
    user_id: str = Field(..., min_length=1)
    level1_codes: List[str] = []
    level2_codes: List[str] = []
    # [{ "item_code": "...", "variant_code": "..." }]
    level3_choices: List[Dict[str, str]] = []

    @validator("level1_codes")
    def max3_level1(cls, v):
        if len(v) > 3:
            raise ValueError("Up to 3 selections in Level 1")
        return v

    @validator("level2_codes")
    def max3_level2(cls, v):
        if len(v) > 3:
            raise ValueError("Up to 3 selections in Level 2")
        return v

# --- Intake Model ---
class IntakeOption(BaseModel):
    id: str
    text: str
    value: Optional[str] = None

class IntakeRange(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None

class IntakeConditional(BaseModel):
    variable_name: str
    value: str

IntakeType = Literal["single-select","multi-select","number","time","time_24h","boolean"]

class IntakeQuestion(BaseModel):
    id: str
    section: str
    variable_name: str
    text: str
    type: IntakeType
    options: Optional[List[IntakeOption]] = None
    range: Optional[IntakeRange] = None
    optional: Optional[bool] = None
    conditional_on: Optional[IntakeConditional] = None
    max_selections: Optional[int] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
