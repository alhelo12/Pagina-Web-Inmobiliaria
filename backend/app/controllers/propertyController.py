"""
Controller: Properties
"""

from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional

from app.dbConfig.databaseSession import get_db
from app.core.config import settings
from app.services import propertyService
from app.core.dependencies import get_current_user, require_advisor_or_admin, verify_user_owns_resource
from app.schemas import (
    PropertyCreate, PropertyUpdate, PropertyResponse,
    PropertyListResponse, PropertySearchFilters, NearbySearchParams
)
from app.models import User, Property, Advisor

router = APIRouter(prefix="/properties", tags=["Properties"])


def get_or_create_advisor(db: Session, user: User) -> int:
    """
    Obtiene el ID del advisor o crea el perfil si no existe
    """
    if user.advisor:
        return user.advisor.id
    
    new_advisor = Advisor(user_id=user.id)
    db.add(new_advisor)
    db.commit()
    db.refresh(new_advisor)
    return new_advisor.id


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
    user_id: Optional[int] = Query(None, description="Filtrar por usuario que publico"),
    db: Session = Depends(get_db)
):
    properties = propertyService.get_properties(
        db, skip=skip, limit=limit, status=status, user_id=user_id
    )
    total = propertyService.count_properties(db, status=status, user_id=user_id)

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
    current_user: User = Depends(require_advisor_or_admin),
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
    current_user: User = Depends(require_advisor_or_admin),
    db: Session = Depends(get_db)
):
    return propertyService.get_property_stats(db)


# ── ANALYTICS AVANZADOS ──────────────────────────────────────────────────────
@router.get("/analytics/trends")
def get_property_trends(
    months: int = Query(12, ge=1, le=24, description="Meses hacia atrás"),
    current_user: User = Depends(require_advisor_or_admin),
    db: Session = Depends(get_db)
):
    return propertyService.get_properties_trends(db, months=months)


@router.get("/analytics/days-on-market")
def get_avg_days_on_market(
    current_user: User = Depends(require_advisor_or_admin),
    db: Session = Depends(get_db)
):
    return propertyService.get_avg_days_on_market(db)


@router.get("/analytics/price-per-m2")
def get_price_per_m2_by_city(
    current_user: User = Depends(require_advisor_or_admin),
    db: Session = Depends(get_db)
):
    return propertyService.get_price_per_m2_by_city(db)


@router.get("/analytics/conversion-rate")
def get_advisor_conversion_rate(
    current_user: User = Depends(require_advisor_or_admin),
    db: Session = Depends(get_db)
):
    return propertyService.get_advisor_conversion_rate(db)


# ── PROPIEDADES DEL ADVISOR ─────────────────────────────────────────────────
@router.get("/by-advisor", response_model=PropertyListResponse)
def get_properties_by_advisor(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_advisor_or_admin),
    db: Session = Depends(get_db)
):
    advisor_id = get_or_create_advisor(db, current_user)
    
    properties, total = propertyService.get_advisor_properties_with_available(
        db, advisor_id, skip=skip, limit=limit
    )
    return PropertyListResponse(
        total=total,
        page=(skip // limit) + 1,
        per_page=limit,
        properties=properties
    )


# ── ESTADÍSTICAS DEL ADVISOR ─────────────────────────────────────────────────
@router.get("/stats/by-advisor")
def get_properties_stats_by_advisor(
    current_user: User = Depends(require_advisor_or_admin),
    db: Session = Depends(get_db)
):
    advisor_id = get_or_create_advisor(db, current_user)
    return propertyService.get_property_stats_by_advisor(db, advisor_id)


# ── TOMAR PROPIEDAD (asesor) ─────────────────────────────────────────────────
@router.patch("/{property_id}/take", response_model=PropertyResponse)
def take_property(
    property_id: int,
    current_user: User = Depends(require_advisor_or_admin),
    db: Session = Depends(get_db)
):
    advisor_id = get_or_create_advisor(db, current_user)
    return propertyService.take_property(db, property_id, advisor_id)


# ── DEVOLVER PROPIEDAD (asesor) ──────────────────────────────────────────────
@router.patch("/{property_id}/return", response_model=PropertyResponse)
def return_property(
    property_id: int,
    current_user: User = Depends(require_advisor_or_admin),
    db: Session = Depends(get_db)
):
    advisor_id = get_or_create_advisor(db, current_user)
    return propertyService.return_property(db, property_id, advisor_id)


# ── PROPIEDADES DISPONIBLES PARA TOMAR ───────────────────────────────────────
@router.get("/available", response_model=PropertyListResponse)
def get_available_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_advisor_or_admin),
    db: Session = Depends(get_db)
):
    properties = propertyService.get_available_properties(db, skip=skip, limit=limit)
    total = db.query(Property).filter(
        Property.status == 'pending',
        Property.advisor_id == None
    ).count()
    return PropertyListResponse(
        total=total,
        page=(skip // limit) + 1,
        per_page=limit,
        properties=properties
    )


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
    current_user: User = Depends(require_advisor_or_admin),
    db: Session = Depends(get_db)
):
    advisor_id = current_user.advisor.id if current_user.advisor else None
    if current_user.is_advisor() and advisor_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Usuario no tiene perfil de advisor")
    return propertyService.approve_property(db, property_id, advisor_id)


# ── RECHAZAR (asesor) ────────────────────────────────────────────────────────
@router.patch("/{property_id}/reject", response_model=PropertyResponse)
def reject_property(
    property_id: int,
    reason: Optional[str] = Query(None),
    current_user: User = Depends(require_advisor_or_admin),
    db: Session = Depends(get_db)
):
    return propertyService.reject_property(db, property_id, reason)


# ── MARCAR VENDIDA (asesor) ──────────────────────────────────────────────────
@router.patch("/{property_id}/mark-sold", response_model=PropertyResponse)
def mark_property_sold(
    property_id: int,
    current_user: User = Depends(require_advisor_or_admin),
    db: Session = Depends(get_db)
):
    return propertyService.mark_as_sold(db, property_id)


@router.post("/{property_id}/images/upload", status_code=status.HTTP_201_CREATED)
async def upload_property_image(
    property_id: int,
    image: UploadFile = File(...),
    is_main: bool = Query(False),
    label: Optional[str] = Query(None, max_length=100),
    is_extra: bool = Query(False),
    image_type: str = Query("general"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    prop = propertyService.get_property_by_id(db, property_id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Propiedad no encontrada")

    verify_user_owns_resource(prop.submitted_by_user_id, current_user)

    clean_label = label.strip() if label else None
    normalized_image_type = (image_type or "general").lower()
    if is_extra:
        normalized_image_type = "extra"
    if normalized_image_type == "extra" and not clean_label:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El extra necesita un nombre"
        )

    ext = Path(image.filename or "").suffix.lower()
    if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato no permitido. Usa: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}"
        )

    content = await image.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La imagen supera el limite de {settings.MAX_UPLOAD_SIZE_MB}MB"
        )

    folder = Path("media") / "properties" / str(property_id)
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{ext}"
    file_path = folder / filename
    file_path.write_bytes(content)

    image_url = f"/media/properties/{property_id}/{filename}"
    created = propertyService.add_property_image(
        db=db,
        property_id=property_id,
        image_url=image_url,
        is_main=is_main,
        label=clean_label,
        is_extra=is_extra,
        image_type=normalized_image_type
    )
    return {
        "id": created.id,
        "property_id": created.property_id,
        "image_url": created.image_url,
        "label": created.label,
        "image_type": created.image_type,
        "is_extra": created.is_extra,
        "is_main": created.is_main
    }
