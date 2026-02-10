"""
Modelo: Property (Propiedades Inmobiliarias)

Descripción:
    Propiedades listadas en el sistema para venta o renta.
    Los clientes pueden publicar propiedades que luego son
    inspeccionadas y aprobadas por asesores.

Tabla: properties

Estados:
    - pending: Esperando inspección del asesor
    - approved: Aprobada y visible públicamente
    - rejected: Rechazada por el asesor
    - sold: Propiedad vendida/rentada

Relaciones:
    - owner: Many-to-One con User (quien publicó)
    - advisor: Many-to-One con Advisor (quien aprobó/gestiona)
    - images: One-to-Many con PropertyImage
    - appointments: One-to-Many con Appointment
    - favorites: One-to-Many con Favorite
"""

from sqlalchemy import Column, String, Text, NUMERIC, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.dbConfig.baseModels import BaseModel


class Property(BaseModel):
    """
    Modelo de Propiedad Inmobiliaria
    
    Attributes:
        id (int): ID único de la propiedad (heredado)
        title (str): Título de la propiedad
        description (str): Descripción detallada
        price (Decimal): Precio en la moneda local
        property_type (str): Tipo (house, apartment, land, commercial)
        transaction_type (str): Operación (sale, rent)
        
        # Ubicación
        address (str): Dirección completa
        city (str): Ciudad
        latitude (float): Coordenada latitud
        longitude (float): Coordenada longitud
        
        # Características
        bedrooms (int): Número de recámaras
        bathrooms (int): Número de baños
        square_meters (int): Metros cuadrados
        
        # Control de aprobación
        status (str): Estado (pending, approved, rejected, sold)
        submitted_by_user_id (int): FK a users (quien publicó)
        advisor_id (int): FK a advisors (quien gestiona)
        
        created_at (datetime): Fecha de creación (heredado)
        updated_at (datetime): Última actualización (heredado)
    
    Relationships:
        owner: Usuario que publicó la propiedad
        advisor: Asesor asignado que gestiona la propiedad
        images: Galería de imágenes
        appointments: Citas programadas para ver esta propiedad
        favorites: Usuarios que marcaron como favorita
    """
    __tablename__ = "properties"
    
    # ==========================================
    # INFORMACIÓN BÁSICA
    # ==========================================
    
    title = Column(
        String(255),
        nullable=False,
        comment="Título de la propiedad"
    )
    
    description = Column(
        Text,
        comment="Descripción detallada de la propiedad"
    )
    
    price = Column(
        NUMERIC(12, 2),
        nullable=False,
        comment="Precio en la moneda local"
    )
    
    property_type = Column(
        String(50),
        nullable=False,
        comment="Tipo: house, apartment, land, commercial"
    )
    
    transaction_type = Column(
        String(50),
        default='sale',
        comment="Operación: sale o rent"
    )
    
    # ==========================================
    # UBICACIÓN
    # ==========================================
    
    address = Column(
        Text,
        nullable=False,
        comment="Dirección completa"
    )
    
    city = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Ciudad"
    )
    
    latitude = Column(
        Float,
        nullable=False,
        comment="Coordenada latitud para el mapa"
    )
    
    longitude = Column(
        Float,
        nullable=False,
        comment="Coordenada longitud para el mapa"
    )
    
    # ==========================================
    # CARACTERÍSTICAS
    # ==========================================
    
    bedrooms = Column(
        Integer,
        default=0,
        comment="Número de recámaras"
    )
    
    bathrooms = Column(
        Integer,
        default=0,
        comment="Número de baños"
    )
    
    square_meters = Column(
        Integer,
        default=0,
        comment="Metros cuadrados de construcción"
    )
    
    # ==========================================
    # CONTROL DE APROBACIÓN
    # ==========================================
    
    status = Column(
        String(50),
        default='pending',
        index=True,
        comment="Estado: pending, approved, rejected, sold"
    )
    
    submitted_by_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        comment="FK al usuario que publicó la propiedad"
    )
    
    advisor_id = Column(
        Integer,
        ForeignKey("advisors.id"),
        comment="FK al asesor asignado"
    )
    
    # ==========================================
    # RELACIONES
    # ==========================================
    
    # Relación Many-to-One con User (quien publicó)
    owner = relationship(
        "User",
        foreign_keys=[submitted_by_user_id],
        back_populates="properties"
    )
    
    # Relación Many-to-One con Advisor (quien gestiona)
    advisor = relationship(
        "Advisor",
        foreign_keys=[advisor_id],
        back_populates="properties"
    )
    
    # Relación One-to-Many con PropertyImage
    images = relationship(
        "PropertyImage",
        back_populates="property",
        cascade="all, delete-orphan",  # Eliminar imágenes si se elimina la propiedad
        lazy="selectin"  # Carga automática de imágenes
    )
    
    # Relación One-to-Many con Appointment
    appointments = relationship(
        "Appointment",
        back_populates="property",
        lazy="dynamic"
    )
    
    # Relación One-to-Many con Favorite
    favorites = relationship(
        "Favorite",
        back_populates="property",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    def __repr__(self):
        """Representación de la propiedad para debugging"""
        return f"<Property(id={self.id}, title='{self.title[:30]}...', status='{self.status}')>"
    
    @property
    def is_available(self) -> bool:
        """
        Verifica si la propiedad está disponible para ver
        
        Returns:
            bool: True si status es 'approved'
        """
        return self.status == 'approved'
    
    @property
    def is_pending(self) -> bool:
        """Verifica si está pendiente de aprobación"""
        return self.status == 'pending'
    
    @property
    def is_sold(self) -> bool:
        """Verifica si ya fue vendida/rentada"""
        return self.status == 'sold'
    
    @property
    def main_image_url(self):
        """
        Obtiene la URL de la imagen principal
        
        Returns:
            str: URL de la imagen principal o None
        """
        main_img = next((img for img in self.images if img.is_main), None)
        return main_img.image_url if main_img else None
    
    @property
    def image_count(self) -> int:
        """
        Cuenta el número total de imágenes
        
        Returns:
            int: Número de imágenes
        """
        return len(self.images)
    
    def get_favorites_count(self) -> int:
        """
        Cuenta cuántos usuarios marcaron esta propiedad como favorita
        
        Returns:
            int: Número de favoritos
        """
        return self.favorites.count()
    
    def approve(self, advisor_id: int):
        """
        Aprueba la propiedad y asigna un asesor
        
        Args:
            advisor_id: ID del asesor que aprueba
        """
        self.status = 'approved'
        self.advisor_id = advisor_id
    
    def reject(self):
        """Rechaza la propiedad"""
        self.status = 'rejected'
    
    def mark_as_sold(self):
        """Marca la propiedad como vendida/rentada"""
        self.status = 'sold'
        