"""
Registro Central de Modelos - Base de Datos

Propósitos:
1. Importar todos los modelos en un solo lugar 
2. Evitar imports circulares entre modelos
3. Punto de referencia único para Alembic (migraciones)

Autor: Backend Team
Fecha: 2026-02-08
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, TIMESTAMP
from sqlalchemy.sql import func

# ==========================================
# BASE - El "Registro Civil" de SQLAlchemy
# ==========================================
# Base = declarative_base()

# # ==========================================
# # CLASE BASE OPCIONAL (Campos Comunes)
# # ==========================================
# class BaseModel(Base):
#     """
#     Modelo base abstracto con campos y métodos comunes.
    
#     Todos los modelos heredan de esta clase para:
#     - Tener campos id, created_at, updated_at automáticamente
#     - Compartir métodos útiles (to_dict, __repr__)
#     - Mantener consistencia en toda la base de datos
    
#     Nota: __abstract__ = True significa que esta clase NO crea
#     una tabla en la base de datos, solo sirve como plantilla.
#     """
#     __abstract__ = True
    
#     id = Column(Integer, primary_key=True, index=True)
#     created_at = Column(
#         TIMESTAMP, 
#         server_default=func.current_timestamp(), 
#         nullable=False,
#         comment="Fecha de creación del registro"
#     )
#     updated_at = Column(
#         TIMESTAMP, 
#         server_default=func.current_timestamp(), 
#         onupdate=func.current_timestamp(),
#         nullable=False,
#         comment="Fecha de última actualización"
#     )
    
#     def to_dict(self):
#         """
#         Convierte el modelo a un diccionario Python.
#         Útil para serialización JSON y debugging.
        
#         Returns:
#             dict: Diccionario con todos los campos del modelo
            
#         Example:
#             user = User(name="Juan", email="juan@example.com")
#             print(user.to_dict())
#             # {'id': 1, 'name': 'Juan', 'email': 'juan@example.com', ...}
#         """
#         return {
#             column.name: getattr(self, column.name) 
#             for column in self.__table__.columns
#         }
    
#     def __repr__(self):
#         """
#         Representación en string del modelo para debugging.
        
#         Returns:
#             str: Representación legible del objeto
            
#         Example:
#             user = User(id=1)
#             print(user)
#             # <User(id=1)>
#         """
#         return f"<{self.__class__.__name__}(id={self.id})>"
    

Base = declarative_base()

class BaseModel(Base):
    """Modelo base abstracto con campos comunes"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)
    
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"


# ==========================================
# IMPORTAR TODOS LOS MODELOS AQUÍ
# ==========================================
# IMPORTANTE: 
# - Estos imports deben estar AL FINAL del archivo
# - Se ejecutan después de que Base y BaseModel estén definidos
# - Esto previene imports circulares entre modelos
# - Permite que las relaciones (relationships) funcionen correctamente
# ==========================================



# TODO: Descomentar a medida que se vayan creando los modelos
# from app.models.roleModel import Role
# from app.models.userModel import User
# from app.models.advisorModel import Advisor
# from app.models.propertyModel import Property
# from app.models.propertyImageModel import PropertyImage
# from app.models.appointmentModel import Appointment
# from app.models.favoriteModel import Favorite

# ==========================================
# EXPORTAR PARA ALEMBIC Y OTROS MÓDULOS
# ==========================================
# Esta lista ayuda a:
# - Alembic encontrar todos los modelos para migraciones
# - Otros módulos importar fácilmente: from baseModels import *
# ==========================================

__all__ = [
    'Base',
    'BaseModel',
    'Role',
    # TODO: Agregar modelos aquí cuando se creen
    # 'User',
    # 'Advisor',
    # 'Property',
    # 'PropertyImage',
    # 'Appointment',
    # 'Favorite'
]
