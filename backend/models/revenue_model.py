from pydantic import BaseModel, Field


class RevenueModel(BaseModel):
    # Limit Price between 1 and 75
    Price: float = Field(..., ge=1, le=75, description="Price must be between 1 and 75")
    # Limit Day between 1 and 31
    Day: float = Field(..., ge=1, le=31, description="Day must be between 1 and 31")
    # Category
    Category: str = Field("Vitamin", description="Product category (e.g., 'Vitamins', 'Herbs', 'Omega')")
    # Location
    Location: str = Field("USA", description="Location of product (US, UK...)")
    # Platform
    Platform: str = Field("Amazon", description="Where the product is sold (Amazon, Wallmart...)")