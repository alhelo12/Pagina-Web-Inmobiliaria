"""
Modelo: Notification (Notificaciones)

Descripción:
    Notificaciones para informar a los clientes sobre el estado
    de sus propiedades y acciones de asesores.

Tabla: notifications

Tipos de notificación:
    - advisor_assigned: Un asesor tomó la propiedad
    - approved: Propiedad aprobada
    - rejected: Propiedad rechazada
    - sold: Propiedad vendida/rentada
    - property_updated: Propiedad actualizada
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.dbConfig.baseModels import BaseModel


class Notification(BaseModel):
    """
    Modelo de Notificación
    
    Attributes:
        id (int): ID único (heredado)
        user_id (int): FK al usuario que recibe la notificación
        property_id (int): FK a la propiedad relacionada
        type (str): Tipo de notificación
        title (str): Título de la notificación
        message (str): Mensaje detallado
        is_read (bool): Si el usuario la ha leído
        created_at (datetime): Fecha de creación (heredado)
    """
    __tablename__ = "notifications"
    
    # ==========================================
    # RELACIONES
    # ==========================================
    
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
        comment="Usuario que recibe la notificación"
    )
    
    property_id = Column(
        Integer,
        ForeignKey("properties.id"),
        nullable=True,
        comment="Propiedad relacionada (opcional)"
    )
    
    # ==========================================
    # CONTENIDO
    # ==========================================
    
    type = Column(
        String(50),
        nullable=False,
        comment="Tipo: advisor_assigned, approved, rejected, sold, property_updated"
    )
    
    title = Column(
        String(255),
        nullable=False,
        comment="Título corto de la notificación"
    )
    
    message = Column(
        Text,
        nullable=False,
        comment="Mensaje detallado de la notificación"
    )
    
    # ==========================================
    # ESTADO
    # ==========================================
    
    is_read = Column(
        Boolean,
        default=False,
        comment="Si la notificación ha sido leída"
    )
    
    # ==========================================
    # RELACIONES SQLALCHEMY
    # ==========================================
    
    user = relationship(
        "User",
        back_populates="notifications"
    )
    
    property = relationship(
        "Property",
        back_populates="notifications"
    )
    
    # ==========================================
    # MÉTODOS AUXILIARES
    # ==========================================
    
    def mark_as_read(self):
        """Marca la notificación como leída"""
        self.is_read = True
    
    def mark_as_unread(self):
        """Marca la notificación como no leída"""
        self.is_read = False
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.type}', user_id={self.user_id})>"