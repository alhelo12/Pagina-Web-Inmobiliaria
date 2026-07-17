"""
Schemas de Asignación Cliente-Asesor (Pydantic)

DTOs para validación de datos de entrada y salida.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


class AssignmentStatusEnum(str, Enum):
    """Estados de la asignación"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class ClientAdvisorAssignmentBase(BaseModel):
    """Schema base"""
    notes: Optional[str] = Field(None, max_length=2000, description="Notas")


class ClientAdvisorAssignmentCreate(BaseModel):
    """Schema para crear una asignación"""
    client_id: int = Field(..., ge=1, description="ID del cliente")
    advisor_id: int = Field(..., ge=1, description="ID del asesor")
    notes: Optional[str] = Field(None, max_length=2000)


class ClientAdvisorAssignmentDeactivate(BaseModel):
    """Schema para desactivar una asignación"""
    reason: Optional[str] = Field(None, max_length=1000, description="Razón")


class ClientAdvisorClientResponse(BaseModel):
    """Schema simplificado del cliente"""
    id: int
    full_name: str
    email: str
    phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ClientAdvisorAdvisorResponse(BaseModel):
    """Schema simplificado del asesor"""
    id: int
    user_id: int
    agency_name: Optional[str] = None
    rating: float
    user: ClientAdvisorClientResponse

    model_config = ConfigDict(from_attributes=True)


class ClientAdvisorAssignmentResponse(BaseModel):
    """Schema de respuesta"""
    id: int
    client_id: int
    advisor_id: int
    assigned_date: datetime
    end_date: Optional[datetime]
    status: AssignmentStatusEnum
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClientAdvisorAssignmentDetailResponse(ClientAdvisorAssignmentResponse):
    """Schema de respuesta detallada con relaciones"""
    client: Optional[ClientAdvisorClientResponse] = None
    advisor: Optional[ClientAdvisorAdvisorResponse] = None

    model_config = ConfigDict(from_attributes=True)


class ClientAdvisorAssignmentListResponse(BaseModel):
    """Schema para lista paginada"""
    total: int
    page: int
    per_page: int
    assignments: list[ClientAdvisorAssignmentDetailResponse]
