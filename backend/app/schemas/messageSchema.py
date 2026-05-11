"""
Schemas de Mensajes (Pydantic)

DTOs para validación de datos de mensajes directos entre
cliente y asesor asignado.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class MessageCreate(BaseModel):
    conversation_id: int = Field(..., description="ID de la conversación")
    content: str = Field(..., min_length=1, max_length=5000, description="Contenido del mensaje")


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    sender_name: Optional[str] = None
    content: str
    is_read: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationCreate(BaseModel):
    advisor_id: int = Field(..., description="ID del asesor")
    content: str = Field(..., min_length=1, max_length=5000, description="Contenido del primer mensaje")


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    advisor_id: int
    last_message_at: Optional[str] = None
    last_message: Optional[str] = None
    unread_count: int = 0
    created_at: datetime
    updated_at: datetime
    user_name: Optional[str] = None
    advisor_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ConversationListResponse(BaseModel):
    total: int
    items: List[ConversationResponse]

    model_config = ConfigDict(from_attributes=True)


class MessageListResponse(BaseModel):
    total: int
    items: List[MessageResponse]

    model_config = ConfigDict(from_attributes=True)
