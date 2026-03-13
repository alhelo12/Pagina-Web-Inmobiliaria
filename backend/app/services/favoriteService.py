# app/services/favoriteService.py
"""
Service: Favorite

Lógica de negocio para gestión de propiedades favoritas.
Maneja agregar, quitar y consultar favoritos de usuarios.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from fastapi import HTTPException, status

from app.models import Favorite, Property, User
from app.schemas import FavoriteCreate


# ==========================================
# CRUD BÁSICO
# ==========================================

def get_favorite_by_id(db: Session, favorite_id: int) -> Optional[Favorite]:
    """
    Obtener favorito por ID
    
    Args:
        db: Sesión de base de datos
        favorite_id: ID del favorito
        
    Returns:
        Favorite o None si no existe
    """
    return db.query(Favorite).filter(Favorite.id == favorite_id).first()


def get_user_favorites(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20
) -> List[Favorite]:
    """
    Obtener favoritos de un usuario
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        skip: Registros a saltar
        limit: Máximo de registros
        
    Returns:
        Lista de favoritos del usuario
    """
    return db.query(Favorite)\
        .filter(Favorite.user_id == user_id)\
        .order_by(Favorite.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()


def count_user_favorites(db: Session, user_id: int) -> int:
    """
    Contar favoritos de un usuario
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        
    Returns:
        Número de favoritos
    """
    return db.query(func.count(Favorite.id))\
        .filter(Favorite.user_id == user_id)\
        .scalar()


def add_favorite(db: Session, user_id: int, property_id: int) -> Favorite:
    """
    Agregar propiedad a favoritos
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        property_id: ID de la propiedad
        
    Returns:
        Favorite creado
        
    Raises:
        HTTPException: Si el usuario/propiedad no existe o ya está en favoritos
    """
    # Verificar que el usuario existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar que la propiedad existe
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propiedad no encontrada"
        )
    
    # Verificar que no esté ya en favoritos
    existing = db.query(Favorite)\
        .filter(Favorite.user_id == user_id)\
        .filter(Favorite.property_id == property_id)\
        .first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La propiedad ya está en favoritos"
        )
    
    # Crear favorito
    db_favorite = Favorite(
        user_id=user_id,
        property_id=property_id
    )
    
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    
    return db_favorite


def remove_favorite(db: Session, user_id: int, property_id: int) -> bool:
    """
    Quitar propiedad de favoritos
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        property_id: ID de la propiedad
        
    Returns:
        True si se quitó, False si no existía
    """
    db_favorite = db.query(Favorite)\
        .filter(Favorite.user_id == user_id)\
        .filter(Favorite.property_id == property_id)\
        .first()
    
    if not db_favorite:
        return False
    
    db.delete(db_favorite)
    db.commit()
    
    return True


def remove_favorite_by_id(db: Session, favorite_id: int, user_id: int) -> bool:
    """
    Quitar favorito por ID (con verificación de usuario)
    
    Args:
        db: Sesión de base de datos
        favorite_id: ID del favorito
        user_id: ID del usuario (para verificar permisos)
        
    Returns:
        True si se quitó, False si no existe
        
    Raises:
        HTTPException: Si no tiene permisos
    """
    db_favorite = get_favorite_by_id(db, favorite_id)
    
    if not db_favorite:
        return False
    
    # Verificar permisos
    if db_favorite.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar este favorito"
        )
    
    db.delete(db_favorite)
    db.commit()
    
    return True


# ==========================================
# TOGGLE (AGREGAR/QUITAR)
# ==========================================

def toggle_favorite(db: Session, user_id: int, property_id: int) -> dict:
    """
    Toggle favorito (agregar si no existe, quitar si existe)
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        property_id: ID de la propiedad
        
    Returns:
        Diccionario con acción realizada e información del favorito
        
    Raises:
        HTTPException: Si el usuario/propiedad no existe
    """
    # Verificar que la propiedad existe
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propiedad no encontrada"
        )
    
    # Buscar si ya existe
    existing = db.query(Favorite)\
        .filter(Favorite.user_id == user_id)\
        .filter(Favorite.property_id == property_id)\
        .first()
    
    if existing:
        # Quitar
        db.delete(existing)
        db.commit()
        return {
            "action": "removed",
            "is_favorite": False,
            "property_id": property_id
        }
    else:
        # Agregar
        db_favorite = Favorite(
            user_id=user_id,
            property_id=property_id
        )
        db.add(db_favorite)
        db.commit()
        db.refresh(db_favorite)
        
        return {
            "action": "added",
            "is_favorite": True,
            "property_id": property_id,
            "favorite_id": db_favorite.id
        }


# ==========================================
# VERIFICACIÓN
# ==========================================

def is_favorite(db: Session, user_id: int, property_id: int) -> bool:
    """
    Verificar si una propiedad está en favoritos de un usuario
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        property_id: ID de la propiedad
        
    Returns:
        True si está en favoritos, False si no
    """
    return db.query(Favorite)\
        .filter(Favorite.user_id == user_id)\
        .filter(Favorite.property_id == property_id)\
        .first() is not None


def check_multiple_favorites(
    db: Session,
    user_id: int,
    property_ids: List[int]
) -> dict:
    """
    Verificar cuáles propiedades están en favoritos
    
    Útil para marcar favoritos en listados de propiedades.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        property_ids: Lista de IDs de propiedades
        
    Returns:
        Diccionario {property_id: is_favorite}
    """
    favorites = db.query(Favorite.property_id)\
        .filter(Favorite.user_id == user_id)\
        .filter(Favorite.property_id.in_(property_ids))\
        .all()
    
    favorite_ids = {fav.property_id for fav in favorites}
    
    return {
        prop_id: prop_id in favorite_ids
        for prop_id in property_ids
    }


# ==========================================
# CONSULTAS ESPECIALES
# ==========================================

def get_favorite_properties(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20
) -> List[Property]:
    """
    Obtener propiedades favoritas de un usuario (solo las Property)
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        skip: Registros a saltar
        limit: Máximo de registros
        
    Returns:
        Lista de propiedades favoritas
    """
    return db.query(Property)\
        .join(Favorite, Favorite.property_id == Property.id)\
        .filter(Favorite.user_id == user_id)\
        .order_by(Favorite.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_most_favorited_properties(
    db: Session,
    limit: int = 10,
    min_favorites: int = 1
) -> List[dict]:
    """
    Obtener propiedades más guardadas en favoritos
    
    Args:
        db: Sesión de base de datos
        limit: Número de propiedades a retornar
        min_favorites: Mínimo de favoritos para incluir
        
    Returns:
        Lista de diccionarios con property y favorite_count
    """
    results = db.query(
        Property,
        func.count(Favorite.id).label('favorite_count')
    )\
        .join(Favorite, Favorite.property_id == Property.id)\
        .filter(Property.status == 'approved')\
        .group_by(Property.id)\
        .having(func.count(Favorite.id) >= min_favorites)\
        .order_by(func.count(Favorite.id).desc())\
        .limit(limit)\
        .all()
    
    return [
        {
            "property": prop,
            "favorite_count": count
        }
        for prop, count in results
    ]


def count_property_favorites(db: Session, property_id: int) -> int:
    """
    Contar cuántos usuarios tienen una propiedad en favoritos
    
    Args:
        db: Sesión de base de datos
        property_id: ID de la propiedad
        
    Returns:
        Número de usuarios que la tienen en favoritos
    """
    return db.query(func.count(Favorite.id))\
        .filter(Favorite.property_id == property_id)\
        .scalar()


# ==========================================
# ESTADÍSTICAS
# ==========================================

def get_favorite_stats(db: Session, user_id: Optional[int] = None) -> dict:
    """
    Obtener estadísticas de favoritos
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario (opcional, si no se proporciona da stats globales)
        
    Returns:
        Diccionario con estadísticas
    """
    if user_id:
        # Stats de un usuario específico
        total = count_user_favorites(db, user_id)
        
        # Contar por tipo de propiedad
        by_type = db.query(
            Property.property_type,
            func.count(Favorite.id).label('count')
        )\
            .join(Property, Favorite.property_id == Property.id)\
            .filter(Favorite.user_id == user_id)\
            .group_by(Property.property_type)\
            .all()
        
        return {
            "user_id": user_id,
            "total_favorites": total,
            "by_property_type": {prop_type: count for prop_type, count in by_type}
        }
    else:
        # Stats globales
        total_favorites = db.query(func.count(Favorite.id)).scalar()
        total_users_with_favorites = db.query(
            func.count(func.distinct(Favorite.user_id))
        ).scalar()
        
        avg_favorites_per_user = db.query(
            func.avg(func.count(Favorite.id))
        )\
            .group_by(Favorite.user_id)\
            .scalar()
        
        return {
            "total_favorites": total_favorites,
            "total_users_with_favorites": total_users_with_favorites,
            "avg_favorites_per_user": float(avg_favorites_per_user) if avg_favorites_per_user else 0.0
        }


# ==========================================
# LIMPIEZA
# ==========================================

def remove_all_user_favorites(db: Session, user_id: int) -> int:
    """
    Quitar todos los favoritos de un usuario
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        
    Returns:
        Número de favoritos eliminados
    """
    count = db.query(Favorite)\
        .filter(Favorite.user_id == user_id)\
        .delete()
    
    db.commit()
    
    return count


def cleanup_orphaned_favorites(db: Session) -> int:
    """
    Eliminar favoritos de propiedades que ya no existen
    
    Útil para mantenimiento de base de datos.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Número de favoritos eliminados
    """
    # Esta query debería estar protegida por CASCADE en la BD,
    # pero se incluye por seguridad
    orphaned = db.query(Favorite)\
        .outerjoin(Property, Favorite.property_id == Property.id)\
        .filter(Property.id == None)\
        .delete(synchronize_session=False)
    
    db.commit()
    
    return orphaned
