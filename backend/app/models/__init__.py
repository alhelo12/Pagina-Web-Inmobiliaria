"""
Modulo de Modelos ORM (SQLAlchemy)

Facilita la importacion de modelos:
    from app.models import Role, User, Property

Modelos disponibles:
- Role: Roles de usuario (admin, advisor, client)
- User: Usuarios del sistema
- Advisor: Perfil extendido de asesores
- Property: Propiedades inmobiliarias
- PropertyImage: Imagenes de propiedades
- Appointment: Citas entre clientes y asesores
- Favorite: Propiedades favoritas de usuarios
- ContactInquiry: Consultas del formulario publico de contacto
"""

from app.models.roleModel import Role
from app.models.userModel import User
from app.models.advisorModel import Advisor
from app.models.propertyModel import Property
from app.models.propertyImageModel import PropertyImage
from app.models.appointmentModel import Appointment
from app.models.favoriteModel import Favorite
from app.models.notificationModel import Notification
from app.models.notificationPreferenceModel import NotificationPreference
from app.models.messageModel import Conversation, Message
from app.models.postSaleFollowupModel import PostSaleFollowup
from app.models.clientAdvisorModel import ClientAdvisorAssignment
from app.models.activityLogModel import ActivityLog
from app.models.contactInquiryModel import ContactInquiry

__all__ = [
    'Role',
    'User',
    'Advisor',
    'Property',
    'PropertyImage',
    'Appointment',
    'Favorite',
    'Notification',
    'NotificationPreference',
    'Conversation',
    'Message',
    'PostSaleFollowup',
    'ClientAdvisorAssignment',
    'ActivityLog',
    'ContactInquiry',
]
