"""
Controller: Appointments

Endpoints para gestión de citas entre clientes y asesores.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.dbConfig.databaseSession import get_db
from app.services import appointmentService
from app.core.activityLogger import log_activity
from app.core.dependencies import (
    get_current_user,
    require_advisor
)
from app.schemas import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentListResponse
)
from app.models import User

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


# ==========================================
# ENDPOINTS PARA CLIENTES
# ==========================================

@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
@log_activity("appointment_created", "appointment")
def create_appointment(
    appointment_data: AppointmentCreate,
    client_id: int = Query(..., description="ID del cliente"),
    current_user: User = Depends(get_current_user),  # 🔐 Requiere autenticación
    db: Session = Depends(get_db)
):
    """
    Crear nueva cita (cliente autenticado)
    
    El cliente solicita una cita con un asesor para ver una propiedad.
    
    Validaciones:
    - Usuario autenticado
    - Usuario debe ser el mismo que client_id (o admin)
    - Fecha de cita debe ser futura
    - Asesor debe existir
    - Propiedad debe existir
    """
    # Verificar que el usuario sea el cliente o admin
    if not current_user.is_admin() and current_user.id != client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes crear citas para otros usuarios"
        )
    
    appointment = appointmentService.create_appointment(db, appointment_data, client_id)
    return appointment


@router.get("", response_model=AppointmentListResponse)
def get_my_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, description="Filtrar por status"),
    current_user: User = Depends(get_current_user),  # 🔐 Requiere autenticación
    db: Session = Depends(get_db)
):
    """
    Listar citas del cliente (autenticado)
    
    El cliente ve sus propias citas. Se obtiene el client_id del token JWT.
    """
    # Usar el ID del usuario autenticado directamente
    client_id = current_user.id
    
    appointments = appointmentService.get_appointments(
        db,
        skip=skip,
        limit=limit,
        client_id=client_id,
        status=status_filter
    )
    total = appointmentService.count_appointments(db, client_id=client_id, status=status_filter)
    
    return AppointmentListResponse(
        total=total,
        page=(skip // limit) + 1,
        per_page=limit,
        appointments=appointments
    )


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),  # 🔐 Requiere autenticación
    db: Session = Depends(get_db)
):
    """
    Obtener detalle de cita (autenticado)
    
    Solo el cliente o el asesor involucrados pueden ver la cita.
    Admin puede ver cualquier cita.
    """
    appointment = appointmentService.get_appointment_by_id(db, appointment_id)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada"
        )
    
    # Verificar que sea el cliente, el asesor o admin
    is_client = appointment.client_id == current_user.id
    is_advisor = current_user.advisor and appointment.advisor_id == current_user.advisor.id
    is_admin = current_user.is_admin()
    
    if not (is_client or is_advisor or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver esta cita"
        )
    
    return appointment


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    current_user: User = Depends(get_current_user),  # 🔐 Requiere autenticación
    db: Session = Depends(get_db)
):
    """
    Actualizar cita (autenticado)
    
    El cliente puede actualizar sus citas.
    Solo si el status es 'pending' o 'confirmed'.
    """
    appointment = appointmentService.get_appointment_by_id(db, appointment_id)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada"
        )
    
    # Verificar ownership
    if not current_user.is_admin() and appointment.client_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes actualizar citas de otros usuarios"
        )
    
    # Verificar que la cita no esté completada o cancelada
    if appointment.status in ['completed', 'cancelled']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede actualizar una cita {appointment.status}"
        )
    
    updated_appointment = appointmentService.update_appointment(db, appointment_id, appointment_data)
    return updated_appointment


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
@log_activity("appointment_cancelled", "appointment", "appointment_id")
def cancel_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),  # 🔐 Requiere autenticación
    db: Session = Depends(get_db)
):
    """
    Cancelar cita (autenticado)
    
    El cliente o asesor pueden cancelar la cita.
    Cambia el status a 'cancelled'.
    """
    appointment = appointmentService.get_appointment_by_id(db, appointment_id)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada"
        )
    
    # Verificar que sea el cliente, el asesor o admin
    is_client = appointment.client_id == current_user.id
    is_advisor = current_user.advisor and appointment.advisor_id == current_user.advisor.id
    is_admin = current_user.is_admin()
    
    if not (is_client or is_advisor or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para cancelar esta cita"
        )
    
    appointmentService.cancel_appointment(db, appointment_id)
    return None


# ==========================================
# ENDPOINTS PARA ADVISORS
# ==========================================

@router.get("/advisor/my-appointments", response_model=AppointmentListResponse)
def get_advisor_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    current_user: User = Depends(require_advisor),  # 🔐 Solo advisors
    db: Session = Depends(get_db)
):
    """
    Listar citas del asesor (solo advisors)
    
    Muestra todas las citas asignadas al asesor autenticado.
    """
    if not current_user.advisor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no tiene perfil de advisor"
        )
    
    advisor_id = current_user.advisor.id
    
    appointments = appointmentService.get_appointments(
        db,
        skip=skip,
        limit=limit,
        advisor_id=advisor_id,
        status=status_filter
    )
    total = appointmentService.count_appointments(db, advisor_id=advisor_id, status=status_filter)
    
    return AppointmentListResponse(
        total=total,
        page=(skip // limit) + 1,
        per_page=limit,
        appointments=appointments
    )


@router.patch("/{appointment_id}/confirm", response_model=AppointmentResponse)
@log_activity("appointment_confirmed", "appointment", "appointment_id")
def confirm_appointment(
    appointment_id: int,
    current_user: User = Depends(require_advisor),  # 🔐 Solo advisors
    db: Session = Depends(get_db)
):
    """
    Confirmar cita (solo asesor asignado)
    
    El asesor confirma la cita solicitada por el cliente.
    Cambia status de 'pending' a 'confirmed'.
    
    Validaciones:
    - Usuario es advisor
    - Cita está asignada a este advisor
    - Status es 'pending'
    """
    appointment = appointmentService.get_appointment_by_id(db, appointment_id)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada"
        )
    
    # Verificar que el advisor es el asignado
    if not current_user.advisor or appointment.advisor_id != current_user.advisor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes confirmar citas de otros asesores"
        )
    
    confirmed_appointment = appointmentService.confirm_appointment(db, appointment_id)
    return confirmed_appointment


@router.patch("/{appointment_id}/complete", response_model=AppointmentResponse)
@log_activity("appointment_completed", "appointment", "appointment_id")
def complete_appointment(
    appointment_id: int,
    current_user: User = Depends(require_advisor),  # 🔐 Solo advisors
    db: Session = Depends(get_db)
):
    """
    Completar cita (solo asesor asignado)
    
    El asesor marca la cita como completada después de realizarla.
    Cambia status de 'confirmed' a 'completed'.
    
    Validaciones:
    - Usuario es advisor
    - Cita está asignada a este advisor
    - Status es 'confirmed'
    """
    appointment = appointmentService.get_appointment_by_id(db, appointment_id)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada"
        )
    
    # Verificar que el advisor es el asignado
    if not current_user.advisor or appointment.advisor_id != current_user.advisor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes completar citas de otros asesores"
        )
    
    completed_appointment = appointmentService.complete_appointment(db, appointment_id)
    return completed_appointment


# ==========================================
# ENDPOINTS DE BÚSQUEDA
# ==========================================

@router.get("/upcoming/list", response_model=AppointmentListResponse)
def get_upcoming_appointments(
    client_id: int = Query(..., description="ID del cliente"),
    days_ahead: int = Query(7, ge=1, le=30, description="Días hacia adelante"),
    current_user: User = Depends(get_current_user),  # 🔐 Requiere autenticación
    db: Session = Depends(get_db)
):
    """
    Citas próximas del cliente (autenticado)
    
    Muestra citas confirmadas en los próximos N días.
    """
    # Verificar ownership
    if not current_user.is_admin() and current_user.id != client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes ver citas de otros usuarios"
        )
    
    result = appointmentService.get_upcoming_appointments(db, client_id, days_ahead)
    return result


@router.get("/property/{property_id}/appointments", response_model=AppointmentListResponse)
def get_property_appointments(
    property_id: int,
    current_user: User = Depends(require_advisor),  # 🔐 Solo advisors/admin
    db: Session = Depends(get_db)
):
    """
    Citas para una propiedad específica (solo advisors/admin)
    
    Muestra todas las citas asociadas a una propiedad.
    """
    result = appointmentService.get_property_appointments(db, property_id)
    return result


@router.get("/stats/summary")
@log_activity("dashboard_appointment_stats", "dashboard")
def get_appointments_stats(
    current_user: User = Depends(require_advisor),  # 🔐 Solo advisors/admin
    db: Session = Depends(get_db)
):
    """
    Estadísticas de citas (solo advisors/admin)
    
    Resumen general de citas por status.
    """
    stats = appointmentService.get_appointments_stats(db)
    return stats
