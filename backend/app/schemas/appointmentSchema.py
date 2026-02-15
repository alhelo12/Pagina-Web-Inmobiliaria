"""
Schemas de Cita (Pydantic)

DTOs para validación de datos de citas entre clientes y asesores.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


# ==========================================
# ENUMS
# ==========================================

class AppointmentTypeEnum(str, Enum):
    """Tipos de cita"""
    VIEWING = "viewing"           # Cliente ve una propiedad
    INSPECTION = "inspection"     # Asesor inspecciona propiedad del vendedor


class AppointmentStatusEnum(str, Enum):
    """Estados de la cita"""
    PENDING = "pending"           # Pendiente de confirmación
    CONFIRMED = "confirmed"       # Confirmada
    COMPLETED = "completed"       # Completada
    CANCELLED = "cancelled"       # Cancelada


# ==========================================
# SCHEMA BASE
# ==========================================

class AppointmentBase(BaseModel):
    """Schema base con campos comunes de cita"""
    scheduled_date: datetime = Field(..., description="Fecha y hora de la cita")
    appointment_type: AppointmentTypeEnum = Field(default=AppointmentTypeEnum.VIEWING, description="Tipo de cita")
    notes: Optional[str] = Field(None, max_length=1000, description="Notas adicionales")
    
    @field_validator('scheduled_date')
    @classmethod
    def validate_future_date(cls, v):
        """Validar que la fecha sea futura"""
        if v < datetime.now():
            raise ValueError('La fecha de la cita debe ser futura')
        return v


# ==========================================
# SCHEMAS DE ENTRADA (Request)
# ==========================================

class AppointmentCreate(AppointmentBase):
    """
    Schema para crear una nueva cita
    
    El client_id se toma del usuario autenticado.
    
    Example (Cliente agenda para ver propiedad):
        {
            "advisor_id": 5,
            "property_id": 10,
            "scheduled_date": "2026-02-10T15:00:00",
            "appointment_type": "viewing",
            "notes": "Me interesa conocer el jardín"
        }
    
    Example (Cliente agenda inspección de su propiedad):
        {
            "advisor_id": 5,
            "property_id": 15,
            "scheduled_date": "2026-02-08T10:00:00",
            "appointment_type": "inspection",
            "notes": "Disponible todo el día"
        }
    """
    advisor_id: int = Field(..., ge=1, description="ID del asesor")
    property_id: Optional[int] = Field(None, ge=1, description="ID de la propiedad (opcional)")


class AppointmentUpdate(BaseModel):
    """
    Schema para actualizar una cita (todos los campos opcionales)
    
    Solo el cliente o el asesor pueden actualizar sus propias citas.
    
    Example:
        {
            "scheduled_date": "2026-02-10T16:00:00",
            "notes": "Preferiblemente por la tarde"
        }
    """
    scheduled_date: Optional[datetime] = None
    appointment_type: Optional[AppointmentTypeEnum] = None
    notes: Optional[str] = Field(None, max_length=1000)
    
    @field_validator('scheduled_date')
    @classmethod
    def validate_future_date(cls, v):
        """Validar que la fecha sea futura"""
        if v and v < datetime.now():
            raise ValueError('La fecha de la cita debe ser futura')
        return v


class AppointmentConfirm(BaseModel):
    """
    Schema para confirmar una cita (Asesor)
    
    Example:
        {
            "notes": "Confirmado, te espero a las 3pm"
        }
    """
    notes: Optional[str] = Field(None, max_length=500, description="Nota de confirmación")


class AppointmentComplete(BaseModel):
    """
    Schema para marcar cita como completada (Asesor)
    
    Example:
        {
            "notes": "Visita realizada exitosamente. Cliente muy interesado."
        }
    """
    notes: Optional[str] = Field(None, max_length=1000, description="Notas sobre la cita completada")


class AppointmentCancel(BaseModel):
    """
    Schema para cancelar una cita
    
    Example:
        {
            "reason": "El cliente no puede asistir por motivos personales"
        }
    """
    reason: str = Field(..., min_length=10, max_length=500, description="Razón de la cancelación")


# ==========================================
# SCHEMAS DE SALIDA (Response)
# ==========================================

class AppointmentClientResponse(BaseModel):
    """Schema simplificado del cliente"""
    id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class AppointmentAdvisorResponse(BaseModel):
    """Schema simplificado del asesor"""
    id: int
    user_id: int
    agency_name: Optional[str] = None
    rating: float
    user: dict  # {id, full_name, email, phone}
    
    model_config = ConfigDict(from_attributes=True)


class AppointmentPropertyResponse(BaseModel):
    """Schema simplificado de la propiedad"""
    id: int
    title: str
    address: str
    city: str
    price: float
    property_type: str
    status: str
    
    model_config = ConfigDict(from_attributes=True)


class AppointmentResponse(AppointmentBase):
    """
    Schema de respuesta de cita
    
    Example:
        {
            "id": 1,
            "client_id": 10,
            "advisor_id": 5,
            "property_id": 15,
            "scheduled_date": "2026-02-10T15:00:00",
            "appointment_type": "viewing",
            "status": "confirmed",
            "notes": "Me interesa el jardín",
            "created_at": "2026-02-05T10:30:00",
            "updated_at": "2026-02-05T10:30:00"
        }
    """
    id: int
    client_id: int
    advisor_id: int
    property_id: Optional[int] = None
    status: AppointmentStatusEnum
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AppointmentDetailResponse(AppointmentResponse):
    """
    Schema de respuesta detallada con relaciones
    
    Se usa en: GET /appointments/{id}
    
    Example:
        {
            "id": 1,
            "client": {...},
            "advisor": {...},
            "related_property": {...},
            "scheduled_date": "2026-02-10T15:00:00",
            "appointment_type": "viewing",
            "status": "confirmed",
            "notes": "Me interesa el jardín",
            "created_at": "2026-02-05T10:30:00",
            "updated_at": "2026-02-05T10:30:00"
        }
    """
    client: Optional[AppointmentClientResponse] = None
    advisor: Optional[AppointmentAdvisorResponse] = None
    related_property: Optional[AppointmentPropertyResponse] = None
    
    model_config = ConfigDict(from_attributes=True)


class AppointmentListResponse(BaseModel):
    """
    Schema para lista paginada de citas
    
    Example:
        {
            "total": 50,
            "page": 1,
            "per_page": 10,
            "appointments": [...]
        }
    """
    total: int = Field(..., description="Total de citas")
    page: int = Field(..., ge=1, description="Página actual")
    per_page: int = Field(..., ge=1, le=100, description="Citas por página")
    appointments: list[AppointmentDetailResponse] = Field(..., description="Lista de citas")


# ==========================================
# SCHEMAS DE FILTROS
# ==========================================

class AppointmentFilter(BaseModel):
    """
    Schema para filtrar citas
    
    Se usa en: GET /appointments?status=pending&appointment_type=viewing
    
    Example:
        {
            "status": "confirmed",
            "appointment_type": "viewing",
            "client_id": 10,
            "advisor_id": 5,
            "property_id": 15,
            "date_from": "2026-02-01T00:00:00",
            "date_to": "2026-02-28T23:59:59"
        }
    """
    status: Optional[AppointmentStatusEnum] = None
    appointment_type: Optional[AppointmentTypeEnum] = None
    client_id: Optional[int] = Field(None, ge=1)
    advisor_id: Optional[int] = Field(None, ge=1)
    property_id: Optional[int] = Field(None, ge=1)
    date_from: Optional[datetime] = Field(None, description="Fecha desde")
    date_to: Optional[datetime] = Field(None, description="Fecha hasta")


# ==========================================
# SCHEMAS DE ESTADÍSTICAS
# ==========================================

class AppointmentStats(BaseModel):
    """
    Schema para estadísticas de citas
    
    Example:
        {
            "total": 100,
            "pending": 20,
            "confirmed": 50,
            "completed": 25,
            "cancelled": 5,
            "by_type": {"viewing": 80, "inspection": 20},
            "upcoming": 30,
            "today": 5
        }
    """
    total: int = 0
    pending: int = 0
    confirmed: int = 0
    completed: int = 0
    cancelled: int = 0
    by_type: dict[str, int] = Field(default_factory=dict)
    upcoming: int = Field(default=0, description="Citas futuras")
    today: int = Field(default=0, description="Citas de hoy")


class AppointmentCalendar(BaseModel):
    """
    Schema para vista de calendario
    
    Agrupa citas por fecha para mostrar en un calendario.
    
    Example:
        {
            "date": "2026-02-10",
            "appointments": [...]
        }
    """
    date: str = Field(..., description="Fecha en formato YYYY-MM-DD")
    appointments: list[AppointmentResponse] = Field(..., description="Citas de ese día")
    