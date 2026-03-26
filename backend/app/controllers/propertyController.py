"""
Controller: Properties

Endpoints para gestión de propiedades inmobiliarias.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.dbConfig.databaseSession import get_db
from app.services import propertyService
from app.core.dependencies import (
    get_current_user,
    require_advisor,
    verify_user_owns_resource
)
from app.schemas import (
    PropertyCreate,
    PropertyUpdate,
    PropertyResponse,
    PropertyListResponse,
    PropertySearchFilters,
    NearbySearchParams
)
from app.models import User

router = APIRouter(
    prefix="/properties",
    tags=["Properties"]
)


# ==========================================
# ENDPOINTS PÚBLICOS (sin autenticación)
# ==========================================

@router.get("", response_model=PropertyListResponse)
def get_properties(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de registros"),
    db: Session = Depends(get_db)
):
    """
    Listar todas las propiedades aprobadas (público)
    
    Solo muestra propiedades con status='approved'.
    Incluye paginación.
    """
    result = propertyService.get_properties(db, skip=skip, limit=limit)
    return result


@router.get("/{property_id}", response_model=PropertyResponse)
def get_property(
    property_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener detalle de una propiedad (público)
    
    Muestra información completa de la propiedad incluyendo:
    - Datos básicos
    - Usuario que la publicó
    - Asesor asignado (si existe)
    - Imágenes
    """
    property_obj = propertyService.get_property_by_id(db, property_id)
    
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propiedad no encontrada"
        )
    
    return property_obj


@router.post("/search", response_model=PropertyListResponse)
def search_properties(
    filters: PropertySearchFilters,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Búsqueda avanzada de propiedades (público)
    
    Filtros disponibles:
    - city: Buscar por ciudad
    - property_type: house, apartment, land, commercial
    - transaction_type: sale, rent
    - min_price, max_price: Rango de precio
    - bedrooms: Recámaras mínimas
    - bathrooms: Baños mínimos
    - min_square_meters, max_square_meters: Rango de m²
    - status: pending, approved, rejected, sold
    """
    result = propertyService.search_properties(db, filters, skip=skip, limit=limit)
    return result


@router.get("/nearby/search", response_model=PropertyListResponse)
def search_nearby_properties(
    latitude: float = Query(..., description="Latitud del punto de referencia"),
    longitude: float = Query(..., description="Longitud del punto de referencia"),
    radius_km: float = Query(5.0, ge=0.1, le=50, description="Radio de búsqueda en kilómetros"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Búsqueda por proximidad geográfica (público)
    
    Encuentra propiedades dentro de un radio especificado.
    Usa la fórmula de Haversine para calcular distancias.
    """
    params = NearbySearchParams(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km
    )
    result = propertyService.search_nearby_properties(db, params, skip=skip, limit=limit)
    return result


# ==========================================
# ENDPOINTS PROTEGIDOS (requieren autenticación)
# ==========================================

@router.post("", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
def create_property(
    property_data: PropertyCreate,
    user_id: int = Query(..., description="ID del usuario que publica"),
    current_user: User = Depends(get_current_user),  # 🔐 Requiere token
    db: Session = Depends(get_db)
):
    """
    Crear nueva propiedad (requiere autenticación)
    
    La propiedad se crea con status='pending' y requiere aprobación.
    
    Validaciones:
    - Usuario debe estar autenticado
    - Usuario debe ser el mismo que user_id (o ser admin)
    """
    # Verificar que el usuario sea dueño o admin
    verify_user_owns_resource(user_id, current_user)
    
    property_obj = propertyService.create_property(db, property_data, user_id)
    return property_obj


@router.put("/{property_id}", response_model=PropertyResponse)
def update_property(
    property_id: int,
    property_data: PropertyUpdate,
    current_user: User = Depends(get_current_user),  # 🔐 Requiere token
    db: Session = Depends(get_db)
):
    """
    Actualizar propiedad existente (requiere autenticación)
    
    Solo el dueño de la propiedad o un admin puede actualizarla.
    
    Validaciones:
    - Usuario autenticado
    - Usuario es dueño o admin
    """
    # Obtener propiedad
    property_obj = propertyService.get_property_by_id(db, property_id)
    
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propiedad no encontrada"
        )
    
    # Verificar ownership
    verify_user_owns_resource(property_obj.submitted_by_user_id, current_user)
    
    # Actualizar
    updated_property = propertyService.update_property(db, property_id, property_data)
    return updated_property


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(
    property_id: int,
    current_user: User = Depends(get_current_user),  # 🔐 Requiere token
    db: Session = Depends(get_db)
):
    """
    Eliminar propiedad (requiere autenticación)
    
    Solo el dueño o admin puede eliminar.
    
    Validaciones:
    - Usuario autenticado
    - Usuario es dueño o admin
    """
    # Obtener propiedad
    property_obj = propertyService.get_property_by_id(db, property_id)
    
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propiedad no encontrada"
        )
    
    # Verificar ownership
    verify_user_owns_resource(property_obj.submitted_by_user_id, current_user)
    
    # Eliminar
    propertyService.delete_property(db, property_id)
    return None


# ==========================================
# ENDPOINTS SOLO PARA ADVISORS
# ==========================================

@router.patch("/{property_id}/approve", response_model=PropertyResponse)
def approve_property(
    property_id: int,
    current_user: User = Depends(require_advisor),  # 🔐 Solo advisors
    db: Session = Depends(get_db)
):
    """
    Aprobar propiedad (solo advisors)
    
    Cambia el status de 'pending' a 'approved'.
    Asigna el advisor que aprobó la propiedad.
    
    Requiere:
    - Token JWT válido
    - Rol de advisor
    """
    # Obtener advisor_id del usuario autenticado
    if not current_user.advisor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no tiene perfil de advisor"
        )
    
    property_obj = propertyService.approve_property(
        db,
        property_id,
        current_user.advisor.id
    )
    
    return property_obj


@router.patch("/{property_id}/reject", response_model=PropertyResponse)
def reject_property(
    property_id: int,
    reason: Optional[str] = Query(None, description="Razón del rechazo"),
    current_user: User = Depends(require_advisor),  # 🔐 Solo advisors
    db: Session = Depends(get_db)
):
    """
    Rechazar propiedad (solo advisors)
    
    Cambia el status de 'pending' a 'rejected'.
    Opcionalmente se puede proporcionar una razón.
    
    Requiere:
    - Token JWT válido
    - Rol de advisor
    """
    property_obj = propertyService.reject_property(db, property_id, reason)
    return property_obj


@router.patch("/{property_id}/mark-sold", response_model=PropertyResponse)
def mark_property_sold(
    property_id: int,
    current_user: User = Depends(require_advisor),  # 🔐 Solo advisors
    db: Session = Depends(get_db)
):
    """
    Marcar propiedad como vendida (solo advisors)
    
    Cambia el status a 'sold'.
    
    Requiere:
    - Token JWT válido
    - Rol de advisor
    """
    property_obj = propertyService.mark_as_sold(db, property_id)
    return property_obj


# ==========================================
# ENDPOINTS DE ESTADÍSTICAS
# ==========================================

@router.get("/stats/summary")
def get_properties_summary(
    current_user: User = Depends(require_advisor),  # 🔐 Solo advisors/admin
    db: Session = Depends(get_db)
):
    """
    Obtener resumen de propiedades (solo advisors/admin)
    
    Estadísticas generales de todas las propiedades.
    """
    stats = propertyService.get_property_stats(db)
    return stats


@router.get("/pending/list", response_model=PropertyListResponse)
def get_pending_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_advisor),  # 🔐 Solo advisors/admin
    db: Session = Depends(get_db)
):
    """
    Listar propiedades pendientes de aprobación (solo advisors/admin)
    
    Muestra todas las propiedades con status='pending'.
    """
    result = propertyService.get_pending_properties(db, skip=skip, limit=limit)
    return result
