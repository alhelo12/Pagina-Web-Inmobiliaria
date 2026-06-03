"""
Schemas de Contacto (Pydantic)

DTOs para validacion del formulario de contacto publico.
"""

from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


# ==========================================
# ENUMS
# ==========================================

class ContactStatusEnum(str, Enum):
    """Estados posibles de una consulta de contacto"""
    NEW = "new"
    CONTACTED = "contacted"
    CLOSED = "closed"


# ==========================================
# SCHEMAS DE ENTRADA (Request)
# ==========================================

class ContactCreate(BaseModel):
    """
    Schema para el formulario publico de contacto.

    No requiere autenticacion. Cualquier visitante puede enviarlo.

    Example:
        {
            "name": "Maria Garcia",
            "email": "maria@example.com",
            "phone": "+52 961 123 4567",
            "service": "Compra de propiedad",
            "message": "Estoy interesada en una casa de 3 recamaras..."
        }
    """
    name: str = Field(..., min_length=2, max_length=100, description="Nombre completo del remitente")
    email: str = Field(..., min_length=5, max_length=100, description="Correo electronico de contacto")
    phone: Optional[str] = Field(None, max_length=20, description="Telefono de contacto (opcional)")
    service: str = Field(
        ...,
        max_length=50,
        description="Servicio de interes: Compra, Venta, Renta o Asesoria Juridica"
    )
    message: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Mensaje o consulta del visitante"
    )


# ==========================================
# SCHEMAS DE SALIDA (Response)
# ==========================================

class ContactResponse(BaseModel):
    """
    Schema de respuesta al crear una consulta de contacto.

    Solo se devuelven datos no sensibles al publico.

    Example:
        {
            "id": 1,
            "status": "new",
            "created_at": "2026-02-05T10:30:00"
        }
    """
    id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContactDetailResponse(BaseModel):
    """
    Schema detallado de una consulta (uso interno/admin).

    Example:
        {
            "id": 1,
            "name": "Maria Garcia",
            "email": "maria@example.com",
            "phone": "+52 961 123 4567",
            "service": "Compra de propiedad",
            "message": "Estoy interesada...",
            "status": "new",
            "created_at": "2026-02-05T10:30:00",
            "updated_at": "2026-02-05T10:30:00"
        }
    """
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    service: str
    message: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContactStatusUpdate(BaseModel):
    """Schema para actualizar el estado de una consulta"""
    status: ContactStatusEnum = Field(..., description="Nuevo estado: new, contacted o closed")


class ContactListResponse(BaseModel):
    """
    Schema para lista paginada de consultas (uso admin/asesor).

    Example:
        {
            "total": 25,
            "page": 1,
            "per_page": 20,
            "inquiries": [...]
        }
    """
    total: int = Field(..., description="Total de consultas")
    page: int = Field(..., ge=1, description="Pagina actual")
    per_page: int = Field(..., ge=1, le=100, description="Consultas por pagina")
    inquiries: list[ContactDetailResponse] = Field(..., description="Lista de consultas")


# ==========================================
# SCHEMA DE RESPUESTA PUBLICA
# ==========================================

class ContactSuccessResponse(BaseModel):
    """
    Respuesta exitosa al enviar el formulario publico.

    Example:
        {
            "success": true,
            "message": "Tu consulta fue recibida. Un asesor te contactara pronto.",
            "inquiry_id": 1
        }
    """
    success: bool
    message: str
    inquiry_id: int
