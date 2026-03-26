"""
Controller: Users

Endpoints para gestión de usuarios.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.dbConfig.databaseSession import get_db
from app.services import userService
from app.core.dependencies import (
    get_current_user,
    require_admin,
    verify_user_owns_resource
)
from app.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse
)
from app.models import User

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# ==========================================
# ENDPOINTS PÚBLICOS/BÁSICOS
# ==========================================

@router.get("", response_model=UserListResponse)
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    role_id: Optional[int] = Query(None, description="Filtrar por rol"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado"),
    current_user: User = Depends(require_admin),  # 🔐 Solo admin
    db: Session = Depends(get_db)
):
    """
    Listar usuarios (solo admin)
    
    Permite filtrar por rol y estado activo.
    """
    result = userService.get_users(
        db,
        skip=skip,
        limit=limit,
        role_id=role_id,
        is_active=is_active
    )
    return result


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),  # 🔐 Requiere autenticación
    db: Session = Depends(get_db)
):
    """
    Obtener detalle de usuario (autenticado)
    
    Los usuarios pueden ver su propia info.
    Admin puede ver cualquier usuario.
    """
    # Verificar que sea el mismo usuario o admin
    if not current_user.is_admin() and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este usuario"
        )
    
    user = userService.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),  # 🔐 Requiere autenticación
    db: Session = Depends(get_db)
):
    """
    Actualizar usuario (autenticado)
    
    El usuario puede actualizar su propia info.
    Admin puede actualizar cualquier usuario.
    """
    # Verificar ownership o admin
    verify_user_owns_resource(user_id, current_user)
    
    user = userService.update_user(db, user_id, user_data)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),  # 🔐 Solo admin
    db: Session = Depends(get_db)
):
    """
    Eliminar usuario (solo admin)
    
    Requiere:
    - Token JWT válido
    - Rol de admin
    
    Nota: Esto es un soft delete (is_active = False).
    """
    userService.delete_user(db, user_id)
    return None


@router.patch("/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: int,
    current_user: User = Depends(require_admin),  # 🔐 Solo admin
    db: Session = Depends(get_db)
):
    """
    Activar usuario desactivado (solo admin)
    
    Cambia is_active a True.
    """
    user = userService.activate_user(db, user_id)
    return user


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_admin),  # 🔐 Solo admin
    db: Session = Depends(get_db)
):
    """
    Desactivar usuario (solo admin)
    
    Cambia is_active a False.
    El usuario no podrá hacer login.
    """
    user = userService.deactivate_user(db, user_id)
    return user


# ==========================================
# ENDPOINTS DE BÚSQUEDA
# ==========================================

@router.get("/search/by-email")
def search_user_by_email(
    email: str = Query(..., description="Email a buscar"),
    current_user: User = Depends(require_admin),  # 🔐 Solo admin
    db: Session = Depends(get_db)
):
    """
    Buscar usuario por email (solo admin)
    """
    user = userService.get_user_by_email(db, email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user
