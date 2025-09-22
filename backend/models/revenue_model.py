from pydantic import BaseModel, Field


class RevenueModel(BaseModel):
    # Limit Price between 1 and 75
    Price: float = Field(..., ge=1, le=75, description="Price must be between 1 and 75")
    # Limita Day between 1 and 31
    Day: float = Field(..., ge=1, le=31, description="Day must be between 1 and 31")