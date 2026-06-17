"""
Sistema Financiero - Google Drive Storage
Organizes and stores invoices (PDF/XML) in categorized Google Drive folders.
"""
import logging
import io
import os
from datetime import datetime, date
from typing import Optional, List
import asyncio

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaFileUpload
from googleapiclient.errors import HttpError

from app.config import get_settings
from app.utils.validators import Validators

logger = logging.getLogger(__name__)


class DriveStorageService:
    """
    Google Drive storage service for invoices.
    Creates and manages folder structure automatically.
    
    Folder Structure:
    📁 FACTURAS/
    ├── 📁 Por Establecimiento/
    │   ├── 📁 Liverpool/2026/
    │   ├── 📁 IKEA/2026/
    │   └── ...
    ├── 📁 Por Tipo de Gasto/
    │   ├── 📁 Alimentos/
    │   ├── 📁 Electrónicos/
    │   └── ...
    ├── 📁 GARANTÍAS/
    │   ├── 📁 Producto/ (cafetera_liverpool_20260615.pdf)
    │   └── ...
    ├── 📁 Tickets Vencidos/
    ├── 📁 Errores/
    └── 📁 Credenciales/
    """

    # Folder structure constants
    MAIN_FOLDER = "FACTURAS"
    SUBFOLDERS = {
        "por_establecimiento": "Por Establecimiento",
        "por_tipo_gasto": "Por Tipo de Gasto",
        "garantias": "GARANTÍAS",
        "vencidos": "Tickets Vencidos",
        "errores": "Errores",
        "credenciales": "Credenciales",
    }

    def __init__(self):
        self.settings = get_settings()
        self.service = None
        self.main_folder_id = None
        self.validators = Validators()
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Drive API."""
        try:
            creds = Credentials(
                token=None,
                refresh_token=self.settings.google_refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.settings.google_client_id,
                client_secret=self.settings.google_client_secret,
                scopes=["https://www.googleapis.com/auth/drive"]
            )
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
            self.service = build("drive", "v3", credentials=creds)
            logger.info("✅ Google Drive API autenticada")
        except Exception as e:
            logger.error(f"❌ Drive auth error: {e}")
            self.service = None

    async def ensure_folder_structure(self) -> bool:
        """Create the main folder structure if it doesn't exist."""
        return await asyncio.to_thread(self._ensure_folders_sync)

    def _ensure_folders_sync(self) -> bool:
        """Synchronous folder creation."""
        if not self.service:
            return False
        
        try:
            # Create or get main folder
            self.main_folder_id = self.settings.google_drive_folder_id
            if not self.main_folder_id:
                self.main_folder_id = self._create_folder(self.MAIN_FOLDER)
            
            # Create subfolders
            for key, name in self.SUBFOLDERS.items():
                self._create_folder(name, parent_id=self.main_folder_id)
            
            logger.info(f"✅ Estructura de carpetas en Drive lista")
            return True
        except Exception as e:
            logger.error(f"Error creating folders: {e}")
            return False

    def _create_folder(self, name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """Create a folder in Drive if it doesn't exist."""
        try:
            # Check if folder exists
            query = f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
            if parent_id:
                query += f" and '{parent_id}' in parents"
            
            response = self.service.files().list(
                q=query,
                spaces="drive",
                fields="files(id, name)",
                pageSize=1
            ).execute()
            
            files = response.get("files", [])
            if files:
                return files[0]["id"]
            
            # Create folder
            metadata = {
                "name": name,
                "mimeType": "application/vnd.google-apps.folder",
            }
            if parent_id:
                metadata["parents"] = [parent_id]
            
            folder = self.service.files().create(body=metadata, fields="id").execute()
            return folder.get("id")
            
        except Exception as e:
            logger.error(f"Error creating folder '{name}': {e}")
            return None

    def _get_subfolder_id(self, folder_key: str) -> Optional[str]:
        """Get ID of a subfolder by key."""
        try:
            name = self.SUBFOLDERS.get(folder_key)
            if not name or not self.main_folder_id:
                return None
            
            return self._create_folder(name, parent_id=self.main_folder_id)
        except Exception as e:
            logger.error(f"Error getting subfolder '{folder_key}': {e}")
            return None

    def _get_or_create_year_folder(self, parent_id: str, year: int) -> Optional[str]:
        """Get or create a year subfolder."""
        return self._create_folder(str(year), parent_id=parent_id)

    def _get_or_create_store_folder(self, store_name: str) -> Optional[str]:
        """Get or create a store folder under 'Por Establecimiento'."""
        parent_id = self._get_subfolder_id("por_establecimiento")
        if not parent_id:
            return None
        return self._create_folder(store_name.capitalize(), parent_id=parent_id)

    def _get_or_create_expense_folder(self, expense_type: str) -> Optional[str]:
        """Get or create an expense type folder under 'Por Tipo de Gasto'."""
        parent_id = self._get_subfolder_id("por_tipo_gasto")
        if not parent_id:
            return None
        
        # Map expense types to folder names
        expense_names = {
            "alimentos": "Alimentos y Bebidas",
            "bebidas": "Alimentos y Bebidas",
            "hogar": "Hogar",
            "electronicos": "Electrónicos",
            "muebles": "Muebles",
            "ropa": "Ropa y Accesorios",
            "salud": "Salud y Farmacia",
            "higiene": "Higiene y Cuidado Personal",
            "limpieza": "Limpieza",
            "herramientas": "Herramientas",
            "automotriz": "Automotriz",
            "combustible": "Combustible",
            "entretenimiento": "Entretenimiento",
            "servicios": "Servicios",
            "otros": "Otros Gastos",
        }
        
        folder_name = expense_names.get(expense_type, "Otros Gastos")
        return self._create_folder(folder_name, parent_id=parent_id)

    async def save_invoice(self, store_name: str, purchase_date: date,
                            pdf_bytes: Optional[bytes], xml_bytes: Optional[bytes],
                            ticket_id: str, store_category: str = "",
                            has_warranty: bool = False,
                            expense_type: str = "") -> dict:
        """
        Save invoice files to the appropriate Drive folders.
        
        Returns:
            dict with: pdf_url, pdf_file_id, xml_url, xml_file_id
        """
        return await asyncio.to_thread(
            self._save_invoice_sync, store_name, purchase_date,
            pdf_bytes, xml_bytes, ticket_id, store_category,
            has_warranty, expense_type
        )

    def _save_invoice_sync(self, store_name: str, purchase_date: date,
                            pdf_bytes: Optional[bytes], xml_bytes: Optional[bytes],
                            ticket_id: str, store_category: str = "",
                            has_warranty: bool = False,
                            expense_type: str = "") -> dict:
        """Synchronous save implementation."""
        result = {
            "pdf_url": None, "pdf_file_id": None,
            "xml_url": None, "xml_file_id": None,
        }
        
        if not self.service:
            logger.warning("Drive no configurado")
            return result
        
        try:
            # Ensure folder structure exists
            self._ensure_folders_sync()
            
            # Generate filenames
            safe_store = self.validators.sanitize_filename(store_name)
            date_str = purchase_date.strftime("%Y%m%d")
            year = purchase_date.year
            
            # Base filename
            base_filename = f"{safe_store}_{date_str}_{ticket_id[:8]}"
            
            # 1. Save to store folder
            store_folder = self._get_or_create_store_folder(store_name)
            if store_folder:
                year_folder = self._get_or_create_year_folder(store_folder, year)
                
                if pdf_bytes:
                    pdf_info = self._upload_file(
                        f"{base_filename}.pdf", pdf_bytes, "application/pdf", year_folder
                    )
                    result["pdf_url"] = pdf_info.get("webViewLink")
                    result["pdf_file_id"] = pdf_info.get("id")
                
                if xml_bytes:
                    xml_info = self._upload_file(
                        f"{base_filename}.xml", xml_bytes, "text/xml", year_folder
                    )
                    result["xml_url"] = xml_info.get("webViewLink")
                    result["xml_file_id"] = xml_info.get("id")
            
            # 2. Save to expense type folder (duplicate)
            if expense_type and (pdf_bytes or xml_bytes):
                expense_folder = self._get_or_create_expense_folder(expense_type)
                if expense_folder:
                    year_folder = self._get_or_create_year_folder(expense_folder, year)
                    
                    if pdf_bytes and not result["pdf_url"]:
                        pdf_info = self._upload_file(
                            f"{base_filename}.pdf", pdf_bytes, "application/pdf", year_folder
                        )
                        result["pdf_url"] = pdf_info.get("webViewLink")
                        result["pdf_file_id"] = pdf_info.get("id")
            
            # 3. Save to GARANTÍAS folder if has warranty
            if has_warranty and pdf_bytes:
                garantias_folder = self._get_subfolder_id("garantias")
                if garantias_folder:
                    warranty_filename = f"{base_filename}_GARANTIA.pdf"
                    self._upload_file(warranty_filename, pdf_bytes, "application/pdf", garantias_folder)
            
            logger.info(f"✅ Archivos guardados en Drive: {base_filename}")
            
        except Exception as e:
            logger.error(f"Error saving to Drive: {e}", exc_info=True)
        
        return result

    async def save_credential(self, store_name: str, username: str, 
                               password: str, rfc: str = "") -> Optional[str]:
        """Save generated credentials to Drive as encrypted file."""
        return await asyncio.to_thread(
            self._save_credential_sync, store_name, username, password, rfc
        )

    def _save_credential_sync(self, store_name: str, username: str,
                               password: str, rfc: str = "") -> Optional[str]:
        """Synchronous credential save."""
        try:
            folder_id = self._get_subfolder_id("credenciales")
            if not folder_id:
                return None
            
            content = (
                f"=== Credenciales {store_name} ===\n"
                f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                f"Tienda: {store_name}\n"
                f"Usuario: {username}\n"
                f"Contraseña: {password}\n"
                f"RFC: {rfc}\n"
                f"URL: -\n"
            )
            
            safe_store = self.validators.sanitize_filename(store_name)
            filename = f"Credenciales_{safe_store}_{datetime.now().strftime('%Y%m%d')}.txt"
            
            file_info = self._upload_file(
                filename, content.encode(), "text/plain", folder_id
            )
            
            return file_info.get("webViewLink")
            
        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
            return None

    def _upload_file(self, filename: str, content: bytes, mime_type: str,
                     parent_id: Optional[str] = None) -> dict:
        """Upload a file to Drive."""
        try:
            metadata = {"name": filename}
            if parent_id:
                metadata["parents"] = [parent_id]
            
            media = MediaIoBaseUpload(io.BytesIO(content), mimetype=mime_type)
            
            file = self.service.files().create(
                body=metadata,
                media_body=media,
                fields="id,name,webViewLink,mimeType"
            ).execute()
            
            return file
            
        except Exception as e:
            logger.error(f"Error uploading {filename}: {e}")
            return {}

    async def list_invoices(self, folder_key: str = "por_establecimiento",
                              store_name: str = "", year: Optional[int] = None) -> list:
        """List invoices in a given folder hierarchy."""
        return await asyncio.to_thread(
            self._list_files_sync, folder_key, store_name, year
        )

    def _list_files_sync(self, folder_key: str, store_name: str = "",
                          year: Optional[int] = None) -> list:
        """List files in Drive."""
        try:
            # Navigate folder structure
            if folder_key == "garantias":
                folder_id = self._get_subfolder_id("garantias")
            else:
                parent_id = self._get_subfolder_id(folder_key)
                if not parent_id:
                    return []
                if store_name:
                    folder_id = self._create_folder(
                        store_name.capitalize(), parent_id=parent_id
                    )
                else:
                    folder_id = parent_id
            
            if not folder_id:
                return []
            
            # Navigate to year folder
            if year:
                year_folder = self._get_or_create_year_folder(folder_id, year)
                if year_folder:
                    folder_id = year_folder
            
            # List files
            query = f"'{folder_id}' in parents and trashed=false"
            response = self.service.files().list(
                q=query,
                spaces="drive",
                fields="files(id, name, mimeType, webViewLink, createdTime, size)",
                orderBy="createdTime desc"
            ).execute()
            
            return response.get("files", [])
            
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []

    async def check_duplicate(self, file_hash: str) -> bool:
        """Check if a file with the given hash already exists."""
        return await asyncio.to_thread(self._check_duplicate_sync, file_hash)

    def _check_duplicate_sync(self, file_hash: str) -> bool:
        """Check for duplicate by name pattern."""
        if not self.service or not self.main_folder_id:
            return False
        
        try:
            # Search for files with matching hash in name
            query = f"name contains '{file_hash[:16]}' and '{self.main_folder_id}' in parents"
            response = self.service.files().list(
                q=query,
                spaces="drive",
                fields="files(id, name)",
                pageSize=1
            ).execute()
            
            return len(response.get("files", [])) > 0
            
        except Exception as e:
            logger.warning(f"Error checking duplicate: {e}")
            return False