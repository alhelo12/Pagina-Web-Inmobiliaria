"""
Modelo: ContactInquiry (Consultas del Formulario de Contacto)

Descripcion:
    Consultas enviadas desde el formulario de contacto publico del sitio web.
    Cualquier visitante (sin autenticacion) puede enviar una consulta y
    todos los asesores activos reciben una notificacion automaticamente.

Tabla: contact_inquiries

Estados:
    - new: Consulta recien recibida, sin gestionar
    - contacted: Un asesor ya se puso en contacto con el cliente
    - closed: Consulta cerrada/descartada
"""

from sqlalchemy import Column, String, Text
from app.dbConfig.baseModels import BaseModel


class ContactInquiry(BaseModel):
    """
    Modelo de Consulta de Contacto

    Attributes:
        id (int): ID unico (heredado)
        name (str): Nombre completo del remitente
        email (str): Correo electronico de contacto
        phone (str): Telefono de contacto (opcional)
        service (str): Servicio de interes (compra/venta/renta/asesoria)
        message (str): Mensaje o consulta
        status (str): Estado de gestion (new, contacted, closed)
        created_at (datetime): Fecha de creacion (heredado)
        updated_at (datetime): Ultima actualizacion (heredado)
    """
    __tablename__ = "contact_inquiries"

    name = Column(
        String(100),
        nullable=False,
        comment="Nombre completo del remitente"
    )

    email = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Correo electronico de contacto"
    )

    phone = Column(
        String(20),
        nullable=True,
        comment="Telefono de contacto (opcional)"
    )

    service = Column(
        String(50),
        nullable=False,
        comment="Servicio de interes: compra, venta, renta, asesoria"
    )

    message = Column(
        Text,
        nullable=False,
        comment="Mensaje o consulta del visitante"
    )

    status = Column(
        String(20),
        nullable=False,
        default='new',
        index=True,
        comment="Estado: new, contacted, closed"
    )

    def __repr__(self):
        return f"<ContactInquiry(id={self.id}, name='{self.name[:30]}', status='{self.status}')>"

    def mark_contacted(self):
        """Marca la consulta como contactada"""
        self.status = 'contacted'

    def mark_closed(self):
        """Cierra la consulta"""
        self.status = 'closed'
