"""
Sistema Financiero - Gmail Invoice Search
Searches Gmail for invoice PDFs and XMLs from store emails.
NOTE: Google client is synchronous, runs in thread pool.
"""
import asyncio
import base64
import email
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class EmailInvoiceResult:
    """Result from searching Gmail for an invoice."""
    found: bool = False
    pdf_bytes: Optional[bytes] = None
    xml_bytes: Optional[bytes] = None
    message_id: Optional[str] = None
    sender: Optional[str] = None
    subject: Optional[str] = None
    received_date: Optional[datetime] = None
    error: Optional[str] = None


class GmailInvoiceService:
    """
    Service for searching Gmail for invoice emails.
    Uses Google Gmail API to search by store, date, and keywords.
    """

    STORE_EMAIL_PATTERNS = {
        "liverpool": ["liverpool.com.mx", "facturacion@liverpool.com.mx"],
        "ikea": ["ikea.com", "ikea.com.mx"],
        "walmart": ["walmart.com", "walmart.com.mx"],
        "amazon": ["amazon.com.mx", "amazon.com"],
        "home_depot": ["homedepot.com.mx"],
        "oxxo": ["oxxo.com"],
        "pemex": ["pemex.com"],
        "costco": ["costco.com.mx"],
        "soriana": ["soriana.com", "soriana.com.mx"],
    }

    INVOICE_KEYWORDS = [
        "factura", "cfdi", "invoice", "recibo electronico",
        "comprobante", "facturación", "xml", "pdf"
    ]

    def __init__(self):
        self.settings = get_settings()
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API using OAuth2."""
        try:
            creds = Credentials(
                token=None,
                refresh_token=self.settings.google_refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.settings.google_client_id,
                client_secret=self.settings.google_client_secret,
                scopes=["https://www.googleapis.com/auth/gmail.readonly"]
            )
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
            self.service = build("gmail", "v1", credentials=creds)
            logger.info("✅ Gmail API autenticada")
        except Exception as e:
            logger.error(f"❌ Gmail API auth error: {e}")
            self.service = None

    def _build_query(self, store_name: str, purchase_date: str,
                     total: float, ticket: str = "") -> str:
        """Build Gmail search query."""
        parts = []
        store_lower = store_name.lower().strip()
        patterns = self.STORE_EMAIL_PATTERNS.get(store_lower, [store_lower])
        from_q = " OR ".join(f"from:({p})" for p in patterns[:2])
        parts.append(f"({{{from_q}}})")

        try:
            dt = datetime.strptime(purchase_date, "%Y-%m-%d")
            parts.append(f"after:{dt.strftime('%Y/%m/%d')}")
            parts.append(f"before:{(dt + timedelta(days=30)).strftime('%Y/%m/%d')}")
        except Exception:
            pass

        kw_q = " OR ".join(f"subject:({kw})" for kw in self.INVOICE_KEYWORDS[:4])
        parts.append(f"({kw_q})")
        parts.append("has:attachment")
        if ticket:
            parts.append(f"({ticket})")
        if total:
            parts.append(f"({int(total)})")

        return " ".join(parts)

    async def search_invoice(self, store_name: str, purchase_date: str,
                              total_amount: float, ticket_number: str = "",
                              max_results: int = 5) -> EmailInvoiceResult:
        """Search Gmail for invoice matching ticket data."""
        return await asyncio.to_thread(
            self._search_invoice_sync, store_name, purchase_date,
            total_amount, ticket_number, max_results
        )

    def _search_invoice_sync(self, store_name: str, purchase_date: str,
                              total_amount: float, ticket_number: str = "",
                              max_results: int = 5) -> EmailInvoiceResult:
        """Synchronous search implementation."""
        result = EmailInvoiceResult()
        if not self.service:
            result.error = "Gmail API no autenticada"
            return result

        try:
            query = self._build_query(store_name, purchase_date, total_amount, ticket_number)
            response = self.service.users().messages().list(
                userId="me", q=query, maxResults=max_results
            ).execute()

            messages = response.get("messages", [])
            if not messages:
                return result

            for msg in messages:
                msg_id = msg["id"]
                msg_data = self.service.users().messages().get(
                    userId="me", id=msg_id, format="full"
                ).execute()

                headers = msg_data["payload"]["headers"]
                subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
                sender = next((h["value"] for h in headers if h["name"] == "From"), "")
                date_str = next((h["value"] for h in headers if h["name"] == "Date"), "")

                pdf_data, xml_data = self._extract_attachments(msg_data, msg_id)

                if pdf_data or xml_data:
                    result.found = True
                    result.message_id = msg_id
                    result.sender = sender
                    result.subject = subject
                    result.pdf_bytes = pdf_data
                    result.xml_bytes = xml_data
                    try:
                        result.received_date = email.utils.parsedate_to_datetime(date_str)
                    except Exception:
                        pass
                    break

            return result

        except HttpError as e:
            result.error = f"Gmail API error: {e}"
            return result
        except Exception as e:
            result.error = f"Error: {e}"
            return result

    def _extract_attachments(self, msg_data: dict, msg_id: str) -> tuple:
        """Extract PDF and XML from email."""
        pdf_bytes = None
        xml_bytes = None

        try:
            all_parts = []
            self._flatten(msg_data["payload"], all_parts)

            for part in all_parts:
                fname = part.get("filename", "").lower()
                mime = part.get("mimeType", "")

                if (fname.endswith(".pdf") or mime == "application/pdf") and not pdf_bytes:
                    data = self._get_attachment(msg_id, part)
                    if data:
                        pdf_bytes = data

                if (fname.endswith(".xml") or "xml" in mime) and not xml_bytes:
                    data = self._get_attachment(msg_id, part)
                    if data:
                        xml_bytes = data

                if pdf_bytes and xml_bytes:
                    break
        except Exception as e:
            logger.warning(f"Error extracting attachments: {e}")

        return pdf_bytes, xml_bytes

    def _flatten(self, part: dict, all_parts: list):
        """Flatten multipart message parts."""
        if "parts" in part:
            for p in part["parts"]:
                self._flatten(p, all_parts)
        else:
            all_parts.append(part)

    def _get_attachment(self, msg_id: str, part: dict) -> Optional[bytes]:
        """Download attachment from Gmail."""
        try:
            body = part.get("body", {})
            if "attachmentId" in body:
                att = self.service.users().messages().attachments().get(
                    userId="me", messageId=msg_id, id=body["attachmentId"]
                ).execute()
                data = att.get("data", "")
                if data:
                    return base64.urlsafe_b64decode(data)
            elif "data" in body:
                return base64.urlsafe_b64decode(body["data"])
        except Exception as e:
            logger.warning(f"Error downloading attachment: {e}")
        return None
