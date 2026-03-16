"""
Módulo de Controllers (Routers de FastAPI)

Contiene los endpoints de la API organizados por funcionalidad.

Routers disponibles:
- authController: Login, registro, refresh token
- userController: CRUD de usuarios
- propertyController: Gestión de propiedades
- appointmentController: Gestión de citas
- advisorController: Gestión de asesores
- favoriteController: gestión de favoritos


Uso en main.py:
    from app.controllers import authController, propertyController
    app.include_router(authController.router)
    app.include_router(propertyController.router)
"""

# TODO: Descomentar a medida que se creen los controllers
from app.controllers import authController
from app.controllers import userController
from app.controllers import propertyController
from app.controllers import appointmentController
from app.controllers import advisorController
from app.controllers import favoriteController


__all__ = [
    # TODO: Agregar controllers aquí cuando se creen
    'authController',
    'userController',
    'propertyController',
    'appointmentController',
    'advisorController',
    'favoriteController'

]
