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

from app.schemas.propertySchema import (
    PropertyTypeEnum,
    TransactionTypeEnum,
    PropertyStatusEnum,
    PropertyImageBase,
    PropertyImageCreate,
    PropertyImageResponse,
    PropertyBase,
    PropertyCreate,
    PropertyUpdate,
    PropertyApprove,
    PropertyReject,
    PropertyResponse,
    PropertyDetailResponse,
    PropertyListResponse,
    PropertyFilter,
    PropertyStats,
    PropertyOwnerResponse,
    PropertyAdvisorResponse
)

from app.schemas.advisorSchema import (
    AdvisorBase,
    AdvisorCreate,
    AdvisorUpdate,
    AdvisorResponse,
    AdvisorDetailResponse,
    AdvisorListResponse,
    AdvisorUserResponse,
    AdvisorStats,
    AdvisorRanking
)

# TODO: Descomentar a medida que se creen los schemas
# from app.schemas.appointmentSchema import AppointmentCreate, AppointmentResponse
# from app.schemas.favoriteSchema import FavoriteCreate, FavoriteResponse

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
    
    # Property schemas
    'PropertyTypeEnum',
    'TransactionTypeEnum',
    'PropertyStatusEnum',
    'PropertyImageBase',
    'PropertyImageCreate',
    'PropertyImageResponse',
    'PropertyBase',
    'PropertyCreate',
    'PropertyUpdate',
    'PropertyApprove',
    'PropertyReject',
    'PropertyResponse',
    'PropertyDetailResponse',
    'PropertyListResponse',
    'PropertyFilter',
    'PropertyStats',
    'PropertyOwnerResponse',
    'PropertyAdvisorResponse',
    
    # Advisor schemas
    'AdvisorBase',
    'AdvisorCreate',
    'AdvisorUpdate',
    'AdvisorResponse',
    'AdvisorDetailResponse',
    'AdvisorListResponse',
    'AdvisorUserResponse',
    'AdvisorStats',
    'AdvisorRanking',
    
    # TODO: Agregar schemas aquí cuando se creen

]
