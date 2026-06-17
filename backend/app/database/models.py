"""
Sistema Financiero - Database Models
Core data models for tickets, invoices, products, credentials, shopping lists, etc.
"""
import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, Date,
    ForeignKey, JSON, Enum as SAEnum, BigInteger, LargeBinary
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .connection import Base
import enum


def generate_uuid():
    return str(uuid.uuid4())


# =============================================================================
# Enums
# =============================================================================

class TicketStatus(str, enum.Enum):
    PENDING = "pending"           # Recibido, pendiente de procesar
    PROCESSING = "processing"     # OCR en progreso
    OCR_COMPLETED = "ocr_completed"  # OCR terminado
    INVOICING = "invoicing"       # Solicitando factura
    INVOICED = "invoiced"         # Factura obtenida exitosamente
    EXPIRED = "expired"           # Plazo vencido
    ERROR = "error"               # Error en el proceso
    DUPLICATED = "duplicated"     # Ticket duplicado


class InvoiceStatus(str, enum.Enum):
    PENDING = "pending"
    REQUESTED = "requested"
    DOWNLOADED = "downloaded"
    FOUND_IN_EMAIL = "found_in_email"
    NOT_FOUND = "not_found"
    ERROR = "error"


class ProductCategory(str, enum.Enum):
    ALIMENTOS = "alimentos"
    BEBIDAS = "bebidas"
    HOGAR = "hogar"
    ELECTRONICOS = "electronicos"
    MUEBLES = "muebles"
    ROPA = "ropa"
    SALUD = "salud"
    HIGIENE = "higiene"
    LIMPIEZA = "limpieza"
    HERRAMIENTAS = "herramientas"
    AUTOMOTRIZ = "automotriz"
    COMBUSTIBLE = "combustible"
    ENTRETENIMIENTO = "entretenimiento"
    SERVICIOS = "servicios"
    OTROS = "otros"


class StoreCategory(str, enum.Enum):
    LIVERPOOL = "liverpool"
    IKEA = "ikea"
    WALMART = "walmart"
    AMAZON = "amazon"
    HOME_DEPOT = "home_depot"
    OXXO = "oxxo"
    FARMACIAS_SIMILARES = "farmacias_similares"
    PEMEX = "pemex"
    BP = "bp"
    COSTCO = "costco"
    SAMS_CLUB = "sams_club"
    SORIANA = "soriana"
    CHEDRAUI = "chedraui"
    OTHER = "other"


class ExpenseType(str, enum.Enum):
    NECESIDAD = "necesidad"       # Gastos esenciales
    DISCRECIONAL = "discrecional" # Gastos no esenciales
    AHORRO = "ahorro"            # Ahorro/inversión
    GARANTIA = "garantia"         # Productos con garantía


class ShoppingListStatus(str, enum.Enum):
    DRAFT = "draft"               # Borrador generado
    FAMILY_REVIEW = "family_review"  # En revisión familiar
    APPROVED = "approved"         # Aprobado por jefe familiar
    IN_PROGRESS = "in_progress"   # Comprando actualmente
    COMPLETED = "completed"       # Compra completada
    CANCELLED = "cancelled"       # Cancelada


class ShoppingItemStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PURCHASED = "purchased"
    NOT_PURCHASED = "not_purchased"


# =============================================================================
# Main Tables
# =============================================================================

class Ticket(Base):
    """Raw ticket receipt data from OCR."""
    __tablename__ = "tickets"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    
    # Store info
    store_name = Column(String(255), nullable=False, index=True)
    store_category = Column(String(50), nullable=True, index=True)
    
    # Receipt data
    receipt_number = Column(String(100), nullable=True)
    purchase_date = Column(Date, nullable=False, index=True)
    purchase_time = Column(String(20), nullable=True)
    total_amount = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=True)
    taxes = Column(Float, nullable=True)
    payment_method = Column(String(100), nullable=True)
    currency = Column(String(10), default="MXN")
    
    # Raw data
    ocr_raw_text = Column(Text, nullable=True)
    ocr_confidence = Column(Float, nullable=True)
    
    # Image storage
    original_image_url = Column(Text, nullable=True)
    processed_image_url = Column(Text, nullable=True)
    
    # Status
    status = Column(String(20), default=TicketStatus.PENDING.value, index=True)
    invoice_status = Column(String(20), default=InvoiceStatus.PENDING.value)
    error_message = Column(Text, nullable=True)
    
    # Warranty
    has_warranty_items = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = relationship("Product", back_populates="ticket", cascade="all, delete-orphan")
    invoice = relationship("Invoice", back_populates="ticket", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Ticket {self.store_name} - {self.purchase_date} - ${self.total_amount}>"


class Product(Base):
    """Individual product from a ticket."""
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=generate_uuid)
    ticket_id = Column(String, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Product info
    name = Column(String(500), nullable=False, index=True)
    brand = Column(String(255), nullable=True)
    quantity = Column(Float, default=1.0)
    unit = Column(String(50), default="pza")  # pza, kg, lt, etc.
    unit_price = Column(Float, nullable=True)
    total_price = Column(Float, nullable=False)
    discount = Column(Float, nullable=True)
    sku = Column(String(100), nullable=True)
    barcode = Column(String(100), nullable=True)
    
    # Classification
    category = Column(String(50), nullable=True, index=True)
    expense_type = Column(String(20), nullable=True, index=True)
    
    # Warranty
    has_warranty = Column(Boolean, default=False, index=True)
    warranty_months = Column(Integer, nullable=True)
    warranty_end_date = Column(Date, nullable=True)
    
    # Consumption cycle (for smart shopping list)
    consumption_cycle_days = Column(Integer, nullable=True)  # Detected cycle
    is_consumable = Column(Boolean, default=True)  # False = durable goods
    is_high_value = Column(Boolean, default=False)  # high-value items
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="products")

    def __repr__(self):
        return f"<Product {self.name} x{self.quantity} = ${self.total_price}>"


class Invoice(Base):
    """Invoice (CFDI) data - PDF and XML metadata."""
    __tablename__ = "invoices"

    id = Column(String, primary_key=True, default=generate_uuid)
    ticket_id = Column(String, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Invoice info
    invoice_uuid = Column(String(100), unique=True, nullable=True)  # CFDI UUID
    invoice_series = Column(String(50), nullable=True)
    invoice_number = Column(String(50), nullable=True)
    invoice_date = Column(Date, nullable=True)
    
    # RFC info
    issuer_rfc = Column(String(13), nullable=True)
    issuer_name = Column(String(255), nullable=True)
    receiver_rfc = Column(String(13), nullable=True)
    
    # Amounts
    subtotal = Column(Float, nullable=True)
    total = Column(Float, nullable=True)
    tax_base = Column(Float, nullable=True)
    tax_rate = Column(Float, nullable=True)
    tax_amount = Column(Float, nullable=True)
    
    # Source
    source = Column(String(50), default="web")  # web, email, manual
    status = Column(String(20), default=InvoiceStatus.PENDING.value)
    
    # File storage
    pdf_drive_url = Column(Text, nullable=True)
    pdf_drive_file_id = Column(String(200), nullable=True)
    xml_drive_url = Column(Text, nullable=True)
    xml_drive_file_id = Column(String(200), nullable=True)
    pdf_hash = Column(String(64), nullable=True)  # SHA-256 for dedup
    xml_hash = Column(String(64), nullable=True)  # SHA-256 for dedup
    
    # Email data (if found via email)
    email_message_id = Column(String(200), nullable=True)
    email_sender = Column(String(255), nullable=True)
    email_subject = Column(Text, nullable=True)
    email_received_date = Column(DateTime, nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="invoice")

    def __repr__(self):
        return f"<Invoice {self.invoice_uuid} - {self.invoice_date} - ${self.total}>"


class StoreCredential(Base):
    """Encrypted credentials for each store's invoicing portal."""
    __tablename__ = "store_credentials"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    
    # Store
    store_name = Column(String(255), nullable=False)
    store_category = Column(String(50), nullable=False, index=True)
    portal_url = Column(Text, nullable=True)
    
    # Credentials (encrypted with AES-256-GCM)
    encrypted_username = Column(LargeBinary, nullable=True)
    encrypted_password = Column(LargeBinary, nullable=True)
    encryption_key_id = Column(String(100), nullable=True)  # Key identifier for re-encryption
    credential_hint = Column(String(255), nullable=True)  # Visible hint
    
    # Account info
    rfc = Column(String(13), nullable=True)  # Mexican tax ID
    email_registered = Column(String(255), nullable=True)
    has_account = Column(Boolean, default=False)
    account_created_automatically = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<StoreCredential {self.store_name} - has_account={self.has_account}>"


class ConsumptionCycle(Base):
    """Detected consumption cycles for smart shopping list."""
    __tablename__ = "consumption_cycles"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    
    # Product
    product_name = Column(String(500), nullable=False)
    product_category = Column(String(50), nullable=True)
    preferred_store = Column(String(255), nullable=True)
    
    # Cycle data
    avg_days_between_purchases = Column(Integer, nullable=True)  # Detected average
    last_purchase_date = Column(Date, nullable=True)
    next_estimated_purchase = Column(Date, nullable=True)
    purchase_count = Column(Integer, default=0)
    total_quantity_purchased = Column(Float, nullable=True)
    avg_unit_price = Column(Float, nullable=True)
    price_trend = Column(Float, default=0.0)  # Positive = increasing
    
    # Preferences
    preferred_brand = Column(String(255), nullable=True)
    preferred_quantity = Column(Float, nullable=True)
    preferred_unit = Column(String(50), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    auto_generate = Column(Boolean, default=True)  # Include in auto lists
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ConsumptionCycle {self.product_name} - every {self.avg_days_between_purchases}d>"


class ShoppingList(Base):
    """Smart shopping lists with family approval flow."""
    __tablename__ = "shopping_lists"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    
    # List info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default=ShoppingListStatus.DRAFT.value, index=True)
    
    # Budget
    estimated_total = Column(Float, nullable=True)
    approved_budget = Column(Float, nullable=True)
    actual_total = Column(Float, nullable=True)
    
    # Generation
    generated_by = Column(String(50), default="auto")  # auto, manual
    source_text = Column(Text, nullable=True)  # AI prompt used
    
    # Printing
    printed = Column(Boolean, default=False)
    printed_at = Column(DateTime, nullable=True)
    printer_width = Column(Integer, nullable=True)
    
    # Start/end dates for the shopping trip
    planned_date_start = Column(Date, nullable=True)
    planned_date_end = Column(Date, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = relationship("ShoppingItem", back_populates="shopping_list", cascade="all, delete-orphan")
    votes = relationship("FamilyVote", back_populates="shopping_list", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ShoppingList {self.title} - {self.status}>"


class ShoppingItem(Base):
    """Individual item in a shopping list."""
    __tablename__ = "shopping_items"

    id = Column(String, primary_key=True, default=generate_uuid)
    shopping_list_id = Column(String, ForeignKey("shopping_lists.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Item info
    product_name = Column(String(500), nullable=False)
    category = Column(String(50), nullable=True)
    quantity = Column(Float, default=1.0)
    unit = Column(String(50), default="pza")
    estimated_price = Column(Float, nullable=True)
    actual_price = Column(Float, nullable=True)
    
    # Store
    preferred_store = Column(String(255), nullable=True)
    product_link = Column(Text, nullable=True)  # URL for pre-order
    
    # Status
    status = Column(String(20), default=ShoppingItemStatus.PENDING.value, index=True)
    added_by_member_id = Column(String(100), nullable=True)  # Who suggested it
    
    # Ticket matching
    matched_ticket_id = Column(String, ForeignKey("tickets.id", ondelete="SET NULL"), nullable=True)
    matched_at = Column(DateTime, nullable=True)
    
    # Priority
    priority = Column(Integer, default=0)  # Higher = more important
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    shopping_list = relationship("ShoppingList", back_populates="items")

    def __repr__(self):
        return f"<ShoppingItem {self.product_name} x{self.quantity} - {self.status}>"


class FamilyVote(Base):
    """Votes and suggestions from family members on shopping lists."""
    __tablename__ = "family_votes"

    id = Column(String, primary_key=True, default=generate_uuid)
    shopping_list_id = Column(String, ForeignKey("shopping_lists.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Member info
    member_name = Column(String(255), nullable=False)
    member_role = Column(String(50), default="member")  # member, head, admin
    chat_id = Column(String(100), nullable=True)  # Telegram/WhatsApp ID
    
    # Vote
    voted_at = Column(DateTime, default=datetime.utcnow)
    approved = Column(Boolean, nullable=True)  # True=approve, False=reject, Null=abstain
    comment = Column(Text, nullable=True)
    
    # Suggestion (if adding an item)
    suggested_item_name = Column(String(500), nullable=True)
    suggested_store = Column(String(255), nullable=True)
    suggested_link = Column(Text, nullable=True)
    suggested_quantity = Column(Float, nullable=True)
    
    # Relationships
    shopping_list = relationship("ShoppingList", back_populates="votes")

    def __repr__(self):
        return f"<FamilyVote {self.member_name} - approved={self.approved}>"


class FinancialAnalysis(Base):
    """Cached financial analysis results."""
    __tablename__ = "financial_analysis"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    
    # Analysis period
    analysis_type = Column(String(50), nullable=False)  # monthly, quarterly, yearly
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Results (stored as JSON for flexibility)
    total_spent = Column(Float, default=0.0)
    total_income = Column(Float, nullable=True)
    savings_rate = Column(Float, nullable=True)
    
    # Category breakdown
    category_spending = Column(JSON, nullable=True)  # {"alimentos": 5000, "hogar": 3000}
    store_spending = Column(JSON, nullable=True)     # {"walmart": 4000, "liverpool": 2000}
    
    # Insights
    detected_leaks = Column(JSON, nullable=True)     # Fugas de dinero detectadas
    savings_suggestions = Column(JSON, nullable=True)  # Sugerencias de ahorro
    predictions = Column(JSON, nullable=True)        # Predicciones de gasto
    
    # Full report
    summary_text = Column(Text, nullable=True)       # Human-readable summary
    report_pdf_url = Column(Text, nullable=True)     # Generated PDF report
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)     # Cache expiration

    def __repr__(self):
        return f"<FinancialAnalysis {self.analysis_type} - {self.period_start} to {self.period_end}>"


class CredentialGenerated(Base):
    """Track generated credentials for new accounts."""
    __tablename__ = "credentials_generated"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    
    # Store
    store_name = Column(String(255), nullable=False)
    store_category = Column(String(50), nullable=False)
    portal_url = Column(Text, nullable=True)
    
    # Generated credentials (encrypted)
    encrypted_username = Column(LargeBinary, nullable=True)
    encrypted_password = Column(LargeBinary, nullable=True)
    
    # Plain text for sending to user (temporary, cleared after sending)
    plain_username = Column(String(255), nullable=True)
    plain_password = Column(String(255), nullable=True)
    
    # Account info
    rfc = Column(String(13), nullable=True)
    email_used = Column(String(255), nullable=True)
    
    # Status
    sent_to_user = Column(Boolean, default=False)
    saved_to_password_manager = Column(Boolean, default=False)
    password_manager_type = Column(String(50), nullable=True)  # apple, google, none
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<CredentialGenerated {self.store_name} - sent={self.sent_to_user}>"


class ProcessingError(Base):
    """Track processing errors for debugging and notifications."""
    __tablename__ = "processing_errors"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=True, index=True)
    ticket_id = Column(String, ForeignKey("tickets.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Error info
    error_type = Column(String(50), nullable=False)  # ocr, scraping, email, auth, etc.
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=False)
    error_details = Column(JSON, nullable=True)
    stack_trace = Column(Text, nullable=True)
    
    # Resolution
    suggested_action = Column(Text, nullable=True)  # What the user can do
    auto_resolvable = Column(Boolean, default=False)  # Can the bot fix it?
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ProcessingError {self.error_type} - {self.error_code}>"


class AuditLog(Base):
    """Audit log for all system actions."""
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=True, index=True)
    
    # Action
    action = Column(String(100), nullable=False, index=True)  # ticket.created, invoice.downloaded, etc.
    entity_type = Column(String(50), nullable=True)           # ticket, invoice, credential, etc.
    entity_id = Column(String, nullable=True)                 # ID of affected entity
    
    # Context
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Channel
    source_channel = Column(String(50), nullable=True)  # telegram, whatsapp, web, api
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<AuditLog {self.action} - {self.entity_type}:{self.entity_id}>"