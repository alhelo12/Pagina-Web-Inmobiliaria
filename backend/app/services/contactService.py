"""
Service: Contact

Logica de negocio para el formulario de contacto publico.
Crea consultas en la base de datos y notifica a todos los asesores activos.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import ContactInquiry, Advisor, User
from app.schemas.contactSchema import ContactCreate, ContactStatusUpdate


# ==========================================
# CREACION DE CONSULTAS
# ==========================================

def create_inquiry(db: Session, data: ContactCreate) -> ContactInquiry:
    """
    Crea una nueva consulta de contacto y notifica a todos los asesores activos.

    Args:
        db: Sesion de base de datos
        data: Datos validados del formulario de contacto

    Returns:
        Consulta creada
    """
    inquiry = ContactInquiry(
        name=data.name.strip(),
        email=data.email.strip().lower(),
        phone=data.phone.strip() if data.phone else None,
        service=data.service.strip(),
        message=data.message.strip(),
        status='new'
    )

    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)

    # Notificar a todos los asesores activos
    try:
        notify_all_advisors(db, inquiry)
    except Exception:
        # No fallar la creacion de la consulta si las notificaciones fallan
        pass

    return inquiry


def notify_all_advisors(db: Session, inquiry: ContactInquiry) -> int:
    """
    Crea una notificacion para cada asesor activo cuando llega una nueva consulta.

    Args:
        db: Sesion de base de datos
        inquiry: Consulta recibida

    Returns:
        Numero de notificaciones creadas
    """
    from app.services.notificationService import create_notification

    active_advisors = (
        db.query(Advisor)
        .join(User, Advisor.user_id == User.id)
        .filter(User.is_active == True)
        .all()
    )

    phone_text = f" Tel: {inquiry.phone}" if inquiry.phone else ""
    message = (
        f"Nueva consulta de {inquiry.name} ({inquiry.email}{phone_text}) "
        f"sobre '{inquiry.service}': {inquiry.message[:120]}"
        f"{'...' if len(inquiry.message) > 120 else ''}"
    )

    notifications_created = 0
    for advisor in active_advisors:
        try:
            notif = create_notification(
                db=db,
                user_id=advisor.user_id,
                notification_type="contact_inquiry",
                title="Nueva consulta desde el formulario de contacto",
                message=message,
                property_id=None
            )
            if notif is not None:
                notifications_created += 1
        except Exception:
            # Continuar con los demas asesores aunque uno falle
            continue

    return notifications_created


# ==========================================
# CONSULTAS
# ==========================================

def get_inquiry_by_id(db: Session, inquiry_id: int) -> Optional[ContactInquiry]:
    """Obtiene una consulta por su ID"""
    return db.query(ContactInquiry).filter(ContactInquiry.id == inquiry_id).first()


def get_inquiries(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None
) -> List[ContactInquiry]:
    """
    Lista consultas con filtros opcionales.

    Args:
        db: Sesion de base de datos
        skip: Registros a saltar (paginacion)
        limit: Maximo de registros
        status: Filtrar por estado (new, contacted, closed)

    Returns:
        Lista de consultas
    """
    query = db.query(ContactInquiry)

    if status:
        query = query.filter(ContactInquiry.status == status)

    return query.order_by(ContactInquiry.created_at.desc()).offset(skip).limit(limit).all()


def count_inquiries(db: Session, status: Optional[str] = None) -> int:
    """Cuenta el total de consultas con filtros opcionales"""
    query = db.query(ContactInquiry)
    if status:
        query = query.filter(ContactInquiry.status == status)
    return query.count()


# ==========================================
# ACTUALIZACION DE ESTADO
# ==========================================

def update_inquiry_status(
    db: Session,
    inquiry_id: int,
    status_data: ContactStatusUpdate
) -> Optional[ContactInquiry]:
    """
    Actualiza el estado de una consulta.

    Args:
        db: Sesion de base de datos
        inquiry_id: ID de la consulta
        status_data: Nuevo estado

    Returns:
        Consulta actualizada o None si no existe
    """
    inquiry = get_inquiry_by_id(db, inquiry_id)
    if not inquiry:
        return None

    new_status = status_data.status.value if hasattr(status_data.status, 'value') else status_data.status

    if new_status == 'contacted':
        inquiry.mark_contacted()
    elif new_status == 'closed':
        inquiry.mark_closed()
    else:
        inquiry.status = new_status

    db.commit()
    db.refresh(inquiry)

    return inquiry
