"""
Service: Property

Lógica de negocio para gestión de propiedades.
Incluye CRUD, sistema de aprobación y filtros avanzados.
"""

from pathlib import Path
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, and_, or_, text
from typing import Optional, List, Tuple
from fastapi import HTTPException, status

from app.models import Property, PropertyImage, User, Advisor, Conversation, Message
from app.schemas import PropertyCreate, PropertyUpdate, PropertySearchFilters
from app.services import notificationService, postSaleService


# ==========================================
# CRUD BÁSICO
# ==========================================

def get_property_by_id(db: Session, property_id: int) -> Optional[Property]:
    """
    Obtener propiedad por ID
    
    Args:
        db: Sesión de base de datos
        property_id: ID de la propiedad
        
    Returns:
        Property o None si no existe
    """
    return (
        db.query(Property)
        .options(
            selectinload(Property.images),
            selectinload(Property.owner),
            selectinload(Property.advisor).selectinload(Advisor.user)
        )
        .filter(Property.id == property_id)
        .first()
    )


def get_properties(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    user_id: Optional[int] = None
) -> List[Property]:
    """
    Obtener lista de propiedades con filtros básicos
    
    Args:
        db: Sesión de base de datos
        skip: Registros a saltar (paginación)
        limit: Máximo de registros
        status: Filtrar por estado (pending, approved, rejected, sold)
        user_id: Filtrar por usuario que publicó
        
    Returns:
        Lista de propiedades
    """
    query = db.query(Property).options(
        selectinload(Property.images),
        selectinload(Property.owner),
        selectinload(Property.advisor).selectinload(Advisor.user)
    )

    if status:
        query = query.filter(Property.status == status)

    if user_id:
        query = query.filter(Property.submitted_by_user_id == user_id)

    return query.offset(skip).limit(limit).all()


def get_approved_properties(
    db: Session,
    skip: int = 0,
    limit: int = 20
) -> List[Property]:
    """
    Obtener propiedades aprobadas (visibles públicamente)
    
    Args:
        db: Sesión de base de datos
        skip: Registros a saltar
        limit: Máximo de registros
        
    Returns:
        Lista de propiedades aprobadas
    """
    return (
        db.query(Property)
        .options(selectinload(Property.images), selectinload(Property.owner))
        .filter(Property.status == 'approved')
        .offset(skip)
        .limit(limit)
        .all()
    )


def count_properties(
    db: Session,
    status: Optional[str] = None,
    user_id: Optional[int] = None
) -> int:
    """
    Contar propiedades con filtros
    
    Args:
        db: Sesión de base de datos
        status: Filtrar por estado
        user_id: Filtrar por usuario
        
    Returns:
        Número total de propiedades
    """
    query = db.query(func.count(Property.id))
    
    if status:
        query = query.filter(Property.status == status)
    
    if user_id:
        query = query.filter(Property.submitted_by_user_id == user_id)
    
    return query.scalar()


def create_property(
    db: Session,
    property_data: PropertyCreate,
    user_id: int
) -> Property:
    """
    Crear nueva propiedad
    
    La propiedad se crea con status='pending' automáticamente.
    
    Args:
        db: Sesión de base de datos
        property_data: Datos de la propiedad
        user_id: ID del usuario que publica
        
    Returns:
        Propiedad creada
        
    Raises:
        HTTPException: Si el usuario no existe
    """
    # Verificar que el usuario existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Admin publica directamente como approved para que sea visible en listado publico.
    initial_status = 'approved' if user.is_admin() else 'pending'

    # Crear propiedad
    db_property = Property(
        title=property_data.title,
        description=property_data.description,
        price=property_data.price,
        property_type=property_data.property_type,
        transaction_type=property_data.transaction_type,
        address=property_data.address,
        city=property_data.city,
        latitude=property_data.latitude,
        longitude=property_data.longitude,
        bedrooms=property_data.bedrooms,
        bathrooms=property_data.bathrooms,
        square_meters=property_data.square_meters,
        status=initial_status,
        submitted_by_user_id=user_id
    )
    
    db.add(db_property)
    db.commit()

    # Recargar con relaciones para evitar lazy loading error al serializar
    db_property = (
        db.query(Property)
        .options(selectinload(Property.images), selectinload(Property.owner))
        .filter(Property.id == db_property.id)
        .first()
    )
    
    return db_property


def update_property(
    db: Session,
    property_id: int,
    property_data: PropertyUpdate,
    user_id: Optional[int] = None
) -> Optional[Property]:
    """
    Actualizar propiedad existente
    
    Args:
        db: Sesión de base de datos
        property_id: ID de la propiedad
        property_data: Datos a actualizar
        user_id: ID del usuario (para verificar permisos)
        
    Returns:
        Propiedad actualizada o None si no existe
        
    Raises:
        HTTPException: Si el usuario no tiene permisos
    """
    db_property = get_property_by_id(db, property_id)
    
    if not db_property:
        return None
    
    # Verificar permisos si se proporciona user_id
    if user_id and db_property.submitted_by_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para editar esta propiedad"
        )
    
    # Actualizar solo los campos proporcionados
    update_data = property_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_property, field, value)
    
    db.commit()
    db.refresh(db_property)
    
    return db_property


def delete_property(db: Session, property_id: int, user_id: Optional[int] = None) -> bool:
    """
    Eliminar propiedad
    
    Args:
        db: Sesión de base de datos
        property_id: ID de la propiedad
        user_id: ID del usuario (para verificar permisos)
        
    Returns:
        True si se eliminó, False si no existe
        
    Raises:
        HTTPException: Si el usuario no tiene permisos
    """
    db_property = get_property_by_id(db, property_id)
    
    if not db_property:
        return False
    
    # Verificar permisos si se proporciona user_id
    if user_id and db_property.submitted_by_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar esta propiedad"
        )
    
    # Eliminar archivos fisicos de las imagenes antes de borrar los registros
    for image in db_property.images:
        _delete_image_file(image.image_url)
    
    db.delete(db_property)
    db.commit()
    
    return True


# ==========================================
# SISTEMA DE APROBACIÓN
# ==========================================

def approve_property(db: Session, property_id: int, advisor_id: Optional[int] = None) -> Property:
    """
    Aprobar propiedad (asesor)
    
    Cambia el estado a 'approved' y asigna el asesor.
    
    Args:
        db: Sesión de base de datos
        property_id: ID de la propiedad
        advisor_id: ID del asesor que aprueba
        
    Returns:
        Propiedad aprobada
        
    Raises:
        HTTPException: Si la propiedad no existe, no está pending,
                      o el asesor no existe
    """
    db_property = get_property_by_id(db, property_id)
    
    if not db_property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propiedad no encontrada"
        )
    
    if db_property.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solo se pueden aprobar propiedades pendientes (estado actual: {db_property.status})"
        )
    
    # Si se pasa advisor_id, verificar que exista
    if advisor_id is not None:
        advisor = db.query(Advisor).filter(Advisor.id == advisor_id).first()
        if not advisor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asesor no encontrado"
            )
    
    # Aprobar
    db_property.status = 'approved'
    db_property.advisor_id = advisor_id
    
    db.commit()
    db.refresh(db_property)
    
    # Crear notificación al propietario
    try:
        notificationService.notify_property_approved(db, property_id)
    except Exception:
        pass  # No fallar si no se puede crear la notificación
    
    return db_property


def reject_property(db: Session, property_id: int, reason: Optional[str] = None) -> Property:
    """
    Rechazar propiedad (asesor)
    
    Cambia el estado a 'rejected'.
    
    Args:
        db: Sesión de base de datos
        property_id: ID de la propiedad
        reason: Razón del rechazo (opcional, puede guardarse en notes)
        
    Returns:
        Propiedad rechazada
        
    Raises:
        HTTPException: Si la propiedad no existe o no está pending
    """
    db_property = get_property_by_id(db, property_id)
    
    if not db_property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propiedad no encontrada"
        )
    
    if db_property.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solo se pueden rechazar propiedades pendientes (estado actual: {db_property.status})"
        )
    
    # Rechazar
    db_property.status = 'rejected'
    
    # TODO: Guardar razón en tabla de notas o historial si es necesario
    # Por ahora solo cambiamos el estado
    
    db.commit()
    db.refresh(db_property)
    
    # Crear notificación al propietario
    try:
        notificationService.notify_property_rejected(db, property_id, reason)
    except Exception:
        pass  # No fallar si no se puede crear la notificación
    
    return db_property


def mark_as_sold(db: Session, property_id: int) -> Property:
    """
    Marcar propiedad como vendida/rentada
    
    Args:
        db: Sesión de base de datos
        property_id: ID de la propiedad
        
    Returns:
        Propiedad marcada como vendida
        
    Raises:
        HTTPException: Si la propiedad no existe o no está approved
    """
    db_property = get_property_by_id(db, property_id)
    
    if not db_property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propiedad no encontrada"
        )
    
    if db_property.status != 'approved':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden marcar como vendidas las propiedades aprobadas"
        )
    
    db_property.status = 'sold'
    
    db.commit()
    db.refresh(db_property)
    
    # Crear notificación al propietario
    try:
        notificationService.notify_property_sold(db, property_id)
    except Exception:
        pass  # No fallar si no se puede crear la notificación
    
    # Crear seguimientos post-venta automáticos
    try:
        postSaleService.create_auto_followups_on_sale(
            db=db,
            property_id=property_id,
            client_id=db_property.submitted_by_user_id,
            advisor_id=db_property.advisor_id
        )
    except Exception:
        pass  # No fallar si no se pueden crear los seguimientos
    
    return db_property


def get_pending_properties(db: Session, skip: int = 0, limit: int = 20) -> List[Property]:
    """
    Obtener propiedades pendientes de aprobación
    
    Args:
        db: Sesión de base de datos
        skip: Registros a saltar
        limit: Máximo de registros
        
    Returns:
        Lista de propiedades pendientes
    """
    return (
        db.query(Property)
        .options(selectinload(Property.images), selectinload(Property.owner))
        .filter(Property.status == 'pending')
        .offset(skip)
        .limit(limit)
        .all()
    )


# ==========================================
# FILTROS AVANZADOS
# ==========================================

def search_properties(
    db: Session,
    filters: PropertySearchFilters,
    skip: int = 0,
    limit: int = 20
) -> Tuple[List[Property], int]:
    """
    Buscar propiedades con filtros avanzados
    
    Args:
        db: Sesión de base de datos
        filters: Filtros de búsqueda
        skip: Registros a saltar
        limit: Máximo de registros
        
    Returns:
        Tupla (lista de propiedades, total)
    """
    query = db.query(Property).options(selectinload(Property.images), selectinload(Property.owner))
    
    # Búsqueda por texto completo (tsvector)
    if filters.query:
        search_query = db.query(Property).filter(
            Property.search_vector.op('@@')(
                func.websearch_to_tsquery('spanish', filters.query)
            )
        ).with_entities(Property.id)
        query = query.filter(Property.id.in_(search_query))
    
    # Filtro por ciudad
    if filters.city:
        query = query.filter(Property.city.ilike(f"%{filters.city}%"))
    
    # Filtro por tipo de propiedad
    if filters.property_type:
        query = query.filter(Property.property_type == filters.property_type)
    
    # Filtro por tipo de transacción
    if filters.transaction_type:
        query = query.filter(Property.transaction_type == filters.transaction_type)
    
    # Filtro por precio
    if filters.min_price is not None:
        query = query.filter(Property.price >= filters.min_price)
    if filters.max_price is not None:
        query = query.filter(Property.price <= filters.max_price)
    
    # Filtro por recámaras
    if filters.bedrooms is not None:
        query = query.filter(Property.bedrooms >= filters.bedrooms)
    
    # Filtro por baños
    if filters.bathrooms is not None:
        query = query.filter(Property.bathrooms >= filters.bathrooms)
    
    # Filtro por metros cuadrados
    if filters.min_square_meters is not None:
        query = query.filter(Property.square_meters >= filters.min_square_meters)
    if filters.max_square_meters is not None:
        query = query.filter(Property.square_meters <= filters.max_square_meters)
    
    # Filtro por estado
    if filters.status:
        query = query.filter(Property.status == filters.status)
    else:
        # Por defecto, solo mostrar aprobadas en búsqueda pública
        query = query.filter(Property.status == 'approved')
    
    # Contar total antes de paginación
    total = query.count()
    
    # Aplicar paginación
    properties = query.offset(skip).limit(limit).all()
    
    return properties, total


def search_by_proximity(
    db: Session,
    latitude: float,
    longitude: float,
    radius_km: float = 5.0,
    skip: int = 0,
    limit: int = 20
) -> List[Property]:
    """
    Buscar propiedades por proximidad (radio)
    
    Usa la fórmula de Haversine simplificada.
    
    Args:
        db: Sesión de base de datos
        latitude: Latitud del punto central
        longitude: Longitud del punto central
        radius_km: Radio de búsqueda en kilómetros
        skip: Registros a saltar
        limit: Máximo de registros
        
    Returns:
        Lista de propiedades dentro del radio
    """
    # Aproximación simple: 1 grado ≈ 111 km
    # Para búsquedas más precisas, usar PostGIS
    lat_range = radius_km / 111.0
    lon_range = radius_km / (111.0 * func.cos(func.radians(latitude)))
    
    return (
        db.query(Property)
        .options(selectinload(Property.images), selectinload(Property.owner))
        .filter(Property.status == 'approved')
        .filter(and_(
            Property.latitude.between(latitude - lat_range, latitude + lat_range),
            Property.longitude.between(longitude - lon_range, longitude + lon_range)
        ))
        .offset(skip)
        .limit(limit)
        .all()
    )


# ==========================================
# LIMPIEZA DE ARCHIVOS
# ==========================================

def _delete_image_file(image_url: str) -> None:
    """
    Elimina el archivo fisico de imagen del disco local.

    Args:
        image_url: Ruta relativa de la imagen (ej: /media/properties/3/abc.webp)
    """
    if not image_url or not image_url.startswith("/media/"):
        return

    file_path = Path(image_url.lstrip("/"))
    try:
        if file_path.exists():
            file_path.unlink(missing_ok=True)
    except (OSError, PermissionError):
        pass


# ==========================================
# GESTIÓN DE IMÁGENES
# ==========================================

def add_property_image(
    db: Session,
    property_id: int,
    image_url: str,
    is_main: bool = False,
    label: Optional[str] = None,
    is_extra: bool = False,
    image_type: str = "general"
) -> PropertyImage:
    """
    Agregar imagen a una propiedad
    
    Args:
        db: Sesión de base de datos
        property_id: ID de la propiedad
        image_url: URL de la imagen
        is_main: Si es la imagen principal
        label: Nombre visible del extra, por ejemplo Cocina o Patio
        is_extra: Si la imagen pertenece al apartado de extras
        image_type: Tipo de imagen: general, extra, bedroom o bathroom
        
    Returns:
        PropertyImage creada
        
    Raises:
        HTTPException: Si la propiedad no existe o ya tiene imagen principal
    """
    db_property = get_property_by_id(db, property_id)
    
    if not db_property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propiedad no encontrada"
        )
    
    normalized_image_type = (image_type or "general").lower()
    if is_extra:
        normalized_image_type = "extra"

    if normalized_image_type not in {"general", "extra", "bedroom", "bathroom"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de imagen no permitido"
        )

    if normalized_image_type == "bedroom":
        allowed = db_property.bedrooms or 0
        current = db.query(PropertyImage).filter(
            PropertyImage.property_id == property_id,
            PropertyImage.image_type == "bedroom"
        ).count()
        if allowed <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La propiedad no tiene habitaciones registradas"
            )
        if current >= allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Solo se permiten {allowed} foto(s) de habitaciones"
            )

    if normalized_image_type == "bathroom":
        allowed = db_property.bathrooms or 0
        current = db.query(PropertyImage).filter(
            PropertyImage.property_id == property_id,
            PropertyImage.image_type == "bathroom"
        ).count()
        if allowed <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La propiedad no tiene baños registrados"
            )
        if current >= allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Solo se permiten {allowed} foto(s) de baños"
            )

    effective_is_extra = normalized_image_type == "extra"
    effective_is_main = False if normalized_image_type != "general" else is_main

    # Si es principal, quitar el flag de las demas
    if effective_is_main:
        db.query(PropertyImage)\
            .filter(PropertyImage.property_id == property_id)\
            .update({"is_main": False})
    
    # Crear imagen
    db_image = PropertyImage(
        property_id=property_id,
        image_url=image_url,
        label=label,
        image_type=normalized_image_type,
        is_extra=effective_is_extra,
        is_main=effective_is_main
    )
    
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    return db_image


def delete_property_image(db: Session, image_id: int) -> bool:
    """
    Eliminar imagen de propiedad
    
    Args:
        db: Sesión de base de datos
        image_id: ID de la imagen
        
    Returns:
        True si se eliminó, False si no existe
    """
    db_image = db.query(PropertyImage).filter(PropertyImage.id == image_id).first()
    
    if not db_image:
        return False
    
    # Eliminar el archivo fisico antes de borrar el registro
    _delete_image_file(db_image.image_url)
    
    db.delete(db_image)
    db.commit()
    
    return True


# ==========================================
# ESTADÍSTICAS
# ==========================================

def get_property_stats(db: Session) -> dict:
    """
    Obtener estadísticas generales de propiedades
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Diccionario con estadísticas
    """
    total = db.query(func.count(Property.id)).scalar()
    approved = db.query(func.count(Property.id))\
        .filter(Property.status == 'approved').scalar()
    pending = db.query(func.count(Property.id))\
        .filter(Property.status == 'pending').scalar()
    rejected = db.query(func.count(Property.id))\
        .filter(Property.status == 'rejected').scalar()
    sold = db.query(func.count(Property.id))\
        .filter(Property.status == 'sold').scalar()
    
    avg_price = db.query(func.avg(Property.price))\
        .filter(Property.status == 'approved').scalar()
    
    return {
        "total": total,
        "approved": approved,
        "pending": pending,
        "rejected": rejected,
        "sold": sold,
        "average_price": float(avg_price) if avg_price else 0.0
    }


def get_properties_by_advisor(
    db: Session,
    advisor_id: int,
    skip: int = 0,
    limit: int = 20
) -> List[Property]:
    """
    Obtener propiedades gestionadas por un asesor
    
    Args:
        db: Sesión de base de datos
        advisor_id: ID del asesor
        skip: Registros a saltar
        limit: Máximo de registros
        
    Returns:
        Lista de propiedades del asesor
    """
    return (
        db.query(Property)
        .options(selectinload(Property.images), selectinload(Property.owner))
        .filter(Property.advisor_id == advisor_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def take_property(db: Session, property_id: int, advisor_id: int) -> Property:
    """
    Asignar una propiedad pendiente a un asesor
    
    Args:
        db: Sesión de base de datos
        property_id: ID de la propiedad
        advisor_id: ID del asesor que toma la propiedad
        
    Returns:
        Propiedad actualizada
        
    Raises:
        HTTPException: Si la propiedad no existe o ya tiene advisor
    """
    db_property = get_property_by_id(db, property_id)
    
    if not db_property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propiedad no encontrada"
        )
    
    if db_property.advisor_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta propiedad ya está asignada a otro asesor"
        )
    
    if db_property.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden tomar propiedades pendientes"
        )
    
    db_property.advisor_id = advisor_id
    db.commit()
    db.refresh(db_property)

    # Crear notificación al propietario
    try:
        notificationService.notify_property_taken(db, property_id, advisor_id)
    except Exception:
        pass  # No fallar si no se puede crear la notificación

    from sqlalchemy import func

    # Crear conversación y mensaje automático
    try:
        existing_conv = db.query(Conversation).filter(
            Conversation.user_id == db_property.submitted_by_user_id,
            Conversation.advisor_id == advisor_id
        ).first()

        if not existing_conv:
            advisor = db.query(Advisor).options(
                selectinload(Advisor.user)
            ).filter(Advisor.id == advisor_id).first()
            advisor_name = advisor.user.full_name if advisor and advisor.user else "un asesor"

            conversation = Conversation(
                user_id=db_property.submitted_by_user_id,
                advisor_id=advisor_id
            )
            db.add(conversation)
            db.flush()

            auto_msg = Message(
                conversation_id=conversation.id,
                sender_id=db_property.submitted_by_user_id,
                content=f"¡Buena noticia! El asesor {advisor_name} acaba de tomar tu propiedad \"{db_property.title}\" y comenzará a revisarla pronto.",
                is_read=True
            )
            db.add(auto_msg)
            db.commit()
            db.refresh(auto_msg)
            conversation.last_message_at = auto_msg.created_at
            db.commit()
    except Exception as e:
        print(f"[propertyService] Error creando conversación: {e}")
    
    return db_property


def return_property(db: Session, property_id: int, advisor_id: int) -> Property:
    """
    Devolver una propiedad (quitar asignación del advisor)
    
    Args:
        db: Sesión de base de datos
        property_id: ID de la propiedad
        advisor_id: ID del asesor que devuelve la propiedad
        
    Returns:
        Propiedad actualizada
        
    Raises:
        HTTPException: Si la propiedad no existe o no está asignada a este asesor
    """
    db_property = get_property_by_id(db, property_id)
    
    if not db_property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propiedad no encontrada"
        )
    
    if db_property.advisor_id != advisor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta propiedad no está asignada a ti"
        )
    
    if db_property.status not in ['pending', 'rejected']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes devolver propiedades ya aprobadas o vendidas"
        )
    
    db_property.advisor_id = None
    db.commit()
    db.refresh(db_property)
    
    return db_property


def get_available_properties(db: Session, skip: int = 0, limit: int = 20) -> List[Property]:
    """
    Obtener propiedades pendientes sin asignar (disponibles para tomar)
    
    Args:
        db: Sesión de base de datos
        skip: Registros a saltar
        limit: Máximo de registros
        
    Returns:
        Lista de propiedades disponibles
    """
    return (
        db.query(Property)
        .options(selectinload(Property.images), selectinload(Property.owner))
        .filter(Property.status == 'pending')
        .filter(Property.advisor_id == None)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_advisor_properties_with_available(
    db: Session,
    advisor_id: int,
    skip: int = 0,
    limit: int = 20
) -> Tuple[List[Property], int]:
    """
    Obtener propiedades del asesor + disponibles para tomar
    
    Args:
        db: Sesión de base de datos
        advisor_id: ID del asesor
        skip: Registros a saltar
        limit: Máximo de registros
        
    Returns:
        Tupla (lista de propiedades, total)
    """
    my_properties = (
        db.query(Property)
        .options(
            selectinload(Property.images),
            selectinload(Property.owner),
            selectinload(Property.advisor).selectinload(Advisor.user)
        )
        .filter(Property.advisor_id == advisor_id)
        .all()
    )
    
    available = (
        db.query(Property)
        .options(selectinload(Property.images), selectinload(Property.owner))
        .filter(Property.status == 'pending')
        .filter(Property.advisor_id == None)
        .all()
    )
    
    all_properties = my_properties + available
    total = len(all_properties)
    
    return all_properties[skip:skip + limit], total


def get_property_stats_by_advisor(db: Session, advisor_id: int) -> dict:
    """
    Obtener estadísticas personales de un asesor
    
    Args:
        db: Sesión de base de datos
        advisor_id: ID del asesor
        
    Returns:
        Diccionario con estadísticas del advisor
    """
    base_query = db.query(Property).filter(Property.advisor_id == advisor_id)
    
    total = base_query.count()
    approved = base_query.filter(Property.status == 'approved').count()
    pending = base_query.filter(Property.status == 'pending').count()
    rejected = base_query.filter(Property.status == 'rejected').count()
    sold = base_query.filter(Property.status == 'sold').count()
    
    available = db.query(func.count(Property.id)).filter(
        Property.status == 'pending',
        Property.advisor_id == None
    ).scalar()
    
    clients_count = db.query(func.count(func.distinct(Property.submitted_by_user_id))).filter(
        Property.advisor_id == advisor_id
    ).scalar()
    
    return {
        "total": total,
        "approved": approved,
        "pending": pending,
        "rejected": rejected,
        "sold": sold,
        "available_to_take": available,
        "clients_count": clients_count
    }


# ==========================================
# ANALYTICS AVANZADOS
# ==========================================

def get_properties_trends(db: Session, months: int = 12) -> List[dict]:
    """
    Obtener tendencias de propiedades por mes (últimos N meses)
    
    Args:
        db: Sesión de base de datos
        months: Número de meses hacia atrás
        
    Returns:
        Lista de diccionarios con mes y conteos por estado
    """
    result = db.execute(text(f"""
        SELECT 
            TO_CHAR(created_at, 'YYYY-MM') as month,
            COUNT(*) FILTER (WHERE status = 'approved') as approved,
            COUNT(*) FILTER (WHERE status = 'pending') as pending,
            COUNT(*) FILTER (WHERE status = 'rejected') as rejected,
            COUNT(*) FILTER (WHERE status = 'sold') as sold,
            COUNT(*) as total
        FROM properties
        WHERE created_at >= NOW() - INTERVAL '{months} months'
        GROUP BY TO_CHAR(created_at, 'YYYY-MM')
        ORDER BY month ASC
    """))
    
    return [dict(row) for row in result]


def get_avg_days_on_market(db: Session) -> dict:
    """
    Obtener días promedio que las propiedades pasan en cada estado
    
    Returns:
        Diccionario con días promedio por estado
    """
    result = db.execute(text("""
        SELECT 
            status,
            ROUND(AVG(EXTRACT(EPOCH FROM (updated_at - created_at)) / 86400)::numeric, 1) as avg_days
        FROM properties
        WHERE status IN ('approved', 'rejected', 'sold')
        GROUP BY status
    """))
    
    return {row[0]: float(row[1]) for row in result}


def get_price_per_m2_by_city(db: Session) -> List[dict]:
    """
    Obtener precio promedio por m² por ciudad
    
    Returns:
        Lista de diccionarios con ciudad y precio/m²
    """
    result = db.execute(text("""
        SELECT 
            city,
            ROUND(AVG(price / NULLIF(square_meters, 0))::numeric, 2) as avg_price_per_m2,
            COUNT(*) as property_count,
            ROUND(AVG(price)::numeric, 2) as avg_price
        FROM properties
        WHERE status = 'approved' AND square_meters > 0
        GROUP BY city
        ORDER BY avg_price_per_m2 DESC
    """))
    
    return [dict(row) for row in result]


def get_advisor_conversion_rate(db: Session) -> List[dict]:
    """
    Obtener tasa de conversión por asesor (ventas / propiedades aprobadas)
    
    Returns:
        Lista de asesores con su tasa de conversión
    """
    result = db.execute(text("""
        SELECT 
            a.id as advisor_id,
            u.full_name as advisor_name,
            a.rating,
            COUNT(p.id) FILTER (WHERE p.status = 'approved') as approved_count,
            COUNT(p.id) FILTER (WHERE p.status = 'sold') as sold_count,
            CASE 
                WHEN COUNT(p.id) FILTER (WHERE p.status = 'approved') > 0 
                THEN ROUND(
                    (COUNT(p.id) FILTER (WHERE p.status = 'sold')::numeric / 
                     COUNT(p.id) FILTER (WHERE p.status = 'approved')) * 100, 1
                )
                ELSE 0 
            END as conversion_rate
        FROM advisors a
        JOIN users u ON a.user_id = u.id
        LEFT JOIN properties p ON p.advisor_id = a.id
        GROUP BY a.id, u.full_name, a.rating
        ORDER BY conversion_rate DESC
    """))
    
    return [dict(row) for row in result]

    