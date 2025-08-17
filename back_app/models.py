# =========================
# 1) models.py (Pydantic)
# =========================
from pydantic import BaseModel, Field, validator
from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Dict, Any

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
    # one chosen variation per selected level3 item
    level3_choices: List[Dict[str, str]] = []  # [{ "item_code": "3.1.1.1", "variant_code": "3.1.1.1.2" }, ...]

    @validator("level1_codes")
    def max3_level1(cls, v):
        if len(v) > 3: raise ValueError("Up to 3 selections in Level 1")
        return v

    @validator("level2_codes")
    def max3_level2(cls, v):
        if len(v) > 3: raise ValueError("Up to 3 selections in Level 2")
        return v


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

IntakeType = Literal[
    "single-select","multi-select","number","time","time_24h","boolean"
]

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