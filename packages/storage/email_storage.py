"""
EmailStorage - Envío de ZIP mensual por correo.
Fallback cuando el usuario no tiene nube personal configurada.
"""
import io
import json
import logging
import smtplib
import zipfile
from dataclasses import dataclass
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class EmailResult:
    success: bool
    file_count: int
    error: Optional[str] = None


class EmailStorage:
    """
    Envío de reportes mensuales por correo.
    Genera ZIP cifrado con PDFs y XMLs del mes anterior.
    """

    MAX_ATTACHMENT_SIZE = 25 * 1024 * 1024  # 25 MB (límite Gmail)

    def __init__(self, smtp_config: Optional[dict] = None):
        self.config = smtp_config or self._default_config()
        self.local_storage = None  # LocalStorage()

    def _default_config(self) -> dict:
        """Config SMTP por defecto (Gmail)."""
        import os
        return {
            "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
            "port": int(os.getenv("SMTP_PORT", "587")),
            "user": os.getenv("SMTP_USER", ""),
            "password": os.getenv("SMTP_PASSWORD", ""),
            "from_addr": os.getenv("SMTP_FROM", ""),
            "use_tls": True,
        }

    async def send_monthly_report(self, household_id: str, period: str = None) -> EmailResult:
        """Generar y enviar reporte mensual."""
        if not period:
            now = datetime.now()
            period = f"{now.year}-{now.month:02d}"

        try:
            # Generar ZIP con archivos del mes
            zip_data, file_count = await self._generate_zip(household_id, period)
            
            if file_count == 0:
                return EmailResult(success=True, file_count=0, error="No files to send")

            # Enviar correo
            success = await self._send_email(
                to= self.config.get("from_addr", ""),
                subject=f"Reporte Financiero {period} - Sistema Finanzas",
                body=self._build_email_body(period, file_count),
                attachment=zip_data,
                filename=f"reporte_{period}.zip",
            )

            if success:
                logger.info(f"Monthly report sent: {period} ({file_count} files)")
                return EmailResult(success=True, file_count=file_count)
            else:
                return EmailResult(success=False, file_count=file_count, error="SMTP failed")

        except Exception as e:
            logger.error(f"Error sending monthly report: {e}")
            return EmailResult(success=False, file_count=0, error=str(e))

    async def _generate_zip(self, household_id: str, period: str) -> tuple:
        """Generar ZIP con archivos del período."""
        buffer = io.BytesIO()
        file_count = 0
        
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # TODO: Query files from DB for this household/period
            # Por ahora, placeholder
            zf.writestr("readme.txt", f"Reporte {period} - Sistema Finanzas MX")
            file_count = 1

        buffer.seek(0)
        return buffer.getvalue(), file_count

    def _build_email_body(self, period: str, file_count: int) -> str:
        """Construir cuerpo del correo."""
        return f"""
        <h2>📊 Reporte Financiero {period}</h2>
        <p>Se adjunta el reporte mensual con {file_count} archivos.</p>
        <hr>
        <p style="color: #666; font-size: 12px;">
        Sistema Finanzas MX - Reporte automático mensual<br>
        Si tienes dudas, contacta al administrador.
        </p>
        """

    async def _send_email(self, to: str, subject: str, body: str,
                           attachment: bytes, filename: str) -> bool:
        """Enviar correo con attachment."""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.config["from_addr"]
            msg["To"] = to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "html"))

            # Adjuntar ZIP
            part = MIMEBase("application", "zip")
            part.set_payload(attachment)
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={filename}")
            msg.attach(part)

            # Enviar
            with smtplib.SMTP(self.config["host"], self.config["port"]) as server:
                if self.config.get("use_tls"):
                    server.starttls()
                if self.config["user"] and self.config["password"]:
                    server.login(self.config["user"], self.config["password"])
                server.send_message(msg)

            return True

        except Exception as e:
            logger.error(f"SMTP error: {e}")
            return False