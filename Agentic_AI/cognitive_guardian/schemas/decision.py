from typing import Optional
from pydantic import BaseModel, Field, field_validator


class DecisionInput(BaseModel):
    decision_text: str = Field(..., min_length=10)
    urgency: int = Field(..., ge=1, le=5)
    reversibility: int = Field(..., ge=1, le=5)
    domain: str

    # 🔹 NEW OPTIONAL FIELDS (LLM-inferred)
    inferred_domain: Optional[str] = None
    emotional_intensity: Optional[float] = None   # 0.0 – 1.0
    impulsiveness: Optional[float] = None         # 0.0 – 1.0
    uncertainty: Optional[float] = None           # 0.0 – 1.0

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v):
        allowed = {"career", "finance", "education", "personal", "health"}
        v = v.lower().strip()
        if v not in allowed:
            raise ValueError(f"domain must be one of {allowed}")
        return v
