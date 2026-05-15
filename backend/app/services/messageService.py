"""
Service: Message

Logica de negocio para mensajes directos entre cliente y asesor.
"""

import logging
import bleach
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_, and_, func, text
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Tuple

from app.models import Conversation, Message, User, Advisor
from app.services import notificationService

logger = logging.getLogger(__name__)


def get_or_create_conversation(
    db: Session,
    user_id: int,
    advisor_id: int
) -> Conversation:
    """
    Obtiene o crea una conversacion entre un cliente y un asesor.
    Maneja race conditions con IntegrityError.
    """
    conversation = db.query(Conversation).filter(
        Conversation.user_id == user_id,
        Conversation.advisor_id == advisor_id
    ).first()

    if conversation:
        return conversation

    conversation = Conversation(user_id=user_id, advisor_id=advisor_id)
    db.add(conversation)
    try:
        db.commit()
        db.refresh(conversation)
        return conversation
    except IntegrityError:
        db.rollback()
        existing = db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.advisor_id == advisor_id
        ).first()
        if existing:
            return existing
        raise


def get_conversations_by_user(
    db: Session,
    user_id: int,
    limit: int = 50,
    offset: int = 0
) -> Tuple[List[Conversation], int]:
    """
    Lista conversaciones del usuario ordenadas por ultimo mensaje.
    No carga todos los mensajes (evita N+1).
    """
    base_query = db.query(Conversation).filter(Conversation.user_id == user_id)
    
    total = base_query.count()
    
    conversations = (
        base_query
        .options(
            selectinload(Conversation.user),
            selectinload(Conversation.advisor).selectinload(Advisor.user),
            selectinload(Conversation.property)
        )
        .order_by(
            func.coalesce(
                Conversation.last_message_at,
                Conversation.created_at
            ).desc()
        )
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    return conversations, total


def get_conversations_by_advisor(
    db: Session,
    advisor_id: int,
    limit: int = 50,
    offset: int = 0
) -> Tuple[List[Conversation], int]:
    """
    Lista conversaciones del asesor ordenadas por ultimo mensaje.
    No carga todos los mensajes (evita N+1).
    """
    base_query = db.query(Conversation).filter(Conversation.advisor_id == advisor_id)
    
    total = base_query.count()
    
    conversations = (
        base_query
        .options(
            selectinload(Conversation.user),
            selectinload(Conversation.advisor).selectinload(Advisor.user),
            selectinload(Conversation.property)
        )
        .order_by(
            func.coalesce(
                Conversation.last_message_at,
                Conversation.created_at
            ).desc()
        )
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    return conversations, total


def search_conversations_by_advisor(
    db: Session,
    advisor_id: int,
    query: str,
    limit: int = 20,
    offset: int = 0
) -> Tuple[List[Conversation], int]:
    """
    Busca conversaciones del asesor por nombre de cliente.
    """
    search_pattern = f"%{query}%"
    
    base_query = (
        db.query(Conversation)
        .join(User, Conversation.user_id == User.id)
        .filter(Conversation.advisor_id == advisor_id)
        .filter(
            or_(
                User.full_name.ilike(search_pattern),
                User.email.ilike(search_pattern)
            )
        )
    )
    
    total = base_query.count()
    
    conversations = (
        base_query
        .options(
            selectinload(Conversation.user),
            selectinload(Conversation.advisor).selectinload(Advisor.user),
            selectinload(Conversation.property)
        )
        .order_by(
            func.coalesce(
                Conversation.last_message_at,
                Conversation.created_at
            ).desc()
        )
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    return conversations, total


def get_messages(
    db: Session,
    conversation_id: int,
    limit: int = 50,
    offset: int = 0,
    before: Optional[str] = None
) -> Tuple[List[Message], int]:
    """
    Obtiene mensajes de una conversacion con paginacion.
    
    Args:
        before: Timestamp ISO para cargar mensajes anteriores (scroll up)
    """
    base_query = (
        db.query(Message)
        .options(selectinload(Message.sender))
        .filter(Message.conversation_id == conversation_id)
    )
    
    if before:
        base_query = base_query.filter(Message.created_at < before)
    
    total = base_query.count()
    
    messages = (
        base_query
        .order_by(Message.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    messages.reverse()
    
    return messages, total


def send_message(
    db: Session,
    conversation_id: int,
    sender_id: int,
    content: str
) -> Message:
    """
    Envia un mensaje y actualiza last_message_at de la conversacion.
    Single transaction, sanitiza contenido.
    """
    sanitized_content = bleach.clean(content, tags=[], strip=True)
    
    message = Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=sanitized_content
    )
    db.add(message)
    db.flush()
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    if conversation:
        conversation.last_message_at = message.created_at
    
    db.commit()
    db.refresh(message)

    try:
        if conversation:
            sender = db.query(User).filter(User.id == sender_id).first()
            sender_name = sender.full_name if sender else "Un usuario"
            sender_is_user = conversation.user_id == sender_id
            recipient_id = conversation.advisor.user_id if sender_is_user else conversation.user_id
            if recipient_id:
                notificationService.create_notification(
                    db=db,
                    user_id=recipient_id,
                    notification_type="message_received",
                    title="Nuevo mensaje",
                    message=f"Tienes un nuevo mensaje de {sender_name}"
                )
    except Exception as e:
        logger.error(f"Error creando notificacion: {e}")

    return message


def get_conversation_by_id(
    db: Session,
    conversation_id: int
) -> Optional[Conversation]:
    """
    Obtiene una conversacion por ID.
    """
    return (
        db.query(Conversation)
        .options(
            selectinload(Conversation.advisor).selectinload(Advisor.user)
        )
        .filter(Conversation.id == conversation_id)
        .first()
    )


def mark_conversation_read(
    db: Session,
    conversation_id: int,
    reader_id: int
) -> int:
    """
    Marca todos los mensajes no leidos de la conversacion como leidos.
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
    Cuenta mensajes no leidos en una conversacion para un usuario.
    """
    return db.query(Message).filter(
        Message.conversation_id == conversation_id,
        Message.sender_id != user_id,
        Message.is_read == False
    ).count()
