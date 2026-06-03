"""
Controller: Contact (Formulario Publico de Contacto)

Endpoints PUBLICOS para recibir consultas desde el formulario del sitio web.
Este es el unico endpoint del sistema que no requiere autenticacion.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import Optional
from slowapi.errors import RateLimitExceeded

from app.dbConfig.databaseSession import get_db
from app.services import contactService
from app.core.dependencies import get_current_user
from app.core.rateLimiter import limiter
from app.models import User
from app.schemas.contactSchema import (
    ContactCreate,
    ContactResponse,
    ContactDetailResponse,
    ContactListResponse,
    ContactStatusUpdate,
    ContactSuccessResponse
)

router = APIRouter(
    prefix="/contact",
    tags=["Contact (Public)"]
)


# ==========================================
# ENDPOINT PUBLICO (sin autenticacion)
# ==========================================

@router.post(
    "",
    response_model=ContactSuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar consulta desde el formulario publico"
)
@limiter.limit("5 per hour")
def submit_contact_form(
    request: Request,
    data: ContactCreate,
    db: Session = Depends(get_db)
):
    """
    Recibe una consulta desde el formulario publico de contacto.

    **No requiere autenticacion.**

    Crea un registro en la base de datos y notifica automaticamente
    a todos los asesores activos del sistema.

    Rate limit: 5 consultas por hora por IP.
    """
    inquiry = contactService.create_inquiry(db=db, data=data)

    return ContactSuccessResponse(
        success=True,
        message="Tu consulta fue recibida. Un asesor te contactara pronto.",
        inquiry_id=inquiry.id
    )


# ==========================================
# ENDPOINTS PROTEGIDOS (admin/asesor)
# ==========================================

@router.get(
    "/inquiries",
    response_model=ContactListResponse,
    summary="Listar consultas de contacto (asesor/admin)"
)
def list_inquiries(
    page: int = Query(1, ge=1, description="Numero de pagina"),
    per_page: int = Query(20, ge=1, le=100, description="Resultados por pagina"),
    status_filter: Optional[str] = Query(None, description="Filtrar por estado: new, contacted, closed"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todas las consultas de contacto.

    Requiere autenticacion. Accesible para asesores y administradores.
    """
    if not (current_user.is_admin() or current_user.is_advisor()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver las consultas de contacto"
        )

    skip = (page - 1) * per_page
    inquiries = contactService.get_inquiries(
        db=db,
        skip=skip,
        limit=per_page,
        status=status_filter
    )
    total = contactService.count_inquiries(db=db, status=status_filter)

    return ContactListResponse(
        total=total,
        page=page,
        per_page=per_page,
        inquiries=inquiries
    )


@router.get(
    "/inquiries/{inquiry_id}",
    response_model=ContactDetailResponse,
    summary="Detalle de una consulta de contacto"
)
def get_inquiry(
    inquiry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el detalle completo de una consulta.

    Requiere autenticacion. Accesible para asesores y administradores.
    """
    if not (current_user.is_admin() or current_user.is_advisor()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver las consultas de contacto"
        )

    inquiry = contactService.get_inquiry_by_id(db=db, inquiry_id=inquiry_id)
    if not inquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta no encontrada"
        )

    return inquiry


@router.patch(
    "/inquiries/{inquiry_id}/status",
    response_model=ContactDetailResponse,
    summary="Actualizar estado de una consulta"
)
def update_inquiry_status(
    inquiry_id: int,
    status_data: ContactStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza el estado de gestion de una consulta.

    Estados: new, contacted, closed.
    Requiere autenticacion. Accesible para asesores y administradores.
    """
    if not (current_user.is_admin() or current_user.is_advisor()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar consultas"
        )

    inquiry = contactService.update_inquiry_status(
        db=db,
        inquiry_id=inquiry_id,
        status_data=status_data
    )
    if not inquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta no encontrada"
        )

    return inquiry
