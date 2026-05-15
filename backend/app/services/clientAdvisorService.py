"""
Service: ClientAdvisorAssignment

Lógica de negocio para asignación formal cliente-asesor.
"""

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException, status

from app.models import ClientAdvisorAssignment, User, Advisor


def get_active_assignment_for_client(db: Session, client_id: int) -> Optional[ClientAdvisorAssignment]:
    """Obtener asignación activa de un cliente"""
    return (
        db.query(ClientAdvisorAssignment)
        .options(
            selectinload(ClientAdvisorAssignment.client),
            selectinload(ClientAdvisorAssignment.advisor).selectinload(Advisor.user)
        )
        .filter(ClientAdvisorAssignment.client_id == client_id)
        .filter(ClientAdvisorAssignment.status == 'active')
        .first()
    )


def get_assignments_by_advisor(
    db: Session,
    advisor_id: int,
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[str] = None
) -> List[ClientAdvisorAssignment]:
    """Obtener asignaciones de un asesor"""
    query = db.query(ClientAdvisorAssignment).options(
        selectinload(ClientAdvisorAssignment.client),
        selectinload(ClientAdvisorAssignment.advisor).selectinload(Advisor.user)
    ).filter(ClientAdvisorAssignment.advisor_id == advisor_id)
    
    if status_filter:
        query = query.filter(ClientAdvisorAssignment.status == status_filter)
    
    query = query.order_by(ClientAdvisorAssignment.assigned_date.desc())
    
    return query.offset(skip).limit(limit).all()


def count_assignments_by_advisor(
    db: Session,
    advisor_id: int,
    status_filter: Optional[str] = None
) -> int:
    """Contar asignaciones de un asesor"""
    query = db.query(func.count(ClientAdvisorAssignment.id)).filter(
        ClientAdvisorAssignment.advisor_id == advisor_id
    )
    
    if status_filter:
        query = query.filter(ClientAdvisorAssignment.status == status_filter)
    
    return query.scalar()


def create_assignment(
    db: Session,
    client_id: int,
    advisor_id: int,
    notes: Optional[str] = None
) -> ClientAdvisorAssignment:
    """Crear una nueva asignación cliente-asesor"""
    client = db.query(User).filter(User.id == client_id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    
    advisor = db.query(Advisor).filter(Advisor.id == advisor_id).first()
    if not advisor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asesor no encontrado")
    
    existing = get_active_assignment_for_client(db, client_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El cliente ya tiene una asignación activa con el asesor {existing.advisor.user.full_name}"
        )
    
    assignment = ClientAdvisorAssignment(
        client_id=client_id,
        advisor_id=advisor_id,
        assigned_date=datetime.now(),
        status='active',
        notes=notes
    )
    
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    return assignment


def deactivate_assignment(
    db: Session,
    assignment_id: int,
    reason: Optional[str] = None
) -> ClientAdvisorAssignment:
    """Desactivar una asignación"""
    assignment = (
        db.query(ClientAdvisorAssignment)
        .filter(ClientAdvisorAssignment.id == assignment_id)
        .first()
    )
    
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignación no encontrada")
    
    if assignment.status != 'active':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La asignación ya está {assignment.status}"
        )
    
    assignment.deactivate(reason=reason)
    
    db.commit()
    db.refresh(assignment)
    
    return assignment


def get_advisor_stats(db: Session, advisor_id: int) -> dict:
    """Obtener estadísticas de asignaciones de un asesor"""
    total = count_assignments_by_advisor(db, advisor_id)
    active = count_assignments_by_advisor(db, advisor_id, status_filter='active')
    inactive = count_assignments_by_advisor(db, advisor_id, status_filter='inactive')
    
    return {
        "total_assignments": total,
        "active_assignments": active,
        "inactive_assignments": inactive
    }
