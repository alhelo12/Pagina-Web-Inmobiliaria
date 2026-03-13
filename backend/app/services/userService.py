"""
Service: User

Lógica de negocio para gestión de usuarios.
Contiene operaciones CRUD y funciones auxiliares.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from fastapi import HTTPException, status

from app.models import User, Role
from app.schemas import UserCreate, UserUpdate


# ==========================================
# CRUD BÁSICO
# ==========================================

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Obtener usuario por ID
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        
    Returns:
        User o None si no existe
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Obtener usuario por email
    
    Args:
        db: Sesión de base de datos
        email: Email del usuario
        
    Returns:
        User o None si no existe
    """
    return db.query(User).filter(User.email == email).first()


def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    role_name: Optional[str] = None,
    is_active: Optional[bool] = None
) -> List[User]:
    """
    Obtener lista de usuarios con filtros opcionales
    
    Args:
        db: Sesión de base de datos
        skip: Número de registros a saltar (paginación)
        limit: Número máximo de registros a retornar
        role_name: Filtrar por rol (admin, advisor, client)
        is_active: Filtrar por estado activo
        
    Returns:
        Lista de usuarios
    """
    query = db.query(User)
    
    # Filtro por rol
    if role_name:
        query = query.join(Role).filter(Role.name == role_name)
    
    # Filtro por estado activo
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()


def count_users(
    db: Session,
    role_name: Optional[str] = None,
    is_active: Optional[bool] = None
) -> int:
    """
    Contar usuarios con filtros opcionales
    
    Args:
        db: Sesión de base de datos
        role_name: Filtrar por rol
        is_active: Filtrar por estado activo
        
    Returns:
        Número total de usuarios
    """
    query = db.query(func.count(User.id))
    
    if role_name:
        query = query.join(Role).filter(Role.name == role_name)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    return query.scalar()


def create_user(db: Session, user_data: UserCreate, password_hash: str) -> User:
    """
    Crear nuevo usuario
    
    Args:
        db: Sesión de base de datos
        user_data: Datos del usuario (schema)
        password_hash: Hash de la contraseña (generado externamente)
        
    Returns:
        Usuario creado
        
    Raises:
        HTTPException: Si el email ya existe o el rol no existe
    """
    # Verificar si el email ya existe
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Verificar que el rol exista
    role = db.query(Role).filter(Role.id == user_data.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El rol con ID {user_data.role_id} no existe"
        )
    
    # Crear usuario
    db_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        phone=user_data.phone,
        password_hash=password_hash,
        role_id=user_data.role_id,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def update_user(
    db: Session,
    user_id: int,
    user_data: UserUpdate
) -> Optional[User]:
    """
    Actualizar usuario existente
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario a actualizar
        user_data: Datos a actualizar (solo campos presentes)
        
    Returns:
        Usuario actualizado o None si no existe
        
    Raises:
        HTTPException: Si el nuevo email ya está en uso
    """
    db_user = get_user_by_id(db, user_id)
    
    if not db_user:
        return None
    
    # Verificar email único si se está actualizando
    if user_data.email and user_data.email != db_user.email:
        existing_user = get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está en uso por otro usuario"
            )
    
    # Actualizar solo los campos proporcionados
    update_data = user_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """
    Eliminar usuario (soft delete - marcar como inactivo)
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario a eliminar
        
    Returns:
        True si se eliminó, False si no existe
    """
    db_user = get_user_by_id(db, user_id)
    
    if not db_user:
        return False
    
    # Soft delete: marcar como inactivo en lugar de eliminar
    db_user.is_active = False
    db.commit()
    
    return True


def hard_delete_user(db: Session, user_id: int) -> bool:
    """
    Eliminar usuario permanentemente (hard delete)
    
    ADVERTENCIA: Esta acción es irreversible
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario a eliminar
        
    Returns:
        True si se eliminó, False si no existe
    """
    db_user = get_user_by_id(db, user_id)
    
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    
    return True


def activate_user(db: Session, user_id: int) -> Optional[User]:
    """
    Reactivar usuario inactivo
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        
    Returns:
        Usuario reactivado o None si no existe
    """
    db_user = get_user_by_id(db, user_id)
    
    if not db_user:
        return None
    
    db_user.is_active = True
    db.commit()
    db.refresh(db_user)
    
    return db_user


# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

def get_users_by_role(db: Session, role_name: str) -> List[User]:
    """
    Obtener todos los usuarios de un rol específico
    
    Args:
        db: Sesión de base de datos
        role_name: Nombre del rol (admin, advisor, client)
        
    Returns:
        Lista de usuarios con ese rol
    """
    return db.query(User)\
        .join(Role)\
        .filter(Role.name == role_name)\
        .all()


def get_active_users_count(db: Session) -> int:
    """
    Contar usuarios activos
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Número de usuarios activos
    """
    return db.query(func.count(User.id))\
        .filter(User.is_active == True)\
        .scalar()


def user_exists(db: Session, email: str) -> bool:
    """
    Verificar si existe un usuario con ese email
    
    Args:
        db: Sesión de base de datos
        email: Email a verificar
        
    Returns:
        True si existe, False si no
    """
    return db.query(User).filter(User.email == email).first() is not None


def get_user_with_role(db: Session, user_id: int) -> Optional[User]:
    """
    Obtener usuario con su rol cargado (eager loading)
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        
    Returns:
        Usuario con role cargado o None
    """
    return db.query(User)\
        .filter(User.id == user_id)\
        .first()  # Ya tiene lazy="joined" en el modelo


# ==========================================
# VALIDACIONES
# ==========================================

def validate_user_can_be_deleted(db: Session, user_id: int) -> tuple[bool, Optional[str]]:
    """
    Validar si un usuario puede ser eliminado
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        
    Returns:
        Tupla (puede_eliminar, mensaje_error)
    """
    user = get_user_by_id(db, user_id)
    
    if not user:
        return False, "Usuario no encontrado"
    
    # Verificar si es admin (no se puede eliminar el último admin)
    if user.is_admin():
        admin_count = db.query(func.count(User.id))\
            .join(Role)\
            .filter(Role.name == 'admin')\
            .filter(User.is_active == True)\
            .scalar()
        
        if admin_count <= 1:
            return False, "No se puede eliminar el único administrador activo"
    
    # Verificar si tiene propiedades activas (si es necesario)
    # active_properties_count = db.query(func.count(Property.id))\
    #     .filter(Property.submitted_by_user_id == user_id)\
    #     .filter(Property.status.in_(['pending', 'approved']))\
    #     .scalar()
    #
    # if active_properties_count > 0:
    #     return False, f"El usuario tiene {active_properties_count} propiedades activas"
    
    return True, None
