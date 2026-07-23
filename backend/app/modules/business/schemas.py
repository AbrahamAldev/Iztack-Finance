"""
Iztack-Finance - Business Schemas
Pydantic models for family business CRUD.
"""
from pydantic import BaseModel, Field


class BusinessCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field("", max_length=1000)
    currency: str = Field("MXN", max_length=10)


class BusinessUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    currency: str | None = Field(None, max_length=10)
