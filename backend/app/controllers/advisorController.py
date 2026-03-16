"""
Controller: Advisor

Endpoints para gestión de perfiles de asesores inmobiliarios.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.dbConfig.databaseSession import get_db
from app.services import advisorService
from app.schemas import (
    AdvisorCreate,
    AdvisorUpdate,
    AdvisorResponse,
    AdvisorDetailResponse,
    AdvisorListResponse,
    AdvisorStats
)

router = APIRouter(
    prefix="/advisors",
    tags=["Advisors"]
)


# ==========================================
# LISTAR ASESORES
# ==========================================

@router.get("", response_model=AdvisorListResponse)
def get_advisors(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de registros"),
    min_rating: Optional[float] = Query(None, ge=0.0, le=5.0, description="Rating mínimo"),
    db: Session = Depends(get_db)
):
    """
    Listar asesores
    
    Query params:
    - **skip**: Paginación
    - **limit**: Máximo de resultados (1-100)
    - **min_rating**: Rating mínimo para filtrar (0.0-5.0)
    
    Retorna:
    - Lista de asesores
    - Total de asesores
    """
    advisors = advisorService.get_advisors(db, skip, limit, min_rating)
    total = advisorService.count_advisors(db)
    
    return {
        "advisors": advisors,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/available", response_model=list[AdvisorResponse])
def get_available_advisors(db: Session = Depends(get_db)):
    """
    Obtener asesores disponibles (rating >= 4.0)
    
    Útil para:
    - Mostrar en formularios de selección
    - Asignar propiedades
    - Recomendaciones
    
    Retorna:
    - Lista de asesores con rating >= 4.0
    - Ordenados por rating descendente
    """
    advisors = advisorService.get_available_advisors(db)
    return advisors


# ==========================================
# OBTENER ASESOR POR ID
# ==========================================

@router.get("/{advisor_id}", response_model=AdvisorDetailResponse)
def get_advisor(
    advisor_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener asesor por ID
    
    Path params:
    - **advisor_id**: ID del asesor
    
    Retorna:
    - Asesor con todos sus datos
    - Información del usuario asociado
    
    Errores:
    - 404: Asesor no encontrado
    """
    advisor = advisorService.get_advisor_by_id(db, advisor_id)
    
    if not advisor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asesor no encontrado"
        )
    
    return advisor


@router.get("/user/{user_id}", response_model=AdvisorDetailResponse)
def get_advisor_by_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener asesor por ID de usuario
    
    Path params:
    - **user_id**: ID del usuario
    
    Retorna:
    - Asesor asociado al usuario
    
    Errores:
    - 404: Asesor no encontrado
    """
    advisor = advisorService.get_advisor_by_user_id(db, user_id)
    
    if not advisor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario no tiene perfil de asesor"
        )
    
    return advisor


# ==========================================
# CREAR PERFIL DE ASESOR
# ==========================================

@router.post("", response_model=AdvisorResponse, status_code=status.HTTP_201_CREATED)
def create_advisor(
    advisor_data: AdvisorCreate,
    user_id: int = Query(..., description="ID del usuario (temporal, con JWT se extraerá del token)"),
    db: Session = Depends(get_db)
):
    """
    Crear perfil de asesor
    
    Query params:
    - **user_id**: ID del usuario (TEMPORAL, con JWT del token)
    
    Body:
    - **license_number**: Número de licencia (opcional)
    - **agency_name**: Nombre de la agencia (opcional)
    - **profile_picture**: URL de foto de perfil (opcional)
    
    El rating inicial es 5.00 automáticamente.
    
    Validaciones:
    - Usuario debe existir
    - Usuario debe tener rol 'advisor'
    - No puede tener perfil de asesor duplicado
    
    Errores:
    - 404: Usuario no encontrado
    - 400: Usuario no es asesor o ya tiene perfil
    
    Nota: Con JWT, se validará que el usuario autenticado sea el mismo.
    """
    advisor = advisorService.create_advisor(db, user_id, advisor_data)
    return advisor


# ==========================================
# ACTUALIZAR PERFIL DE ASESOR
# ==========================================

@router.put("/{advisor_id}", response_model=AdvisorResponse)
def update_advisor(
    advisor_id: int,
    advisor_data: AdvisorUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar perfil de asesor
    
    Path params:
    - **advisor_id**: ID del asesor
    
    Body (todos opcionales):
    - **license_number**: Número de licencia
    - **agency_name**: Nombre de la agencia
    - **profile_picture**: URL de foto de perfil
    
    Validaciones:
    - Asesor debe existir
    
    Errores:
    - 404: Asesor no encontrado
    
    Nota: Con JWT, solo el mismo asesor o admin podrá actualizar.
    """
    advisor = advisorService.update_advisor(db, advisor_id, advisor_data)
    
    if not advisor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asesor no encontrado"
        )
    
    return advisor


# ==========================================
# ELIMINAR PERFIL DE ASESOR
# ==========================================

@router.delete("/{advisor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_advisor(
    advisor_id: int,
    db: Session = Depends(get_db)
):
    """
    Eliminar perfil de asesor
    
    Path params:
    - **advisor_id**: ID del asesor
    
    NOTA: Esto solo elimina el perfil de asesor, NO el usuario.
    El usuario permanece con rol 'advisor' pero sin perfil extendido.
    
    Errores:
    - 404: Asesor no encontrado
    
    Nota: Con JWT, solo admin podrá eliminar perfiles de asesores.
    """
    success = advisorService.delete_advisor(db, advisor_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asesor no encontrado"
        )
    
    return None


# ==========================================
# ESTADÍSTICAS
# ==========================================

@router.get("/{advisor_id}/stats", response_model=AdvisorStats)
def get_advisor_stats(
    advisor_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas de un asesor
    
    Path params:
    - **advisor_id**: ID del asesor
    
    Retorna:
    - Total de propiedades gestionadas
    - Propiedades por estado (approved, pending, sold)
    - Total de citas
    - Citas completadas y pendientes
    - Rating promedio
    - Valor total de ventas
    
    Errores:
    - 404: Asesor no encontrado
    """
    stats = advisorService.get_advisor_stats(db, advisor_id)
    return stats


@router.get("/with-stats/list")
def get_advisors_with_stats(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Obtener asesores con sus estadísticas básicas
    
    Query params:
    - **skip**: Paginación
    - **limit**: Máximo de resultados
    
    Retorna:
    - Lista de asesores con:
      * Datos del asesor
      * Propiedades activas
      * Rating
    
    Útil para dashboards y comparaciones.
    """
    advisors_with_stats = advisorService.get_advisors_with_stats(db, skip, limit)
    return {
        "advisors": advisors_with_stats,
        "total": advisorService.count_advisors(db),
        "skip": skip,
        "limit": limit
    }


# ==========================================
# RANKINGS
# ==========================================

@router.get("/rankings/top")
def get_top_advisors(
    limit: int = Query(10, ge=1, le=50, description="Número de asesores a retornar"),
    order_by: str = Query(
        "rating",
        description="Criterio de ordenamiento",
        regex="^(rating|properties|sales)$"
    ),
    db: Session = Depends(get_db)
):
    """
    Obtener top asesores
    
    Query params:
    - **limit**: Número de asesores a retornar (1-50)
    - **order_by**: Criterio de ordenamiento
      * rating: Por rating más alto (default)
      * properties: Por más propiedades gestionadas
      * sales: Por más ventas completadas
    
    Retorna:
    - Lista de top asesores según criterio
    
    Útil para:
    - Mostrar mejores asesores
    - Leaderboards
    - Recomendaciones
    """
    top_advisors = advisorService.get_top_advisors(db, limit, order_by)
    return {
        "top_advisors": top_advisors,
        "limit": limit,
        "order_by": order_by
    }


# ==========================================
# GESTIÓN DE RATING
# ==========================================

@router.patch("/{advisor_id}/rating", response_model=AdvisorResponse)
def update_advisor_rating(
    advisor_id: int,
    new_rating: float = Query(..., ge=0.0, le=5.0, description="Nuevo rating (0.0-5.0)"),
    db: Session = Depends(get_db)
):
    """
    Actualizar rating de asesor
    
    Path params:
    - **advisor_id**: ID del asesor
    
    Query params:
    - **new_rating**: Nuevo rating (0.0-5.0)
    
    Validaciones:
    - Rating debe estar entre 0.0 y 5.0
    - Asesor debe existir
    
    Errores:
    - 404: Asesor no encontrado
    - 400: Rating inválido
    
    Nota: Con JWT, solo admin podrá actualizar ratings.
    En producción, implementar sistema de reviews para cálculo automático.
    """
    advisor = advisorService.update_advisor_rating(db, advisor_id, new_rating)
    return advisor


# ==========================================
# UTILIDADES
# ==========================================

@router.get("/{advisor_id}/has-active-properties")
def check_active_properties(
    advisor_id: int,
    db: Session = Depends(get_db)
):
    """
    Verificar si un asesor tiene propiedades activas
    
    Path params:
    - **advisor_id**: ID del asesor
    
    Retorna:
    - has_active_properties: True si tiene propiedades activas (approved o pending)
    
    Útil para:
    - Validar antes de eliminar asesor
    - Mostrar estado de actividad
    """
    has_active = advisorService.advisor_has_active_properties(db, advisor_id)
    return {
        "advisor_id": advisor_id,
        "has_active_properties": has_active
    }
    