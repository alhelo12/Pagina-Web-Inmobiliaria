"""
Modelo: Role (Roles de Usuario)

Descripción:
    Define los tipos de usuarios en el sistema:
    - admin: Administrador con permisos totales
    - advisor: Asesor inmobiliario que gestiona propiedades
    - client: Cliente que busca y/o publica propiedades

Tabla: roles

Campos heredados de BaseModel:
    - id: Integer (PK)
    - created_at: Timestamp
    - updated_at: Timestamp
"""

from sqlalchemy import Column, String
from app.dbConfig.baseModels import BaseModel


class Role(BaseModel):
    """
    Modelo de Roles de Usuario
    
    Attributes:
        id (int): ID único del rol (heredado de BaseModel)
        name (str): Nombre del rol (admin, advisor, client)
        created_at (datetime): Fecha de creación (heredado de BaseModel)
        updated_at (datetime): Fecha de actualización (heredado de BaseModel)
    
    Example:
        >>> role = Role(name="admin")
        >>> print(role)
        <Role(id=None, name='admin')>
    """
    __tablename__ = "roles"
    
    # Campos específicos del modelo
    # (id, created_at, updated_at vienen de BaseModel)
    name = Column(
        String(50), 
        unique=True, 
        nullable=False, 
        index=True,
        comment="Nombre del rol (admin, advisor, client)"
    )
    
    def __repr__(self):
        """Representación en string del rol para debugging"""
        return f"<Role(id={self.id}, name='{self.name}')>"
    