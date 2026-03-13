"""
Módulo de Services (Lógica de Negocio)

Contiene la lógica de negocio separada de los controllers.

Estructura:
- authService: Autenticación y registro
- userService: CRUD de usuarios
- propertyService: Gestión de propiedades
- appointmentService: Gestión de citas
- advisorService: Gestión de asesores

Uso:
    from app.services import userService
    users = userService.get_all_users(db)
"""

# TODO: Descomentar a medida que se creen los services
from app.services import authService
from app.services import userService
# from app.services import propertyService
# from app.services import appointmentService
# from app.services import advisorService

__all__ = [
    # TODO: Agregar services aquí cuando se creen
    'authService',
    'userService',
    # 'propertyService',
    # 'appointmentService',
    # 'advisorService'
]
