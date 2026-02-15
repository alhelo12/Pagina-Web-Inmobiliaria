"""
Schemas de Usuario (Pydantic)

DTOs (Data Transfer Objects) para validación de datos
de entrada y salida relacionados con usuarios.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


# ==========================================
# SCHEMA BASE
# ==========================================

class UserBase(BaseModel):
    """Schema base con campos comunes de usuario"""
    full_name: str = Field(..., min_length=2, max_length=100, description="Nombre completo del usuario")
    email: EmailStr = Field(..., description="Email único del usuario")
    phone: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto")


# ==========================================
# SCHEMAS DE ENTRADA (Request)
# ==========================================

class UserCreate(UserBase):
    """
    Schema para crear un nuevo usuario (Registro)
    
    Example:
        {
            "full_name": "Juan Pérez",
            "email": "juan@example.com",
            "phone": "5551234567",
            "password": "SecurePass123!",
            "role_id": 3
        }
    """
    password: str = Field(..., min_length=8, max_length=100, description="Contraseña (mínimo 8 caracteres)")
    role_id: int = Field(..., ge=1, description="ID del rol (1=admin, 2=advisor, 3=client)")


class UserLogin(BaseModel):
    """
    Schema para login de usuario
    
    Example:
        {
            "email": "juan@example.com",
            "password": "SecurePass123!"
        }
    """
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., description="Contraseña")


class UserUpdate(BaseModel):
    """
    Schema para actualizar usuario (todos los campos opcionales)
    
    Example:
        {
            "full_name": "Juan Pérez Updated",
            "phone": "5559876543"
        }
    """
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class PasswordChange(BaseModel):
    """
    Schema para cambio de contraseña
    
    Example:
        {
            "current_password": "OldPass123!",
            "new_password": "NewPass456!"
        }
    """
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., min_length=8, max_length=100, description="Nueva contraseña")


# ==========================================
# SCHEMAS DE SALIDA (Response)
# ==========================================

class RoleResponse(BaseModel):
    """Schema de respuesta para el rol del usuario"""
    id: int
    name: str
    
    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    """
    Schema de respuesta de usuario (SIN password)
    
    Se usa en:
    - GET /users/{id}
    - GET /users/me
    - Respuesta después de registro
    
    Example:
        {
            "id": 1,
            "full_name": "Juan Pérez",
            "email": "juan@example.com",
            "phone": "5551234567",
            "role_id": 3,
            "role": {
                "id": 3,
                "name": "client"
            },
            "is_active": true,
            "created_at": "2026-02-05T10:30:00",
            "updated_at": "2026-02-05T10:30:00"
        }
    """
    id: int
    role_id: int
    role: Optional[RoleResponse] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserResponseWithAdvisor(UserResponse):
    """
    Schema de respuesta de usuario CON perfil de asesor (si aplica)
    
    Se usa cuando el usuario tiene rol 'advisor' y queremos
    incluir su información extendida.
    """
    advisor: Optional[dict] = None  # Lo definiremos mejor después con AdvisorResponse
    
    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """
    Schema para lista paginada de usuarios
    
    Example:
        {
            "total": 50,
            "page": 1,
            "per_page": 10,
            "users": [...]
        }
    """
    total: int = Field(..., description="Total de usuarios")
    page: int = Field(..., ge=1, description="Página actual")
    per_page: int = Field(..., ge=1, le=100, description="Usuarios por página")
    users: list[UserResponse] = Field(..., description="Lista de usuarios")


# ==========================================
# SCHEMAS DE AUTENTICACIÓN
# ==========================================

class Token(BaseModel):
    """
    Schema de respuesta tras login exitoso
    
    Example:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Tipo de token")


class TokenData(BaseModel):
    """
    Schema de datos decodificados del token JWT
    
    Se usa internamente para validar tokens.
    """
    email: Optional[str] = None
    user_id: Optional[int] = None
    