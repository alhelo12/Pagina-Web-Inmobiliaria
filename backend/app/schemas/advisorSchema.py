"""
Schemas de Asesor (Pydantic)

DTOs para validación de datos de asesores inmobiliarios.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


# ==========================================
# SCHEMA BASE
# ==========================================

class AdvisorBase(BaseModel):
    """Schema base con campos comunes de asesor"""
    license_number: Optional[str] = Field(None, max_length=50, description="Número de licencia profesional")
    agency_name: Optional[str] = Field(None, max_length=100, description="Nombre de la agencia")
    profile_picture: Optional[str] = Field(None, description="URL de la foto de perfil")


# ==========================================
# SCHEMAS DE ENTRADA (Request)
# ==========================================

class AdvisorCreate(AdvisorBase):
    """
    Schema para crear perfil de asesor
    
    Se usa cuando un usuario con rol 'advisor' completa su perfil.
    El user_id se toma del usuario autenticado.
    
    Example:
        {
            "license_number": "LIC-12345",
            "agency_name": "González Propiedades",
            "profile_picture": "/media/advisors/profile.jpg"
        }
    """
    pass


class AdvisorUpdate(BaseModel):
    """
    Schema para actualizar perfil de asesor (todos los campos opcionales)
    
    Example:
        {
            "agency_name": "Nueva Agencia Inmobiliaria",
            "profile_picture": "/media/advisors/new_profile.jpg"
        }
    """
    license_number: Optional[str] = Field(None, max_length=50)
    agency_name: Optional[str] = Field(None, max_length=100)
    profile_picture: Optional[str] = None


# ==========================================
# SCHEMAS DE SALIDA (Response)
# ==========================================

class AdvisorUserResponse(BaseModel):
    """Schema simplificado del usuario asociado al asesor"""
    id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class AdvisorResponse(AdvisorBase):
    """
    Schema de respuesta de asesor
    
    Example:
        {
            "id": 1,
            "user_id": 5,
            "license_number": "LIC-12345",
            "agency_name": "González Propiedades",
            "profile_picture": "/media/advisors/profile.jpg",
            "rating": 4.85,
            "created_at": "2026-02-05T10:30:00",
            "updated_at": "2026-02-05T10:30:00"
        }
    """
    id: int
    user_id: int
    rating: float = Field(default=5.00, ge=0, le=5)
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AdvisorDetailResponse(AdvisorResponse):
    """
    Schema de respuesta detallada con información del usuario
    
    Se usa en: GET /advisors/{id}
    
    Example:
        {
            "id": 1,
            "user_id": 5,
            "user": {
                "id": 5,
                "full_name": "María González",
                "email": "maria@inmobiliaria.com",
                "phone": "5551234567"
            },
            "license_number": "LIC-12345",
            "agency_name": "González Propiedades",
            "profile_picture": "/media/advisors/profile.jpg",
            "rating": 4.85,
            "total_properties": 15,
            "active_properties": 12,
            "created_at": "2026-02-05T10:30:00",
            "updated_at": "2026-02-05T10:30:00"
        }
    """
    user: Optional[AdvisorUserResponse] = None
    total_properties: int = Field(default=0, description="Total de propiedades gestionadas")
    active_properties: int = Field(default=0, description="Propiedades activas (approved)")
    
    model_config = ConfigDict(from_attributes=True)


class AdvisorListResponse(BaseModel):
    """
    Schema para lista paginada de asesores
    
    Example:
        {
            "total": 25,
            "page": 1,
            "per_page": 10,
            "advisors": [...]
        }
    """
    total: int = Field(..., description="Total de asesores")
    page: int = Field(..., ge=1, description="Página actual")
    per_page: int = Field(..., ge=1, le=100, description="Asesores por página")
    advisors: list[AdvisorDetailResponse] = Field(..., description="Lista de asesores")


# ==========================================
# SCHEMAS DE ESTADÍSTICAS
# ==========================================

class AdvisorStats(BaseModel):
    """
    Schema para estadísticas de un asesor
    
    Example:
        {
            "advisor_id": 1,
            "total_properties": 20,
            "properties_approved": 18,
            "properties_pending": 2,
            "properties_sold": 5,
            "total_appointments": 30,
            "completed_appointments": 25,
            "average_rating": 4.85,
            "total_sales_value": 50000000
        }
    """
    advisor_id: int
    total_properties: int = 0
    properties_approved: int = 0
    properties_pending: int = 0
    properties_sold: int = 0
    total_appointments: int = 0
    completed_appointments: int = 0
    average_rating: float = 5.00
    total_sales_value: float = 0.0


class AdvisorRanking(BaseModel):
    """
    Schema para ranking de asesores
    
    Se usa para mostrar top asesores por ventas, rating, etc.
    
    Example:
        {
            "advisor": {...},
            "rank": 1,
            "total_sales": 10,
            "total_value": 35000000,
            "average_rating": 4.9
        }
    """
    advisor: AdvisorDetailResponse
    rank: int = Field(..., ge=1, description="Posición en el ranking")
    total_sales: int = Field(default=0, description="Total de ventas realizadas")
    total_value: float = Field(default=0.0, description="Valor total de ventas")
    average_rating: float = Field(default=5.00, ge=0, le=5, description="Rating promedio")
    