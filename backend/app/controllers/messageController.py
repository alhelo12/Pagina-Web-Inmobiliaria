"""
Controller: Messages

Endpoints para mensajes directos entre cliente y asesor.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.dbConfig.databaseSession import get_db
from app.services import messageService
from app.core.dependencies import get_current_user
from app.schemas import (
    MessageCreate,
    MessageResponse,
    MessageListResponse,
    ConversationCreate,
    ConversationResponse,
    ConversationListResponse,
)
from app.models import User, Advisor


router = APIRouter(prefix="/messages", tags=["Messages"])


@router.get("/conversations", response_model=ConversationListResponse)
def get_my_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista las conversaciones del usuario autenticado.
    Si es cliente: conversaciones donde es participant.
    Si es asesor: conversaciones donde el asesor es participant.
    """
    if current_user.advisor:
        conversations = messageService.get_conversations_by_advisor(
            db, current_user.advisor.id
        )
    else:
        conversations = messageService.get_conversations_by_user(
            db, current_user.id
        )

    items = []
    for conv in conversations:
        unread = messageService.count_unread_messages(db, conv.id, current_user.id)
        last_msg = conv.messages[-1] if conv.messages else None
        items.append(ConversationResponse(
            id=conv.id,
            user_id=conv.user_id,
            advisor_id=conv.advisor_id,
            last_message_at=conv.last_message_at,
            last_message=last_msg.content if last_msg else None,
            unread_count=unread,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            user_name=conv.user.full_name if conv.user else None,
            advisor_name=(
                conv.advisor.user.full_name
                if conv.advisor and conv.advisor.user
                else None
            )
        ))

    return ConversationListResponse(total=len(items), items=items)


@router.get("", response_model=MessageListResponse)
def get_messages(
    conversation_id: int = Query(..., description="ID de la conversación"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los mensajes de una conversación.
    """
    conv = messageService.get_conversation_by_id(db, conversation_id)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversación no encontrada"
        )

    is_participant = (
        conv.user_id == current_user.id
        or (current_user.advisor and conv.advisor_id == current_user.advisor.id)
    )
    if not is_participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta conversación"
        )

    messageService.mark_conversation_read(db, conversation_id, current_user.id)

    messages = messageService.get_messages(db, conversation_id)
    items = [
        MessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            sender_id=msg.sender_id,
            sender_name=msg.sender.full_name if msg.sender else None,
            content=msg.content,
            is_read=msg.is_read,
            created_at=msg.created_at,
            updated_at=msg.updated_at
        )
        for msg in messages
    ]

    return MessageListResponse(total=len(items), items=items)


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Envía un mensaje en una conversación existente.
    """
    conv = messageService.get_conversation_by_id(db, data.conversation_id)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversación no encontrada"
        )

    is_participant = (
        conv.user_id == current_user.id
        or (current_user.advisor and conv.advisor_id == current_user.advisor.id)
    )
    if not is_participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta conversación"
        )

    message = messageService.send_message(
        db, data.conversation_id, current_user.id, data.content
    )

    return MessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        sender_id=message.sender_id,
        sender_name=current_user.full_name,
        content=message.content,
        is_read=message.is_read,
        created_at=message.created_at,
        updated_at=message.updated_at
    )


@router.post("/start", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def start_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Inicia una nueva conversación con un asesor y envía el primer mensaje.
    Si la conversación ya existe, reutiliza esa.
    """
    if current_user.advisor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo los clientes pueden iniciar conversaciones"
        )

    advisor = db.query(Advisor).filter(Advisor.id == data.advisor_id).first()
    if not advisor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asesor no encontrado"
        )

    conversation = messageService.get_or_create_conversation(
        db, current_user.id, data.advisor_id
    )

    message = messageService.send_message(
        db, conversation.id, current_user.id, data.content
    )

    return ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        advisor_id=conversation.advisor_id,
        last_message_at=conversation.last_message_at,
        last_message=message.content,
        unread_count=0,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        user_name=current_user.full_name,
        advisor_name=advisor.user.full_name if advisor.user else None
    )
