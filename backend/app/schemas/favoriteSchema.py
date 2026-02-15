"""
Schemas de Favorito (Pydantic)

DTOs para validación de datos de propiedades favoritas.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


# ==========================================
# SCHEMAS DE ENTRADA (Request)
# ==========================================

class FavoriteCreate(BaseModel):
    """
    Schema para marcar una propiedad como favorita
    
    El user_id se toma del usuario autenticado.
    
    Example:
        {
            "property_id": 15
        }
    """
    property_id: int = Field(..., ge=1, description="ID de la propiedad a marcar como favorita")


class FavoriteDelete(BaseModel):
    """
    Schema para eliminar una propiedad de favoritos
    
    Example:
        {
            "property_id": 15
        }
    """
    property_id: int = Field(..., ge=1, description="ID de la propiedad a eliminar de favoritos")


# ==========================================
# SCHEMAS DE SALIDA (Response)
# ==========================================

class FavoritePropertyResponse(BaseModel):
    """
    Schema simplificado de la propiedad favorita
    
    Incluye solo la información esencial de la propiedad.
    """
    id: int
    title: str
    price: float
    property_type: str
    transaction_type: str
    city: str
    address: str
    bedrooms: int
    bathrooms: int
    square_meters: int
    status: str
    main_image_url: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class FavoriteResponse(BaseModel):
    """
    Schema de respuesta de favorito
    
    Example:
        {
            "id": 1,
            "user_id": 10,
            "property_id": 15,
            "created_at": "2026-02-05T10:30:00"
        }
    """
    id: int
    user_id: int
    property_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class FavoriteDetailResponse(FavoriteResponse):
    """
    Schema de respuesta detallada con información de la propiedad
    
    Se usa en: GET /favorites (lista de favoritos del usuario)
    
    Example:
        {
            "id": 1,
            "user_id": 10,
            "property_id": 15,
            "favorited_property": {
                "id": 15,
                "title": "Casa en Venta - Col. Del Valle",
                "price": 3500000,
                "property_type": "house",
                "transaction_type": "sale",
                "city": "CDMX",
                "address": "Calle Insurgentes 123",
                "bedrooms": 3,
                "bathrooms": 2,
                "square_meters": 150,
                "status": "approved",
                "main_image_url": "/media/properties/15/main.jpg"
            },
            "created_at": "2026-02-05T10:30:00"
        }
    """
    favorited_property: Optional[FavoritePropertyResponse] = None
    
    model_config = ConfigDict(from_attributes=True)


class FavoriteListResponse(BaseModel):
    """
    Schema para lista paginada de favoritos
    
    Example:
        {
            "total": 25,
            "page": 1,
            "per_page": 10,
            "favorites": [...]
        }
    """
    total: int = Field(..., description="Total de favoritos")
    page: int = Field(..., ge=1, description="Página actual")
    per_page: int = Field(..., ge=1, le=100, description="Favoritos por página")
    favorites: list[FavoriteDetailResponse] = Field(..., description="Lista de favoritos")


# ==========================================
# SCHEMAS DE OPERACIONES
# ==========================================

class FavoriteToggle(BaseModel):
    """
    Schema para alternar estado de favorito (agregar/quitar)
    
    Si existe, se elimina. Si no existe, se crea.
    
    Example:
        {
            "property_id": 15
        }
    """
    property_id: int = Field(..., ge=1, description="ID de la propiedad")


class FavoriteToggleResponse(BaseModel):
    """
    Schema de respuesta al alternar favorito
    
    Example (agregado):
        {
            "property_id": 15,
            "is_favorited": true,
            "message": "Propiedad agregada a favoritos"
        }
    
    Example (eliminado):
        {
            "property_id": 15,
            "is_favorited": false,
            "message": "Propiedad eliminada de favoritos"
        }
    """
    property_id: int
    is_favorited: bool = Field(..., description="True si está en favoritos, False si fue eliminado")
    message: str = Field(..., description="Mensaje descriptivo de la acción")


class FavoriteCheck(BaseModel):
    """
    Schema para verificar si una propiedad está en favoritos
    
    Example:
        {
            "property_id": 15,
            "is_favorited": true
        }
    """
    property_id: int
    is_favorited: bool = Field(..., description="True si está en favoritos del usuario")


# ==========================================
# SCHEMAS DE ESTADÍSTICAS
# ==========================================

class FavoriteStats(BaseModel):
    """
    Schema para estadísticas de favoritos
    
    Example (para un usuario):
        {
            "total_favorites": 15,
            "by_city": {"CDMX": 8, "Guadalajara": 5, "Monterrey": 2},
            "by_type": {"house": 10, "apartment": 5},
            "average_price": 3200000,
            "price_range": {"min": 1500000, "max": 8000000}
        }
    """
    total_favorites: int = Field(default=0, description="Total de propiedades favoritas")
    by_city: dict[str, int] = Field(default_factory=dict, description="Favoritos por ciudad")
    by_type: dict[str, int] = Field(default_factory=dict, description="Favoritos por tipo")
    average_price: float = Field(default=0.0, description="Precio promedio de favoritos")
    price_range: dict[str, float] = Field(default_factory=dict, description="Rango de precios (min, max)")
    