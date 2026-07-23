"""
Iztack-Finance - Ticket Repository
Persists OCR results into Ticket and Product records, applying
classification and warranty rules.
"""
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Product, Ticket
from app.modules.clasificacion.service import ClassificationService
from app.modules.garantias.service import WarrantyService
from app.modules.ocr.schemas import OCRProduct, OCRTicketData
from app.modules.shopping_list.service import ShoppingListService

logger = logging.getLogger(__name__)


class TicketRepository:
    """Repository for persisting tickets and products from OCR data."""

    @staticmethod
    def _enrich_product(ocr_product: OCRProduct, purchase_date) -> dict:
        """Apply classification and warranty rules to an OCR product."""
        # Use OCR category as primary, fallback to keyword classification
        category = ocr_product.category or "otros"
        if not category or category.lower() == "otros":
            classification = ClassificationService.classify_product(
                product_name=ocr_product.name,
                price=ocr_product.total_price or 0,
            )
            category = classification["category"]
            has_warranty = classification["has_warranty"]
            is_consumable = classification["is_consumable"]
            is_high_value = classification["is_high_value"]
        else:
            classification = ClassificationService.classify_product(
                product_name=ocr_product.name,
                price=ocr_product.total_price or 0,
            )
            has_warranty = classification["has_warranty"]
            is_consumable = classification["is_consumable"]
            is_high_value = classification["is_high_value"]

        # Override warranty decision with WarrantyService rules
        warranty_status = WarrantyService.get_warranty_status(
            purchase_date=purchase_date,
            category=category,
            price=ocr_product.total_price or 0,
        )

        warranty_months = None
        warranty_end_date = None
        if warranty_status.get("has_warranty"):
            has_warranty = True
            warranty_months = WarrantyService.get_warranty_months(
                category=category,
                price=ocr_product.total_price or 0,
            )
            warranty_end_date = warranty_status.get("end_date")

        # Estimate consumption cycle for consumables
        consumption_cycle_days = ClassificationService.estimate_consumption_cycle(
            product_name=ocr_product.name,
            category=category,
        )

        return {
            "name": ocr_product.name,
            "brand": ocr_product.brand,
            "quantity": ocr_product.quantity or 1.0,
            "unit": ocr_product.unit or "pza",
            "unit_price": ocr_product.unit_price,
            "total_price": ocr_product.total_price or 0,
            "discount": ocr_product.discount,
            "sku": ocr_product.sku,
            "category": category,
            "expense_type": None,
            "has_warranty": has_warranty,
            "warranty_months": warranty_months,
            "warranty_end_date": warranty_end_date,
            "consumption_cycle_days": consumption_cycle_days,
            "is_consumable": is_consumable,
            "is_high_value": is_high_value,
        }

    @classmethod
    async def save_ocr_result(
        cls,
        db: AsyncSession,
        ocr_data: OCRTicketData,
        user_id: str,
        raw_image_url: Optional[str] = None,
        processed_image_url: Optional[str] = None,
    ) -> Ticket:
        """
        Persist OCR data as a Ticket with its Products.

        Args:
            db: Async SQLAlchemy session.
            ocr_data: Validated OCR output.
            user_id: ID of the ticket owner.
            raw_image_url: Optional URL/path to the original image.
            processed_image_url: Optional URL/path to the preprocessed image.

        Returns:
            The persisted Ticket instance.
        """
        ticket = Ticket(
            user_id=user_id,
            store_name=ocr_data.store_name,
            store_category=ocr_data.store_category,
            receipt_number=ocr_data.receipt_number,
            purchase_date=ocr_data.purchase_date,
            purchase_time=ocr_data.purchase_time,
            total_amount=ocr_data.total_amount or 0,
            subtotal=ocr_data.subtotal,
            taxes=ocr_data.taxes,
            payment_method=ocr_data.payment_method,
            currency=ocr_data.currency or "MXN",
            ocr_raw_text=ocr_data.raw_text,
            ocr_confidence=ocr_data.confidence,
            original_image_url=raw_image_url,
            processed_image_url=processed_image_url,
            status="ocr_completed",
            invoice_status="pending",
        )

        has_warranty_items = False
        for ocr_product in ocr_data.products or []:
            enriched = cls._enrich_product(ocr_product, ocr_data.purchase_date)
            product = Product(**enriched)
            if product.has_warranty:
                has_warranty_items = True
            ticket.products.append(product)

        ticket.has_warranty_items = has_warranty_items or ocr_data.has_warranty_items

        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)
        logger.info(f"Ticket {ticket.id} saved for user {user_id} with {len(ticket.products)} products")

        # Update consumption cycles for smart shopping list
        try:
            shopping_service = ShoppingListService(db)
            await shopping_service.update_consumption_cycles(user_id, ticket)
        except Exception as exc:
            logger.warning(f"Could not update consumption cycles for ticket {ticket.id}: {exc}")

        return ticket
