"""
Sistema Financiero - Portal Factory
Dynamically selects and instantiates the correct portal driver for each store.
"""
import logging
from typing import Optional, Dict, Type

from .base import BasePortal, PortalCredentials, InvoiceResult

logger = logging.getLogger(__name__)


class PortalFactory:
    """
    Factory for creating portal instances based on store category.
    
    Registers new portals automatically when they implement BasePortal.
    """

    _portals: Dict[str, Type[BasePortal]] = {}

    @classmethod
    def register(cls, store_category: str):
        """Decorator to register a portal class for a store category."""
        def wrapper(portal_class: Type[BasePortal]):
            cls._portals[store_category] = portal_class
            logger.info(f"Portal registrado: {store_category} -> {portal_class.__name__}")
            return portal_class
        return wrapper

    @classmethod
    def create(cls, store_category: str) -> Optional[BasePortal]:
        """
        Create a portal instance for the given store category.
        
        Args:
            store_category: Store category string (e.g., "liverpool", "ikea", "walmart")
            
        Returns:
            Portal instance or None if not found
        """
        portal_class = cls._portals.get(store_category)
        if not portal_class:
            logger.warning(f"No hay portal registrado para: {store_category}")
            return None
        
        try:
            return portal_class()
        except Exception as e:
            logger.error(f"Error creando portal {store_category}: {e}")
            return None

    @classmethod
    def get_supported_stores(cls) -> list:
        """Get list of supported store categories."""
        return list(cls._portals.keys())


# Register portals
# These imports trigger the decorator registration

try:
    from .liverpool import LiverpoolPortal
    PortalFactory.register("liverpool")(LiverpoolPortal)
    logger.info("✅ Portal Liverpool registrado")
except ImportError as e:
    logger.warning(f"❌ No se pudo registrar Liverpool: {e}")

try:
    from .ikea import IKEAPortal
    PortalFactory.register("ikea")(IKEAPortal)
    logger.info("✅ Portal IKEA registrado")
except ImportError as e:
    logger.warning(f"❌ No se pudo registrar IKEA: {e}")

# Future registrations (to be implemented):
# PortalFactory.register("walmart")(WalmartPortal)
# PortalFactory.register("amazon")(AmazonPortal)
# PortalFactory.register("home_depot")(HomeDepotPortal)
# PortalFactory.register("oxxo")(OxxoPortal)
# PortalFactory.register("farmacias_similares")(FarmaciasSimilaresPortal)
# PortalFactory.register("pemex")(PemexPortal)
# PortalFactory.register("bp")(BPPortal)
# PortalFactory.register("costco")(CostcoPortal)
# PortalFactory.register("sams_club")(SamsClubPortal)
# PortalFactory.register("soriana")(SorianaPortal)
# PortalFactory.register("chedraui")(ChedrauiPortal)