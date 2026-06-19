"""
Shared Models - SQLAlchemy models with household_id for multi-tenant.
Plan Maestro v2 — 18 tablas.
"""
import uuid
from datetime import datetime, date
from sqlalchemy import (Column, String, Text, Integer, Float, Boolean,
                        DateTime, Date, ForeignKey, JSON, BigInteger, LargeBinary)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


def gen_id():
    return str(uuid.uuid4())


# =============================================================================
# Enums
# =============================================================================

TICKET_STATUSES = (
    "received", "processing", "parsed", "error",
    "invoicing", "invoiced", "expired"
)

CFDI_STATUSES = (
    "pending", "success", "error", "duplicate",
    "account_needed", "manual"
)

ITEM_CATEGORIES = ("consumible", "durable", "garantia", "servicio")

ROLES = ("owner", "spouse", "child", "accountant")

CLOUD_PROVIDERS = ("google_drive", "dropbox", "onedrive")


# =============================================================================
# Core Tables
# =============================================================================

class Household(Base):
    """Multi-tenant household/group."""
    __tablename__ = "households"

    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    settings_json = Column(JSON, default=dict)  # cloud_provider, retention, etc.

    members = relationship("Member", back_populates="household", cascade="all")
    businesses = relationship("Business", back_populates="household", cascade="all")
    tickets = relationship("Ticket", back_populates="household", cascade="all")
    shopping_lists = relationship("ShoppingList", back_populates="household", cascade="all")
    warranties = relationship("Warranty", back_populates="household", cascade="all")


class Member(Base):
    """Household member."""
    __tablename__ = "members"

    id = Column(String, primary_key=True, default=gen_id)
    household_id = Column(String, ForeignKey("households.id"), nullable=False, index=True)
    telegram_user_id = Column(String(100), nullable=True, unique=True)
    role = Column(String(20), default="member")  # owner, spouse, child, accountant
    email = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    household = relationship("Household", back_populates="members")


class Business(Base):
    """Business/negocio dentro de un household."""
    __tablename__ = "businesses"

    id = Column(String, primary_key=True, default=gen_id)
    household_id = Column(String, ForeignKey("households.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    rfc = Column(String(13), nullable=True)
    pos_type = Column(String(50), nullable=True)
    pos_api_key_hash = Column(String(128), nullable=True)
    settings_json = Column(JSON, default=dict)

    household = relationship("Household", back_populates="businesses")


class Ticket(Base):
    """Ticket receipt from OCR."""
    __tablename__ = "tickets"

    id = Column(String, primary_key=True, default=gen_id)
    household_id = Column(String, ForeignKey("households.id"), nullable=False, index=True)
    business_id = Column(String, ForeignKey("businesses.id"), nullable=True)
    source_telegram_user_id = Column(String(100), nullable=True)
    
    received_at = Column(DateTime, default=datetime.utcnow)
    photo_local_path = Column(String(500), nullable=True)
    photo_hash = Column(String(64), nullable=True, index=True)  # SHA-256
    
    # Merchant info
    merchant_name = Column(String(255), nullable=True)
    merchant_rfc = Column(String(13), nullable=True)
    ticket_date = Column(Date, nullable=True)
    subtotal = Column(Float, nullable=True)
    tax = Column(Float, nullable=True)
    total = Column(Float, nullable=True)
    currency = Column(String(10), default="MXN")
    
    # OCR results
    raw_ocr_json = Column(JSON, nullable=True)
    parsed_json = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Status
    status = Column(String(20), default="received", index=True)
    error_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    household = relationship("Household", back_populates="tickets")
    items = relationship("TicketItem", back_populates="ticket", cascade="all")
    cfdi_attempts = relationship("CFDIAttempt", back_populates="ticket", cascade="all")


class TicketItem(Base):
    """Individual product from a ticket."""
    __tablename__ = "ticket_items"

    id = Column(String, primary_key=True, default=gen_id)
    ticket_id = Column(String, ForeignKey("tickets.id"), nullable=False, index=True)
    
    sku = Column(String(100), nullable=True)
    description = Column(String(500), nullable=False)
    quantity = Column(Float, default=1)
    unit_price = Column(Float, nullable=True)
    line_total = Column(Float, nullable=False)
    category = Column(String(20), nullable=True, index=True)  # consumible, durable, garantia, servicio
    
    # Warranty
    warranty_months = Column(Integer, nullable=True)
    exp_date = Column(Date, nullable=True)
    
    ticket = relationship("Ticket", back_populates="items")


class CFDIAttempt(Base):
    """CFDI invoice attempt tracking."""
    __tablename__ = "cfdi_attempts"

    id = Column(String, primary_key=True, default=gen_id)
    ticket_id = Column(String, ForeignKey("tickets.id"), nullable=False, index=True)
    
    portal = Column(String(50), nullable=False)  # liverpool, amazon, etc.
    status = Column(String(20), default="pending", index=True)
    cfdi_uuid = Column(String(100), nullable=True, unique=True)
    
    # File paths
    pdf_local_path = Column(String(500), nullable=True)
    xml_local_path = Column(String(500), nullable=True)
    pdf_cloud_url = Column(String(1000), nullable=True)
    xml_cloud_url = Column(String(1000), nullable=True)
    
    error_detail = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    attempted_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    ticket = relationship("Ticket", back_populates="cfdi_attempts")


class CFDICredential(Base):
    """Encrypted credentials for portals and cloud services."""
    __tablename__ = "cfdi_credentials"

    id = Column(String, primary_key=True, default=gen_id)
    household_id = Column(String, ForeignKey("households.id"), nullable=False, index=True)
    business_id = Column(String, ForeignKey("businesses.id"), nullable=True)
    
    kind = Column(String(10), nullable=False)  # cfdi or cloud
    provider = Column(String(50), nullable=False)  # liverpool, google_drive, etc.
    
    # Encrypted fields
    username_encrypted = Column(LargeBinary, nullable=True)
    password_encrypted = Column(LargeBinary, nullable=True)
    access_token_encrypted = Column(LargeBinary, nullable=True)
    refresh_token_encrypted = Column(LargeBinary, nullable=True)
    
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="active")


class ShoppingList(Base):
    """Smart shopping list runs."""
    __tablename__ = "shopping_lists"

    id = Column(String, primary_key=True, default=gen_id)
    household_id = Column(String, ForeignKey("households.id"), nullable=False, index=True)
    business_id = Column(String, ForeignKey("businesses.id"), nullable=True)
    
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=True)
    status = Column(String(20), default="draft", index=True)
    
    items_json = Column(JSON, default=list)
    approvers_json = Column(JSON, default=dict)
    
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    household = relationship("Household", back_populates="shopping_lists")
    votes = relationship("ShoppingListVote", back_populates="shopping_list", cascade="all")


class ShoppingListVote(Base):
    """Votes on shopping list items."""
    __tablename__ = "shopping_list_votes"

    id = Column(String, primary_key=True, default=gen_id)
    shopping_list_id = Column(String, ForeignKey("shopping_lists.id"), nullable=False, index=True)
    member_id = Column(String, ForeignKey("members.id"), nullable=False)
    
    decision = Column(String(20), nullable=False)  # approve, reject, suggest
    comments = Column(Text, nullable=True)
    voted_at = Column(DateTime, default=datetime.utcnow)
    
    shopping_list = relationship("ShoppingList", back_populates="votes")


class Warranty(Base):
    """Product warranty tracking."""
    __tablename__ = "garantias"

    id = Column(String, primary_key=True, default=gen_id)
    household_id = Column(String, ForeignKey("households.id"), nullable=False, index=True)
    business_id = Column(String, ForeignKey("businesses.id"), nullable=True)
    ticket_item_id = Column(String, ForeignKey("ticket_items.id"), nullable=True)
    
    product = Column(String(500), nullable=False)
    store = Column(String(255), nullable=False)
    purchase_date = Column(Date, nullable=False)
    warranty_until = Column(Date, nullable=False, index=True)
    status = Column(String(20), default="active", index=True)  # active, expiring_soon, expired
    notes = Column(Text, nullable=True)
    
    household = relationship("Household", back_populates="warranties")


class AuditLog(Base):
    """Audit trail for sensitive actions."""
    __tablename__ = "audit_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    household_id = Column(String, ForeignKey("households.id"), nullable=True, index=True)
    actor = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False, index=True)
    target = Column(String(100), nullable=True)
    before_json = Column(JSON, nullable=True)
    after_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class SavingsGoal(Base):
    """Savings goals."""
    __tablename__ = "savings_goals"

    id = Column(String, primary_key=True, default=gen_id)
    household_id = Column(String, ForeignKey("households.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    target_amount = Column(Float, nullable=False)
    target_date = Column(Date, nullable=True)
    weekly_suggestion = Column(Float, nullable=True)
    current_amount = Column(Float, default=0)


class MonthlyEmailLog(Base):
    """Monthly email report log."""
    __tablename__ = "monthly_email_log"

    id = Column(String, primary_key=True, default=gen_id)
    household_id = Column(String, ForeignKey("households.id"), nullable=False, index=True)
    period = Column(String(7), nullable=False)  # YYYY-MM
    sent_at = Column(DateTime, default=datetime.utcnow)
    file_count = Column(Integer, default=0)
    recipient_email = Column(String(255), nullable=True)
    status = Column(String(20), default="sent")