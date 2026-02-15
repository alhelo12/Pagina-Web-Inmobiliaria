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

from app.schemas.appointmentSchema import (
    AppointmentTypeEnum,
    AppointmentStatusEnum,
    AppointmentBase,
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentConfirm,
    AppointmentComplete,
    AppointmentCancel,
    AppointmentResponse,
    AppointmentDetailResponse,
    AppointmentListResponse,
    AppointmentFilter,
    AppointmentStats,
    AppointmentCalendar,
    AppointmentClientResponse,
    AppointmentAdvisorResponse,
    AppointmentPropertyResponse
)

# TODO: Descomentar a medida que se creen los schemas
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
    
    # Appointment schemas
    'AppointmentTypeEnum',
    'AppointmentStatusEnum',
    'AppointmentBase',
    'AppointmentCreate',
    'AppointmentUpdate',
    'AppointmentConfirm',
    'AppointmentComplete',
    'AppointmentCancel',
    'AppointmentResponse',
    'AppointmentDetailResponse',
    'AppointmentListResponse',
    'AppointmentFilter',
    'AppointmentStats',
    'AppointmentCalendar',
    'AppointmentClientResponse',
    'AppointmentAdvisorResponse',
    'AppointmentPropertyResponse',
    
    # TODO: Agregar schemas aquí cuando se creen

]
