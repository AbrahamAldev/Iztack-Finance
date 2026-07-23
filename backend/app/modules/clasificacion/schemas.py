"""
Iztack-Finance - Classification Schemas
Pydantic models for product classification and savings analysis.
"""
from typing import Dict

from pydantic import BaseModel, Field


class ClassifyProductRequest(BaseModel):
    product_name: str = Field(..., min_length=1, description="Product name to classify")
    price: float = Field(0.0, ge=0, description="Product price in MXN")


class ClassifyProductResponse(BaseModel):
    category: str
    has_warranty: bool
    is_consumable: bool
    is_high_value: bool
    warranty_months: int
    estimated_consumption_days: int | None


class BulkDetectRequest(BaseModel):
    product_name: str = Field(..., min_length=1)
    unit_price: float = Field(..., ge=0)
    bulk_price: float = Field(..., ge=0)
    bulk_quantity: int = Field(..., ge=1)


class SavingsGoalRequest(BaseModel):
    monthly_expenses: Dict[str, float] = Field(..., description="Category -> amount mapping")
    target_savings_percent: float = Field(15.0, ge=0, le=100)
