"""
Sistema Financiero - OCR Routes
API endpoints for ticket OCR processing.
"""
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from .schemas import OCRRequest, OCRResponse
from .service import OCRService

router = APIRouter()
ocr_service = OCRService()


@router.post("/process-image", response_model=OCRResponse)
async def process_ticket_image(
    file: UploadFile = File(...),
    chat_id: Optional[str] = Form(None),
    source_channel: Optional[str] = Form("api"),
):
    """
    Process a ticket image and extract structured data.
    
    Accepts: JPEG, PNG, WEBP
    Returns: Structured ticket data including store, products, and totals.
    """
    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no soportado: {file.content_type}. Usa JPEG, PNG o WEBP."
        )

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="La imagen es demasiado grande. Máximo 10MB."
        )

    result = ocr_service.extract_from_image(contents)
    return result


@router.post("/process-base64", response_model=OCRResponse)
async def process_ticket_base64(request: OCRRequest):
    """Process a ticket image from base64 encoded string."""
    if not request.image_base64:
        raise HTTPException(status_code=400, detail="Se requiere image_base64")

    result = ocr_service.extract_from_base64(request.image_base64)
    return result


@router.post("/preprocess")
async def preprocess_image(file: UploadFile = File(...)):
    """Preprocess an image for better OCR and return the enhanced version."""
    contents = await file.read()
    processed = ocr_service.preprocess_image(contents)

    return Response(
        content=processed,
        media_type="image/jpeg",
        headers={
            "Content-Disposition": f"attachment; filename=preprocessed_{file.filename}"
        }
    )
