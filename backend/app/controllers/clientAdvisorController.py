"""
Controller: Client-Advisor Assignments

Endpoints para gestión de asignación formal cliente-asesor.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.dbConfig.databaseSession import get_db
from app.services import clientAdvisorService
from app.core.dependencies import get_current_user
from app.schemas.clientAdvisorSchema import (
    ClientAdvisorAssignmentCreate,
    ClientAdvisorAssignmentDeactivate,
    ClientAdvisorAssignmentDetailResponse,
    ClientAdvisorAssignmentListResponse
)
from app.models import User, Advisor

router = APIRouter(
    prefix="/advisors/assignments",
    tags=["Client-Advisor Assignments"]
)


@router.post("/assign", response_model=ClientAdvisorAssignmentDetailResponse)
def assign_client_to_advisor(
    assignment_data: ClientAdvisorAssignmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Asignar un cliente a un asesor. Solo admin o el propio asesor."""
    if not current_user.is_admin():
        advisor = db.query(Advisor).filter(Advisor.user_id == current_user.id).first()
        if not advisor or advisor.id != assignment_data.advisor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo administradores o el propio asesor pueden asignar clientes"
            )
    
    return clientAdvisorService.create_assignment(
        db=db,
        client_id=assignment_data.client_id,
        advisor_id=assignment_data.advisor_id,
        notes=assignment_data.notes
    )


@router.get("/my-advisor", response_model=ClientAdvisorAssignmentDetailResponse)
def get_my_advisor(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener el asesor asignado al cliente actual"""
    if not current_user.is_client():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo clientes pueden consultar su asesor asignado"
        )
    
    assignment = clientAdvisorService.get_active_assignment_for_client(db, current_user.id)
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tienes un asesor asignado actualmente"
        )
    
    return assignment


@router.get("/my-clients", response_model=ClientAdvisorAssignmentListResponse)
def get_my_clients(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener clientes asignados al asesor actual"""
    if not current_user.is_advisor():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo asesores pueden ver sus clientes asignados"
        )
    
    advisor = db.query(Advisor).filter(Advisor.user_id == current_user.id).first()
    if not advisor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil de asesor no encontrado")
    
    skip = (page - 1) * per_page
    
    assignments = clientAdvisorService.get_assignments_by_advisor(
        db=db,
        advisor_id=advisor.id,
        skip=skip,
        limit=per_page,
        status_filter=status_filter
    )
    
    total = clientAdvisorService.count_assignments_by_advisor(
        db=db,
        advisor_id=advisor.id,
        status_filter=status_filter
    )
    
    return ClientAdvisorAssignmentListResponse(
        total=total,
        page=page,
        per_page=per_page,
        assignments=assignments
    )


@router.post("/{assignment_id}/deactivate", response_model=ClientAdvisorAssignmentDetailResponse)
def deactivate_assignment(
    assignment_id: int,
    deactivate_data: ClientAdvisorAssignmentDeactivate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Desactivar una asignación"""
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden desactivar asignaciones"
        )
    
    return clientAdvisorService.deactivate_assignment(
        db=db,
        assignment_id=assignment_id,
        reason=deactivate_data.reason
    )


@router.get("/stats", response_model=dict)
def get_advisor_assignment_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de asignaciones del asesor actual"""
    if not current_user.is_advisor():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo asesores pueden ver sus estadísticas"
        )
    
    advisor = db.query(Advisor).filter(Advisor.user_id == current_user.id).first()
    if not advisor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil de asesor no encontrado")
    
    return clientAdvisorService.get_advisor_stats(db=db, advisor_id=advisor.id)
