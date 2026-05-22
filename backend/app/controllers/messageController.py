"""
Controller: Messages

Endpoints para mensajes directos entre cliente y asesor.
"""

import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.dbConfig.databaseSession import get_db
from app.services import messageService
from app.core.dependencies import get_current_user
from app.core.websocket import manager
from app.schemas import (
    MessageCreate,
    MessageResponse,
    MessageListResponse,
    ConversationCreate,
    ConversationResponse,
    ConversationListResponse,
    PropertyBrief,
)
from app.models import User, Advisor, Property


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/messages", tags=["Messages"])


@router.get("/conversations", response_model=ConversationListResponse)
def get_my_conversations(
    page: int = Query(1, ge=1, description="Pagina"),
    limit: int = Query(50, ge=1, le=100, description="Por pagina"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista las conversaciones del usuario autenticado con paginacion.
    """
    offset = (page - 1) * limit
    
    if current_user.advisor:
        conversations, total = messageService.get_conversations_by_advisor(
            db, current_user.advisor.id, limit=limit, offset=offset
        )
    else:
        conversations, total = messageService.get_conversations_by_user(
            db, current_user.id, limit=limit, offset=offset
        )

    items = []
    for conv in conversations:
        unread = messageService.count_unread_messages(db, conv.id, current_user.id)
        last_msg = conv.messages[-1] if conv.messages else None
        
        property_brief = None
        if conv.property:
            property_brief = PropertyBrief(
                id=conv.property.id,
                title=conv.property.title,
                property_type=conv.property.property_type,
                city=conv.property.city
            )
        
        items.append(ConversationResponse(
            id=conv.id,
            user_id=conv.user_id,
            advisor_id=conv.advisor_id,
            property_id=conv.property_id,
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
            ),
            property=property_brief
        ))

    return ConversationListResponse(total=total, items=items)


@router.get("/conversations/search")
def search_conversations(
    q: str = Query(..., min_length=1, description="Termino de busqueda"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Busca conversaciones por nombre de cliente (solo asesores).
    """
    if not current_user.advisor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los asesores pueden buscar conversaciones"
        )
    
    offset = (page - 1) * limit
    conversations, total = messageService.search_conversations_by_advisor(
        db, current_user.advisor.id, q, limit=limit, offset=offset
    )
    
    items = []
    for conv in conversations:
        unread = messageService.count_unread_messages(db, conv.id, current_user.id)
        last_msg = conv.messages[-1] if conv.messages else None
        
        property_brief = None
        if conv.property:
            property_brief = PropertyBrief(
                id=conv.property.id,
                title=conv.property.title,
                property_type=conv.property.property_type,
                city=conv.property.city
            )
        
        items.append(ConversationResponse(
            id=conv.id,
            user_id=conv.user_id,
            advisor_id=conv.advisor_id,
            property_id=conv.property_id,
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
            ),
            property=property_brief
        ))
    
    return {"total": total, "items": items}


@router.get("", response_model=MessageListResponse)
def get_messages(
    conversation_id: int = Query(..., description="ID de la conversacion"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    before: str = Query(None, description="Timestamp ISO para cargar mensajes anteriores"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene mensajes de una conversacion con paginacion.
    """
    conv = messageService.get_conversation_by_id(db, conversation_id)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversacion no encontrada"
        )

    is_participant = (
        conv.user_id == current_user.id
        or (current_user.advisor and conv.advisor_id == current_user.advisor.id)
    )
    if not is_participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta conversacion"
        )

    messages, total = messageService.get_messages(
        db, conversation_id, limit=limit, offset=offset, before=before
    )
    
    has_more = (offset + len(messages)) < total
    
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

    return MessageListResponse(total=total, items=items, has_more=has_more)


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Envia un mensaje en una conversacion existente.
    """
    conv = messageService.get_conversation_by_id(db, data.conversation_id)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversacion no encontrada"
        )

    is_participant = (
        conv.user_id == current_user.id
        or (current_user.advisor and conv.advisor_id == current_user.advisor.id)
    )
    if not is_participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta conversacion"
        )

    message = messageService.send_message(
        db, data.conversation_id, current_user.id, data.content
    )

    try:
        is_client = conv.user_id == current_user.id
        recipient_user_id = conv.advisor.user_id if is_client else conv.user_id
        sender_info = {
            "id": current_user.id,
            "name": current_user.full_name or current_user.email,
            "role": "client" if is_client else "advisor"
        }
        message_data = {
            "type": "message",
            "data": {
                "id": message.id,
                "conversation_id": message.conversation_id,
                "sender_id": message.sender_id,
                "content": message.content,
                "is_read": message.is_read,
                "created_at": message.created_at.isoformat() if message.created_at else None,
                "sender": sender_info
            }
        }
        await manager.send_personal_message(message_data, current_user.id)
        if recipient_user_id:
            await manager.send_personal_message(message_data, recipient_user_id)
    except Exception as e:
        logger.error(f"Error broadcasting message via WebSocket: {e}")

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
async def start_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Inicia una nueva conversacion con un asesor y envia el primer mensaje.
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
    
    if data.property_id and not conversation.property_id:
        property_exists = db.query(Property).filter(
            Property.id == data.property_id,
            Property.submitted_by_user_id == current_user.id
        ).first()
        if property_exists:
            conversation.property_id = data.property_id
            db.commit()

    message = messageService.send_message(
        db, conversation.id, current_user.id, data.content
    )

    try:
        sender_info = {
            "id": current_user.id,
            "name": current_user.full_name or current_user.email,
            "role": "client"
        }
        message_data = {
            "type": "message",
            "data": {
                "id": message.id,
                "conversation_id": message.conversation_id,
                "sender_id": message.sender_id,
                "content": message.content,
                "is_read": message.is_read,
                "created_at": message.created_at.isoformat() if message.created_at else None,
                "sender": sender_info
            }
        }
        await manager.send_personal_message(message_data, current_user.id)
        recipient_user_id = advisor.user_id if advisor else None
        if recipient_user_id:
            await manager.send_personal_message(message_data, recipient_user_id)
    except Exception as e:
        logger.error(f"Error broadcasting via WebSocket: {e}")

    property_brief = None
    if conversation.property:
        property_brief = PropertyBrief(
            id=conversation.property.id,
            title=conversation.property.title,
            property_type=conversation.property.property_type,
            city=conversation.property.city
        )

    return ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        advisor_id=conversation.advisor_id,
        property_id=conversation.property_id,
        last_message_at=conversation.last_message_at,
        last_message=message.content,
        unread_count=0,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        user_name=current_user.full_name,
        advisor_name=advisor.user.full_name if advisor.user else None,
        property=property_brief
    )


@router.post("/conversations/{conversation_id}/read")
def mark_conversation_read(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Marca una conversacion como leida sin devolver mensajes.
    """
    conv = messageService.get_conversation_by_id(db, conversation_id)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversacion no encontrada"
        )

    is_participant = (
        conv.user_id == current_user.id
        or (current_user.advisor and conv.advisor_id == current_user.advisor.id)
    )
    if not is_participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta conversacion"
        )

    marked = messageService.mark_conversation_read(db, conversation_id, current_user.id)
    
    return {"marked_read": marked}
