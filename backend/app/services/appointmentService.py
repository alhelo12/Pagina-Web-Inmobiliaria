"""
Service: Appointment

Lógica de negocio para gestión de citas.
Maneja programación, confirmación, cancelación y seguimiento.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from app.models import Appointment, User, Advisor, Property
from app.schemas import AppointmentCreate, AppointmentUpdate


# ==========================================
# CRUD BÁSICO
# ==========================================

def get_appointment_by_id(db: Session, appointment_id: int) -> Optional[Appointment]:
    """
    Obtener cita por ID
    
    Args:
        db: Sesión de base de datos
        appointment_id: ID de la cita
        
    Returns:
        Appointment o None si no existe
    """
    return db.query(Appointment).filter(Appointment.id == appointment_id).first()


def get_appointments(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    client_id: Optional[int] = None,
    advisor_id: Optional[int] = None,
    property_id: Optional[int] = None,
    status: Optional[str] = None
) -> List[Appointment]:
    """
    Obtener lista de citas con filtros
    
    Args:
        db: Sesión de base de datos
        skip: Registros a saltar
        limit: Máximo de registros
        client_id: Filtrar por cliente
        advisor_id: Filtrar por asesor
        property_id: Filtrar por propiedad
        status: Filtrar por estado
        
    Returns:
        Lista de citas
    """
    query = db.query(Appointment)
    
    if client_id:
        query = query.filter(Appointment.client_id == client_id)
    
    if advisor_id:
        query = query.filter(Appointment.advisor_id == advisor_id)
    
    if property_id:
        query = query.filter(Appointment.property_id == property_id)
    
    if status:
        query = query.filter(Appointment.status == status)
    
    # Ordenar por fecha (más recientes primero)
    query = query.order_by(Appointment.scheduled_date.desc())
    
    return query.offset(skip).limit(limit).all()


def count_appointments(
    db: Session,
    client_id: Optional[int] = None,
    advisor_id: Optional[int] = None,
    status: Optional[str] = None
) -> int:
    """
    Contar citas con filtros
    
    Args:
        db: Sesión de base de datos
        client_id: Filtrar por cliente
        advisor_id: Filtrar por asesor
        status: Filtrar por estado
        
    Returns:
        Número total de citas
    """
    query = db.query(func.count(Appointment.id))
    
    if client_id:
        query = query.filter(Appointment.client_id == client_id)
    
    if advisor_id:
        query = query.filter(Appointment.advisor_id == advisor_id)
    
    if status:
        query = query.filter(Appointment.status == status)
    
    return query.scalar()


def create_appointment(
    db: Session,
    appointment_data: AppointmentCreate,
    client_id: int
) -> Appointment:
    """
    Crear nueva cita
    
    Args:
        db: Sesión de base de datos
        appointment_data: Datos de la cita
        client_id: ID del cliente (usuario autenticado)
        
    Returns:
        Appointment creada
        
    Raises:
        HTTPException: Si el asesor/propiedad no existe o fecha inválida
    """
    # Verificar que el asesor existe
    advisor = db.query(Advisor).filter(Advisor.id == appointment_data.advisor_id).first()
    if not advisor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asesor no encontrado"
        )
    
    # Verificar propiedad si se proporciona
    if appointment_data.property_id:
        property_obj = db.query(Property).filter(Property.id == appointment_data.property_id).first()
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Propiedad no encontrada"
            )
    
    # Validar que la fecha sea futura
    if appointment_data.scheduled_date < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de la cita debe ser futura"
        )
    
    # Validar disponibilidad del asesor (opcional)
    # has_conflict = check_advisor_availability(db, appointment_data.advisor_id, appointment_data.scheduled_date)
    # if has_conflict:
    #     raise HTTPException(...)
    
    # Crear cita
    db_appointment = Appointment(
        client_id=client_id,
        advisor_id=appointment_data.advisor_id,
        property_id=appointment_data.property_id,
        appointment_type=appointment_data.appointment_type,
        scheduled_date=appointment_data.scheduled_date,
        notes=appointment_data.notes,
        status='pending'
    )
    
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    return db_appointment


def update_appointment(
    db: Session,
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    user_id: Optional[int] = None
) -> Optional[Appointment]:
    """
    Actualizar cita existente
    
    Args:
        db: Sesión de base de datos
        appointment_id: ID de la cita
        appointment_data: Datos a actualizar
        user_id: ID del usuario (para verificar permisos)
        
    Returns:
        Appointment actualizada o None si no existe
        
    Raises:
        HTTPException: Si no tiene permisos o fecha inválida
    """
    db_appointment = get_appointment_by_id(db, appointment_id)
    
    if not db_appointment:
        return None
    
    # Verificar permisos si se proporciona user_id
    if user_id and db_appointment.client_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para editar esta cita"
        )
    
    # Solo permitir editar si está pending o confirmed
    if db_appointment.status in ['completed', 'cancelled']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede editar una cita {db_appointment.status}"
        )
    
    # Actualizar campos
    update_data = appointment_data.model_dump(exclude_unset=True)
    
    # Validar fecha si se actualiza
    if 'scheduled_date' in update_data:
        if update_data['scheduled_date'] < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de la cita debe ser futura"
            )
    
    for field, value in update_data.items():
        setattr(db_appointment, field, value)
    
    db.commit()
    db.refresh(db_appointment)
    
    return db_appointment


def delete_appointment(db: Session, appointment_id: int, user_id: Optional[int] = None) -> bool:
    """
    Eliminar cita (cancelar es preferible)
    
    Args:
        db: Sesión de base de datos
        appointment_id: ID de la cita
        user_id: ID del usuario (para verificar permisos)
        
    Returns:
        True si se eliminó, False si no existe
        
    Raises:
        HTTPException: Si no tiene permisos
    """
    db_appointment = get_appointment_by_id(db, appointment_id)
    
    if not db_appointment:
        return False
    
    # Verificar permisos
    if user_id and db_appointment.client_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar esta cita"
        )
    
    db.delete(db_appointment)
    db.commit()
    
    return True


# ==========================================
# GESTIÓN DE ESTADO
# ==========================================

def confirm_appointment(db: Session, appointment_id: int, advisor_id: Optional[int] = None) -> Appointment:
    """
    Confirmar cita (asesor)
    
    Args:
        db: Sesión de base de datos
        appointment_id: ID de la cita
        advisor_id: ID del asesor (para verificar permisos)
        
    Returns:
        Appointment confirmada
        
    Raises:
        HTTPException: Si la cita no existe, no está pending, o sin permisos
    """
    db_appointment = get_appointment_by_id(db, appointment_id)
    
    if not db_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada"
        )
    
    # Verificar permisos
    if advisor_id and db_appointment.advisor_id != advisor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el asesor asignado puede confirmar esta cita"
        )
    
    # Verificar estado
    if db_appointment.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solo se pueden confirmar citas pendientes (estado actual: {db_appointment.status})"
        )
    
    db_appointment.status = 'confirmed'
    db.commit()
    db.refresh(db_appointment)
    
    return db_appointment


def complete_appointment(db: Session, appointment_id: int, advisor_id: Optional[int] = None) -> Appointment:
    """
    Marcar cita como completada (asesor)
    
    Args:
        db: Sesión de base de datos
        appointment_id: ID de la cita
        advisor_id: ID del asesor (para verificar permisos)
        
    Returns:
        Appointment completada
        
    Raises:
        HTTPException: Si la cita no existe, no está confirmed, o sin permisos
    """
    db_appointment = get_appointment_by_id(db, appointment_id)
    
    if not db_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada"
        )
    
    # Verificar permisos
    if advisor_id and db_appointment.advisor_id != advisor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el asesor asignado puede completar esta cita"
        )
    
    # Verificar estado
    if db_appointment.status != 'confirmed':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solo se pueden completar citas confirmadas (estado actual: {db_appointment.status})"
        )
    
    db_appointment.status = 'completed'
    db.commit()
    db.refresh(db_appointment)
    
    return db_appointment


def cancel_appointment(
    db: Session,
    appointment_id: int,
    user_id: Optional[int] = None,
    reason: Optional[str] = None
) -> Appointment:
    """
    Cancelar cita (cliente o asesor)
    
    Args:
        db: Sesión de base de datos
        appointment_id: ID de la cita
        user_id: ID del usuario (cliente o asesor)
        reason: Razón de la cancelación
        
    Returns:
        Appointment cancelada
        
    Raises:
        HTTPException: Si la cita no existe, ya está completada/cancelada, o sin permisos
    """
    db_appointment = get_appointment_by_id(db, appointment_id)
    
    if not db_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada"
        )
    
    # Verificar permisos (cliente o asesor pueden cancelar)
    if user_id:
        advisor = db.query(Advisor).filter(Advisor.user_id == user_id).first()
        advisor_id = advisor.id if advisor else None
        
        if db_appointment.client_id != user_id and db_appointment.advisor_id != advisor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para cancelar esta cita"
            )
    
    # Verificar estado
    if db_appointment.status in ['completed', 'cancelled']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede cancelar una cita {db_appointment.status}"
        )
    
    db_appointment.status = 'cancelled'
    
    # Guardar razón en notes si se proporciona
    if reason:
        current_notes = db_appointment.notes or ""
        db_appointment.notes = f"{current_notes}\n[CANCELADA] {reason}".strip()
    
    db.commit()
    db.refresh(db_appointment)
    
    return db_appointment


# ==========================================
# CONSULTAS ESPECIALES
# ==========================================

def get_upcoming_appointments(
    db: Session,
    client_id: Optional[int] = None,
    advisor_id: Optional[int] = None,
    days_ahead: int = 7
) -> List[Appointment]:
    """
    Obtener citas próximas
    
    Args:
        db: Sesión de base de datos
        client_id: Filtrar por cliente
        advisor_id: Filtrar por asesor
        days_ahead: Días hacia adelante a consultar
        
    Returns:
        Lista de citas próximas
    """
    now = datetime.now()
    future_date = now + timedelta(days=days_ahead)
    
    query = db.query(Appointment)\
        .filter(Appointment.scheduled_date >= now)\
        .filter(Appointment.scheduled_date <= future_date)\
        .filter(Appointment.status.in_(['pending', 'confirmed']))
    
    if client_id:
        query = query.filter(Appointment.client_id == client_id)
    
    if advisor_id:
        query = query.filter(Appointment.advisor_id == advisor_id)
    
    return query.order_by(Appointment.scheduled_date.asc()).all()


def get_today_appointments(
    db: Session,
    advisor_id: Optional[int] = None
) -> List[Appointment]:
    """
    Obtener citas de hoy
    
    Args:
        db: Sesión de base de datos
        advisor_id: Filtrar por asesor
        
    Returns:
        Lista de citas de hoy
    """
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    query = db.query(Appointment)\
        .filter(Appointment.scheduled_date >= today_start)\
        .filter(Appointment.scheduled_date < today_end)\
        .filter(Appointment.status.in_(['pending', 'confirmed']))
    
    if advisor_id:
        query = query.filter(Appointment.advisor_id == advisor_id)
    
    return query.order_by(Appointment.scheduled_date.asc()).all()


def check_advisor_availability(
    db: Session,
    advisor_id: int,
    scheduled_date: datetime,
    duration_minutes: int = 60
) -> bool:
    """
    Verificar si un asesor está disponible en una fecha/hora
    
    Args:
        db: Sesión de base de datos
        advisor_id: ID del asesor
        scheduled_date: Fecha/hora propuesta
        duration_minutes: Duración estimada de la cita
        
    Returns:
        True si está disponible, False si hay conflicto
    """
    end_time = scheduled_date + timedelta(minutes=duration_minutes)
    
    # Buscar citas confirmadas que se traslapen
    conflicts = db.query(Appointment)\
        .filter(Appointment.advisor_id == advisor_id)\
        .filter(Appointment.status.in_(['pending', 'confirmed']))\
        .filter(
            or_(
                and_(
                    Appointment.scheduled_date >= scheduled_date,
                    Appointment.scheduled_date < end_time
                ),
                and_(
                    Appointment.scheduled_date < scheduled_date,
                    Appointment.scheduled_date >= scheduled_date - timedelta(minutes=duration_minutes)
                )
            )
        )\
        .count()
    
    return conflicts == 0


# ==========================================
# ESTADÍSTICAS
# ==========================================

def get_appointment_stats(
    db: Session,
    client_id: Optional[int] = None,
    advisor_id: Optional[int] = None
) -> dict:
    """
    Obtener estadísticas de citas
    
    Args:
        db: Sesión de base de datos
        client_id: Filtrar por cliente
        advisor_id: Filtrar por asesor
        
    Returns:
        Diccionario con estadísticas
    """
    query = db.query(Appointment)
    
    if client_id:
        query = query.filter(Appointment.client_id == client_id)
    
    if advisor_id:
        query = query.filter(Appointment.advisor_id == advisor_id)
    
    total = query.count()
    pending = query.filter(Appointment.status == 'pending').count()
    confirmed = query.filter(Appointment.status == 'confirmed').count()
    completed = query.filter(Appointment.status == 'completed').count()
    cancelled = query.filter(Appointment.status == 'cancelled').count()
    
    # Citas próximas (próximos 7 días)
    now = datetime.now()
    future_date = now + timedelta(days=7)
    upcoming = query\
        .filter(Appointment.scheduled_date >= now)\
        .filter(Appointment.scheduled_date <= future_date)\
        .filter(Appointment.status.in_(['pending', 'confirmed']))\
        .count()
    
    return {
        "total": total,
        "pending": pending,
        "confirmed": confirmed,
        "completed": completed,
        "cancelled": cancelled,
        "upcoming": upcoming
    }
    