"""
Controller: Favorite

Endpoints para gestión de propiedades favoritas.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.dbConfig.databaseSession import get_db
from app.services import favoriteService
from app.schemas import (
    FavoriteResponse,
    FavoriteDetailResponse,
    FavoriteListResponse,
    FavoriteToggleResponse,
    PropertyResponse
)

router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"]
)


# ==========================================
# LISTAR FAVORITOS
# ==========================================

@router.get("", response_model=FavoriteListResponse)
def get_user_favorites(
    user_id: int = Query(..., description="ID del usuario (temporal, con JWT se extraerá del token)"),
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de registros"),
    db: Session = Depends(get_db)
):
    """
    Listar favoritos de un usuario
    
    Query params:
    - **user_id**: ID del usuario (TEMPORAL, con JWT del token)
    - **skip**: Paginación
    - **limit**: Máximo de resultados (1-100)
    
    Retorna:
    - Lista de favoritos del usuario
    - Total de favoritos
    - Ordenados por fecha de agregado (más recientes primero)
    """
    favorites = favoriteService.get_user_favorites(db, user_id, skip, limit)
    total = favoriteService.count_user_favorites(db, user_id)
    
    return {
        "favorites": favorites,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/properties", response_model=list[PropertyResponse])
def get_favorite_properties(
    user_id: int = Query(..., description="ID del usuario"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Obtener propiedades favoritas (solo las Property)
    
    Query params:
    - **user_id**: ID del usuario (TEMPORAL)
    - **skip**: Paginación
    - **limit**: Máximo de resultados
    
    Retorna:
    - Lista de propiedades favoritas (objetos Property completos)
    - Sin el wrapper de Favorite
    
    Útil para:
    - Mostrar grid de propiedades favoritas
    - Integración con componentes de propiedades
    """
    properties = favoriteService.get_favorite_properties(db, user_id, skip, limit)
    return properties


# ==========================================
# AGREGAR/QUITAR FAVORITO
# ==========================================

@router.post("/{property_id}", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
def add_favorite(
    property_id: int,
    user_id: int = Query(..., description="ID del usuario"),
    db: Session = Depends(get_db)
):
    """
    Agregar propiedad a favoritos
    
    Path params:
    - **property_id**: ID de la propiedad
    
    Query params:
    - **user_id**: ID del usuario (TEMPORAL)
    
    Validaciones:
    - Usuario debe existir
    - Propiedad debe existir
    - No puede estar ya en favoritos
    
    Errores:
    - 404: Usuario o propiedad no encontrado
    - 400: Ya está en favoritos
    """
    favorite = favoriteService.add_favorite(db, user_id, property_id)
    return favorite


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    property_id: int,
    user_id: int = Query(..., description="ID del usuario"),
    db: Session = Depends(get_db)
):
    """
    Quitar propiedad de favoritos
    
    Path params:
    - **property_id**: ID de la propiedad
    
    Query params:
    - **user_id**: ID del usuario (TEMPORAL)
    
    Retorna 204 si se quitó correctamente.
    También retorna 204 si no existía (idempotente).
    """
    favoriteService.remove_favorite(db, user_id, property_id)
    return None


# ==========================================
# TOGGLE FAVORITO
# ==========================================

@router.post("/toggle/{property_id}", response_model=FavoriteToggleResponse)
def toggle_favorite(
    property_id: int,
    user_id: int = Query(..., description="ID del usuario"),
    db: Session = Depends(get_db)
):
    """
    Toggle favorito (agregar si no existe, quitar si existe)
    
    Path params:
    - **property_id**: ID de la propiedad
    
    Query params:
    - **user_id**: ID del usuario (TEMPORAL)
    
    Retorna:
    - action: "added" o "removed"
    - is_favorite: True o False
    - property_id: ID de la propiedad
    - favorite_id: ID del favorito (solo si action="added")
    
    Este endpoint es ideal para UX simple con un solo botón.
    
    Errores:
    - 404: Propiedad no encontrada
    """
    result = favoriteService.toggle_favorite(db, user_id, property_id)
    return result


# ==========================================
# VERIFICACIÓN
# ==========================================

@router.get("/check/{property_id}")
def check_is_favorite(
    property_id: int,
    user_id: int = Query(..., description="ID del usuario"),
    db: Session = Depends(get_db)
):
    """
    Verificar si una propiedad está en favoritos
    
    Path params:
    - **property_id**: ID de la propiedad
    
    Query params:
    - **user_id**: ID del usuario (TEMPORAL)
    
    Retorna:
    - is_favorite: True o False
    - property_id: ID de la propiedad
    
    Útil para:
    - Mostrar icono de corazón lleno/vacío
    - Validaciones en frontend
    """
    is_favorite = favoriteService.is_favorite(db, user_id, property_id)
    return {
        "property_id": property_id,
        "is_favorite": is_favorite
    }


@router.post("/check-multiple")
def check_multiple_favorites(
    property_ids: List[int],
    user_id: int = Query(..., description="ID del usuario"),
    db: Session = Depends(get_db)
):
    """
    Verificar múltiples propiedades a la vez
    
    Query params:
    - **user_id**: ID del usuario (TEMPORAL)
    
    Body:
    - Lista de property_ids
    
    Retorna:
    - Diccionario {property_id: is_favorite}
    
    Útil para:
    - Marcar favoritos en listados de propiedades
    - Evitar múltiples llamadas al API
    
    Ejemplo:
```json
    [1, 2, 3, 4, 5]
```
    
    Respuesta:
```json
    {
      "1": true,
      "2": false,
      "3": true,
      "4": false,
      "5": true
    }
```
    """
    result = favoriteService.check_multiple_favorites(db, user_id, property_ids)
    return result


# ==========================================
# CONSULTAS ESPECIALES
# ==========================================

@router.get("/most-favorited/list")
def get_most_favorited_properties(
    limit: int = Query(10, ge=1, le=50, description="Número de propiedades"),
    min_favorites: int = Query(1, ge=1, description="Mínimo de favoritos"),
    db: Session = Depends(get_db)
):
    """
    Obtener propiedades más guardadas en favoritos
    
    Query params:
    - **limit**: Número de propiedades a retornar (1-50)
    - **min_favorites**: Mínimo de favoritos para incluir (default: 1)
    
    Retorna:
    - Lista de propiedades más populares
    - Cada una con su contador de favoritos
    
    Solo incluye propiedades con status='approved'.
    
    Útil para:
    - "Propiedades más populares"
    - Recomendaciones
    - Trending
    """
    most_favorited = favoriteService.get_most_favorited_properties(
        db,
        limit=limit,
        min_favorites=min_favorites
    )
    return {
        "properties": most_favorited,
        "total": len(most_favorited)
    }


@router.get("/property/{property_id}/count")
def count_property_favorites(
    property_id: int,
    db: Session = Depends(get_db)
):
    """
    Contar cuántos usuarios tienen una propiedad en favoritos
    
    Path params:
    - **property_id**: ID de la propiedad
    
    Retorna:
    - property_id: ID de la propiedad
    - favorite_count: Número de usuarios que la tienen
    
    Útil para:
    - Mostrar "X personas guardaron esta propiedad"
    - Métricas de popularidad
    """
    count = favoriteService.count_property_favorites(db, property_id)
    return {
        "property_id": property_id,
        "favorite_count": count
    }


# ==========================================
# ESTADÍSTICAS
# ==========================================

@router.get("/stats/user")
def get_user_favorite_stats(
    user_id: int = Query(..., description="ID del usuario"),
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas de favoritos de un usuario
    
    Query params:
    - **user_id**: ID del usuario (TEMPORAL)
    
    Retorna:
    - Total de favoritos
    - Desglose por tipo de propiedad
    
    Útil para:
    - Perfil de usuario
    - Analytics
    """
    stats = favoriteService.get_favorite_stats(db, user_id=user_id)
    return stats


@router.get("/stats/global")
def get_global_favorite_stats(db: Session = Depends(get_db)):
    """
    Obtener estadísticas globales de favoritos
    
    Retorna:
    - Total de favoritos en el sistema
    - Total de usuarios con favoritos
    - Promedio de favoritos por usuario
    
    Útil para:
    - Dashboard de admin
    - Métricas del sistema
    """
    stats = favoriteService.get_favorite_stats(db)
    return stats


# ==========================================
# LIMPIEZA (ADMIN)
# ==========================================

@router.delete("/user/{user_id}/all", status_code=status.HTTP_204_NO_CONTENT)
def remove_all_user_favorites(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Quitar todos los favoritos de un usuario
    
    Path params:
    - **user_id**: ID del usuario
    
    Retorna 204 y el número de favoritos eliminados.
    
    Útil para:
    - Limpiar cuenta de usuario
    - Admin tools
    
    Nota: Con JWT, solo el mismo usuario o admin podrá hacer esto.
    """
    count = favoriteService.remove_all_user_favorites(db, user_id)
    return None
