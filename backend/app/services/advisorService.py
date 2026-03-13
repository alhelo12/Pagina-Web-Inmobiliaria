"""
Service: Advisor

Lógica de negocio para gestión de asesores inmobiliarios.
Maneja perfiles extendidos, estadísticas y ratings.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from fastapi import HTTPException, status

from app.models import Advisor, User, Property, Appointment
from app.schemas import AdvisorCreate, AdvisorUpdate


# ==========================================
# CRUD BÁSICO
# ==========================================

def get_advisor_by_id(db: Session, advisor_id: int) -> Optional[Advisor]:
    """
    Obtener asesor por ID
    
    Args:
        db: Sesión de base de datos
        advisor_id: ID del asesor
        
    Returns:
        Advisor o None si no existe
    """
    return db.query(Advisor).filter(Advisor.id == advisor_id).first()


def get_advisor_by_user_id(db: Session, user_id: int) -> Optional[Advisor]:
    """
    Obtener asesor por ID de usuario
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        
    Returns:
        Advisor o None si no existe
    """
    return db.query(Advisor).filter(Advisor.user_id == user_id).first()


def get_advisors(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    min_rating: Optional[float] = None
) -> List[Advisor]:
    """
    Obtener lista de asesores
    
    Args:
        db: Sesión de base de datos
        skip: Registros a saltar
        limit: Máximo de registros
        min_rating: Rating mínimo para filtrar
        
    Returns:
        Lista de asesores
    """
    query = db.query(Advisor)
    
    if min_rating is not None:
        query = query.filter(Advisor.rating >= min_rating)
    
    return query.offset(skip).limit(limit).all()


def count_advisors(db: Session) -> int:
    """
    Contar total de asesores
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Número total de asesores
    """
    return db.query(func.count(Advisor.id)).scalar()


def create_advisor(
    db: Session,
    user_id: int,
    advisor_data: AdvisorCreate
) -> Advisor:
    """
    Crear perfil de asesor
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario (debe tener rol 'advisor')
        advisor_data: Datos del perfil de asesor
        
    Returns:
        Advisor creado
        
    Raises:
        HTTPException: Si el usuario no existe, no es asesor,
                      o ya tiene perfil de asesor
    """
    # Verificar que el usuario existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar que es asesor
    if not user.is_advisor():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no tiene rol de asesor"
        )
    
    # Verificar que no tiene perfil ya
    existing_advisor = get_advisor_by_user_id(db, user_id)
    if existing_advisor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya tiene un perfil de asesor"
        )
    
    # Crear perfil
    db_advisor = Advisor(
        user_id=user_id,
        license_number=advisor_data.license_number,
        agency_name=advisor_data.agency_name,
        profile_picture=advisor_data.profile_picture,
        rating=5.00  # Rating inicial perfecto
    )
    
    db.add(db_advisor)
    db.commit()
    db.refresh(db_advisor)
    
    return db_advisor


def update_advisor(
    db: Session,
    advisor_id: int,
    advisor_data: AdvisorUpdate
) -> Optional[Advisor]:
    """
    Actualizar perfil de asesor
    
    Args:
        db: Sesión de base de datos
        advisor_id: ID del asesor
        advisor_data: Datos a actualizar
        
    Returns:
        Advisor actualizado o None si no existe
    """
    db_advisor = get_advisor_by_id(db, advisor_id)
    
    if not db_advisor:
        return None
    
    # Actualizar solo los campos proporcionados
    update_data = advisor_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_advisor, field, value)
    
    db.commit()
    db.refresh(db_advisor)
    
    return db_advisor


def delete_advisor(db: Session, advisor_id: int) -> bool:
    """
    Eliminar perfil de asesor
    
    NOTA: Esto solo elimina el perfil, no el usuario.
    
    Args:
        db: Sesión de base de datos
        advisor_id: ID del asesor
        
    Returns:
        True si se eliminó, False si no existe
    """
    db_advisor = get_advisor_by_id(db, advisor_id)
    
    if not db_advisor:
        return False
    
    db.delete(db_advisor)
    db.commit()
    
    return True


# ==========================================
# ESTADÍSTICAS
# ==========================================

def get_advisor_stats(db: Session, advisor_id: int) -> dict:
    """
    Obtener estadísticas de un asesor
    
    Args:
        db: Sesión de base de datos
        advisor_id: ID del asesor
        
    Returns:
        Diccionario con estadísticas
        
    Raises:
        HTTPException: Si el asesor no existe
    """
    advisor = get_advisor_by_id(db, advisor_id)
    
    if not advisor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asesor no encontrado"
        )
    
    # Contar propiedades
    total_properties = db.query(func.count(Property.id))\
        .filter(Property.advisor_id == advisor_id)\
        .scalar()
    
    properties_approved = db.query(func.count(Property.id))\
        .filter(Property.advisor_id == advisor_id)\
        .filter(Property.status == 'approved')\
        .scalar()
    
    properties_pending = db.query(func.count(Property.id))\
        .filter(Property.advisor_id == advisor_id)\
        .filter(Property.status == 'pending')\
        .scalar()
    
    properties_sold = db.query(func.count(Property.id))\
        .filter(Property.advisor_id == advisor_id)\
        .filter(Property.status == 'sold')\
        .scalar()
    
    # Contar citas
    total_appointments = db.query(func.count(Appointment.id))\
        .filter(Appointment.advisor_id == advisor_id)\
        .scalar()
    
    completed_appointments = db.query(func.count(Appointment.id))\
        .filter(Appointment.advisor_id == advisor_id)\
        .filter(Appointment.status == 'completed')\
        .scalar()
    
    pending_appointments = db.query(func.count(Appointment.id))\
        .filter(Appointment.advisor_id == advisor_id)\
        .filter(Appointment.status.in_(['pending', 'confirmed']))\
        .scalar()
    
    # Calcular valor total de ventas
    total_sales_value = db.query(func.sum(Property.price))\
        .filter(Property.advisor_id == advisor_id)\
        .filter(Property.status == 'sold')\
        .scalar()
    
    return {
        "advisor_id": advisor_id,
        "total_properties": total_properties,
        "properties_approved": properties_approved,
        "properties_pending": properties_pending,
        "properties_sold": properties_sold,
        "total_appointments": total_appointments,
        "completed_appointments": completed_appointments,
        "pending_appointments": pending_appointments,
        "average_rating": float(advisor.rating),
        "total_sales_value": float(total_sales_value) if total_sales_value else 0.0
    }


def get_top_advisors(
    db: Session,
    limit: int = 10,
    order_by: str = "rating"
) -> List[Advisor]:
    """
    Obtener top asesores
    
    Args:
        db: Sesión de base de datos
        limit: Número de asesores a retornar
        order_by: Criterio de ordenamiento (rating, properties, sales)
        
    Returns:
        Lista de top asesores
    """
    query = db.query(Advisor)
    
    if order_by == "rating":
        query = query.order_by(Advisor.rating.desc())
    elif order_by == "properties":
        # Subquery para contar propiedades
        properties_count = db.query(
            Property.advisor_id,
            func.count(Property.id).label('count')
        ).filter(Property.status.in_(['approved', 'sold']))\
         .group_by(Property.advisor_id)\
         .subquery()
        
        query = db.query(Advisor)\
            .outerjoin(properties_count, Advisor.id == properties_count.c.advisor_id)\
            .order_by(properties_count.c.count.desc().nullslast())
    elif order_by == "sales":
        # Subquery para sumar ventas
        sales_sum = db.query(
            Property.advisor_id,
            func.count(Property.id).label('sales_count')
        ).filter(Property.status == 'sold')\
         .group_by(Property.advisor_id)\
         .subquery()
        
        query = db.query(Advisor)\
            .outerjoin(sales_sum, Advisor.id == sales_sum.c.advisor_id)\
            .order_by(sales_sum.c.sales_count.desc().nullslast())
    
    return query.limit(limit).all()


# ==========================================
# GESTIÓN DE RATING
# ==========================================

def update_advisor_rating(
    db: Session,
    advisor_id: int,
    new_rating: float
) -> Advisor:
    """
    Actualizar rating de asesor
    
    Args:
        db: Sesión de base de datos
        advisor_id: ID del asesor
        new_rating: Nuevo rating (0.00 - 5.00)
        
    Returns:
        Advisor actualizado
        
    Raises:
        HTTPException: Si el asesor no existe o rating inválido
    """
    if new_rating < 0.0 or new_rating > 5.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El rating debe estar entre 0.00 y 5.00"
        )
    
    db_advisor = get_advisor_by_id(db, advisor_id)
    
    if not db_advisor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asesor no encontrado"
        )
    
    db_advisor.rating = new_rating
    db.commit()
    db.refresh(db_advisor)
    
    return db_advisor


# ==========================================
# UTILIDADES
# ==========================================

def get_available_advisors(db: Session) -> List[Advisor]:
    """
    Obtener asesores disponibles (con buen rating)
    
    Útil para asignar propiedades o mostrar en formularios.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Lista de asesores con rating >= 4.0
    """
    return db.query(Advisor)\
        .filter(Advisor.rating >= 4.0)\
        .order_by(Advisor.rating.desc())\
        .all()


def advisor_has_active_properties(db: Session, advisor_id: int) -> bool:
    """
    Verificar si un asesor tiene propiedades activas
    
    Args:
        db: Sesión de base de datos
        advisor_id: ID del asesor
        
    Returns:
        True si tiene propiedades activas (approved o pending)
    """
    count = db.query(func.count(Property.id))\
        .filter(Property.advisor_id == advisor_id)\
        .filter(Property.status.in_(['approved', 'pending']))\
        .scalar()
    
    return count > 0


def get_advisors_with_stats(
    db: Session,
    skip: int = 0,
    limit: int = 20
) -> List[dict]:
    """
    Obtener asesores con sus estadísticas básicas
    
    Args:
        db: Sesión de base de datos
        skip: Registros a saltar
        limit: Máximo de registros
        
    Returns:
        Lista de diccionarios con asesor + stats
    """
    advisors = get_advisors(db, skip, limit)
    
    result = []
    for advisor in advisors:
        # Contar propiedades activas
        active_properties = db.query(func.count(Property.id))\
            .filter(Property.advisor_id == advisor.id)\
            .filter(Property.status.in_(['approved', 'pending']))\
            .scalar()
        
        result.append({
            "advisor": advisor,
            "active_properties": active_properties,
            "rating": float(advisor.rating)
        })
    
    return result
