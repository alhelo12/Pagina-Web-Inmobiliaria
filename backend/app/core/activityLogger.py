"""
Middleware: Activity Logger

Registra automáticamente actividades de usuarios en endpoints clave.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable
import json
import re

from app.dbConfig.databaseSession import SessionLocal
from app.services import activityLogService
from app.core.security import decode_access_token

LOGGED_PATHS = {
    "POST": [
        (r"^/properties$", "property_created", "property"),
        (r"^/properties/\d+/images/upload$", "property_image_uploaded", "property"),
        (r"^/appointments$", "appointment_created", "appointment"),
        (r"^/messages/\d+$", "message_sent", "message"),
    ],
    "PUT": [
        (r"^/properties/\d+$", "property_updated", "property"),
    ],
    "PATCH": [
        (r"^/properties/\d+/approve$", "property_approved", "property"),
        (r"^/properties/\d+/reject$", "property_rejected", "property"),
        (r"^/properties/\d+/mark-sold$", "property_sold", "property"),
        (r"^/properties/\d+/take$", "property_taken", "property"),
        (r"^/appointments/\d+/confirm$", "appointment_confirmed", "appointment"),
        (r"^/appointments/\d+/cancel$", "appointment_cancelled", "appointment"),
        (r"^/appointments/\d+/complete$", "appointment_completed", "appointment"),
    ],
    "DELETE": [
        (r"^/properties/\d+$", "property_deleted", "property"),
    ],
}

SKIP_PATHS = {
    "/auth/login",
    "/auth/register",
    "/auth/register/client",
    "/auth/exchange",
    "/auth/check-email",
    "/auth/validate-password",
    "/health",
    "/health/db",
    "/",
}


class ActivityLoggerMiddleware(BaseHTTPMiddleware):
    """Middleware que registra actividades de usuarios"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        method = request.method

        if path in SKIP_PATHS:
            return await call_next(request)

        action = None
        entity_type = None
        entity_id = None

        patterns = LOGGED_PATHS.get(method, [])
        for pattern, act, etype in patterns:
            match = re.match(pattern, path)
            if match:
                action = act
                entity_type = etype
                path_parts = path.strip("/").split("/")
                if len(path_parts) >= 2 and path_parts[1].isdigit():
                    entity_id = int(path_parts[1])
                break

        if not action:
            return await call_next(request)

        user_id = None
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if token:
            try:
                payload = decode_access_token(token)
                if payload:
                    user_id = payload.get("user_id")
            except Exception:
                pass

        ip_address = request.client.host if request.client else None

        response = await call_next(request)

        if response.status_code < 400:
            try:
                db = SessionLocal()
                activityLogService.log_activity(
                    db=db,
                    user_id=user_id,
                    action=action,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    ip_address=ip_address
                )
                db.close()
            except Exception:
                pass

        return response
