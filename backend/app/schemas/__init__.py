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
    ClientRegister,
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
    PropertySearchFilters,
    NearbySearchParams,
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

from app.schemas.favoriteSchema import (
    FavoriteCreate,
    FavoriteDelete,
    FavoriteResponse,
    FavoriteDetailResponse,
    FavoriteListResponse,
    FavoriteToggle,
    FavoriteToggleResponse,
    FavoriteCheck,
    FavoriteStats,
    FavoritePropertyResponse
)

from app.schemas.notificationSchema import (
    NotificationBase,
    NotificationCreate,
    NotificationResponse,
    NotificationListResponse,
    NotificationCountResponse,
    NotificationMarkReadResponse,
    NotificationMarkRead,
    NOTIFICATION_TYPES,
    get_notification_type_info
)

from app.schemas.messageSchema import (
    MessageCreate,
    MessageResponse,
    MessageListResponse,
    ConversationCreate,
    ConversationResponse,
    ConversationListResponse,
    PropertyBrief,
)

from app.schemas.postSaleSchema import (
    FollowupTypeEnum,
    FollowupStatusEnum,
    PostSaleFollowupBase,
    PostSaleFollowupCreate,
    PostSaleFollowupComplete,
    PostSaleFollowupSkip,
    PostSaleFollowupResponse,
    PostSaleFollowupDetailResponse,
    PostSaleFollowupListResponse,
    PostSaleStats,
    PostSaleFollowupFilter,
    FOLLOWUP_TYPE_CONFIG,
    get_followup_type_info
)

from app.schemas.clientAdvisorSchema import (
    AssignmentStatusEnum,
    ClientAdvisorAssignmentBase,
    ClientAdvisorAssignmentCreate,
    ClientAdvisorAssignmentDeactivate,
    ClientAdvisorAssignmentResponse,
    ClientAdvisorAssignmentDetailResponse,
    ClientAdvisorAssignmentListResponse,
)

from app.schemas.contactSchema import (
    ContactStatusEnum,
    ContactCreate,
    ContactResponse,
    ContactDetailResponse,
    ContactStatusUpdate,
    ContactListResponse,
    ContactSuccessResponse,
)

# TODO: Descomentar a medida que se creen los schemas


__all__ = [
    # User schemas
    'UserBase',
    'UserCreate',
    "ClientRegister",
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
    'PropertySearchFilters',
    'NearbySearchParams',
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
    
    # Favorite schemas
    'FavoriteCreate',
    'FavoriteDelete',
    'FavoriteResponse',
    'FavoriteDetailResponse',
    'FavoriteListResponse',
    'FavoriteToggle',
    'FavoriteToggleResponse',
    'FavoriteCheck',
    'FavoriteStats',
    'FavoritePropertyResponse',
    
    # Notification schemas
    'NotificationBase',
    'NotificationCreate',
    'NotificationResponse',
    'NotificationListResponse',
    'NotificationCountResponse',
    'NotificationMarkReadResponse',
    'NotificationMarkRead',
    'NOTIFICATION_TYPES',
    'get_notification_type_info',

    # Message schemas
    'MessageCreate',
    'MessageResponse',
    'MessageListResponse',
    'ConversationCreate',
    'ConversationResponse',
    'ConversationListResponse',
    'PropertyBrief',

    # Post-Sale schemas
    'FollowupTypeEnum',
    'FollowupStatusEnum',
    'PostSaleFollowupBase',
    'PostSaleFollowupCreate',
    'PostSaleFollowupComplete',
    'PostSaleFollowupSkip',
    'PostSaleFollowupResponse',
    'PostSaleFollowupDetailResponse',
    'PostSaleFollowupListResponse',
    'PostSaleStats',
    'PostSaleFollowupFilter',
    'FOLLOWUP_TYPE_CONFIG',
    'get_followup_type_info',

    # Client-Advisor schemas
    'AssignmentStatusEnum',
    'ClientAdvisorAssignmentBase',
    'ClientAdvisorAssignmentCreate',
    'ClientAdvisorAssignmentDeactivate',
    'ClientAdvisorAssignmentResponse',
    'ClientAdvisorAssignmentDetailResponse',
    'ClientAdvisorAssignmentListResponse',

    # Contact schemas
    'ContactStatusEnum',
    'ContactCreate',
    'ContactResponse',
    'ContactDetailResponse',
    'ContactStatusUpdate',
    'ContactListResponse',
    'ContactSuccessResponse',

    # TODO: Agregar schemas aquí cuando se creen

]