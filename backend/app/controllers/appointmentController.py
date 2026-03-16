"""
Controller: Appointment

Endpoints para gestión de citas entre clientes y asesores.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.dbConfig.databaseSession import get_db
from app.services import appointmentService
from app.schemas import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentDetailResponse,
    AppointmentListResponse
)

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


# ==========================================
# LISTAR CITAS
# ==========================================

@router.get("", response_model=AppointmentListResponse)
def get_appointments(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de registros"),
    client_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    advisor_id: Optional[int] = Query(None, description="Filtrar por asesor"),
    property_id: Optional[int] = Query(None, description="Filtrar por propiedad"),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db)
):
    """
    Listar citas con filtros opcionales
    
    Query params:
    - **skip**: Paginación
    - **limit**: Máximo de resultados (1-100)
    - **client_id**: Filtrar por cliente
    - **advisor_id**: Filtrar por asesor
    - **property_id**: Filtrar por propiedad
    - **status**: Filtrar por estado (pending, confirmed, completed, cancelled)
    
    Retorna:
    - Lista de citas ordenadas por fecha (más recientes primero)
    - Total de citas
    
    Nota: Con JWT, usuarios verán solo sus citas.
    Advisors verán sus citas asignadas. Admin verá todas.
    """
    appointments = appointmentService.get_appointments(
        db,
        skip=skip,
        limit=limit,
        client_id=client_id,
        advisor_id=advisor_id,
        property_id=property_id,
        status=status
    )
    
    total = appointmentService.count_appointments(
        db,
        client_id=client_id,
        advisor_id=advisor_id,
        status=status
    )
    
    return {
        "appointments": appointments,
        "total": total,
        "skip": skip,
        "limit": limit
    }


# ==========================================
# OBTENER CITA POR ID
# ==========================================

@router.get("/{appointment_id}", response_model=AppointmentDetailResponse)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener cita por ID
    
    Path params:
    - **appointment_id**: ID de la cita
    
    Retorna:
    - Cita con todos sus datos
    - Información del cliente
    - Información del asesor
    - Información de la propiedad (si aplica)
    
    Errores:
    - 404: Cita no encontrada
    """
    appointment = appointmentService.get_appointment_by_id(db, appointment_id)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada"
        )
    
    return appointment


# ==========================================
# CREAR CITA
# ==========================================

@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    appointment_data: AppointmentCreate,
    client_id: int = Query(..., description="ID del cliente (temporal, con JWT se extraerá del token)"),
    db: Session = Depends(get_db)
):
    """
    Crear nueva cita
    
    Query params:
    - **client_id**: ID del cliente (TEMPORAL, con JWT del token)
    
    Body:
    - **advisor_id**: ID del asesor
    - **property_id**: ID de la propiedad (opcional)
    - **appointment_type**: Tipo (viewing, inspection)
    - **scheduled_date**: Fecha y hora de la cita (formato ISO)
    - **notes**: Notas adicionales (opcional)
    
    La cita se crea con status='pending' automáticamente.
    
    Validaciones:
    - Asesor debe existir
    - Propiedad debe existir (si se proporciona)
    - Fecha debe ser futura
    
    Errores:
    - 404: Asesor o propiedad no encontrado
    - 400: Fecha inválida
    """
    appointment = appointmentService.create_appointment(
        db,
        appointment_data,
        client_id
    )
    return appointment


# ==========================================
# ACTUALIZAR CITA
# ==========================================

@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    user_id: int = Query(..., description="ID del usuario (temporal)"),
    db: Session = Depends(get_db)
):
    """
    Actualizar cita existente
    
    Path params:
    - **appointment_id**: ID de la cita
    
    Query params:
    - **user_id**: ID del usuario (TEMPORAL, con JWT del token)
    
    Body (todos opcionales):
    - Campos de AppointmentUpdate
    
    Validaciones:
    - Solo el cliente puede editar la cita
    - Solo se puede editar si está pending o confirmed
    - Fecha debe ser futura
    
    Errores:
    - 404: Cita no encontrada
    - 403: Sin permisos
    - 400: Estado inválido o fecha inválida
    """
    appointment = appointmentService.update_appointment(
        db,
        appointment_id,
        appointment_data,
        user_id=user_id
    )
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada"
        )
    
    return appointment


# ==========================================
# ELIMINAR CITA
# ==========================================

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(
    appointment_id: int,
    user_id: int = Query(..., description="ID del usuario"),
    db: Session = Depends(get_db)
):
    """
    Eliminar cita
    
    Path params:
    - **appointment_id**: ID de la cita
    
    Query params:
    - **user_id**: ID del usuario (TEMPORAL)
    
    Validaciones:
    - Solo el cliente puede eliminar su cita
    
    Errores:
    - 404: Cita no encontrada
    - 403: Sin permisos
    
    Nota: Es preferible usar el endpoint de cancelar (/cancel)
    en lugar de eliminar permanentemente.
    """
    success = appointmentService.delete_appointment(
        db,
        appointment_id,
        user_id=user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada"
        )
    
    return None


# ==========================================
# GESTIÓN DE ESTADO
# ==========================================

@router.patch("/{appointment_id}/confirm", response_model=AppointmentResponse)
def confirm_appointment(
    appointment_id: int,
    advisor_id: int = Query(..., description="ID del asesor (temporal)"),
    db: Session = Depends(get_db)
):
    """
    Confirmar cita (solo asesor)
    
    Path params:
    - **appointment_id**: ID de la cita
    
    Query params:
    - **advisor_id**: ID del asesor (TEMPORAL, con JWT se extraerá)
    
    Cambia el estado de 'pending' a 'confirmed'.
    
    Validaciones:
    - Solo el asesor asignado puede confirmar
    - Cita debe estar en estado 'pending'
    
    Errores:
    - 404: Cita no encontrada
    - 403: Sin permisos
    - 400: Estado inválido
    
    Nota: Con JWT, solo usuarios con rol 'advisor' podrán confirmar.
    """
    appointment = appointmentService.confirm_appointment(
        db,
        appointment_id,
        advisor_id=advisor_id
    )
    return appointment


@router.patch("/{appointment_id}/complete", response_model=AppointmentResponse)
def complete_appointment(
    appointment_id: int,
    advisor_id: int = Query(..., description="ID del asesor"),
    db: Session = Depends(get_db)
):
    """
    Marcar cita como completada (solo asesor)
    
    Path params:
    - **appointment_id**: ID de la cita
    
    Query params:
    - **advisor_id**: ID del asesor (TEMPORAL)
    
    Cambia el estado de 'confirmed' a 'completed'.
    
    Validaciones:
    - Solo el asesor asignado puede completar
    - Cita debe estar en estado 'confirmed'
    
    Errores:
    - 404: Cita no encontrada
    - 403: Sin permisos
    - 400: Estado inválido
    """
    appointment = appointmentService.complete_appointment(
        db,
        appointment_id,
        advisor_id=advisor_id
    )
    return appointment


@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(
    appointment_id: int,
    user_id: int = Query(..., description="ID del usuario"),
    reason: Optional[str] = Query(None, description="Razón de la cancelación"),
    db: Session = Depends(get_db)
):
    """
    Cancelar cita (cliente o asesor)
    
    Path params:
    - **appointment_id**: ID de la cita
    
    Query params:
    - **user_id**: ID del usuario (TEMPORAL)
    - **reason**: Razón de la cancelación (opcional)
    
    Cambia el estado a 'cancelled'.
    Tanto el cliente como el asesor pueden cancelar.
    
    Validaciones:
    - Solo cliente o asesor asignado pueden cancelar
    - No se puede cancelar si ya está completed o cancelled
    
    Errores:
    - 404: Cita no encontrada
    - 403: Sin permisos
    - 400: Estado inválido
    """
    appointment = appointmentService.cancel_appointment(
        db,
        appointment_id,
        user_id=user_id,
        reason=reason
    )
    return appointment


# ==========================================
# CONSULTAS ESPECIALES
# ==========================================

@router.get("/upcoming/list", response_model=AppointmentListResponse)
def get_upcoming_appointments(
    client_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    advisor_id: Optional[int] = Query(None, description="Filtrar por asesor"),
    days_ahead: int = Query(7, ge=1, le=90, description="Días hacia adelante"),
    db: Session = Depends(get_db)
):
    """
    Obtener citas próximas
    
    Query params:
    - **client_id**: Filtrar por cliente (opcional)
    - **advisor_id**: Filtrar por asesor (opcional)
    - **days_ahead**: Días hacia adelante a consultar (1-90, default: 7)
    
    Retorna:
    - Lista de citas próximas (pending o confirmed)
    - Ordenadas por fecha ascendente
    
    Útil para:
    - "Mis próximas citas"
    - "Citas de esta semana"
    - Calendarios
    """
    appointments = appointmentService.get_upcoming_appointments(
        db,
        client_id=client_id,
        advisor_id=advisor_id,
        days_ahead=days_ahead
    )
    
    return {
        "appointments": appointments,
        "total": len(appointments),
        "skip": 0,
        "limit": len(appointments)
    }


@router.get("/today/list", response_model=AppointmentListResponse)
def get_today_appointments(
    advisor_id: Optional[int] = Query(None, description="Filtrar por asesor"),
    db: Session = Depends(get_db)
):
    """
    Obtener citas de hoy
    
    Query params:
    - **advisor_id**: Filtrar por asesor (opcional)
    
    Retorna:
    - Lista de citas de hoy (pending o confirmed)
    - Ordenadas por hora
    
    Útil para:
    - "Mis citas de hoy"
    - Dashboard de asesor
    """
    appointments = appointmentService.get_today_appointments(
        db,
        advisor_id=advisor_id
    )
    
    return {
        "appointments": appointments,
        "total": len(appointments),
        "skip": 0,
        "limit": len(appointments)
    }


@router.get("/check-availability/{advisor_id}")
def check_advisor_availability(
    advisor_id: int,
    scheduled_date: str = Query(..., description="Fecha/hora en formato ISO"),
    duration_minutes: int = Query(60, ge=15, le=480, description="Duración en minutos"),
    db: Session = Depends(get_db)
):
    """
    Verificar disponibilidad de asesor
    
    Path params:
    - **advisor_id**: ID del asesor
    
    Query params:
    - **scheduled_date**: Fecha/hora propuesta (ISO 8601)
    - **duration_minutes**: Duración estimada (15-480 minutos, default: 60)
    
    Retorna:
    - available: True si está disponible, False si hay conflicto
    
    Útil para:
    - Validar antes de crear cita
    - Mostrar horarios disponibles
    """
    from datetime import datetime
    
    try:
        date_obj = datetime.fromisoformat(scheduled_date.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de fecha inválido. Use ISO 8601 (YYYY-MM-DDTHH:MM:SS)"
        )
    
    available = appointmentService.check_advisor_availability(
        db,
        advisor_id,
        date_obj,
        duration_minutes
    )
    
    return {
        "advisor_id": advisor_id,
        "scheduled_date": scheduled_date,
        "duration_minutes": duration_minutes,
        "available": available
    }


# ==========================================
# ESTADÍSTICAS
# ==========================================

@router.get("/stats/general")
def get_appointment_stats(
    client_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    advisor_id: Optional[int] = Query(None, description="Filtrar por asesor"),
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas de citas
    
    Query params:
    - **client_id**: Filtrar por cliente (opcional)
    - **advisor_id**: Filtrar por asesor (opcional)
    
    Retorna:
    - Total de citas
    - Citas por estado (pending, confirmed, completed, cancelled)
    - Citas próximas (próximos 7 días)
    
    Útil para:
    - Dashboard de usuario
    - Dashboard de asesor
    - Reportes
    """
    stats = appointmentService.get_appointment_stats(
        db,
        client_id=client_id,
        advisor_id=advisor_id
    )
    return stats
