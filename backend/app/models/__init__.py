"""
Módulo de Modelos ORM (SQLAlchemy)

Facilita la importación de modelos:
    from app.models import Role, User, Property

Modelos disponibles:
- Role: Roles de usuario (admin, advisor, client)
- User: Usuarios del sistema
- Advisor: Perfil extendido de asesores
- Property: Propiedades inmobiliarias
- PropertyImage: Imágenes de propiedades
- Appointment: Citas entre clientes y asesores
- Favorite: Propiedades favoritas de usuarios
"""

from app.models.roleModel import Role
from app.models.userModel import User
from app.models.advisorModel import Advisor
from app.models.propertyModel import Property
from app.models.propertyImageModel import PropertyImage
from app.models.appointmentModel import Appointment
from app.models.favoriteModel import Favorite

__all__ = [
    'Role',
    'User',
    'Advisor',
    'Property',
    'PropertyImage',
    'Appointment',
    'Favorite'

]
