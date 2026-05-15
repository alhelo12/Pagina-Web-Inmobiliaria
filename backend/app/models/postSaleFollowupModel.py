"""
Modelo: PostSaleFollowup (Seguimiento Post-Venta)

Descripción:
    Seguimiento automatizado después de que una propiedad es vendida/rentada.
    Incluye encuestas de satisfacción, llamadas de seguimiento, solicitud de
    referidos y recordatorios de mantenimiento.

Tabla: post_sale_followups

Tipos de seguimiento:
    - satisfaction_survey: Encuesta de satisfacción (día +7)
    - check_in_call: Llamada de seguimiento (día +30)
    - referral_request: Solicitud de referido (día +60)
    - maintenance_reminder: Recordatorio de mantenimiento (día +90)

Estados:
    - pending: Pendiente de completar
    - completed: Completado exitosamente
    - skipped: Omitido
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, TIMESTAMP, SmallInteger
from sqlalchemy.orm import relationship
from app.dbConfig.baseModels import BaseModel


class PostSaleFollowup(BaseModel):
    """
    Modelo de Seguimiento Post-Venta
    
    Attributes:
        id (int): ID único (heredado)
        property_id (int): FK a properties (propiedad vendida)
        client_id (int): FK a users (cliente que compró/rentó)
        advisor_id (int): FK a advisors (asesor responsable)
        sale_date (datetime): Fecha de la venta
        followup_type (str): Tipo de seguimiento
        scheduled_date (datetime): Fecha programada
        completed_date (datetime): Fecha de completado
        status (str): Estado (pending, completed, skipped)
        notes (str): Notas adicionales
        satisfaction_score (int): Puntuación 1-5
        created_at (datetime): Fecha de creación (heredado)
        updated_at (datetime): Última actualización (heredado)
    
    Relationships:
        property: Propiedad vendida
        client: Usuario cliente
        advisor: Asesor responsable
    """
    __tablename__ = "post_sale_followups"
    
    # ==========================================
    # RELACIONES
    # ==========================================
    
    property_id = Column(
        Integer,
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK a la propiedad vendida"
    )
    
    client_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK al cliente"
    )
    
    advisor_id = Column(
        Integer,
        ForeignKey("advisors.id", ondelete="SET NULL"),
        nullable=True,
        comment="FK al asesor responsable"
    )
    
    # ==========================================
    # INFORMACIÓN DE VENTA
    # ==========================================
    
    sale_date = Column(
        TIMESTAMP,
        nullable=False,
        comment="Fecha de la venta/renta"
    )
    
    # ==========================================
    # TIPO Y PROGRAMACIÓN
    # ==========================================
    
    followup_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Tipo: satisfaction_survey, check_in_call, referral_request, maintenance_reminder"
    )
    
    scheduled_date = Column(
        TIMESTAMP,
        nullable=False,
        index=True,
        comment="Fecha programada para el seguimiento"
    )
    
    completed_date = Column(
        TIMESTAMP,
        nullable=True,
        comment="Fecha en que se completó el seguimiento"
    )
    
    # ==========================================
    # ESTADO Y DETALLES
    # ==========================================
    
    status = Column(
        String(50),
        default='pending',
        index=True,
        comment="Estado: pending, completed, skipped"
    )
    
    notes = Column(
        Text,
        comment="Notas adicionales del seguimiento"
    )
    
    satisfaction_score = Column(
        SmallInteger,
        nullable=True,
        comment="Puntuación de satisfacción (1-5)"
    )
    
    # ==========================================
    # RELACIONES SQLALCHEMY
    # ==========================================
    
    related_property = relationship(
        "Property",
        foreign_keys=[property_id]
    )
    
    client = relationship(
        "User",
        foreign_keys=[client_id]
    )
    
    advisor = relationship(
        "Advisor",
        foreign_keys=[advisor_id]
    )
    
    # ==========================================
    # MÉTODOS AUXILIARES
    # ==========================================
    
    def __repr__(self):
        return f"<PostSaleFollowup(id={self.id}, type='{self.followup_type}', status='{self.status}')>"
    
    @property
    def is_pending(self) -> bool:
        """Verifica si está pendiente"""
        return self.status == 'pending'
    
    @property
    def is_completed(self) -> bool:
        """Verifica si fue completado"""
        return self.status == 'completed'
    
    @property
    def is_skipped(self) -> bool:
        """Verifica si fue omitido"""
        return self.status == 'skipped'
    
    def complete(self, notes: str = None, satisfaction_score: int = None):
        """
        Marca el seguimiento como completado
        
        Args:
            notes: Notas adicionales
            satisfaction_score: Puntuación de satisfacción (1-5)
        """
        from datetime import datetime
        self.status = 'completed'
        self.completed_date = datetime.now()
        if notes:
            self.notes = notes
        if satisfaction_score is not None:
            self.satisfaction_score = satisfaction_score
    
    def skip(self, reason: str = None):
        """
        Omite el seguimiento
        
        Args:
            reason: Razón para omitir
        """
        self.status = 'skipped'
        if reason:
            self.notes = f"Omitido: {reason}"
