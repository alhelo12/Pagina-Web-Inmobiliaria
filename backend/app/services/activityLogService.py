"""
Service: ActivityLog

Lógica de negocio para registro de actividad de usuarios.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime, timedelta

from app.models import ActivityLog


def log_activity(
    db: Session,
    user_id: Optional[int],
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None
) -> ActivityLog:
    """
    Registrar una actividad del usuario
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        action: Tipo de acción
        entity_type: Tipo de entidad afectada
        entity_id: ID de la entidad
        details: Detalles adicionales
        ip_address: Dirección IP
        
    Returns:
        ActivityLog creado
    """
    activity = ActivityLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip_address
    )
    
    db.add(activity)
    db.commit()
    db.refresh(activity)
    
    return activity


def get_user_activities(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    action: Optional[str] = None,
    days: int = 30
) -> List[ActivityLog]:
    """
    Obtener actividades de un usuario
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        skip: Registros a saltar
        limit: Máximo de registros
        action: Filtrar por tipo de acción
        days: Días hacia atrás
        
    Returns:
        Lista de actividades
    """
    query = db.query(ActivityLog).filter(
        ActivityLog.user_id == user_id,
        ActivityLog.created_at >= datetime.now() - timedelta(days=days)
    )
    
    if action:
        query = query.filter(ActivityLog.action == action)
    
    return query.order_by(ActivityLog.created_at.desc()).offset(skip).limit(limit).all()


def get_recent_activities(
    db: Session,
    limit: int = 20,
    days: int = 7
) -> List[ActivityLog]:
    """
    Obtener actividades recientes de todos los usuarios
    
    Args:
        db: Sesión de base de datos
        limit: Máximo de registros
        days: Días hacia atrás
        
    Returns:
        Lista de actividades
    """
    return (
        db.query(ActivityLog)
        .filter(ActivityLog.created_at >= datetime.now() - timedelta(days=days))
        .order_by(ActivityLog.created_at.desc())
        .limit(limit)
        .all()
    )


def get_activity_stats(db: Session, user_id: Optional[int] = None) -> dict:
    """
    Obtener estadísticas de actividad
    
    Args:
        db: Sesión de base de datos
        user_id: Filtrar por usuario
        
    Returns:
        Diccionario con estadísticas
    """
    query = db.query(ActivityLog)
    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)
    
    total = query.count()
    today = query.filter(
        ActivityLog.created_at >= datetime.now().replace(hour=0, minute=0, second=0)
    ).count()
    
    by_action = db.query(
        ActivityLog.action,
        func.count(ActivityLog.id)
    )
    if user_id:
        by_action = by_action.filter(ActivityLog.user_id == user_id)
    
    by_action = by_action.group_by(ActivityLog.action).order_by(
        func.count(ActivityLog.id).desc()
    ).limit(10).all()
    
    return {
        "total": total,
        "today": today,
        "by_action": [{"action": row[0], "count": row[1]} for row in by_action]
    }
