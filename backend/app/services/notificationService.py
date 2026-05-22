"""
Service: Notification

Lógica de negocio para gestión de notificaciones.
"""

import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from fastapi import HTTPException, status

from app.models import Notification, Property, Advisor, User


# ==========================================
# CRUD BÁSICO
# ==========================================

def get_notification_by_id(db: Session, notification_id: int) -> Optional[Notification]:
    """
    Obtener notificación por ID
    
    Args:
        db: Sesión de base de datos
        notification_id: ID de la notificación
        
    Returns:
        Notification o None si no existe
    """
    return db.query(Notification).filter(Notification.id == notification_id).first()


def get_notifications_by_user(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    include_read: bool = True
) -> List[Notification]:
    """
    Obtener notificaciones de un usuario
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        skip: Registros a saltar
        limit: Máximo de registros
        include_read: Si incluir notificaciones leídas
        
    Returns:
        Lista de notificaciones
    """
    query = db.query(Notification).filter(Notification.user_id == user_id)
    
    if not include_read:
        query = query.filter(Notification.is_read == False)
    
    return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()


def get_unread_count(db: Session, user_id: int) -> int:
    """
    Contar notificaciones no leídas de un usuario
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        
    Returns:
        Número de notificaciones no leídas
    """
    return db.query(func.count(Notification.id)).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).scalar()


def count_total_notifications(db: Session, user_id: int) -> int:
    """
    Contar total de notificaciones de un usuario
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        
    Returns:
        Número total de notificaciones
    """
    return db.query(func.count(Notification.id)).filter(
        Notification.user_id == user_id
    ).scalar()


def create_notification(
    db: Session,
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    property_id: Optional[int] = None
) -> Notification:
    """
    Crear una nueva notificación
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario que recibe
        notification_type: Tipo de notificación
        title: Título de la notificación
        message: Mensaje detallado
        property_id: ID de la propiedad relacionada (opcional)
        
    Returns:
        Notificación creada
    """
    # Verificar que el usuario existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar la propiedad si se proporciona
    if property_id:
        prop = db.query(Property).filter(Property.id == property_id).first()
        if not prop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Propiedad no encontrada"
            )
    
    # Verificar preferencias del usuario
    if not _is_notification_enabled(db, user_id, notification_type):
        return None
    
    notification = Notification(
        user_id=user_id,
        property_id=property_id,
        type=notification_type,
        title=title,
        message=message,
        is_read=False
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    _push_via_websocket(notification)
    
    return notification


def mark_as_read(db: Session, notification_id: int, user_id: int) -> Notification:
    """
    Marcar una notificación como leída
    
    Args:
        db: Sesión de base de datos
        notification_id: ID de la notificación
        user_id: ID del usuario (para verificar propiedad)
        
    Returns:
        Notificación actualizada
        
    Raises:
        HTTPException: Si no existe o no pertenece al usuario
    """
    notification = get_notification_by_id(db, notification_id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    
    if notification.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta notificación"
        )
    
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    
    return notification


def mark_all_as_read(db: Session, user_id: int) -> int:
    """
    Marcar todas las notificaciones del usuario como leídas
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        
    Returns:
        Número de notificaciones actualizadas
    """
    result = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    
    return result


def delete_notification(db: Session, notification_id: int, user_id: int) -> bool:
    """
    Eliminar una notificación
    
    Args:
        db: Sesión de base de datos
        notification_id: ID de la notificación
        user_id: ID del usuario (para verificar propiedad)
        
    Returns:
        True si se eliminó
        
    Raises:
        HTTPException: Si no existe o no pertenece al usuario
    """
    notification = get_notification_by_id(db, notification_id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    
    if notification.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta notificación"
        )
    
    db.delete(notification)
    db.commit()
    
    return True


# ==========================================
# FUNCIONES DE CREACIÓN AUTOMÁTICA
# ==========================================

def notify_property_taken(db: Session, property_id: int, advisor_id: int) -> Optional[Notification]:
    """
    Crear notificación cuando un asesor toma una propiedad
    
    Args:
        db: Sesión de base de datos
        property_id: ID de la propiedad
        advisor_id: ID del asesor
        
    Returns:
        Notificación creada o None si hay error
    """
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop or not prop.submitted_by_user_id:
        return None
    
    advisor = db.query(Advisor).filter(Advisor.id == advisor_id).first()
    advisor_name = advisor.user.full_name if advisor else "un asesor"
    
    return create_notification(
        db=db,
        user_id=prop.submitted_by_user_id,
        notification_type="advisor_assigned",
        title="Asesor asignado a tu propiedad",
        message=f"El asesor {advisor_name} ha tomado tu propiedad '{prop.title}' y está en proceso de revisión. Te contactará pronto.",
        property_id=property_id
    )


def notify_property_approved(db: Session, property_id: int) -> Optional[Notification]:
    """
    Crear notificación cuando una propiedad es aprobada
    
    Args:
        db: Sesión de base de datos
        property_id: ID de la propiedad
        
    Returns:
        Notificación creada o None si hay error
    """
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop or not prop.submitted_by_user_id:
        return None
    
    return create_notification(
        db=db,
        user_id=prop.submitted_by_user_id,
        notification_type="approved",
        title="¡Tu propiedad fue aprobada!",
        message=f"Tu propiedad '{prop.title}' ha sido aprobada y ahora está visible para el público.",
        property_id=property_id
    )


def notify_property_rejected(db: Session, property_id: int, reason: Optional[str] = None) -> Optional[Notification]:
    """
    Crear notificación cuando una propiedad es rechazada
    
    Args:
        db: Sesión de base de datos
        property_id: ID de la propiedad
        reason: Razón del rechazo
        
    Returns:
        Notificación creada o None si hay error
    """
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop or not prop.submitted_by_user_id:
        return None
    
    reason_text = f" Razón: {reason}" if reason else " Por favor revisa los requisitos."
    
    return create_notification(
        db=db,
        user_id=prop.submitted_by_user_id,
        notification_type="rejected",
        title="Tu propiedad fue rechazada",
        message=f"Tu propiedad '{prop.title}' no fue aprobada.{reason_text} Te recomendamos corregir los datos e intentar nuevamente.",
        property_id=property_id
    )


def notify_property_sold(db: Session, property_id: int) -> Optional[Notification]:
    """
    Crear notificación cuando una propiedad es marcada como vendida
    
    Args:
        db: Sesión de base de datos
        property_id: ID de la propiedad
        
    Returns:
        Notificación creada o None si hay error
    """
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop or not prop.submitted_by_user_id:
        return None
    
    return create_notification(
        db=db,
        user_id=prop.submitted_by_user_id,
        notification_type="sold",
        title="¡Tu propiedad ha sido vendido/rentada!",
        message=f"Congratulations! Tu propiedad '{prop.title}' ha sido marcada como vendida/rentada. Gracias por usar nossos servicios.",
        property_id=property_id
    )


# ==========================================
# NOTIFICACIONES DE CITAS
# ==========================================

def notify_appointment_confirmed(db: Session, appointment_id: int) -> Optional[Notification]:
    """
    Crear notificación cuando una cita es confirmada
    
    Args:
        db: Sesión de base de datos
        appointment_id: ID de la cita
        
    Returns:
        Notificación creada o None si hay error
    """
    from app.models import Appointment, Advisor
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        return None
    
    advisor = db.query(Advisor).filter(Advisor.id == appointment.advisor_id).first()
    advisor_name = advisor.user.full_name if advisor else "el asesor"
    
    date_str = appointment.scheduled_date.strftime("%d/%m/%Y a las %H:%M")
    
    return create_notification(
        db=db,
        user_id=appointment.client_id,
        notification_type="appointment_confirmed",
        title="Cita confirmada",
        message=f"{advisor_name} ha confirmado tu cita para el {date_str}.",
        property_id=appointment.property_id
    )


def notify_appointment_cancelled(
    db: Session,
    appointment_id: int,
    cancelled_by_user_id: int,
    reason: Optional[str] = None
) -> List[Notification]:
    """
    Crear notificaciones cuando una cita es cancelada (al cliente y al asesor)
    
    Args:
        db: Sesión de base de datos
        appointment_id: ID de la cita
        cancelled_by_user_id: ID del usuario que canceló
        reason: Razón de la cancelación
        
    Returns:
        Lista de notificaciones creadas
    """
    from app.models import Appointment, Advisor
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        return []
    
    notifications = []
    reason_text = f" Razón: {reason}" if reason else ""
    
    # Notificar al cliente (si no fue quien canceló)
    if cancelled_by_user_id != appointment.client_id:
        notifications.append(create_notification(
            db=db,
            user_id=appointment.client_id,
            notification_type="appointment_cancelled",
            title="Cita cancelada",
            message=f"Tu cita ha sido cancelada.{reason_text}",
            property_id=appointment.property_id
        ))
    
    # Notificar al asesor (si no fue quien canceló)
    advisor = db.query(Advisor).filter(Advisor.id == appointment.advisor_id).first()
    if advisor and cancelled_by_user_id != advisor.user_id:
        notifications.append(create_notification(
            db=db,
            user_id=advisor.user_id,
            notification_type="appointment_cancelled",
            title="Cita cancelada por cliente",
            message=f"El cliente ha cancelado la cita.{reason_text}",
            property_id=appointment.property_id
        ))
    
    return notifications


# ==========================================
# PREFERENCIAS
# ==========================================


def _is_notification_enabled(db: Session, user_id: int, notification_type: str) -> bool:
    """Verifica si el usuario tiene habilitado este tipo de notificación."""
    try:
        from app.services.notificationPreferenceService import is_enabled
        return is_enabled(db, user_id, notification_type)
    except Exception:
        return True  # Por defecto, habilitado


# ==========================================
# WEBSOCKET PUSH
# ==========================================

def _push_via_websocket(notification: Notification) -> None:
    """Envía la notificación en tiempo real vía WebSocket."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return  # No hay event loop (tests, CLI, etc.)

    if not loop.is_running():
        return

    async def _send():
        from app.core.websocket import manager
        data = {
            "type": "notification",
            "data": {
                "id": notification.id,
                "user_id": notification.user_id,
                "type": notification.type,
                "title": notification.title,
                "message": notification.message,
                "property_id": notification.property_id,
                "is_read": notification.is_read,
                "created_at": notification.created_at.isoformat() if notification.created_at else None
            }
        }
        await manager.send_personal_message(data, notification.user_id)

    asyncio.ensure_future(_send())


def notify_appointment_reminder(db: Session, appointment_id: int) -> Optional[Notification]:
    """
    Crear notificación de recordatorio 24h antes de una cita
    
    Args:
        db: Sesión de base de datos
        appointment_id: ID de la cita
        
    Returns:
        Notificación creada o None si hay error
    """
    from app.models import Appointment, Property
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        return None
    
    date_str = appointment.scheduled_date.strftime("%d/%m/%Y a las %H:%M")
    property_title = ""
    
    if appointment.property_id:
        prop = db.query(Property).filter(Property.id == appointment.property_id).first()
        property_title = f" para ver '{prop.title}'" if prop else ""
    
    return create_notification(
        db=db,
        user_id=appointment.client_id,
        notification_type="appointment_reminder",
        title="Recordatorio de cita",
        message=f"Recuerda que tienes una cita{property_title} el {date_str}.",
        property_id=appointment.property_id
    )