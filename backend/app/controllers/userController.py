"""
Controller: User

Endpoints para gestión de usuarios (CRUD).
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.dbConfig.databaseSession import get_db
from app.services import userService
from app.schemas import (
    UserResponse,
    UserResponseWithAdvisor,
    UserUpdate,
    UserListResponse
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# ==========================================
# LISTAR USUARIOS
# ==========================================

@router.get("", response_model=UserListResponse)
def get_users(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de registros"),
    role_name: Optional[str] = Query(None, description="Filtrar por rol (admin, advisor, client)"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    db: Session = Depends(get_db)
):
    """
    Listar usuarios con filtros opcionales
    
    Query params:
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Máximo de registros a retornar (1-100)
    - **role_name**: Filtrar por rol (admin, advisor, client)
    - **is_active**: Filtrar por estado (true/false)
    
    Retorna:
    - Lista de usuarios
    - Total de usuarios (para paginación)
    """
    users = userService.get_users(
        db,
        skip=skip,
        limit=limit,
        role_name=role_name,
        is_active=is_active
    )
    
    total = userService.count_users(
        db,
        role_name=role_name,
        is_active=is_active
    )
    
    return {
        "users": users,
        "total": total,
        "skip": skip,
        "limit": limit
    }


# ==========================================
# OBTENER USUARIO POR ID
# ==========================================

@router.get("/{user_id}", response_model=UserResponseWithAdvisor)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener usuario por ID
    
    Path params:
    - **user_id**: ID del usuario
    
    Retorna:
    - Usuario con todos sus datos
    - Perfil de asesor si tiene rol advisor
    
    Errores:
    - 404: Usuario no encontrado
    """
    user = userService.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user


# ==========================================
# ACTUALIZAR USUARIO
# ==========================================

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar usuario
    
    Path params:
    - **user_id**: ID del usuario
    
    Body (todos opcionales):
    - **full_name**: Nombre completo
    - **email**: Email (debe ser único)
    - **phone**: Teléfono
    - **is_active**: Estado activo
    
    Validaciones:
    - Email único si se cambia
    - Usuario debe existir
    
    Errores:
    - 404: Usuario no encontrado
    - 400: Email ya en uso
    
    Nota: Por ahora cualquiera puede actualizar.
    Con JWT, solo el mismo usuario o admin podrá actualizar.
    """
    user = userService.update_user(db, user_id, user_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user


# ==========================================
# ELIMINAR USUARIO
# ==========================================

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    permanent: bool = Query(False, description="Eliminación permanente (true) o soft delete (false)"),
    db: Session = Depends(get_db)
):
    """
    Eliminar usuario
    
    Path params:
    - **user_id**: ID del usuario
    
    Query params:
    - **permanent**: Si es true, elimina permanentemente. Si es false (default), soft delete.
    
    Soft delete (default):
    - Marca el usuario como inactivo (is_active=false)
    - El usuario puede ser reactivado después
    - Sus datos permanecen en la BD
    
    Hard delete (permanent=true):
    - Elimina el usuario permanentemente
    - ADVERTENCIA: Esta acción es irreversible
    - Se eliminan todos sus datos relacionados (CASCADE)
    
    Validaciones:
    - No se puede eliminar el último admin activo
    
    Errores:
    - 404: Usuario no encontrado
    - 400: No se puede eliminar último admin
    
    Nota: Con JWT, solo admin podrá eliminar usuarios.
    """
    # Validar si puede ser eliminado
    can_delete, error_msg = userService.validate_user_can_be_deleted(db, user_id)
    
    if not can_delete:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Eliminar
    if permanent:
        success = userService.hard_delete_user(db, user_id)
    else:
        success = userService.delete_user(db, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return None


# ==========================================
# REACTIVAR USUARIO
# ==========================================

@router.patch("/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Reactivar usuario inactivo
    
    Path params:
    - **user_id**: ID del usuario
    
    Cambia is_active a true.
    
    Errores:
    - 404: Usuario no encontrado
    
    Nota: Con JWT, solo admin podrá reactivar usuarios.
    """
    user = userService.activate_user(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user


# ==========================================
# OBTENER PERFIL (PLACEHOLDER PARA JWT)
# ==========================================

@router.get("/me/profile", response_model=UserResponseWithAdvisor)
def get_my_profile(
    user_id: int = Query(..., description="ID del usuario (temporal, con JWT se extraerá del token)"),
    db: Session = Depends(get_db)
):
    """
    Obtener perfil del usuario autenticado
    
    Query params:
    - **user_id**: ID del usuario (TEMPORAL)
    
    Retorna:
    - Usuario con todos sus datos
    - Perfil de asesor si tiene rol advisor
    
    Nota: Por ahora requiere user_id en query params.
    Con JWT, se extraerá automáticamente del token.
    
    Errores:
    - 404: Usuario no encontrado
    """
    user = userService.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user


# ==========================================
# OBTENER USUARIOS POR ROL
# ==========================================

@router.get("/role/{role_name}", response_model=list[UserResponse])
def get_users_by_role(
    role_name: str,
    db: Session = Depends(get_db)
):
    """
    Obtener usuarios de un rol específico
    
    Path params:
    - **role_name**: Nombre del rol (admin, advisor, client)
    
    Retorna:
    - Lista de usuarios con ese rol
    
    Útil para:
    - Listar todos los asesores
    - Listar todos los admins
    - Listar todos los clientes
    """
    users = userService.get_users_by_role(db, role_name)
    return users


# ==========================================
# ESTADÍSTICAS
# ==========================================

@router.get("/stats/general")
def get_user_stats(db: Session = Depends(get_db)):
    """
    Obtener estadísticas de usuarios
    
    Retorna:
    - Total de usuarios activos
    - Total de usuarios inactivos
    - Usuarios por rol
    """
    total_active = userService.get_active_users_count(db)
    total_users = userService.count_users(db)
    total_inactive = total_users - total_active
    
    # Por rol
    admins = userService.count_users(db, role_name='admin')
    advisors = userService.count_users(db, role_name='advisor')
    clients = userService.count_users(db, role_name='client')
    
    return {
        "total": total_users,
        "active": total_active,
        "inactive": total_inactive,
        "by_role": {
            "admin": admins,
            "advisor": advisors,
            "client": clients
        }
    }
    