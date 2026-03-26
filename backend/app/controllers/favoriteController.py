"""
Controller: Favorites

Endpoints para gestión de favoritos de propiedades.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.dbConfig.databaseSession import get_db
from app.services import favoriteService
from app.core.dependencies import get_current_user
from app.schemas import (
    FavoriteResponse,
    FavoriteListResponse,
    FavoriteToggleResponse
)
from app.models import User

router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"]
)


# ==========================================
# TODOS LOS ENDPOINTS REQUIEREN AUTENTICACIÓN
# ==========================================

@router.post("/toggle/{property_id}", response_model=FavoriteToggleResponse)
def toggle_favorite(
    property_id: int,
    user_id: int = Query(..., description="ID del usuario"),
    current_user: User = Depends(get_current_user),  # 🔐 Requiere autenticación
    db: Session = Depends(get_db)
):
    """
    Agregar/quitar favorito (autenticado)
    
    Si la propiedad ya es favorita, la quita.
    Si no es favorita, la agrega.
    
    Validaciones:
    - Usuario autenticado
    - Usuario debe ser el mismo que user_id (o admin)
    - Propiedad debe existir
    
    Retorna:
    - action: "added" o "removed"
    - is_favorite: True o False
    - favorite_id: ID del favorito (solo si action="added")
    """
    # Verificar que el usuario sea el dueño o admin
    if not current_user.is_admin() and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes gestionar favoritos de otros usuarios"
        )
    
    result = favoriteService.toggle_favorite(db, user_id, property_id)
    return result


@router.get("", response_model=FavoriteListResponse)
def get_my_favorites(
    user_id: int = Query(..., description="ID del usuario"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),  # 🔐 Requiere autenticación
    db: Session = Depends(get_db)
):
    """
    Listar favoritos del usuario (autenticado)
    
    Retorna todas las propiedades marcadas como favoritas.
    
    Validaciones:
    - Usuario autenticado
    - Usuario debe ser el mismo que user_id (o admin)
    """
    # Verificar ownership
    if not current_user.is_admin() and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes ver favoritos de otros usuarios"
        )
    
    result = favoriteService.get_user_favorites(db, user_id, skip=skip, limit=limit)
    return result


@router.get("/{favorite_id}", response_model=FavoriteResponse)
def get_favorite(
    favorite_id: int,
    current_user: User = Depends(get_current_user),  # 🔐 Requiere autenticación
    db: Session = Depends(get_db)
):
    """
    Obtener detalle de un favorito (autenticado)
    
    Validaciones:
    - Usuario autenticado
    - Favorito debe pertenecer al usuario (o ser admin)
    """
    favorite = favoriteService.get_favorite_by_id(db, favorite_id)
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorito no encontrado"
        )
    
    # Verificar ownership
    if not current_user.is_admin() and favorite.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este favorito no te pertenece"
        )
    
    return favorite


@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    favorite_id: int,
    current_user: User = Depends(get_current_user),  # 🔐 Requiere autenticación
    db: Session = Depends(get_db)
):
    """
    Eliminar favorito por ID (autenticado)
    
    Alternativa a usar toggle.
    
    Validaciones:
    - Usuario autenticado
    - Favorito debe pertenecer al usuario (o ser admin)
    """
    favorite = favoriteService.get_favorite_by_id(db, favorite_id)
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorito no encontrado"
        )
    
    # Verificar ownership
    if not current_user.is_admin() and favorite.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes eliminar favoritos de otros usuarios"
        )
    
    favoriteService.remove_favorite(db, favorite_id)
    return None


# ==========================================
# ENDPOINTS DE VERIFICACIÓN
# ==========================================

@router.get("/check/{property_id}")
def check_is_favorite(
    property_id: int,
    user_id: int = Query(..., description="ID del usuario"),
    current_user: User = Depends(get_current_user),  # 🔐 Requiere autenticación
    db: Session = Depends(get_db)
):
    """
    Verificar si una propiedad es favorita (autenticado)
    
    Útil para mostrar el ícono de corazón en el frontend.
    
    Validaciones:
    - Usuario autenticado
    - Usuario debe ser el mismo que user_id (o admin)
    
    Retorna:
    - property_id: ID de la propiedad
    - is_favorite: True o False
    """
    # Verificar ownership
    if not current_user.is_admin() and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes verificar favoritos de otros usuarios"
        )
    
    is_fav = favoriteService.is_favorite(db, user_id, property_id)
    
    return {
        "property_id": property_id,
        "is_favorite": is_fav
    }


@router.post("/check-multiple")
def check_multiple_favorites(
    property_ids: List[int],
    user_id: int = Query(..., description="ID del usuario"),
    current_user: User = Depends(get_current_user),  # 🔐 Requiere autenticación
    db: Session = Depends(get_db)
):
    """
    Verificar múltiples propiedades a la vez (autenticado)
    
    Útil para marcar favoritos en listados de propiedades.
    
    Validaciones:
    - Usuario autenticado
    - Usuario debe ser el mismo que user_id (o admin)
    
    Body:
    - Lista de property_ids
    
    Retorna:
    - Diccionario con property_id como key y booleano como value
    
    Ejemplo:
    Input: [1, 2, 3, 4, 5]
    Output: {"1": true, "2": false, "3": true, "4": false, "5": true}
    """
    # Verificar ownership
    if not current_user.is_admin() and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes verificar favoritos de otros usuarios"
        )
    
    result = favoriteService.check_multiple_favorites(db, user_id, property_ids)
    return result


# ==========================================
# ENDPOINTS DE ESTADÍSTICAS
# ==========================================

@router.get("/stats/summary")
def get_favorites_stats(
    user_id: int = Query(..., description="ID del usuario"),
    current_user: User = Depends(get_current_user),  # 🔐 Requiere autenticación
    db: Session = Depends(get_db)
):
    """
    Estadísticas de favoritos del usuario (autenticado)
    
    Muestra:
    - Total de favoritos
    - Favoritos por tipo de propiedad
    - Rango de precios promedio
    
    Validaciones:
    - Usuario autenticado
    - Usuario debe ser el mismo que user_id (o admin)
    """
    # Verificar ownership
    if not current_user.is_admin() and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes ver estadísticas de otros usuarios"
        )
    
    stats = favoriteService.get_user_favorites_stats(db, user_id)
    return stats


@router.get("/property/{property_id}/count")
def get_property_favorites_count(
    property_id: int,
    db: Session = Depends(get_db)
):
    """
    Contar cuántos usuarios tienen esta propiedad como favorita (público)
    
    No requiere autenticación.
    Útil para mostrar "X personas marcaron esto como favorito".
    """
    count = favoriteService.get_property_favorites_count(db, property_id)
    
    return {
        "property_id": property_id,
        "favorites_count": count
    }
    