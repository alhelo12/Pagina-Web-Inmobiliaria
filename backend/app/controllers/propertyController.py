"""
Controller: Property

Endpoints para gestión de propiedades.
Incluye CRUD, sistema de aprobación, búsquedas y estadísticas.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.dbConfig.databaseSession import get_db
from app.services import propertyService
from app.schemas import (
    PropertyCreate,
    PropertyUpdate,
    PropertyResponse,
    PropertyDetailResponse,
    PropertyListResponse,
    PropertyFilter,
    PropertyImageCreate,
    PropertyImageResponse
)

router = APIRouter(
    prefix="/properties",
    tags=["Properties"]
)


# ==========================================
# CRUD BÁSICO
# ==========================================

@router.get("", response_model=PropertyListResponse)
def get_properties(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de registros"),
    status: Optional[str] = Query(None, description="Filtrar por estado (pending, approved, rejected, sold)"),
    user_id: Optional[int] = Query(None, description="Filtrar por usuario que publicó"),
    db: Session = Depends(get_db)
):
    """
    Listar propiedades con filtros básicos
    
    Query params:
    - **skip**: Paginación
    - **limit**: Máximo de registros (1-100)
    - **status**: Estado de la propiedad
    - **user_id**: Propiedades de un usuario específico
    
    Retorna:
    - Lista de propiedades
    - Total para paginación
    """
    properties = propertyService.get_properties(
        db,
        skip=skip,
        limit=limit,
        status=status,
        user_id=user_id
    )
    
    total = propertyService.count_properties(
        db,
        status=status,
        user_id=user_id
    )
    
    return {
        "properties": properties,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/approved", response_model=PropertyListResponse)
def get_approved_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Listar propiedades aprobadas (visibles públicamente)
    
    Solo retorna propiedades con status='approved'.
    Útil para el catálogo público.
    """
    properties = propertyService.get_approved_properties(db, skip, limit)
    total = propertyService.count_properties(db, status='approved')
    
    return {
        "properties": properties,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/pending", response_model=PropertyListResponse)
def get_pending_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Listar propiedades pendientes de aprobación
    
    Solo retorna propiedades con status='pending'.
    Útil para el panel de asesores.
    
    Nota: Con JWT, solo asesores y admins podrán ver este endpoint.
    """
    properties = propertyService.get_pending_properties(db, skip, limit)
    total = propertyService.count_properties(db, status='pending')
    
    return {
        "properties": properties,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{property_id}", response_model=PropertyDetailResponse)
def get_property(
    property_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener propiedad por ID
    
    Retorna:
    - Propiedad con todos sus detalles
    - Imágenes
    - Información del dueño
    - Información del asesor (si está aprobada)
    
    Errores:
    - 404: Propiedad no encontrada
    """
    property_obj = propertyService.get_property_by_id(db, property_id)
    
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propiedad no encontrada"
        )
    
    return property_obj


@router.post("", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
def create_property(
    property_data: PropertyCreate,
    user_id: int = Query(..., description="ID del usuario que publica (temporal, con JWT se extraerá del token)"),
    db: Session = Depends(get_db)
):
    """
    Crear nueva propiedad
    
    Body:
    - **title**: Título de la propiedad
    - **description**: Descripción detallada
    - **price**: Precio
    - **property_type**: Tipo (house, apartment, land, commercial)
    - **transaction_type**: Transacción (sale, rent)
    - **address**: Dirección completa
    - **city**: Ciudad
    - **latitude**: Latitud
    - **longitude**: Longitud
    - **bedrooms**: Número de recámaras
    - **bathrooms**: Número de baños
    - **square_meters**: Metros cuadrados
    
    La propiedad se crea automáticamente con status='pending'.
    
    Nota: Con JWT, user_id se extraerá del token automáticamente.
    """
    property_obj = propertyService.create_property(db, property_data, user_id)
    return property_obj


@router.put("/{property_id}", response_model=PropertyResponse)
def update_property(
    property_id: int,
    property_data: PropertyUpdate,
    user_id: Optional[int] = Query(None, description="ID del usuario (para verificar permisos)"),
    db: Session = Depends(get_db)
):
    """
    Actualizar propiedad
    
    Todos los campos son opcionales.
    
    Validaciones:
    - Solo el dueño puede editar (si se proporciona user_id)
    - Propiedad debe existir
    
    Errores:
    - 404: Propiedad no encontrada
    - 403: Sin permisos para editar
    
    Nota: Con JWT, user_id se extraerá del token y se validará automáticamente.
    """
    property_obj = propertyService.update_property(
        db,
        property_id,
        property_data,
        user_id
    )
    
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propiedad no encontrada"
        )
    
    return property_obj


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(
    property_id: int,
    user_id: Optional[int] = Query(None, description="ID del usuario (para verificar permisos)"),
    db: Session = Depends(get_db)
):
    """
    Eliminar propiedad
    
    Validaciones:
    - Solo el dueño puede eliminar (si se proporciona user_id)
    - Propiedad debe existir
    
    Errores:
    - 404: Propiedad no encontrada
    - 403: Sin permisos para eliminar
    
    Nota: Esta es eliminación permanente.
    Con JWT, user_id se extraerá del token.
    """
    success = propertyService.delete_property(db, property_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propiedad no encontrada"
        )
    
    return None


# ==========================================
# SISTEMA DE APROBACIÓN
# ==========================================

@router.patch("/{property_id}/approve", response_model=PropertyResponse)
def approve_property(
    property_id: int,
    advisor_id: int = Query(..., description="ID del asesor que aprueba"),
    db: Session = Depends(get_db)
):
    """
    Aprobar propiedad (asesor)
    
    Cambia el estado a 'approved' y asigna el asesor.
    
    Validaciones:
    - Propiedad debe existir
    - Propiedad debe estar en estado 'pending'
    - Asesor debe existir
    
    Errores:
    - 404: Propiedad o asesor no encontrado
    - 400: Propiedad no está pending
    
    Nota: Con JWT, solo usuarios con rol 'advisor' podrán usar este endpoint.
    advisor_id se extraerá del token.
    """
    property_obj = propertyService.approve_property(db, property_id, advisor_id)
    return property_obj


@router.patch("/{property_id}/reject", response_model=PropertyResponse)
def reject_property(
    property_id: int,
    reason: Optional[str] = Query(None, description="Razón del rechazo"),
    db: Session = Depends(get_db)
):
    """
    Rechazar propiedad (asesor)
    
    Cambia el estado a 'rejected'.
    
    Validaciones:
    - Propiedad debe existir
    - Propiedad debe estar en estado 'pending'
    
    Errores:
    - 404: Propiedad no encontrada
    - 400: Propiedad no está pending
    
    Nota: Con JWT, solo usuarios con rol 'advisor' podrán usar este endpoint.
    """
    property_obj = propertyService.reject_property(db, property_id, reason)
    return property_obj


@router.patch("/{property_id}/sold", response_model=PropertyResponse)
def mark_as_sold(
    property_id: int,
    db: Session = Depends(get_db)
):
    """
    Marcar propiedad como vendida/rentada
    
    Cambia el estado a 'sold'.
    
    Validaciones:
    - Propiedad debe existir
    - Propiedad debe estar en estado 'approved'
    
    Errores:
    - 404: Propiedad no encontrada
    - 400: Propiedad no está approved
    
    Nota: Con JWT, solo el asesor asignado podrá marcar como vendida.
    """
    property_obj = propertyService.mark_as_sold(db, property_id)
    return property_obj


# ==========================================
# BÚSQUEDAS AVANZADAS
# ==========================================

@router.post("/search", response_model=PropertyListResponse)
def search_properties(
    filters: PropertyFilter,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Búsqueda avanzada de propiedades
    
    Body (todos opcionales):
    - **city**: Ciudad (búsqueda ILIKE)
    - **property_type**: Tipo de propiedad
    - **transaction_type**: Tipo de transacción
    - **min_price**: Precio mínimo
    - **max_price**: Precio máximo
    - **bedrooms**: Mínimo de recámaras
    - **bathrooms**: Mínimo de baños
    - **min_square_meters**: Metros cuadrados mínimos
    - **max_square_meters**: Metros cuadrados máximos
    - **status**: Estado (default: 'approved' para búsqueda pública)
    
    Por defecto solo muestra propiedades aprobadas.
    
    Retorna:
    - Propiedades que cumplen los filtros
    - Total para paginación
    """
    properties, total = propertyService.search_properties(
        db,
        filters,
        skip,
        limit
    )
    
    return {
        "properties": properties,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/search/proximity", response_model=PropertyListResponse)
def search_by_proximity(
    latitude: float = Query(..., description="Latitud del punto central"),
    longitude: float = Query(..., description="Longitud del punto central"),
    radius_km: float = Query(5.0, ge=0.1, le=50, description="Radio de búsqueda en kilómetros"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Buscar propiedades por proximidad geográfica
    
    Query params:
    - **latitude**: Latitud del centro de búsqueda
    - **longitude**: Longitud del centro de búsqueda
    - **radius_km**: Radio en kilómetros (0.1 - 50)
    
    Retorna propiedades dentro del radio especificado.
    Solo propiedades aprobadas.
    
    Usa fórmula de Haversine simplificada.
    Para búsquedas más precisas, considerar PostGIS.
    """
    properties = propertyService.search_by_proximity(
        db,
        latitude,
        longitude,
        radius_km,
        skip,
        limit
    )
    
    # Contar sin skip/limit para total
    all_properties = propertyService.search_by_proximity(
        db,
        latitude,
        longitude,
        radius_km,
        0,
        999999
    )
    
    return {
        "properties": properties,
        "total": len(all_properties),
        "skip": skip,
        "limit": limit
    }


# ==========================================
# GESTIÓN DE IMÁGENES
# ==========================================

@router.post("/{property_id}/images", response_model=PropertyImageResponse, status_code=status.HTTP_201_CREATED)
def add_property_image(
    property_id: int,
    image_data: PropertyImageCreate,
    db: Session = Depends(get_db)
):
    """
    Agregar imagen a una propiedad
    
    Body:
    - **image_url**: URL de la imagen
    - **is_main**: Si es la imagen principal (default: false)
    
    Si is_main=true, automáticamente quita el flag de las demás imágenes.
    
    Errores:
    - 404: Propiedad no encontrada
    """
    image = propertyService.add_property_image(
        db,
        property_id,
        image_data.image_url,
        image_data.is_main
    )
    return image


@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property_image(
    image_id: int,
    db: Session = Depends(get_db)
):
    """
    Eliminar imagen de propiedad
    
    Errores:
    - 404: Imagen no encontrada
    """
    success = propertyService.delete_property_image(db, image_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagen no encontrada"
        )
    
    return None


# ==========================================
# ESTADÍSTICAS Y CONSULTAS ESPECIALES
# ==========================================

@router.get("/stats/general")
def get_property_stats(db: Session = Depends(get_db)):
    """
    Obtener estadísticas generales de propiedades
    
    Retorna:
    - Total de propiedades
    - Totales por estado (approved, pending, rejected, sold)
    - Precio promedio de propiedades aprobadas
    """
    stats = propertyService.get_property_stats(db)
    return stats


@router.get("/advisor/{advisor_id}", response_model=PropertyListResponse)
def get_properties_by_advisor(
    advisor_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Obtener propiedades gestionadas por un asesor
    
    Retorna todas las propiedades que un asesor ha aprobado.
    
    Útil para:
    - Portafolio del asesor
    - Estadísticas de desempeño
    """
    properties = propertyService.get_properties_by_advisor(
        db,
        advisor_id,
        skip,
        limit
    )
    
    # Contar total
    all_properties = propertyService.get_properties_by_advisor(
        db,
        advisor_id,
        0,
        999999
    )
    
    return {
        "properties": properties,
        "total": len(all_properties),
        "skip": skip,
        "limit": limit
    }
    