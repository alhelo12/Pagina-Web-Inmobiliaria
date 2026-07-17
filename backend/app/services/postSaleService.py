"""
Service: PostSaleFollowup

Lógica de negocio para seguimiento post-venta.
Maneja creación automática, encuestas, métricas de satisfacción.
"""

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from app.models import PostSaleFollowup, Property, User, Advisor
from app.schemas.postSaleSchema import (
    PostSaleFollowupCreate,
    PostSaleFollowupComplete,
    PostSaleFollowupSkip,
    FOLLOWUP_TYPE_CONFIG
)


# ==========================================
# CREACIÓN AUTOMÁTICA AL VENDER
# ==========================================

def create_auto_followups_on_sale(
    db: Session,
    property_id: int,
    client_id: int,
    advisor_id: Optional[int] = None
) -> List[PostSaleFollowup]:
    """
    Crear seguimientos automáticos cuando una propiedad se marca como vendida.
    
    Genera 4 seguimientos programados:
    - Día +7: Encuesta de satisfacción
    - Día +30: Llamada de seguimiento
    - Día +60: Solicitud de referido
    - Día +90: Recordatorio de mantenimiento
    
    Args:
        db: Sesión de base de datos
        property_id: ID de la propiedad vendida
        client_id: ID del cliente
        advisor_id: ID del asesor (opcional)
        
    Returns:
        Lista de seguimientos creados
    """
    sale_date = datetime.now()
    followups = []
    
    for followup_type, config in FOLLOWUP_TYPE_CONFIG.items():
        scheduled_date = sale_date + timedelta(days=config["days_after_sale"])
        
        followup = PostSaleFollowup(
            property_id=property_id,
            client_id=client_id,
            advisor_id=advisor_id,
            sale_date=sale_date,
            followup_type=followup_type,
            scheduled_date=scheduled_date,
            status='pending'
        )
        
        db.add(followup)
        followups.append(followup)
    
    db.commit()
    
    for followup in followups:
        db.refresh(followup)
    
    return followups


# ==========================================
# CRUD BÁSICO
# ==========================================

def get_followup_by_id(db: Session, followup_id: int) -> Optional[PostSaleFollowup]:
    """Obtener seguimiento por ID"""
    return (
        db.query(PostSaleFollowup)
        .options(
            selectinload(PostSaleFollowup.related_property),
            selectinload(PostSaleFollowup.client),
            selectinload(PostSaleFollowup.advisor).selectinload(Advisor.user)
        )
        .filter(PostSaleFollowup.id == followup_id)
        .first()
    )


def get_followups(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    client_id: Optional[int] = None,
    advisor_id: Optional[int] = None,
    property_id: Optional[int] = None,
    status: Optional[str] = None,
    followup_type: Optional[str] = None
) -> List[PostSaleFollowup]:
    """Obtener lista de seguimientos con filtros"""
    query = db.query(PostSaleFollowup).options(
        selectinload(PostSaleFollowup.related_property),
        selectinload(PostSaleFollowup.client),
        selectinload(PostSaleFollowup.advisor).selectinload(Advisor.user)
    )
    
    if client_id:
        query = query.filter(PostSaleFollowup.client_id == client_id)
    
    if advisor_id:
        query = query.filter(PostSaleFollowup.advisor_id == advisor_id)
    
    if property_id:
        query = query.filter(PostSaleFollowup.property_id == property_id)
    
    if status:
        query = query.filter(PostSaleFollowup.status == status)
    
    if followup_type:
        query = query.filter(PostSaleFollowup.followup_type == followup_type)
    
    query = query.order_by(PostSaleFollowup.scheduled_date.desc())
    
    return query.offset(skip).limit(limit).all()


def count_followups(
    db: Session,
    client_id: Optional[int] = None,
    advisor_id: Optional[int] = None,
    status: Optional[str] = None
) -> int:
    """Contar seguimientos con filtros"""
    query = db.query(func.count(PostSaleFollowup.id))
    
    if client_id:
        query = query.filter(PostSaleFollowup.client_id == client_id)
    
    if advisor_id:
        query = query.filter(PostSaleFollowup.advisor_id == advisor_id)
    
    if status:
        query = query.filter(PostSaleFollowup.status == status)
    
    return query.scalar()


def create_followup(db: Session, followup_data: PostSaleFollowupCreate) -> PostSaleFollowup:
    """Crear seguimiento manualmente"""
    prop = db.query(Property).filter(Property.id == followup_data.property_id).first()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Propiedad no encontrada")
    
    client = db.query(User).filter(User.id == followup_data.client_id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    
    if followup_data.advisor_id:
        advisor = db.query(Advisor).filter(Advisor.id == followup_data.advisor_id).first()
        if not advisor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asesor no encontrado")
    
    followup = PostSaleFollowup(
        property_id=followup_data.property_id,
        client_id=followup_data.client_id,
        advisor_id=followup_data.advisor_id,
        sale_date=datetime.now(),
        followup_type=followup_data.followup_type.value,
        scheduled_date=followup_data.scheduled_date,
        status='pending',
        notes=followup_data.notes
    )
    
    db.add(followup)
    db.commit()
    db.refresh(followup)
    
    return followup


# ==========================================
# GESTIÓN DE ESTADO
# ==========================================

def complete_followup(
    db: Session,
    followup_id: int,
    complete_data: PostSaleFollowupComplete
) -> PostSaleFollowup:
    """Marcar seguimiento como completado"""
    followup = get_followup_by_id(db, followup_id)
    
    if not followup:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seguimiento no encontrado")
    
    if followup.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solo se pueden completar seguimientos pendientes (estado actual: {followup.status})"
        )
    
    followup.complete(
        notes=complete_data.notes,
        satisfaction_score=complete_data.satisfaction_score
    )
    
    db.commit()
    db.refresh(followup)
    
    return followup


def skip_followup(
    db: Session,
    followup_id: int,
    skip_data: PostSaleFollowupSkip
) -> PostSaleFollowup:
    """Omitir seguimiento"""
    followup = get_followup_by_id(db, followup_id)
    
    if not followup:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seguimiento no encontrado")
    
    if followup.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solo se pueden omitir seguimientos pendientes (estado actual: {followup.status})"
        )
    
    followup.skip(reason=skip_data.reason)
    
    db.commit()
    db.refresh(followup)
    
    return followup


# ==========================================
# CONSULTAS ESPECIALES
# ==========================================

def get_pending_followups_for_advisor(
    db: Session,
    advisor_id: int,
    limit: int = 20
) -> List[PostSaleFollowup]:
    """Obtener seguimientos pendientes de un asesor"""
    return (
        db.query(PostSaleFollowup)
        .options(
            selectinload(PostSaleFollowup.related_property),
            selectinload(PostSaleFollowup.client)
        )
        .filter(PostSaleFollowup.advisor_id == advisor_id)
        .filter(PostSaleFollowup.status == 'pending')
        .filter(PostSaleFollowup.scheduled_date <= datetime.now() + timedelta(days=7))
        .order_by(PostSaleFollowup.scheduled_date.asc())
        .limit(limit)
        .all()
    )


def get_overdue_followups(
    db: Session,
    advisor_id: Optional[int] = None,
    limit: int = 20
) -> List[PostSaleFollowup]:
    """Obtener seguimientos vencidos (scheduled_date pasada y aún pending)"""
    query = (
        db.query(PostSaleFollowup)
        .options(
            selectinload(PostSaleFollowup.related_property),
            selectinload(PostSaleFollowup.client),
            selectinload(PostSaleFollowup.advisor).selectinload(Advisor.user)
        )
        .filter(PostSaleFollowup.status == 'pending')
        .filter(PostSaleFollowup.scheduled_date < datetime.now())
        .order_by(PostSaleFollowup.scheduled_date.asc())
    )
    
    if advisor_id:
        query = query.filter(PostSaleFollowup.advisor_id == advisor_id)
    
    return query.limit(limit).all()


# ==========================================
# ESTADÍSTICAS
# ==========================================

def get_post_sale_stats(
    db: Session,
    advisor_id: Optional[int] = None
) -> dict:
    """Obtener estadísticas generales de post-venta"""
    query = db.query(PostSaleFollowup)
    
    if advisor_id:
        query = query.filter(PostSaleFollowup.advisor_id == advisor_id)
    
    total = query.count()
    pending = query.filter(PostSaleFollowup.status == 'pending').count()
    completed = query.filter(PostSaleFollowup.status == 'completed').count()
    skipped = query.filter(PostSaleFollowup.status == 'skipped').count()
    
    avg_score = query.filter(
        PostSaleFollowup.status == 'completed',
        PostSaleFollowup.satisfaction_score.isnot(None)
    ).with_entities(func.avg(PostSaleFollowup.satisfaction_score)).scalar()
    
    total_surveys = query.filter(PostSaleFollowup.followup_type == 'satisfaction_survey').count()
    completed_surveys = query.filter(
        PostSaleFollowup.followup_type == 'satisfaction_survey',
        PostSaleFollowup.status == 'completed'
    ).count()
    
    total_referrals = query.filter(PostSaleFollowup.followup_type == 'referral_request').count()
    completed_referrals = query.filter(
        PostSaleFollowup.followup_type == 'referral_request',
        PostSaleFollowup.status == 'completed'
    ).count()
    
    return {
        "total_followups": total,
        "pending": pending,
        "completed": completed,
        "skipped": skipped,
        "avg_satisfaction_score": float(avg_score) if avg_score else 0.0,
        "total_surveys": total_surveys,
        "completed_surveys": completed_surveys,
        "total_referrals": total_referrals,
        "completed_referrals": completed_referrals
    }


def get_advisor_post_sale_ranking(
    db: Session,
    limit: int = 10
) -> List[dict]:
    """Ranking de asesores por satisfacción post-venta"""
    results = (
        db.query(
            PostSaleFollowup.advisor_id,
            func.count(PostSaleFollowup.id).label('total'),
            func.avg(PostSaleFollowup.satisfaction_score).label('avg_score'),
            func.sum(
                func.case(
                    (PostSaleFollowup.status == 'completed', 1),
                    else_=0
                )
            ).label('completed')
        )
        .filter(PostSaleFollowup.advisor_id.isnot(None))
        .group_by(PostSaleFollowup.advisor_id)
        .order_by(func.avg(PostSaleFollowup.satisfaction_score).desc())
        .limit(limit)
        .all()
    )
    
    ranking = []
    for row in results:
        advisor = db.query(Advisor).options(
            selectinload(Advisor.user)
        ).filter(Advisor.id == row.advisor_id).first()
        
        ranking.append({
            "advisor_id": row.advisor_id,
            "advisor_name": advisor.user.full_name if advisor else "Desconocido",
            "total_followups": row.total,
            "completed": row.completed or 0,
            "avg_satisfaction_score": float(row.avg_score) if row.avg_score else 0.0
        })
    
    return ranking
