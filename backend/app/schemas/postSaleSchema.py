"""
Schemas de Post-Venta (Pydantic)

DTOs para validación de datos de entrada y salida
relacionados con seguimiento post-venta.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


# ==========================================
# ENUMS
# ==========================================

class FollowupTypeEnum(str, Enum):
    """Tipos de seguimiento post-venta"""
    SATISFACTION_SURVEY = "satisfaction_survey"
    CHECK_IN_CALL = "check_in_call"
    REFERRAL_REQUEST = "referral_request"
    MAINTENANCE_REMINDER = "maintenance_reminder"


class FollowupStatusEnum(str, Enum):
    """Estados del seguimiento"""
    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"


# ==========================================
# SCHEMA BASE
# ==========================================

class PostSaleFollowupBase(BaseModel):
    """Schema base con campos comunes"""
    followup_type: FollowupTypeEnum = Field(..., description="Tipo de seguimiento")
    notes: Optional[str] = Field(None, max_length=2000, description="Notas adicionales")
    satisfaction_score: Optional[int] = Field(None, ge=1, le=5, description="Puntuación 1-5")


# ==========================================
# SCHEMAS DE ENTRADA (Request)
# ==========================================

class PostSaleFollowupCreate(BaseModel):
    """Schema para crear un seguimiento manualmente"""
    property_id: int = Field(..., ge=1, description="ID de la propiedad vendida")
    client_id: int = Field(..., ge=1, description="ID del cliente")
    advisor_id: Optional[int] = Field(None, ge=1, description="ID del asesor")
    followup_type: FollowupTypeEnum = Field(..., description="Tipo de seguimiento")
    scheduled_date: datetime = Field(..., description="Fecha programada")
    notes: Optional[str] = Field(None, max_length=2000)


class PostSaleFollowupComplete(BaseModel):
    """Schema para completar un seguimiento"""
    notes: Optional[str] = Field(None, max_length=2000, description="Notas del seguimiento")
    satisfaction_score: Optional[int] = Field(None, ge=1, le=5, description="Puntuación de satisfacción")


class PostSaleFollowupSkip(BaseModel):
    """Schema para omitir un seguimiento"""
    reason: str = Field(..., min_length=1, max_length=500, description="Razón para omitir")


# ==========================================
# SCHEMAS DE SALIDA (Response)
# ==========================================

class PostSaleFollowupPropertyResponse(BaseModel):
    """Schema simplificado de la propiedad"""
    id: int
    title: str
    address: str
    city: str
    price: float
    property_type: str

    model_config = ConfigDict(from_attributes=True)


class PostSaleFollowupClientResponse(BaseModel):
    """Schema simplificado del cliente"""
    id: int
    full_name: str
    email: str
    phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PostSaleFollowupAdvisorResponse(BaseModel):
    """Schema simplificado del asesor"""
    id: int
    user_id: int
    agency_name: Optional[str] = None
    rating: float
    user: PostSaleFollowupClientResponse

    model_config = ConfigDict(from_attributes=True)


class PostSaleFollowupResponse(PostSaleFollowupBase):
    """Schema de respuesta de seguimiento"""
    id: int
    property_id: int
    client_id: int
    advisor_id: Optional[int]
    sale_date: datetime
    scheduled_date: datetime
    completed_date: Optional[datetime]
    status: FollowupStatusEnum
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostSaleFollowupDetailResponse(PostSaleFollowupResponse):
    """Schema de respuesta detallada con relaciones"""
    property: Optional[PostSaleFollowupPropertyResponse] = Field(
        None, validation_alias="related_property"
    )
    client: Optional[PostSaleFollowupClientResponse] = None
    advisor: Optional[PostSaleFollowupAdvisorResponse] = None

    model_config = ConfigDict(from_attributes=True)


class PostSaleFollowupListResponse(BaseModel):
    """Schema para lista paginada de seguimientos"""
    total: int = Field(..., description="Total de seguimientos")
    page: int = Field(..., ge=1, description="Página actual")
    per_page: int = Field(..., ge=1, le=100, description="Seguimientos por página")
    followups: list[PostSaleFollowupDetailResponse] = Field(..., description="Lista de seguimientos")


# ==========================================
# SCHEMAS DE ESTADÍSTICAS
# ==========================================

class PostSaleStats(BaseModel):
    """Schema para estadísticas post-venta"""
    total_followups: int = 0
    pending: int = 0
    completed: int = 0
    skipped: int = 0
    avg_satisfaction_score: float = 0.0
    total_surveys: int = 0
    completed_surveys: int = 0
    total_referrals: int = 0
    completed_referrals: int = 0


class PostSaleAdvisorStats(BaseModel):
    """Schema para estadísticas post-venta por asesor"""
    advisor_id: int
    advisor_name: str
    total_followups: int = 0
    completed: int = 0
    avg_satisfaction_score: float = 0.0
    total_sales: int = 0


# ==========================================
# SCHEMAS DE FILTROS
# ==========================================

class PostSaleFollowupFilter(BaseModel):
    """Schema para filtrar seguimientos"""
    status: Optional[FollowupStatusEnum] = None
    followup_type: Optional[FollowupTypeEnum] = None
    client_id: Optional[int] = Field(None, ge=1)
    advisor_id: Optional[int] = Field(None, ge=1)
    property_id: Optional[int] = Field(None, ge=1)
    date_from: Optional[datetime] = Field(None, description="Fecha desde")
    date_to: Optional[datetime] = Field(None, description="Fecha hasta")


# ==========================================
# UTILIDADES
# ==========================================

FOLLOWUP_TYPE_CONFIG = {
    "satisfaction_survey": {
        "icon": "📋",
        "label": "Encuesta de Satisfacción",
        "days_after_sale": 7,
        "description": "Encuesta para medir satisfacción del cliente"
    },
    "check_in_call": {
        "icon": "📞",
        "label": "Llamada de Seguimiento",
        "days_after_sale": 30,
        "description": "Llamada para verificar adaptación del cliente"
    },
    "referral_request": {
        "icon": "🤝",
        "label": "Solicitud de Referido",
        "days_after_sale": 60,
        "description": "Solicitar referidos al cliente satisfecho"
    },
    "maintenance_reminder": {
        "icon": "🔧",
        "label": "Recordatorio de Mantenimiento",
        "days_after_sale": 90,
        "description": "Recordar mantenimiento de la propiedad"
    }
}


def get_followup_type_info(followup_type: str) -> dict:
    """Retorna la información de un tipo de seguimiento"""
    return FOLLOWUP_TYPE_CONFIG.get(followup_type, {
        "icon": "📌",
        "label": "Seguimiento",
        "days_after_sale": 0,
        "description": "Seguimiento post-venta"
    })
