"""
Sistema Financiero - OCR Schemas
Pydantic models for OCR request/response data.
"""
from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class OCRProduct(BaseModel):
    """A single product extracted from a ticket."""
    name: str = Field(..., description="Product name")
    brand: Optional[str] = Field(None, description="Brand name if detected")
    quantity: float = Field(1.0, description="Quantity purchased")
    unit: str = Field("pza", description="Unit of measure (pza, kg, lt, etc.)")
    unit_price: Optional[float] = Field(None, description="Price per unit")
    total_price: float = Field(..., description="Total price for this line")
    discount: Optional[float] = Field(None, description="Discount applied")
    sku: Optional[str] = Field(None, description="Product SKU if visible")
    category: Optional[str] = Field(None, description="Detected product category")
    has_warranty: bool = Field(False, description="Whether this product has warranty")
    warranty_info: Optional[str] = Field(None, description="Warranty details if available")


class OCRTicketData(BaseModel):
    """Complete ticket data extracted via OCR."""
    # Store info
    store_name: str = Field(..., description="Store or business name")
    store_category: Optional[str] = Field(None, description="Detected store category")

    # Receipt metadata
    receipt_number: Optional[str] = Field(None, description="Receipt/folio number")
    purchase_date: date = Field(..., description="Date of purchase")
    purchase_time: Optional[str] = Field(None, description="Time of purchase (HH:MM)")

    # Financial data
    subtotal: Optional[float] = Field(None, description="Subtotal before taxes")
    taxes: Optional[float] = Field(None, description="Tax amount (IVA)")
    total_amount: float = Field(..., description="Total amount paid")
    payment_method: Optional[str] = Field(None, description="Payment method (cash, card, etc.)")
    currency: str = Field("MXN", description="Currency code")

    # Products
    products: List[OCRProduct] = Field(default_factory=list, description="List of purchased products")

    # Raw OCR
    raw_text: str = Field("", description="Raw OCR text output")
    confidence: float = Field(0.0, description="OCR confidence score (0-1)")

    # Classification
    has_warranty_items: bool = Field(False, description="Whether any product has warranty")
    expense_type: Optional[str] = Field(None, description="Detected expense type")

    class Config:
        json_schema_extra = {
            "example": {
                "store_name": "Liverpool",
                "store_category": "liverpool",
                "receipt_number": "T123456",
                "purchase_date": "2026-06-15",
                "purchase_time": "14:30",
                "subtotal": 1890.50,
                "taxes": 302.48,
                "total_amount": 2350.00,
                "payment_method": "credit_card",
                "currency": "MXN",
                "products": [
                    {
                        "name": "Cafetera Automática",
                        "brand": "Krups",
                        "quantity": 1,
                        "unit": "pza",
                        "unit_price": 1299.00,
                        "total_price": 1299.00,
                        "category": "electronicos"
                    },
                    {
                        "name": "Camisa",
                        "brand": "Lacoste",
                        "quantity": 1,
                        "unit": "pza",
                        "unit_price": 851.00,
                        "total_price": 851.00,
                        "category": "ropa"
                    }
                ],
                "raw_text": "...",
                "confidence": 0.95,
                "has_warranty_items": True,
                "expense_type": "necesidad"
            }
        }


class OCRRequest(BaseModel):
    """OCR processing request."""
    image_base64: Optional[str] = Field(None, description="Base64 encoded image")
    image_url: Optional[str] = Field(None, description="URL of the image to process")
    chat_id: Optional[str] = Field(None, description="Chat ID for sending notifications")
    source_channel: str = Field("api", description="Source: telegram, whatsapp, api")


class OCRResponse(BaseModel):
    """OCR processing response."""
    success: bool = Field(..., description="Whether OCR was successful")
    ticket_id: Optional[str] = Field(None, description="Created ticket ID in database")
    data: Optional[OCRTicketData] = Field(None, description="Extracted ticket data")
    error: Optional[str] = Field(None, description="Error message if failed")
    processing_time_ms: int = Field(0, description="Processing time in milliseconds")
