"""
Iztack-Finance - OCR Service (OpenRouter GPT-4o-mini Vision)
Extracts store name, date, products, prices, and totals from receipt images.
"""
import base64
import io
import json
import re
from datetime import date, datetime
from typing import Optional, List, Tuple
from PIL import Image, ImageEnhance
from openai import OpenAI

import logging
import os
from app.utils.validators import Validators
from .schemas import OCRTicketData, OCRProduct, OCRResponse

logger = logging.getLogger(__name__)


class OCRService:
    """Service for processing ticket images with OpenRouter GPT-4o-mini Vision."""

    def __init__(self):
        self.api_key = os.environ.get("OPENROUTER_API_KEY", "")
        self.validators = Validators()

    def _get_client(self) -> Optional[OpenAI]:
        if not self.api_key or not self.api_key.startswith("sk-or-v1-"):
            return None
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            default_headers={
                "HTTP-Referer": "https://finance.iztack.com",
                "X-Title": "Iztack-Finance",
            },
        )

    def preprocess_image(self, image_bytes: bytes) -> bytes:
        """Resize and enhance image for better OCR accuracy."""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Enhance contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)

            # Resize if too large
            max_dimension = 1536
            if max(img.size) > max_dimension:
                ratio = max_dimension / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.LANCZOS)

            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85)
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"Image preprocessing error: {e}")
            return image_bytes

    def _build_ocr_prompt(self) -> str:
        return """Eres un experto en leer tickets de compra mexicanos. Analiza la imagen y extrae TODA la información en formato JSON.

IMPORTANTE: Responde **SOLO** con el JSON, sin markdown, sin explicaciones.

El JSON debe tener esta estructura EXACTA:
{
  "store_name": "Nombre exacto de la tienda",
  "store_category": "liverpool|ikea|walmart|amazon|home_depot|oxxo|farmacias_similares|pemex|bp|costco|sams_club|soriana|chedraui|other",
  "receipt_number": "folio o null",
  "purchase_date": "YYYY-MM-DD",
  "subtotal": 123.45,
  "taxes": 12.34,
  "total_amount": 135.79,
  "payment_method": "cash|credit_card|debit_card|transfer|null",
  "currency": "MXN",
  "products": [
    {
      "name": "Nombre del producto",
      "brand": "Marca o null",
      "quantity": 1,
      "unit": "pza|kg|lt|etc",
      "unit_price": 99.90,
      "total_price": 99.90,
      "discount": null,
      "sku": "código o null",
      "has_warranty": false,
      "warranty_info": "info de garantía o null",
      "category": "alimentos|bebidas|hogar|electronicos|muebles|ropa|salud|higiene|limpieza|herramientas|automotriz|combustible|entretenimiento|servicios|otros"
    }
  ],
  "has_warranty_items": false,
  "confidence": 0.95
}

Si no puedes leer algo, pon null. Si es un ticket largo y la tienda no tiene categoría exacta, usa "other"."""

    def extract_from_image(self, image_bytes: bytes) -> OCRResponse:
        """Process an image with OpenRouter GPT-4o-mini and extract structured data."""
        client = self._get_client()
        if not client:
            return OCRResponse(
                success=False,
                error="OpenRouter API Key no configurada. Revisa OPENROUTER_API_KEY en .env",
                raw_text="",
            )

        try:
            processed_bytes = self.preprocess_image(image_bytes)
            b64_image = base64.b64encode(processed_bytes).decode("utf-8")

            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self._build_ocr_prompt()},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{b64_image}",
                                    "detail": "high",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=2048,
                temperature=0.0,
            )

            raw_text = response.choices[0].message.content or ""
            logger.info(f"OCR raw: {raw_text[:200]}")

            # Try to parse JSON from response
            data = self._parse_ocr_response(raw_text)
            if data:
                return OCRResponse(
                    success=True,
                    data=OCRTicketData(**data),
                    raw_text=raw_text,
                )
            else:
                return OCRResponse(
                    success=False,
                    error="No se pudo interpretar el ticket. Intenta con mejor iluminación y sin sombras.",
                    raw_text=raw_text,
                )

        except Exception as e:
            logger.error(f"OCR error: {e}", exc_info=True)
            return OCRResponse(
                success=False,
                error=f"Error al procesar la imagen: {str(e)[:100]}",
                raw_text="",
            )

    def _parse_ocr_response(self, raw_text: str) -> Optional[dict]:
        """Extract JSON from LLM response, handling markdown code blocks."""
        # Try to find JSON in code blocks first
        code_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", raw_text, re.DOTALL)
        if code_match:
            json_str = code_match.group(1).strip()
        else:
            # Try to find JSON object directly
            json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                return None

        try:
            data = json.loads(json_str)
            # Validate minimum required fields
            if "store_name" not in data:
                return None
            return data
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error: {e}")
            return None