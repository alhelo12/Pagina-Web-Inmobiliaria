"""
Modelo: User (Usuarios del Sistema)

Descripción:
    Usuarios generales del sistema. Pueden tener diferentes roles:
    - admin: Acceso total al sistema
    - advisor: Asesor inmobiliario (tiene perfil extendido en Advisor)
    - client: Cliente que busca o publica propiedades

Tabla: users

Relaciones:
    - role: Many-to-One con Role
    - advisor: One-to-One con Advisor (si es asesor)
    - properties: One-to-Many con Property (propiedades que publicó)
    - appointments_as_client: One-to-Many con Appointment
    - favorites: One-to-Many con Favorite
"""

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.dbConfig.baseModels import BaseModel


class User(BaseModel):
    """
    Modelo de Usuario
    
    Attributes:
        id (int): ID único del usuario (heredado)
        full_name (str): Nombre completo del usuario
        email (str): Email único del usuario
        phone (str): Teléfono de contacto
        password_hash (str): Hash de la contraseña (bcrypt)
        role_id (int): FK a roles
        is_active (bool): Si el usuario está activo
        created_at (datetime): Fecha de creación (heredado)
        updated_at (datetime): Última actualización (heredado)
    
    Relationships:
        role: Rol del usuario (admin/advisor/client)
        advisor: Perfil de asesor (si role_id = advisor)
        properties: Propiedades que el usuario publicó
        appointments_as_client: Citas donde es el cliente
        favorites: Propiedades marcadas como favoritas
    """
    __tablename__ = "users"
    
    # Campos básicos
    full_name = Column(
        String(100), 
        nullable=False,
        comment="Nombre completo del usuario"
    )
    
    email = Column(
        String(100), 
        unique=True, 
        nullable=False, 
        index=True,
        comment="Email único del usuario"
    )
    
    phone = Column(
        String(20),
        comment="Teléfono de contacto"
    )
    
    password_hash = Column(
        String, 
        nullable=False,
        comment="Hash bcrypt de la contraseña"
    )
    
    role_id = Column(
        Integer, 
        ForeignKey("roles.id"),
        comment="FK al rol del usuario"
    )
    
    is_active = Column(
        Boolean, 
        default=True,
        comment="Si el usuario está activo en el sistema"
    )
    
    # ==========================================
    # RELACIONES (Usar STRINGS para evitar imports circulares)
    # ==========================================
    
    # Relación con Role (Many-to-One)
    role = relationship(
        "Role",
        lazy="joined"  # Carga el role automáticamente con el user
    )
    
    # Relación con Advisor (One-to-One)
    # Un usuario puede tener un perfil de asesor
    advisor = relationship(
        "Advisor",
        back_populates="user",
        uselist=False,  # One-to-One
        cascade="all, delete-orphan"
    )
    
    # Relación con Property (One-to-Many)
    # Propiedades que este usuario publicó
    properties = relationship(
        "Property",
        foreign_keys="Property.submitted_by_user_id",
        back_populates="owner",
        lazy="dynamic"  # Query object para filtrar
    )
    
    # Relación con Appointment (One-to-Many)
    # Citas donde este usuario es el cliente
    appointments_as_client = relationship(
        "Appointment",
        foreign_keys="Appointment.client_id",
        back_populates="client",
        lazy="dynamic"
    )
    
    # Relación con Favorite (One-to-Many)
    # Propiedades marcadas como favoritas
    favorites = relationship(
        "Favorite",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    def __repr__(self):
        """Representación del usuario para debugging"""
        return f"<User(id={self.id}, email='{self.email}', role={self.role_id})>"
    
    def has_role(self, role_name: str) -> bool:
        """
        Verifica si el usuario tiene un rol específico
        
        Args:
            role_name: Nombre del rol (admin, advisor, client)
            
        Returns:
            bool: True si tiene el rol, False en caso contrario
        
        Example:
            >>> user.has_role('admin')
            True
        """
        return self.role and self.role.name == role_name
    
    def is_admin(self) -> bool:
        """Verifica si el usuario es administrador"""
        return self.has_role('admin')
    
    def is_advisor(self) -> bool:
        """Verifica si el usuario es asesor"""
        return self.has_role('advisor')
    
    def is_client(self) -> bool:
        """Verifica si el usuario es cliente"""
        return self.has_role('client')
    