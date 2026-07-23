"""
Sistema Financiero - Portal Factory
Dynamically selects and instantiates the correct portal driver for each store.
"""
import logging
from typing import Dict, Optional, Type

from .base import BasePortal
from .base import InvoiceResult as InvoiceResult
from .base import PortalCredentials as PortalCredentials

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

try:
    from .walmart import WalmartPortal
    PortalFactory.register("walmart")(WalmartPortal)
    logger.info("✅ Portal Walmart registrado")
except ImportError as e:
    logger.warning(f"❌ No se pudo registrar Walmart: {e}")

try:
    from .amazon import AmazonPortal
    PortalFactory.register("amazon")(AmazonPortal)
    logger.info("✅ Portal Amazon registrado")
except ImportError as e:
    logger.warning(f"❌ No se pudo registrar Amazon: {e}")

try:
    from .homedepot import HomeDepotPortal
    PortalFactory.register("home_depot")(HomeDepotPortal)
    logger.info("✅ Portal Home Depot registrado")
except ImportError as e:
    logger.warning(f"❌ No se pudo registrar Home Depot: {e}")

try:
    from .oxxo import OxxoPortal
    PortalFactory.register("oxxo")(OxxoPortal)
    logger.info("✅ Portal Oxxo registrado")
except ImportError as e:
    logger.warning(f"❌ No se pudo registrar Oxxo: {e}")

try:
    from .farmacias_similares import FarmaciasSimilaresPortal
    PortalFactory.register("farmacias_similares")(FarmaciasSimilaresPortal)
    logger.info("✅ Portal Farmacias Similares registrado")
except ImportError as e:
    logger.warning(f"❌ No se pudo registrar Farmacias Similares: {e}")

try:
    from .pemex import PemexPortal
    PortalFactory.register("pemex")(PemexPortal)
    logger.info("✅ Portal Pemex registrado")
except ImportError as e:
    logger.warning(f"❌ No se pudo registrar Pemex: {e}")

try:
    from .bp import BPPortal
    PortalFactory.register("bp")(BPPortal)
    logger.info("✅ Portal BP registrado")
except ImportError as e:
    logger.warning(f"❌ No se pudo registrar BP: {e}")
