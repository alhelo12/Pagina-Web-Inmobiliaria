"""
Configuración de Rate Limiting

Límites de peticiones por IP para proteger la API contra abuso.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"],
    storage_uri="memory://"
)

RATE_LIMITS = {
    "auth_login": "5 per minute",
    "auth_register": "3 per hour",
    "auth_exchange": "10 per minute",
    "property_create": "20 per hour",
    "appointment_create": "10 per hour",
    "message_send": "30 per minute",
    "upload_image": "20 per hour",
}
