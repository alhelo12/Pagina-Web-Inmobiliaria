"""
Controller: Notifications

Endpoints para gestión de notificaciones de usuarios.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.dbConfig.databaseSession import get_db
from app.services import notificationService
from app.core.dependencies import get_current_user
from app.schemas import (
    NotificationResponse,
    NotificationListResponse,
    NotificationCountResponse,
    NotificationMarkReadResponse
)
from app.schemas.notificationSchema import NOTIFICATION_TYPES
from app.models import User

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


@router.get("/meta")
def get_notification_types():
    """
    Retorna los tipos de notificación disponibles con su metadata visual.
    Sin autenticación — usado por el frontend para renderizar iconos, colores y etiquetas.
    """
    return NOTIFICATION_TYPES


@router.get("", response_model=NotificationListResponse)
def get_my_notifications(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de registros"),
    include_read: bool = Query(True, description="Incluir notificaciones leídas"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener notificaciones del usuario actual
    
    Returns:
        Lista de notificaciones con conteo de no leídas
    """
    notifications = notificationService.get_notifications_by_user(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        include_read=include_read
    )
    
    total = notificationService.count_total_notifications(db, current_user.id)
    unread_count = notificationService.get_unread_count(db, current_user.id)
    
    return NotificationListResponse(
        notifications=notifications,
        total=total,
        unread_count=unread_count
    )


@router.get("/unread-count", response_model=NotificationCountResponse)
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener contador de notificaciones no leídas
    
    Returns:
        Número de notificaciones sin leer
    """
    count = notificationService.get_unread_count(db, current_user.id)
    return NotificationCountResponse(unread_count=count)


@router.patch("/{notification_id}/read", response_model=NotificationMarkReadResponse)
def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Marcar una notificación como leída
    
    Args:
        notification_id: ID de la notificación
        
    Returns:
        Notificación actualizada
    """
    notification = notificationService.mark_as_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )
    
    return NotificationMarkReadResponse(
        id=notification.id,
        is_read=notification.is_read
    )


@router.patch("/read-all", response_model=NotificationMarkReadResponse)
def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Marcar todas las notificaciones como leídas
    
    Returns:
        Resultado de la operación
    """
    count = notificationService.mark_all_as_read(db, current_user.id)
    
    return NotificationMarkReadResponse(
        id=0,
        is_read=True,
        message=f"Se marcaron {count} notificaciones como leídas"
    )


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar una notificación
    
    Args:
        notification_id: ID de la notificación
        
    Returns:
        Confirmación de eliminación
    """
    result = notificationService.delete_notification(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )
    
    if result:
        return {"message": "Notificación eliminada correctamente"}
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Notificación no encontrada"
    )