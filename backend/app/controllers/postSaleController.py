"""
Controller: Post-Sale Followups

Endpoints para gestión de seguimiento post-venta.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.dbConfig.databaseSession import get_db
from app.services import postSaleService
from app.core.dependencies import get_current_user
from app.schemas.postSaleSchema import (
    PostSaleFollowupCreate,
    PostSaleFollowupComplete,
    PostSaleFollowupSkip,
    PostSaleFollowupResponse,
    PostSaleFollowupDetailResponse,
    PostSaleFollowupListResponse,
    PostSaleStats,
    PostSaleFollowupFilter
)
from app.models import User

router = APIRouter(
    prefix="/post-sale",
    tags=["Post-Sale Followups"]
)


@router.post("/create", response_model=PostSaleFollowupDetailResponse)
def create_followup(
    followup_data: PostSaleFollowupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear seguimiento post-venta manualmente.
    Solo admin o el asesor asignado pueden crear.
    """
    if not current_user.is_admin() and not current_user.is_advisor():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores y asesores pueden crear seguimientos"
        )
    
    followup = postSaleService.create_followup(db=db, followup_data=followup_data)
    
    return (
        db.query(postSaleService.PostSaleFollowup)
        .filter(postSaleService.PostSaleFollowup.id == followup.id)
        .first()
    )


@router.get("/list", response_model=PostSaleFollowupListResponse)
def get_followups(
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(20, ge=1, le=100, description="Resultados por página"),
    status_filter: Optional[str] = Query(None, description="Filtrar por estado"),
    followup_type: Optional[str] = Query(None, description="Filtrar por tipo"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de seguimientos post-venta"""
    skip = (page - 1) * per_page
    
    client_id = None
    advisor_id = None
    
    if current_user.is_client():
        client_id = current_user.id
    elif current_user.is_advisor():
        from app.models import Advisor
        advisor = db.query(Advisor).filter(Advisor.user_id == current_user.id).first()
        advisor_id = advisor.id if advisor else None
    
    followups = postSaleService.get_followups(
        db=db,
        skip=skip,
        limit=per_page,
        client_id=client_id,
        advisor_id=advisor_id,
        status=status_filter,
        followup_type=followup_type
    )
    
    total = postSaleService.count_followups(
        db=db,
        client_id=client_id,
        advisor_id=advisor_id,
        status=status_filter
    )
    
    return PostSaleFollowupListResponse(
        total=total,
        page=page,
        per_page=per_page,
        followups=followups
    )


@router.get("/pending", response_model=list[PostSaleFollowupDetailResponse])
def get_pending_followups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener seguimientos pendientes del asesor actual"""
    if not current_user.is_advisor():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo asesores pueden ver seguimientos pendientes"
        )
    
    from app.models import Advisor
    advisor = db.query(Advisor).filter(Advisor.user_id == current_user.id).first()
    
    if not advisor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de asesor no encontrado"
        )
    
    return postSaleService.get_pending_followups_for_advisor(
        db=db,
        advisor_id=advisor.id
    )


@router.get("/overdue", response_model=list[PostSaleFollowupDetailResponse])
def get_overdue_followups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener seguimientos vencidos"""
    if not current_user.is_admin() and not current_user.is_advisor():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores y asesores pueden ver seguimientos vencidos"
        )
    
    advisor_id = None
    if current_user.is_advisor():
        from app.models import Advisor
        advisor = db.query(Advisor).filter(Advisor.user_id == current_user.id).first()
        advisor_id = advisor.id if advisor else None
    
    return postSaleService.get_overdue_followups(
        db=db,
        advisor_id=advisor_id
    )


@router.get("/{followup_id}", response_model=PostSaleFollowupDetailResponse)
def get_followup(
    followup_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener detalle de un seguimiento"""
    followup = postSaleService.get_followup_by_id(db=db, followup_id=followup_id)
    
    if not followup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seguimiento no encontrado"
        )
    
    if current_user.is_client() and followup.client_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a este seguimiento"
        )
    
    return followup


@router.patch("/{followup_id}/complete", response_model=PostSaleFollowupDetailResponse)
def complete_followup(
    followup_id: int,
    complete_data: PostSaleFollowupComplete,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marcar seguimiento como completado"""
    followup = postSaleService.get_followup_by_id(db=db, followup_id=followup_id)
    
    if not followup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seguimiento no encontrado"
        )
    
    if current_user.is_client() and followup.client_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a este seguimiento"
        )
    
    return postSaleService.complete_followup(
        db=db,
        followup_id=followup_id,
        complete_data=complete_data
    )


@router.patch("/{followup_id}/skip", response_model=PostSaleFollowupDetailResponse)
def skip_followup(
    followup_id: int,
    skip_data: PostSaleFollowupSkip,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Omitir seguimiento"""
    if not current_user.is_admin() and not current_user.is_advisor():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores y asesores pueden omitir seguimientos"
        )
    
    return postSaleService.skip_followup(
        db=db,
        followup_id=followup_id,
        skip_data=skip_data
    )


@router.get("/stats", response_model=PostSaleStats)
def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de post-venta"""
    advisor_id = None
    if current_user.is_advisor():
        from app.models import Advisor
        advisor = db.query(Advisor).filter(Advisor.user_id == current_user.id).first()
        advisor_id = advisor.id if advisor else None
    
    return postSaleService.get_post_sale_stats(db=db, advisor_id=advisor_id)


@router.get("/ranking", response_model=list[dict])
def get_advisor_ranking(
    limit: int = Query(10, ge=1, le=50, description="Número de asesores"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener ranking de asesores por satisfacción post-venta"""
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden ver el ranking"
        )
    
    return postSaleService.get_advisor_post_sale_ranking(db=db, limit=limit)
