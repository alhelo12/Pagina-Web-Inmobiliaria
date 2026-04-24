"""
Controller: Users
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.dbConfig.databaseSession import get_db
from app.services import userService
from app.core.dependencies import get_current_user, require_admin, verify_user_owns_resource
from app.schemas import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.models import User

router = APIRouter(prefix="/users", tags=["Users"])


# ── LISTAR USUARIOS (solo admin) ─────────────────────────────────────────────
@router.get("", response_model=UserListResponse)
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    role_name: Optional[str] = Query(None, description="Filtrar por rol: admin, advisor, client"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    # El service espera role_name (string), no role_id (int)
    users = userService.get_users(
        db,
        skip=skip,
        limit=limit,
        role_name=role_name,
        is_active=is_active
    )
    total = userService.count_users(db, role_name=role_name, is_active=is_active)

    # Construir la respuesta paginada que exige UserListResponse
    return UserListResponse(
        total=total,
        page=(skip // limit) + 1,
        per_page=limit,
        users=users
    )


# ── DETALLE DE USUARIO ───────────────────────────────────────────────────────
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_admin() and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="No tienes permisos para ver este usuario")

    user = userService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Usuario no encontrado")
    return user


# ── ACTUALIZAR USUARIO ───────────────────────────────────────────────────────
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    verify_user_owns_resource(user_id, current_user)
    return userService.update_user(db, user_id, user_data)


# ── ELIMINAR USUARIO (hard delete, solo admin) ───────────────────────────────
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    userService.hard_delete_user(db, user_id)
    return None


# ── ACTIVAR / DESACTIVAR ─────────────────────────────────────────────────────
@router.patch("/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = userService.activate_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Usuario no encontrado")
    return user


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = userService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Usuario no encontrado")
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


# ── BUSCAR POR EMAIL ─────────────────────────────────────────────────────────
@router.get("/search/by-email", response_model=UserResponse)
def search_user_by_email(
    email: str = Query(..., description="Email a buscar"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = userService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Usuario no encontrado")
    return user
