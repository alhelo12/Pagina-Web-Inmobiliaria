"""
Controller: Activity Log

Endpoints para consultar el registro de actividad.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.dbConfig.databaseSession import get_db
from app.services import activityLogService
from app.core.dependencies import get_current_user
from app.models import User

router = APIRouter(
    prefix="/activity",
    tags=["Activity Log"]
)


@router.get("/my-activities")
def get_my_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    action: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener actividades del usuario actual"""
    activities = activityLogService.get_user_activities(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        action=action,
        days=days
    )
    
    total = activityLogService.get_activity_stats(db, current_user.id)["total"]
    
    return {
        "total": total,
        "page": (skip // limit) + 1,
        "per_page": limit,
        "activities": [a.to_dict() for a in activities]
    }


@router.get("/recent")
def get_recent_activities(
    limit: int = Query(20, ge=1, le=50),
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener actividades recientes (solo admin)"""
    if not current_user.is_admin():
        return {"activities": []}
    
    activities = activityLogService.get_recent_activities(db=db, limit=limit, days=days)
    
    return {
        "activities": [a.to_dict() for a in activities]
    }


@router.get("/stats")
def get_activity_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de actividad"""
    return activityLogService.get_activity_stats(db=db, user_id=current_user.id)
