"""
Controller: Properties
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.dbConfig.databaseSession import get_db
from app.services import propertyService
from app.core.dependencies import get_current_user, require_advisor, verify_user_owns_resource
from app.schemas import (
    PropertyCreate, PropertyUpdate, PropertyResponse,
    PropertyListResponse, PropertySearchFilters, NearbySearchParams
)
from app.models import User

router = APIRouter(prefix="/properties", tags=["Properties"])


# ── LISTAR PROPIEDADES (público) ─────────────────────────────────────────────
@router.get("", response_model=PropertyListResponse)
def get_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    city: Optional[str] = Query(None),
    property_type: Optional[str] = Query(None),
    transaction_type: Optional[str] = Query(None),
    max_price: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    properties = propertyService.get_properties(
        db, skip=skip, limit=limit, status=status
    )
    total = propertyService.count_properties(db, status=status)

    # Construir la respuesta paginada que exige PropertyListResponse
    return PropertyListResponse(
        total=total,
        page=(skip // limit) + 1,
        per_page=limit,
        properties=properties
    )


# ── BUSCAR PROPIEDADES AVANZADO ──────────────────────────────────────────────
@router.post("/search", response_model=PropertyListResponse)
def search_properties(
    filters: PropertySearchFilters,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    properties, total = propertyService.search_properties(db, filters, skip=skip, limit=limit)
    return PropertyListResponse(
        total=total,
        page=(skip // limit) + 1,
        per_page=limit,
        properties=properties
    )


# ── PROPIEDADES PENDIENTES (asesor/admin) ────────────────────────────────────
@router.get("/pending/list", response_model=PropertyListResponse)
def get_pending_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_advisor),
    db: Session = Depends(get_db)
):
    properties = propertyService.get_pending_properties(db, skip=skip, limit=limit)
    total = propertyService.count_properties(db, status="pending")
    return PropertyListResponse(
        total=total,
        page=(skip // limit) + 1,
        per_page=limit,
        properties=properties
    )


# ── ESTADÍSTICAS (asesor/admin) ──────────────────────────────────────────────
@router.get("/stats/summary")
def get_properties_summary(
    current_user: User = Depends(require_advisor),
    db: Session = Depends(get_db)
):
    return propertyService.get_property_stats(db)


# ── DETALLE DE PROPIEDAD (público) ───────────────────────────────────────────
@router.get("/{property_id}", response_model=PropertyResponse)
def get_property(
    property_id: int,
    db: Session = Depends(get_db)
):
    prop = propertyService.get_property_by_id(db, property_id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Propiedad no encontrada")
    return prop


# ── CREAR PROPIEDAD (cliente autenticado) ────────────────────────────────────
@router.post("", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
def create_property(
    property_data: PropertyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # El user_id viene del token, no de un query param (evita suplantación)
    return propertyService.create_property(db, property_data, current_user.id)


# ── ACTUALIZAR PROPIEDAD ─────────────────────────────────────────────────────
@router.put("/{property_id}", response_model=PropertyResponse)
def update_property(
    property_id: int,
    property_data: PropertyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    prop = propertyService.get_property_by_id(db, property_id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Propiedad no encontrada")
    verify_user_owns_resource(prop.submitted_by_user_id, current_user)
    return propertyService.update_property(db, property_id, property_data)


# ── ELIMINAR PROPIEDAD ───────────────────────────────────────────────────────
@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(
    property_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    prop = propertyService.get_property_by_id(db, property_id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Propiedad no encontrada")
    verify_user_owns_resource(prop.submitted_by_user_id, current_user)
    propertyService.delete_property(db, property_id)
    return None


# ── APROBAR (asesor) ─────────────────────────────────────────────────────────
@router.patch("/{property_id}/approve", response_model=PropertyResponse)
def approve_property(
    property_id: int,
    current_user: User = Depends(require_advisor),
    db: Session = Depends(get_db)
):
    if not current_user.advisor:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Usuario no tiene perfil de advisor")
    return propertyService.approve_property(db, property_id, current_user.advisor.id)


# ── RECHAZAR (asesor) ────────────────────────────────────────────────────────
@router.patch("/{property_id}/reject", response_model=PropertyResponse)
def reject_property(
    property_id: int,
    reason: Optional[str] = Query(None),
    current_user: User = Depends(require_advisor),
    db: Session = Depends(get_db)
):
    return propertyService.reject_property(db, property_id, reason)


# ── MARCAR VENDIDA (asesor) ──────────────────────────────────────────────────
@router.patch("/{property_id}/mark-sold", response_model=PropertyResponse)
def mark_property_sold(
    property_id: int,
    current_user: User = Depends(require_advisor),
    db: Session = Depends(get_db)
):
    return propertyService.mark_as_sold(db, property_id)
