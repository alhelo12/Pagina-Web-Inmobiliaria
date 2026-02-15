"""
Módulo de Schemas (Pydantic)

Schemas para validación de datos de entrada/salida (DTOs).

Facilita importación:
    from app.schemas import UserCreate, UserResponse, PropertyCreate

Schemas disponibles:
- User schemas: UserCreate, UserUpdate, UserResponse, UserLogin
- Property schemas: PropertyCreate, PropertyUpdate, PropertyResponse
- Appointment schemas: AppointmentCreate, AppointmentResponse
- etc.
"""

from app.schemas.userSchema import (
    UserBase,
    UserCreate,
    UserLogin,
    UserUpdate,
    PasswordChange,
    UserResponse,
    UserResponseWithAdvisor,
    UserListResponse,
    RoleResponse,
    Token,
    TokenData
)

# TODO: Descomentar a medida que se creen los schemas
# from app.schemas.propertySchema import PropertyCreate, PropertyResponse
# from app.schemas.appointmentSchema import AppointmentCreate, AppointmentResponse
# from app.schemas.advisorSchema import AdvisorCreate, AdvisorResponse

__all__ = [
    # User schemas
    'UserBase',
    'UserCreate',
    'UserLogin',
    'UserUpdate',
    'PasswordChange',
    'UserResponse',
    'UserResponseWithAdvisor',
    'UserListResponse',
    'RoleResponse',
    'Token',
    'TokenData',
    
    # TODO: Agregar schemas aquí cuando se creen
    # 'PropertyCreate',
    # 'PropertyResponse',
]
