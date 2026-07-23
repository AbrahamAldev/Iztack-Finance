"""
Iztack-Finance - OCR Service (Local Tesseract + OpenRouter Vision)
Extracts store name, date, products, prices, and totals from receipt images.
Uses local Tesseract OCR as primary (free, no limits), with OpenRouter
vision models as optional enhancement when available.
"""
import base64
import io
import json
import logging
import os
import re
from typing import Optional

from openai import OpenAI
from PIL import Image, ImageEnhance

from app.utils.validators import Validators

from .schemas import OCRResponse, OCRTicketData
from .local_service import LocalOCRService, ReceiptParser

logger = logging.getLogger(__name__)


class OCRService:
    """Service for processing ticket images with local OCR + optional LLM enhancement."""

    def __init__(self):
        self.api_key = os.environ.get("OPENROUTER_API_KEY", "")
        self.validators = Validators()
        self.local_ocr = LocalOCRService()
        self.parser = ReceiptParser()

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
        return """Eres un EXPERTO en lectura de tickets de compra mexicanos. Tu ÚNICA tarea es extraer datos precisos.

⚠️ REGLAS CRÍTICAS:
1. Responde **SOLO** con JSON válido, sin texto antes ni después, sin markdown.
2. Las fechas DEBEN ser exactamente como aparecen en el ticket. Formato: YYYY-MM-DD.
   - Si ves "10/07/2026" → "2026-07-10"
   - Si NO ves la fecha claramente → null
   - NO INVENTES fechas. Si no se lee bien, usa null.
3. Los totales DEBEN coincidir exactamente con el ticket.
   - Busca la palabra "TOTAL" o el número más grande al final
   - NO sumes productos para calcular el total
   - Si no se lee bien, usa null
4. Si NO estás 100% seguro de un dato, usa null. Es mejor no dar dato que dar uno falso.
5. El campo "confidence" debe reflejar qué tan legible está el ticket: 0.0-0.3 = borroso/dañado, 0.4-0.7 = legible pero con dudas, 0.8-1.0 = perfectamente claro.

⚠️ FORMATO EXACTO DEL JSON (no cambies los nombres de las claves):
{
  "store_name": "Nombre EXACTO de la tienda (ej: Chedraui, Walmart, Oxxo, Liverpool)",
  "store_category": "liverpool|ikea|walmart|amazon|home_depot|oxxo|farmacias_similares|pemex|bp|costco|sams_club|soriana|chedraui|other",
  "receipt_number": "número de ticket/folio o null",
  "purchase_date": "YYYY-MM-DD o null",
  "purchase_time": "HH:MM o null",
  "subtotal": 123.45,
  "taxes": 12.34,
  "total_amount": 135.79,
  "payment_method": "cash|credit_card|debit_card|transfer|null",
  "currency": "MXN",
  "products": [
    {
      "name": "Nombre del producto como aparece en el ticket",
      "brand": "Marca si se detecta, o null",
      "quantity": 1,
      "unit": "pza|kg|lt|etc",
      "unit_price": 99.90,
      "total_price": 99.90,
      "discount": null,
      "sku": "código de barras o null",
      "has_warranty": false,
      "warranty_info": "info de garantía si aparece, o null",
      "category": "alimentos|bebidas|hogar|electronicos|muebles|ropa|salud|higiene|limpieza|herramientas|automotriz|combustible|entretenimiento|servicios|otros"
    }
  ],
  "has_warranty_items": false,
  "confidence": 0.0
}"""

    def extract_from_image(self, image_bytes: bytes) -> OCRResponse:
        """Extract structured data from receipt image.

        Uses local Tesseract OCR as primary method (free, no limits).
        Falls back to OpenRouter vision models if available but not required.
        """
        raw_text = self.local_ocr.extract_text(image_bytes)
        local_result = self.parser.parse(raw_text)

        if local_result.success and local_result.data and local_result.data.confidence >= 0.5:
            logger.info(f"Local OCR OK: {local_result.data.store_name}, {len(local_result.data.products)} products")
            return local_result

        client = self._get_client()
        if not client:
            if local_result.success:
                return local_result
            return OCRResponse(
                success=False,
                error="No se pudo leer el ticket con OCR local. "
                      "Configura OPENROUTER_API_KEY para mejorar la precisión.",
                raw_text=raw_text,
            )

        processed_bytes = self.preprocess_image(image_bytes)
        b64_image = base64.b64encode(processed_bytes).decode("utf-8")

        primary_model = os.getenv("OCR_MODEL", "qwen/qwen3-vl-32b-instruct")
        fallback_models = [
            m.strip()
            for m in os.getenv("OCR_FALLBACK_MODELS", "google/gemini-2.5-flash-image,nvidia/nemotron-nano-12b-v2-vl:free").split(",")
            if m.strip()
        ]
        models_to_try = [primary_model] + fallback_models

        for idx, model in enumerate(models_to_try):
            try:
                response = client.chat.completions.create(
                    model=model,
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

                llm_raw = response.choices[0].message.content or ""
                logger.info(f"OCR LLM ({model}) raw: {llm_raw[:200]}")

                data = self._parse_ocr_response(llm_raw)
                if data:
                    return OCRResponse(
                        success=True,
                        data=OCRTicketData(**data),
                        raw_text=llm_raw,
                    )
                else:
                    if local_result.success:
                        return local_result
                    return OCRResponse(
                        success=False,
                        error="No se pudo interpretar el ticket con IA. Usando OCR local.",
                        raw_text=llm_raw,
                    )

            except Exception as e:
                error_str = str(e)
                is_rate = "429" in error_str or "rate limit" in error_str.lower()
                is_quota = "insufficient_quota" in error_str or "free-models-per-day" in error_str
                is_credits = "402" in error_str or "insufficient credits" in error_str.lower()

                if (is_rate or is_quota or is_credits) and idx < len(models_to_try) - 1:
                    logger.warning(f"LLM {model} no disponible, probando fallback: {models_to_try[idx + 1]}")
                    continue

                if idx < len(models_to_try) - 1:
                    logger.warning(f"Error con LLM {model}, probando fallback: {error_str[:80]}")
                    continue

                logger.warning(f"LLM OCR no disponible: {error_str[:100]}")

        if local_result.success:
            return local_result

        return OCRResponse(
            success=False,
            error="No se pudo leer el ticket. Intenta con mejor iluminación.",
            raw_text=raw_text or "",
        )

    def extract_from_base64(self, image_base64: str) -> OCRResponse:
        """Process a base64-encoded ticket image and extract structured data."""
        try:
            # Strip data URL prefix if present
            if "," in image_base64:
                image_base64 = image_base64.split(",", 1)[1]
            image_bytes = base64.b64decode(image_base64)
        except Exception as e:
            logger.error(f"Base64 decode error: {e}")
            return OCRResponse(
                success=False,
                error="La imagen base64 no es válida.",
                raw_text="",
            )
        return self.extract_from_image(image_bytes)

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
