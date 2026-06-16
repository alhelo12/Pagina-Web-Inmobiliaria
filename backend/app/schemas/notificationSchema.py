"""
Schemas de Notificación (Pydantic)

DTOs (Data Transfer Objects) para validación de datos
de entrada y salida relacionados con notificaciones.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


# ==========================================
# SCHEMA BASE
# ==========================================

class NotificationBase(BaseModel):
    """Schema base con campos comunes de notificación"""
    type: str = Field(..., description="Tipo de notificación")
    title: str = Field(..., min_length=1, max_length=255, description="Título")
    message: str = Field(..., min_length=1, description="Mensaje")


# ==========================================
# SCHEMAS DE ENTRADA (Request)
# ==========================================


class NotificationCreate(NotificationBase):
    """Schema para crear una notificación manualmente"""
    user_id: int = Field(..., description="ID del usuario que recibe")
    property_id: Optional[int] = Field(None, description="ID de la propiedad relacionada")


# ==========================================
# SCHEMAS DE SALIDA (Response)
# ==========================================


class NotificationResponse(NotificationBase):
    """Schema para devolver una notificación"""
    id: int
    user_id: int
    property_id: Optional[int]
    is_read: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    """Schema para lista de notificaciones"""
    notifications: list[NotificationResponse]
    total: int
    unread_count: int


class NotificationCountResponse(BaseModel):
    """Schema para contador de notificaciones no leídas"""
    unread_count: int


class NotificationMarkReadResponse(BaseModel):
    """Schema para marcar notificación como leída"""
    id: int
    is_read: bool
    message: str = "Notificación actualizada correctamente"


# ==========================================
# SCHEMAS DE ACTUALIZACIÓN (PATCH)
# ==========================================


class NotificationMarkRead(BaseModel):
    """Schema para marcar notificación como leída"""
    is_read: bool = Field(True, description="Estado de lectura")


# ==========================================
# UTILIDADES
# ==========================================

NOTIFICATION_TYPES = {
    "advisor_assigned": {
        "icon": "user",
        "color": "#d6a848",
        "label": "Asesor asignado",
        "roles": ["client"],
        "description": "Un asesor tomó la propiedad"
    },
    "approved": {
        "icon": "check",
        "color": "#22c55e",
        "label": "Aprobada",
        "roles": ["client"],
        "description": "Propiedad aprobada"
    },
    "rejected": {
        "icon": "x-circle",
        "color": "#dc2626",
        "label": "Rechazada",
        "roles": ["client"],
        "description": "Propiedad rechazada"
    },
    "sold": {
        "icon": "home",
        "color": "#7c3aed",
        "label": "Vendida / Rentada",
        "roles": ["client"],
        "description": "Propiedad vendida/rentada"
    },
    "property_updated": {
        "icon": "pencil",
        "color": "#3b82f6",
        "label": "Actualizada",
        "roles": ["client"],
        "description": "Propiedad actualizada"
    },
    "appointment_confirmed": {
        "icon": "calendar",
        "color": "#22c55e",
        "label": "Cita confirmada",
        "roles": ["client", "advisor"],
        "description": "Cita confirmada"
    },
    "appointment_cancelled": {
        "icon": "x-circle",
        "color": "#dc2626",
        "label": "Cita cancelada",
        "roles": ["client", "advisor"],
        "description": "Cita cancelada"
    },
    "appointment_reminder": {
        "icon": "calendar",
        "color": "#f59e0b",
        "label": "Recordatorio",
        "roles": ["client", "advisor"],
        "description": "Recordatorio de cita"
    },
    "post_sale_survey": {
        "icon": "envelope",
        "color": "#3b82f6",
        "label": "Encuesta",
        "roles": ["client"],
        "description": "Encuesta de satisfacción post-venta"
    },
    "post_sale_checkin": {
        "icon": "envelope",
        "color": "#8b5cf6",
        "label": "Seguimiento",
        "roles": ["client"],
        "description": "Seguimiento post-venta"
    },
    "message_received": {
        "icon": "chat",
        "color": "#6366f1",
        "label": "Nuevo mensaje",
        "roles": ["client", "advisor"],
        "description": "Nuevo mensaje recibido"
    }
}


def get_notification_type_info(notification_type: str) -> dict:
    """Retorna la información de un tipo de notificación"""
    return NOTIFICATION_TYPES.get(notification_type, {
        "icon": "📢",
        "color": "#65717e",
        "description": "Notificación"
    })