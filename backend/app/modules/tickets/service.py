"""
Iztack-Finance - Tickets Service
Handle ticket uploads, multi-image stitching, and OCR processing.
"""
import logging
import io
from typing import List
from PIL import Image

from app.modules.ocr.service import OCRService
from app.modules.ocr.schemas import OCRResponse

logger = logging.getLogger(__name__)


class TicketsService:
    """Service for processing ticket uploads (single and multi-image)."""

    def __init__(self):
        self.ocr_service = OCRService()

    async def process_single(self, image_bytes: bytes, user_id: str) -> OCRResponse:
        """Process a single ticket image."""
        result = self.ocr_service.extract_from_image(image_bytes)
        return result

    async def process_multi(
        self, images: List[bytes], user_id: str
    ) -> OCRResponse:
        """
        Process multiple images as a single ticket (stitch them vertically).
        Uses feature matching to detect overlap and merge seamlessly.
        """
        if len(images) == 1:
            return await self.process_single(images[0], user_id)

        # Stitch images
        stitched = self._stitch_images(images)

        # Run OCR on stitched image
        result = self.ocr_service.extract_from_image(stitched)

        # If stitching failed or OCR is better on individual, process individually
        if not result.success:
            logger.warning("Stitching failed, processing images individually")
            combined = self._combine_ocr_results(images)
            return combined

        return result

    def _stitch_images(self, images: List[bytes]) -> bytes:
        """
        Stitch multiple images vertically, detecting overlap.
        Uses OpenCV to find overlapping regions and merge seamlessly.
        """
        try:
            import cv2
            import numpy as np

            pil_images = []
            for img_bytes in images:
                pil_img = Image.open(io.BytesIO(img_bytes))
                # Convert to RGB if needed
                if pil_img.mode != "RGB":
                    pil_img = pil_img.convert("RGB")
                pil_images.append(pil_img)

            if len(pil_images) == 1:
                buf = io.BytesIO()
                pil_images[0].save(buf, format="JPEG", quality=90)
                return buf.getvalue()

            # Convert PIL to OpenCV
            cv_images = []
            for pil_img in pil_images:
                np_img = np.array(pil_img)
                cv_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
                cv_images.append(cv_img)

            # Start with first image
            base = cv_images[0]

            for i in range(1, len(cv_images)):
                next_img = cv_images[i]

                # Try to find overlap using ORB feature matching
                overlap = self._find_overlap(base, next_img)

                if overlap > 0:
                    # Remove overlap from next image
                    h, w = next_img.shape[:2]
                    next_crop = next_img[overlap:, :]
                    # Concatenate vertically
                    base = cv2.vconcat([base, next_crop])
                else:
                    # No overlap detected, just concatenate
                    base = cv2.vconcat([base, next_img])

            # Convert back to bytes
            _, buffer = cv2.imencode(".jpg", base, [cv2.IMWRITE_JPEG_QUALITY, 90])
            return buffer.tobytes()

        except ImportError:
            logger.warning("OpenCV not available, using PIL fallback")
            return self._stitch_pil_fallback(pil_images)
        except Exception as e:
            logger.error(f"Stitching error: {e}", exc_info=True)
            # Fallback: just concatenate the first image
            buf = io.BytesIO()
            pil_images[0].save(buf, format="JPEG", quality=90)
            return buf.getvalue()

    def _find_overlap(self, img1, img2) -> int:
        """
        Find vertical overlap between two images using feature matching.
        Returns the number of overlapping rows from the bottom of img1.
        """
        try:
            import cv2

            # Use ORB detector
            orb = cv2.ORB_create(nfeatures=500)

            h1, w1 = img1.shape[:2]
            h2, w2 = img2.shape[:2]

            # Check overlap in the bottom 30% of img1 and top 30% of img2
            overlap_region_rows = min(h1, h2) // 3
            if overlap_region_rows < 20:
                return 0  # Too small to find overlap

            # Bottom of img1
            bottom_region = img1[h1 - overlap_region_rows:, :]
            # Top of img2
            top_region = img2[:overlap_region_rows, :]

            kp1, des1 = orb.detectAndCompute(bottom_region, None)
            kp2, des2 = orb.detectAndCompute(top_region, None)

            if des1 is None or des2 is None or len(kp1) < 4 or len(kp2) < 4:
                return 0

            # Match features
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = bf.match(des1, des2)

            if len(matches) < 4:
                return 0

            # Sort by distance (best matches first)
            matches = sorted(matches, key=lambda x: x.distance)

            # Use top matches to estimate overlap
            good_matches = matches[:min(20, len(matches))]
            avg_distance = sum(m.distance for m in good_matches) / len(good_matches)

            # If matches are good (low distance), estimate overlap
            if avg_distance < 60:
                # Find the average y-shift in the matched points
                shifts = []
                for m in good_matches:
                    y1 = kp1[m.queryIdx].pt[1]
                    shifts.append(y1)

                if shifts:
                    avg_shift = sum(shifts) / len(shifts)
                    # Return estimated overlap rows
                    return max(0, min(int(avg_shift), overlap_region_rows))

            return 0

        except Exception as e:
            logger.error(f"Overlap detection error: {e}")
            return 0

    def _stitch_pil_fallback(self, images: List) -> bytes:
        """Fallback stitching using PIL (simple vertical concatenation)."""
        widths = [img.width for img in images]
        heights = [img.height for img in images]
        total_height = sum(heights)
        max_width = max(widths)

        stitched = Image.new("RGB", (max_width, total_height))
        y_offset = 0
        for img in images:
            stitched.paste(img, (0, y_offset))
            y_offset += img.height

        buf = io.BytesIO()
        stitched.save(buf, format="JPEG", quality=90)
        return buf.getvalue()

    def _combine_ocr_results(self, images: List[bytes]) -> OCRResponse:
        """Fallback: process each image individually and combine results."""
        combined = None
        all_products = []

        for img_bytes in images:
            result = self.ocr_service.extract_from_image(img_bytes)
            if result.success and result.data:
                if combined is None:
                    combined = result
                else:
                    # Merge data
                    if result.data.products:
                        all_products.extend(result.data.products)

        if combined and combined.data:
            combined.data.products = all_products
            # Recalculate total
            if all_products:
                combined.data.total_amount = sum(
                    p.total_price for p in all_products if p.total_price
                )

        return combined or OCRResponse(
            success=False, error="No se pudo procesar ninguna imagen"
        )

    async def upload_and_process(
        self, images: List[bytes], is_continuation: bool, user_id: str
    ) -> OCRResponse:
        """
        Main upload handler.
        If is_continuation is True, stitch images together.
        Otherwise process each independently.
        """
        if is_continuation and len(images) > 1:
            return await self.process_multi(images, user_id)

        # Process first image (or only image)
        result = await self.process_single(images[0], user_id)

        # If there are additional images (not continuation), process separately
        # For now, just return first result
        return result