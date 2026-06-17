"""
Sistema Financiero - OCR Service
Ticket receipt OCR using Google Gemini Vision API.
Extracts store name, date, products, prices, and totals from receipt images.
"""
import base64
import io
import json
import time
import re
from datetime import date, datetime
from typing import Optional, List, Tuple
from PIL import Image, ImageEnhance, ImageFilter

import google.generativeai as genai

import logging
from app.config import get_settings
from app.utils.validators import Validators
from .schemas import OCRTicketData, OCRProduct, OCRResponse

settings = get_settings()
logger = logging.getLogger(__name__)


class OCRService:
    """Service for processing ticket images with Gemini Vision."""

    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.model = None
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.validators = Validators()

    def preprocess_image(self, image_bytes: bytes) -> bytes:
        """
        Preprocess image to improve OCR accuracy:
        - Convert to grayscale
        - Enhance contrast
        - Sharpen
        - Auto-rotate based on text orientation
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)
            
            # Resize if too large (Gemini has limits)
            max_dimension = 2048
            if max(img.size) > max_dimension:
                ratio = max_dimension / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            
            # Save to bytes
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=95)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Image preprocessing error: {e}")
            return image_bytes  # Return original on error

    def _build_gemini_prompt(self) -> str:
        """Build the prompt for Gemini Vision API to extract ticket data."""
        return """Eres un experto en leer tickets de compra mexicanos y extraer información estructurada.

Analiza la imagen del ticket y extrae TODA la información en formato JSON. 
IMPORTANTE: Responde **SOLO** con el JSON, sin markdown, sin explicaciones.

El JSON debe tener esta estructura EXACTA:
{
  "store_name": "Nombre de la tienda exactamente como aparece",
  "store_category": "Categoría detectada (liverpool, ikea, walmart, amazon, home_depot, oxxo, farmacias_similares, pemex, bp, costco, sams_club, soriana, chedraui, other)",
  "receipt_number": "Número de ticket o folio (o null si no se ve)",
  "purchase_date": "Fecha en formato YYYY-MM-DD",
  "purchase_time": "Hora en formato HH:MM (o null si no se ve)",
  "subtotal": 123.45,
  "taxes": 12.34,
  "total_amount": 135.79,
  "payment_method": "Método de pago (cash, credit_card, debit_card, transfer, null si no se ve)",
  "currency": "MXN",
  "products": [
    {
      "name": "Nombre del producto",
      "brand": "Marca si se detecta (o null)",
      "quantity": 1,
      "unit": "pza, kg, lt, etc.",
      "unit_price": 10.50,
      "total_price": 10.50,
      "discount": null,
      "sku": null,
      "category": "Categoría del producto (alimentos, bebidas, hogar, electronicos, muebles, ropa, salud, higiene, limpieza, herramientas, automotriz, combustible, entretenimiento, servicios, otros)"
    }
  ],
  "has_warranty_items": false
}

REGLAS CRÍTICAS:
1. purchase_date SIEMPRE debe ser una fecha válida en formato YYYY-MM-DD
2. Si no ves el año, asume el año actual
3. store_name debe ser el nombre exacto de la tienda
4. Extrae CADA producto individualmente, incluyendo descuentos
5. El total_amount debe coincidir con el total del ticket
6. Para has_warranty_items: true si hay electrónicos, electrodomésticos, muebles o herramientas
7. Si no hay productos visibles, devuelve products: []"""

    def extract_from_image(self, image_bytes: bytes, preprocess: bool = True) -> OCRResponse:
        """
        Extract ticket data from an image using Gemini Vision.
        
        Args:
            image_bytes: Raw image bytes (JPEG or PNG)
            preprocess: Whether to preprocess the image first
            
        Returns:
            OCRResponse with extracted data or error
        """
        start_time = time.time()
        
        if not self.model or not self.api_key:
            return OCRResponse(
                success=False,
                error="Gemini API no configurada. Revisa GEMINI_API_KEY en .env",
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        
        try:
            # Preprocess image
            if preprocess:
                processed_bytes = self.preprocess_image(image_bytes)
            else:
                processed_bytes = image_bytes
            
            # Prepare image for Gemini
            image_parts = [
                {
                    "mime_type": "image/jpeg",
                    "data": processed_bytes
                }
            ]
            
            # Call Gemini
            prompt = self._build_gemini_prompt()
            response = self.model.generate_content([prompt, image_parts[0]])
            
            # Parse response
            raw_text = response.text
            
            # Clean response - remove markdown code blocks if present
            cleaned_text = raw_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()
            
            # Parse JSON
            try:
                data = json.loads(cleaned_text)
            except json.JSONDecodeError:
                # Try to find JSON in the response
                json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                else:
                    return OCRResponse(
                        success=False,
                        error=f"Error al parsear respuesta de Gemini: {raw_text[:500]}",
                        processing_time_ms=int((time.time() - start_time) * 1000)
                    )
            
            # Validate and convert dates
            purchase_date = None
            raw_date = data.get("purchase_date", "")
            if raw_date:
                try:
                    purchase_date = date.fromisoformat(raw_date)
                except (ValueError, TypeError):
                    # Try common Mexican date formats
                    for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"]:
                        try:
                            purchase_date = datetime.strptime(str(raw_date), fmt).date()
                            break
                        except ValueError:
                            continue
                    if not purchase_date:
                        purchase_date = date.today()
            
            # Build structured data
            ticket_data = OCRTicketData(
                store_name=data.get("store_name", "Desconocida"),
                store_category=data.get("store_category"),
                receipt_number=data.get("receipt_number"),
                purchase_date=purchase_date or date.today(),
                purchase_time=data.get("purchase_time"),
                subtotal=data.get("subtotal"),
                taxes=data.get("taxes"),
                total_amount=data.get("total_amount", 0),
                payment_method=data.get("payment_method"),
                currency=data.get("currency", "MXN"),
                products=[
                    OCRProduct(
                        name=p.get("name", "Producto"),
                        brand=p.get("brand"),
                        quantity=p.get("quantity", 1),
                        unit=p.get("unit", "pza"),
                        unit_price=p.get("unit_price"),
                        total_price=p.get("total_price", 0),
                        discount=p.get("discount"),
                        sku=p.get("sku"),
                        category=p.get("category"),
                    )
                    for p in data.get("products", [])
                ],
                raw_text=raw_text,
                confidence=0.85,  # Gemini doesn't provide confidence, use default
                has_warranty_items=data.get("has_warranty_items", False),
                expense_type=self._classify_expense_type(data.get("products", []), 
                                                          data.get("store_category", ""),
                                                          data.get("has_warranty_items", False)),
            )
            
            # Override store_category with validator
            detected_category = self.validators.classify_store_from_name(
                ticket_data.store_name
            )
            if detected_category != "other":
                ticket_data.store_category = detected_category
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return OCRResponse(
                success=True,
                data=ticket_data,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Gemini OCR error: {str(e)}", exc_info=True)
            return OCRResponse(
                success=False,
                error=f"Error en OCR: {str(e)}",
                processing_time_ms=int((time.time() - start_time) * 1000)
            )

    def _classify_expense_type(self, products: list, store_category: str, 
                                has_warranty: bool) -> str:
        """Classify the expense type based on products and store."""
        if has_warranty:
            return "garantia"
        
        # Essentials
        essential_stores = {"walmart", "soriana", "chedraui", "oxxo", "costco", "sams_club"}
        essential_categories = {"alimentos", "bebidas", "higiene", "limpieza", "salud"}
        
        product_categories = {p.get("category", "") for p in products if p.get("category")}
        
        if store_category in essential_stores or product_categories & essential_categories:
            return "necesidad"
        
        if store_category in {"liverpool", "ikea", "amazon"}:
            if has_warranty:
                return "garantia"
            return "discrecional"
        
        if store_category in {"pemex", "bp"}:
            return "necesidad"
        
        return "discrecional"

    def extract_from_base64(self, base64_str: str, preprocess: bool = True) -> OCRResponse:
        """Extract ticket data from a base64 encoded image."""
        try:
            image_bytes = base64.b64decode(base64_str)
            return self.extract_from_image(image_bytes, preprocess=preprocess)
        except Exception as e:
            return OCRResponse(
                success=False,
                error=f"Error decodificando imagen base64: {str(e)}",
                processing_time_ms=0
            )