"""
Iztack-Finance - Classification Routes
API endpoints for product classification, warranty detection, and savings analysis.
"""
from datetime import date

from fastapi import APIRouter

from app.modules.clasificacion.schemas import (
    BulkDetectRequest,
    ClassifyProductRequest,
    ClassifyProductResponse,
    SavingsGoalRequest,
)
from app.modules.clasificacion.service import ClassificationService

router = APIRouter(prefix="/api/clasificacion", tags=["Clasificación"])


@router.post("/classify", response_model=ClassifyProductResponse)
async def classify_product(payload: ClassifyProductRequest):
    """Classify a product and determine warranty/consumption attributes."""
    result = ClassificationService.classify_product(payload.product_name, payload.price)
    warranty_months = ClassificationService.get_warranty_period(
        result["category"], payload.price
    )
    consumption_days = ClassificationService.estimate_consumption_cycle(
        payload.product_name, result["category"]
    )
    return {
        "category": result["category"],
        "has_warranty": result["has_warranty"],
        "is_consumable": result["is_consumable"],
        "is_high_value": result["is_high_value"],
        "warranty_months": warranty_months,
        "estimated_consumption_days": consumption_days,
    }


@router.post("/bulk-detect")
async def detect_bulk_savings(payload: BulkDetectRequest):
    """Detect whether buying in bulk is cheaper than the current unit purchase."""
    return ClassificationService.detect_money_leak(
        payload.product_name,
        payload.unit_price,
        payload.bulk_price,
        payload.bulk_quantity,
    )


@router.post("/savings-goal")
async def calculate_savings_goal(payload: SavingsGoalRequest):
    """Calculate savings goals based on monthly expenses by category."""
    return ClassificationService.calculate_savings_goal(
        payload.monthly_expenses,
        payload.target_savings_percent,
    )


@router.get("/ticket-expired")
async def check_ticket_expired(purchase_date: date, max_days: int = 60):
    """Check if a ticket is still eligible for CFDI invoicing."""
    is_expired, days_remaining = ClassificationService.check_expired_ticket(
        purchase_date, max_days
    )
    return {
        "is_expired": is_expired,
        "days_remaining": days_remaining,
        "max_days": max_days,
    }
