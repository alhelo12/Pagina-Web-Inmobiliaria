"""
Modelo: Appointment (Citas)

Descripción:
    Citas programadas entre clientes y asesores.
    Puede ser para:
    - Ver una propiedad (viewing)
    - Inspección de propiedad del vendedor (inspection)

Tabla: appointments

Estados:
    - pending: Pendiente de confirmación
    - confirmed: Confirmada
    - completed: Completada
    - cancelled: Cancelada

Relaciones:
    - client: Many-to-One con User (cliente)
    - advisor: Many-to-One con Advisor (asesor)
    - property: Many-to-One con Property (opcional)
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.dbConfig.baseModels import BaseModel


class Appointment(BaseModel):
    """
    Modelo de Cita
    
    Attributes:
        id (int): ID único de la cita (heredado)
        client_id (int): FK a users (cliente)
        advisor_id (int): FK a advisors (asesor)
        property_id (int): FK a properties (opcional)
        
        appointment_type (str): Tipo (viewing, inspection)
        scheduled_date (datetime): Fecha y hora programada
        status (str): Estado (pending, confirmed, completed, cancelled)
        
        notes (str): Notas adicionales
        created_at (datetime): Fecha de creación (heredado)
        updated_at (datetime): Última actualización (heredado)
    
    Relationships:
        client: Usuario cliente que agenda la cita
        advisor: Asesor que atenderá la cita
        property: Propiedad relacionada (si aplica)
    """
    __tablename__ = "appointments"
    
    # ==========================================
    # PARTICIPANTES
    # ==========================================
    
    client_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK al usuario cliente"
    )
    
    advisor_id = Column(
        Integer,
        ForeignKey("advisors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK al asesor"
    )
    
    property_id = Column(
        Integer,
        ForeignKey("properties.id", ondelete="CASCADE"),
        comment="FK a la propiedad (opcional)"
    )
    
    # ==========================================
    # INFORMACIÓN DE LA CITA
    # ==========================================
    
    appointment_type = Column(
        String(50),
        default='viewing',
        comment="Tipo: viewing (ver propiedad) o inspection (inspección)"
    )
    
    scheduled_date = Column(
        TIMESTAMP,
        nullable=False,
        index=True,
        comment="Fecha y hora programada"
    )
    
    status = Column(
        String(50),
        default='pending',
        index=True,
        comment="Estado: pending, confirmed, completed, cancelled"
    )
    
    notes = Column(
        Text,
        comment="Notas adicionales sobre la cita"
    )
    
    # ==========================================
    # RELACIONES
    # ==========================================
    
    # Relación Many-to-One con User (cliente)
    client = relationship(
        "User",
        foreign_keys=[client_id],
        back_populates="appointments_as_client"
    )
    
    # Relación Many-to-One con Advisor
    advisor = relationship(
        "Advisor",
        foreign_keys=[advisor_id],
        back_populates="appointments"
    )
    
    # Relación Many-to-One con Property
    related_property = relationship(
        "Property",
        back_populates="appointments"
    )
    
    def __repr__(self):
        """Representación de la cita para debugging"""
        return f"<Appointment(id={self.id}, type='{self.appointment_type}', status='{self.status}')>"
    
    @property
    def is_pending(self) -> bool:
        """Verifica si la cita está pendiente"""
        return self.status == 'pending'
    
    @property
    def is_confirmed(self) -> bool:
        """Verifica si la cita está confirmada"""
        return self.status == 'confirmed'
    
    @property
    def is_completed(self) -> bool:
        """Verifica si la cita fue completada"""
        return self.status == 'completed'
    
    @property
    def is_cancelled(self) -> bool:
        """Verifica si la cita fue cancelada"""
        return self.status == 'cancelled'
    
    def confirm(self):
        """Confirma la cita"""
        if self.status == 'pending':
            self.status = 'confirmed'
    
    def complete(self):
        """Marca la cita como completada"""
        if self.status == 'confirmed':
            self.status = 'completed'
    
    def cancel(self):
        """Cancela la cita"""
        if self.status in ['pending', 'confirmed']:
            self.status = 'cancelled'
    
    def is_viewing(self) -> bool:
        """Verifica si es una cita para ver propiedad"""
        return self.appointment_type == 'viewing'
    
    def is_inspection(self) -> bool:
        """Verifica si es una inspección de propiedad"""
        return self.appointment_type == 'inspection'
    