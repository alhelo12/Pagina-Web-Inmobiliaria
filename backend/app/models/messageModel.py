"""
Modelo: Message (Mensajes)

Descripcion:
    Mensajes directos entre cliente y asesor asignado.

Tabla: conversations
    Hilo de conversacion entre dos usuarios.

Tabla: messages
    Mensajes individuales dentro de una conversacion.
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.dbConfig.baseModels import BaseModel


class Conversation(BaseModel):
    """
    Modelo de Conversacion

    Un hilo de chat entre un cliente y su asesor asignado.
    """
    __tablename__ = "conversations"
    __table_args__ = (
        UniqueConstraint('user_id', 'advisor_id', name='uq_conversation_user_advisor'),
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    advisor_id = Column(
        Integer,
        ForeignKey("advisors.id"),
        nullable=False,
        index=True
    )

    property_id = Column(
        Integer,
        ForeignKey("properties.id"),
        nullable=True,
        index=True,
        comment="FK a la propiedad asociada (opcional)"
    )

    last_message_at = Column(
        DateTime,
        nullable=True,
        index=True
    )

    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="conversations"
    )

    advisor = relationship(
        "Advisor",
        foreign_keys=[advisor_id],
        back_populates="conversations"
    )

    property = relationship(
        "Property",
        foreign_keys=[property_id],
        back_populates="conversations"
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at.asc()"
    )

    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id}, advisor_id={self.advisor_id})>"


class Message(BaseModel):
    """
    Modelo de Mensaje

    Mensaje individual dentro de una conversacion.
    """
    __tablename__ = "messages"

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id"),
        nullable=False,
        index=True
    )

    sender_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    content = Column(
        Text,
        nullable=False
    )

    is_read = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )

    sender = relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_messages"
    )

    def __repr__(self):
        return f"<Message(id={self.id}, sender_id={self.sender_id})>"
