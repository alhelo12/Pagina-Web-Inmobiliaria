"""
Service: Message

Lógica de negocio para mensajes directos entre cliente y asesor.
"""

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_, and_, func
from typing import List, Optional, Tuple

from app.models import Conversation, Message, User, Advisor


def get_or_create_conversation(
    db: Session,
    user_id: int,
    advisor_id: int
) -> Conversation:
    """
    Obtiene o crea una conversación entre un cliente y un asesor.

    Args:
        db: Sesión de base de datos
        user_id: ID del usuario cliente
        advisor_id: ID del asesor

    Returns:
        Conversation creada o existente
    """
    conversation = db.query(Conversation).filter(
        Conversation.user_id == user_id,
        Conversation.advisor_id == advisor_id
    ).first()

    if conversation:
        return conversation

    conversation = Conversation(user_id=user_id, advisor_id=advisor_id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_conversations_by_user(
    db: Session,
    user_id: int
) -> List[Conversation]:
    """
    Lista conversaciones del usuario ordenadas por último mensaje.

    Args:
        db: Sesión de base de datos
        user_id: ID del usuario

    Returns:
        Lista de conversaciones con relaciones cargadas
    """
    return (
        db.query(Conversation)
        .options(
            selectinload(Conversation.user),
            selectinload(Conversation.advisor).selectinload(Advisor.user),
            selectinload(Conversation.messages)
        )
        .filter(Conversation.user_id == user_id)
        .order_by(
            func.coalesce(
                Conversation.last_message_at,
                Conversation.created_at
            ).desc()
        )
        .all()
    )


def get_conversations_by_advisor(
    db: Session,
    advisor_id: int
) -> List[Conversation]:
    """
    Lista conversaciones del asesor ordenadas por último mensaje.

    Args:
        db: Sesión de base de datos
        advisor_id: ID del asesor

    Returns:
        Lista de conversaciones con relaciones cargadas
    """
    return (
        db.query(Conversation)
        .options(
            selectinload(Conversation.user),
            selectinload(Conversation.advisor).selectinload(Advisor.user),
            selectinload(Conversation.messages)
        )
        .filter(Conversation.advisor_id == advisor_id)
        .order_by(
            func.coalesce(
                Conversation.last_message_at,
                Conversation.created_at
            ).desc()
        )
        .all()
    )


def get_messages(
    db: Session,
    conversation_id: int
) -> List[Message]:
    """
    Obtiene mensajes de una conversación.

    Args:
        db: Sesión de base de datos
        conversation_id: ID de la conversación

    Returns:
        Lista de mensajes ordenados por fecha
    """
    return (
        db.query(Message)
        .options(selectinload(Message.sender))
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )


def send_message(
    db: Session,
    conversation_id: int,
    sender_id: int,
    content: str
) -> Message:
    """
    Envía un mensaje y actualiza last_message_at de la conversación.

    Args:
        db: Sesión de base de datos
        conversation_id: ID de la conversación
        sender_id: ID del usuario que envía
        content: Contenido del mensaje

    Returns:
        Message creado
    """
    message = Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=content
    )
    db.add(message)

    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    if conversation:
        conversation.last_message_at = message.created_at.strftime("%Y-%m-%dT%H:%M:%S")

    db.commit()
    db.refresh(message)
    return message


def get_conversation_by_id(
    db: Session,
    conversation_id: int
) -> Optional[Conversation]:
    """
    Obtiene una conversación por ID.

    Args:
        db: Sesión de base de datos
        conversation_id: ID de la conversación

    Returns:
        Conversation o None
    """
    return db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()


def mark_conversation_read(
    db: Session,
    conversation_id: int,
    reader_id: int
) -> int:
    """
    Marca todos los mensajes no leídos de la conversación como leídos,
    excepto los enviados por el lector.

    Args:
        db: Sesión de base de datos
        conversation_id: ID de la conversación
        reader_id: ID del usuario que marca como leído

    Returns:
        Número de mensajes marcados como leídos
    """
    result = db.query(Message).filter(
        Message.conversation_id == conversation_id,
        Message.sender_id != reader_id,
        Message.is_read == False
    ).update({"is_read": True}, synchronize_session=False)
    db.commit()
    return result


def count_unread_messages(
    db: Session,
    conversation_id: int,
    user_id: int
) -> int:
    """
    Cuenta mensajes no leídos en una conversación para un usuario.

    Args:
        db: Sesión de base de datos
        conversation_id: ID de la conversación
        user_id: ID del usuario

    Returns:
        Número de mensajes no leídos
    """
    return db.query(Message).filter(
        Message.conversation_id == conversation_id,
        Message.sender_id != user_id,
        Message.is_read == False
    ).count()
