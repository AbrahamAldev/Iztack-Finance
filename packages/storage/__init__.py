"""Sistema Finanzas MX - Storage Package
Almacenamiento local, cifrado, multi-cloud y retención."""
from .local import LocalStorage
from .sensitive import SensitiveStorage
from .email_storage import EmailStorage
from .retention import RetentionManager