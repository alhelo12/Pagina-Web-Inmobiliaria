"""
Schemas de Propiedad (Pydantic)

DTOs para validación de datos de propiedades inmobiliarias.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ==========================================
# ENUMS
# ==========================================

class PropertyTypeEnum(str, Enum):
    """Tipos de propiedad"""
    HOUSE = "house"
    APARTMENT = "apartment"
    LAND = "land"
    COMMERCIAL = "commercial"


class TransactionTypeEnum(str, Enum):
    """Tipo de operación"""
    SALE = "sale"
    RENT = "rent"


class PropertyStatusEnum(str, Enum):
    """Estados de la propiedad"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SOLD = "sold"


# ==========================================
# SCHEMAS DE IMÁGENES
# ==========================================

class PropertyImageBase(BaseModel):
    """Schema base de imagen"""
    image_url: str = Field(..., description="URL de la imagen")
    is_main: bool = Field(default=False, description="Si es la imagen principal")


class PropertyImageCreate(PropertyImageBase):
    """
    Schema para crear una imagen de propiedad
    
    Example:
        {
            "image_url": "/media/properties/1/image1.jpg",
            "is_main": true
        }
    """
    pass


class PropertyImageResponse(PropertyImageBase):
    """
    Schema de respuesta de imagen
    
    Example:
        {
            "id": 1,
            "property_id": 5,
            "image_url": "/media/properties/1/image1.jpg",
            "is_main": true,
            "created_at": "2026-02-05T10:30:00"
        }
    """
    id: int
    property_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# SCHEMA BASE DE PROPIEDAD
# ==========================================

class PropertyBase(BaseModel):
    """Schema base con campos comunes de propiedad"""
    title: str = Field(..., min_length=10, max_length=255, description="Título de la propiedad")
    description: Optional[str] = Field(None, max_length=5000, description="Descripción detallada")
    price: float = Field(..., gt=0, description="Precio en la moneda local")
    property_type: PropertyTypeEnum = Field(..., description="Tipo de propiedad")
    transaction_type: TransactionTypeEnum = Field(default=TransactionTypeEnum.SALE, description="Venta o renta")
    
    # Ubicación
    address: str = Field(..., min_length=10, max_length=500, description="Dirección completa")
    city: str = Field(..., min_length=2, max_length=100, description="Ciudad")
    latitude: float = Field(..., ge=-90, le=90, description="Latitud")
    longitude: float = Field(..., ge=-180, le=180, description="Longitud")
    
    # Características
    bedrooms: int = Field(default=0, ge=0, description="Número de recámaras")
    bathrooms: int = Field(default=0, ge=0, description="Número de baños")
    square_meters: int = Field(default=0, ge=0, description="Metros cuadrados")


# ==========================================
# SCHEMAS DE ENTRADA (Request)
# ==========================================

class PropertyCreate(PropertyBase):
    """
    Schema para crear una nueva propiedad
    
    El cliente envía esto cuando publica una propiedad.
    El sistema automáticamente:
    - Asigna submitted_by_user_id del usuario autenticado
    - Establece status = 'pending'
    
    Example:
        {
            "title": "Casa en Venta - Col. Del Valle",
            "description": "Hermosa casa con jardín",
            "price": 3500000,
            "property_type": "house",
            "transaction_type": "sale",
            "address": "Calle Insurgentes 123",
            "city": "Ciudad de México",
            "latitude": 19.3679,
            "longitude": -99.1745,
            "bedrooms": 3,
            "bathrooms": 2,
            "square_meters": 150
        }
    """
    pass


class PropertyUpdate(BaseModel):
    """
    Schema para actualizar una propiedad (todos los campos opcionales)
    
    Example:
        {
            "title": "Casa en Venta - Col. Del Valle (ACTUALIZADO)",
            "price": 3400000,
            "description": "Hermosa casa con jardín amplio"
        }
    """
    title: Optional[str] = Field(None, min_length=10, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    price: Optional[float] = Field(None, gt=0)
    property_type: Optional[PropertyTypeEnum] = None
    transaction_type: Optional[TransactionTypeEnum] = None
    address: Optional[str] = Field(None, min_length=10, max_length=500)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    bedrooms: Optional[int] = Field(None, ge=0)
    bathrooms: Optional[int] = Field(None, ge=0)
    square_meters: Optional[int] = Field(None, ge=0)


class PropertyApprove(BaseModel):
    """
    Schema para aprobar una propiedad (asesor)
    
    Example:
        {
            "advisor_id": 5
        }
    """
    advisor_id: int = Field(..., description="ID del asesor que aprueba")


class PropertyReject(BaseModel):
    """
    Schema para rechazar una propiedad
    
    Example:
        {
            "reason": "Las fotos no son claras suficientes"
        }
    """
    reason: str = Field(..., min_length=10, max_length=500, description="Razón del rechazo")


# ==========================================
# SCHEMAS DE SALIDA (Response)
# ==========================================

class PropertyOwnerResponse(BaseModel):
    """Schema simplificado del dueño de la propiedad"""
    id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class PropertyAdvisorResponse(BaseModel):
    """Schema simplificado del asesor"""
    id: int
    agency_name: Optional[str] = None
    rating: Optional[float] = None
    user: dict  # Simplificado: {id, full_name, email, phone}
    
    model_config = ConfigDict(from_attributes=True)


class PropertyResponse(PropertyBase):
    """
    Schema de respuesta de propiedad
    
    Incluye toda la información de la propiedad con relaciones.
    
    Example:
        {
            "id": 1,
            "title": "Casa en Venta",
            "description": "Hermosa casa...",
            "price": 3500000,
            "property_type": "house",
            "transaction_type": "sale",
            "address": "Calle 123",
            "city": "CDMX",
            "latitude": 19.3679,
            "longitude": -99.1745,
            "bedrooms": 3,
            "bathrooms": 2,
            "square_meters": 150,
            "status": "approved",
            "submitted_by_user_id": 5,
            "advisor_id": 2,
            "images": [...],
            "created_at": "2026-02-05T10:30:00",
            "updated_at": "2026-02-05T10:30:00"
        }
    """
    id: int
    status: PropertyStatusEnum
    submitted_by_user_id: int
    advisor_id: Optional[int] = None
    images: List[PropertyImageResponse] = []
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PropertyDetailResponse(PropertyResponse):
    """
    Schema de respuesta detallada con owner y advisor
    
    Se usa en: GET /properties/{id}
    """
    owner: Optional[PropertyOwnerResponse] = None
    advisor: Optional[PropertyAdvisorResponse] = None
    favorites_count: int = Field(default=0, description="Número de favoritos")
    
    model_config = ConfigDict(from_attributes=True)


class PropertyListResponse(BaseModel):
    """
    Schema para lista paginada de propiedades
    
    Example:
        {
            "total": 150,
            "page": 1,
            "per_page": 20,
            "properties": [...]
        }
    """
    total: int = Field(..., description="Total de propiedades")
    page: int = Field(..., ge=1, description="Página actual")
    per_page: int = Field(..., ge=1, le=100, description="Propiedades por página")
    properties: List[PropertyResponse] = Field(..., description="Lista de propiedades")


# ==========================================
# SCHEMAS DE FILTROS
# ==========================================

class PropertyFilter(BaseModel):
    """
    Schema para filtrar propiedades
    
    Se usa en: GET /properties?city=CDMX&min_price=1000000&...
    
    Example:
        {
            "city": "Ciudad de México",
            "property_type": "house",
            "transaction_type": "sale",
            "min_price": 1000000,
            "max_price": 5000000,
            "bedrooms": 3,
            "bathrooms": 2,
            "status": "approved"
        }
    """
    city: Optional[str] = None
    property_type: Optional[PropertyTypeEnum] = None
    transaction_type: Optional[TransactionTypeEnum] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    bedrooms: Optional[int] = Field(None, ge=0)
    bathrooms: Optional[int] = Field(None, ge=0)
    min_square_meters: Optional[int] = Field(None, ge=0)
    max_square_meters: Optional[int] = Field(None, ge=0)
    status: Optional[PropertyStatusEnum] = None
    
    # Búsqueda por proximidad (radio)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    radius_km: Optional[float] = Field(None, gt=0, le=50, description="Radio de búsqueda en km")


class PropertyStats(BaseModel):
    """
    Schema para estadísticas de propiedades
    
    Example:
        {
            "total": 500,
            "approved": 450,
            "pending": 30,
            "rejected": 10,
            "sold": 10,
            "average_price": 2500000,
            "by_city": {"CDMX": 200, "Guadalajara": 150, ...}
        }
    """
    total: int
    approved: int
    pending: int
    rejected: int
    sold: int
    average_price: float
    by_city: dict[str, int] = Field(default_factory=dict)
    by_type: dict[str, int] = Field(default_factory=dict)
    