"""
Modelo: ActivityLog (Registro de Actividad)

Descripción:
    Registro automático de acciones realizadas por los usuarios.
    Útil para auditoría, debugging y dashboards de actividad.

Tabla: activity_logs
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.dbConfig.baseModels import BaseModel


class ActivityLog(BaseModel):
    """
    Modelo de Registro de Actividad
    
    Attributes:
        id (int): ID único (heredado)
        user_id (int): FK a users (quien realizó la acción)
        action (str): Tipo de acción realizada
        entity_type (str): Tipo de entidad afectada
        entity_id (int): ID de la entidad afectada
        details (str): Detalles adicionales en JSON
        ip_address (str): IP del usuario
        created_at (datetime): Fecha de creación (heredado)
    """
    __tablename__ = "activity_logs"
    
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Usuario que realizó la acción"
    )
    
    action = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Tipo de acción: login, property_created, property_viewed, etc."
    )
    
    entity_type = Column(
        String(50),
        nullable=True,
        comment="Tipo de entidad: property, appointment, user, message"
    )
    
    entity_id = Column(
        Integer,
        nullable=True,
        comment="ID de la entidad afectada"
    )
    
    details = Column(
        Text,
        nullable=True,
        comment="Detalles adicionales (JSON)"
    )
    
    ip_address = Column(
        String(45),
        nullable=True,
        comment="Dirección IP del usuario"
    )
    
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<ActivityLog(user={self.user_id}, action='{self.action}', entity='{self.entity_type}')>"
