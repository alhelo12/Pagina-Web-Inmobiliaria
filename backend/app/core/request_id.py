"""
Core: Request ID Middleware

Middleware para propagar request IDs a través de la aplicación.
"""

import uuid
from contextvars import ContextVar
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def get_request_id() -> Optional[str]:
    return request_id_var.get()


def set_request_id(request_id: str) -> None:
    request_id_var.set(request_id)


def clear_request_id() -> None:
    request_id_var.set(None)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware que extrae o genera request_id y lo propaga:
    - En headers de respuesta (X-Request-ID)
    - En contextvar para logging estructurado
    """

    async def dispatch(self, request: Request, call_next):
        # Extraer o generar request ID
        request_id = request.headers.get("x-request-id")
        if not request_id:
            request_id = str(uuid.uuid4())[:8]
        
        set_request_id(request_id)
        try:
            response = await call_next(request)
            response.headers["x-request-id"] = request_id
            return response
        finally:
            clear_request_id()
