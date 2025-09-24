from pydantic import BaseModel


# Define the data model for the discount prediction endpoint.
# This ensures data integrity and provides clear documentation.
class DiscountPayload(BaseModel):
    product_name: str
    category: str
    price: float
    units_sold: int
    location: str
    platform: str

class DiscountPredictionResult(BaseModel):
    predicted_discount: float
