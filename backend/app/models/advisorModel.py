"""
Modelo: Advisor (Asesores Inmobiliarios)

Descripción:
    Perfil extendido para usuarios con rol 'advisor'.
    Relación One-to-One con User.
    Contiene información específica del asesor como licencia,
    agencia, foto de perfil y rating.

Tabla: advisors

Relaciones:
    - user: One-to-One con User (back_populates)
    - properties: One-to-Many con Property (propiedades que gestiona)
    - appointments: One-to-Many con Appointment (citas con clientes)
"""

from sqlalchemy import Column, String, Integer, ForeignKey, NUMERIC
from sqlalchemy.orm import relationship
from app.dbConfig.baseModels import BaseModel


class Advisor(BaseModel):
    """
    Modelo de Asesor Inmobiliario
    
    Attributes:
        id (int): ID único del asesor (heredado)
        user_id (int): FK a users (One-to-One)
        license_number (str): Número de licencia profesional
        agency_name (str): Nombre de la agencia inmobiliaria
        profile_picture (str): URL de la foto de perfil
        rating (Decimal): Calificación del asesor (0.00 - 5.00)
        created_at (datetime): Fecha de creación (heredado)
        updated_at (datetime): Última actualización (heredado)
    
    Relationships:
        user: Usuario asociado a este perfil de asesor
        properties: Propiedades que este asesor gestiona
        appointments: Citas programadas con clientes
    """
    __tablename__ = "advisors"
    
    # Relación One-to-One con User
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        comment="FK a users (One-to-One)"
    )
    
    # Información del asesor
    license_number = Column(
        String(50),
        comment="Número de licencia profesional"
    )
    
    agency_name = Column(
        String(100),
        comment="Nombre de la agencia inmobiliaria"
    )
    
    profile_picture = Column(
        String,
        comment="URL de la foto de perfil del asesor"
    )
    
    rating = Column(
        NUMERIC(3, 2),
        default=5.00,
        comment="Calificación del asesor (0.00 - 5.00)"
    )
    
    # ==========================================
    # RELACIONES
    # ==========================================
    
    # Relación One-to-One con User
    user = relationship(
        "User",
        back_populates="advisor",
        lazy="joined"  # Carga el user automáticamente
    )
    
    # Relación One-to-Many con Property
    # Propiedades que este asesor gestiona
    properties = relationship(
        "Property",
        foreign_keys="Property.advisor_id",
        back_populates="advisor",
        lazy="dynamic"
    )
    
    # Relación One-to-Many con Appointment
    # Citas donde este asesor participa
    appointments = relationship(
        "Appointment",
        foreign_keys="Appointment.advisor_id",
        back_populates="advisor",
        lazy="dynamic"
    )
    
    def __repr__(self):
        """Representación del asesor para debugging"""
        return f"<Advisor(id={self.id}, user_id={self.user_id}, agency='{self.agency_name}')>"
    
    @property
    def full_name(self):
        """
        Obtiene el nombre completo desde el usuario relacionado
        
        Returns:
            str: Nombre completo del asesor
        
        Example:
            >>> advisor.full_name
            'Juan Pérez'
        """
        return self.user.full_name if self.user else None
    
    @property
    def email(self):
        """
        Obtiene el email desde el usuario relacionado
        
        Returns:
            str: Email del asesor
        """
        return self.user.email if self.user else None
    
    def get_active_properties_count(self):
        """
        Cuenta las propiedades activas (approved) del asesor
        
        Returns:
            int: Número de propiedades activas
        """
        return self.properties.filter_by(status='approved').count()
    