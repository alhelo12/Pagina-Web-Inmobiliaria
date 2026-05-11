"""
Modelo: Message (Mensajes)

Descripción:
    Mensajes directos entre cliente y asesor asignado.

Tabla: conversations
    Hilo de conversación entre dos usuarios.

Tabla: messages
    Mensajes individuales dentro de una conversación.
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.dbConfig.baseModels import BaseModel


class Conversation(BaseModel):
    """
    Modelo de Conversación

    Un hilo de chat entre un cliente y su asesor asignado.

    Attributes:
        id (int): ID único (heredado)
        user_id (int): FK al usuario cliente
        advisor_id (int): FK al asesor
        last_message_at (datetime): Fecha del último mensaje (para ordenar)
    """
    __tablename__ = "conversations"

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

    last_message_at = Column(
        String(30),
        nullable=True,
        index=True
    )

    # ==========================================
    # RELACIONES SQLALCHEMY
    # ==========================================

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

    Mensaje individual dentro de una conversación.

    Attributes:
        id (int): ID único (heredado)
        conversation_id (int): FK a la conversación
        sender_id (int): FK al usuario que envía
        content (str): Contenido del mensaje
        is_read (bool): Si el receptor lo ha leído
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

    # ==========================================
    # RELACIONES SQLALCHEMY
    # ==========================================

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
