"""
Modelo: ClientAdvisorAssignment (Asignación Cliente-Asesor)

Descripción:
    Relación formal entre un cliente y un asesor inmobiliario.
    Permite tracking de qué asesor está atendiendo a cada cliente,
    independientemente de las propiedades.

Tabla: client_advisor_assignments

Estados:
    - active: Asignación activa
    - inactive: Asignación finalizada
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.dbConfig.baseModels import BaseModel


class ClientAdvisorAssignment(BaseModel):
    """
    Modelo de Asignación Cliente-Asesor
    
    Attributes:
        id (int): ID único (heredado)
        client_id (int): FK a users (cliente)
        advisor_id (int): FK a advisors (asesor)
        assigned_date (datetime): Fecha de asignación
        end_date (datetime): Fecha de finalización
        status (str): Estado (active, inactive)
        notes (str): Notas sobre la asignación
        created_at (datetime): Fecha de creación (heredado)
        updated_at (datetime): Última actualización (heredado)
    
    Relationships:
        client: Usuario cliente
        advisor: Asesor asignado
    """
    __tablename__ = "client_advisor_assignments"
    
    # ==========================================
    # RELACIONES
    # ==========================================
    
    client_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK al cliente"
    )
    
    advisor_id = Column(
        Integer,
        ForeignKey("advisors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK al asesor"
    )
    
    # ==========================================
    # FECHAS
    # ==========================================
    
    assigned_date = Column(
        TIMESTAMP,
        nullable=False,
        comment="Fecha de asignación"
    )
    
    end_date = Column(
        TIMESTAMP,
        nullable=True,
        comment="Fecha de finalización"
    )
    
    # ==========================================
    # ESTADO Y DETALLES
    # ==========================================
    
    status = Column(
        String(50),
        default='active',
        index=True,
        comment="Estado: active, inactive"
    )
    
    notes = Column(
        Text,
        comment="Notas sobre la asignación"
    )
    
    # ==========================================
    # RELACIONES SQLALCHEMY
    # ==========================================
    
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
        return f"<ClientAdvisorAssignment(client={self.client_id}, advisor={self.advisor_id})>"
    
    @property
    def is_active(self) -> bool:
        """Verifica si la asignación está activa"""
        return self.status == 'active'
    
    def deactivate(self, reason: str = None):
        """
        Desactiva la asignación
        
        Args:
            reason: Razón para desactivar
        """
        from datetime import datetime
        self.status = 'inactive'
        self.end_date = datetime.now()
        if reason:
            self.notes = f"{self.notes or ''}\nFinalizada: {reason}".strip()
